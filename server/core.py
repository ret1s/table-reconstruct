import PIL
import cv2
import numpy as np
import pandas as pd
import torch
import os
import io
import urllib.parse
# import sys
# import json
from collections import OrderedDict, defaultdict
import xml.etree.ElementTree as ET
import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Patch

from paddleocr import PaddleOCR
# import pytesseract
# from pytesseract import Output
from fitz import Rect

import postprocess

cv2.setNumThreads(1)


def load_ocr_instance():
    ocr_instance = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=True)
    return ocr_instance


def load_detection_model():
    detection_model = torch.hub.load('ultralytics/yolov5', 'custom', 'weights/detection_wts.pt', force_reload=True, skip_validation=True, trust_repo=True)
    return detection_model


def load_structure_model():
    structure_model = torch.hub.load('ultralytics/yolov5', 'custom', 'weights/structure_wts.pt', force_reload=True, skip_validation=True, trust_repo=True)
    return structure_model


ocr_instance, detection_model, structure_model = load_ocr_instance(), load_detection_model(), load_structure_model()

detection_class_names = ['table', 'table rotated', 'no object']
structure_class_names = [
    'table', 'table column', 'table row', 'table column header',
    'table projected row header', 'table spanning cell', 'no object'
]

detection_class_map = {k: v for v, k in enumerate(detection_class_names)}
structure_class_map = {k: v for v, k in enumerate(structure_class_names)}

detection_class_thresholds = {
    'table': 0.5,
    'table rotated': 0.5,
    'no object': 10
}
structure_class_thresholds = {
    "table": 0.45,
    "table column": 0.6,
    "table row": 0.5,
    "table column header": 0.4,
    "table projected row header": 0.3,
    "table spanning cell": 0.5,
    "no object": 10
}


def PIL_to_cv(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def cv_to_PIL(cv_img):
    return PIL.Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


def table_detection(pil_img, imgsz=640):
    image = PIL_to_cv(pil_img)
    pred = detection_model(image, size=imgsz)
    pred = pred.xywhn[0]
    result = pred.detach().cpu().numpy()
    return result


def table_structure(pil_img, imgsz=640):
    image = PIL_to_cv(pil_img)
    pred = structure_model(image, size=imgsz)
    pred = pred.xywhn[0]
    result = pred.detach().cpu().numpy()
    return result


def crop_image(pil_img, detection_result):
    crop_images = []
    image = PIL_to_cv(pil_img)
    width = image.shape[1]
    height = image.shape[0]
    # print(width, height)
    for idx, result in enumerate(detection_result):
        class_id = int(result[5])
        score = float(result[4])
        min_x = result[0]
        min_y = result[1]
        w = result[2]
        h = result[3]

        if score < detection_class_thresholds[detection_class_names[class_id]]:
            continue

        x1 = int((min_x - w / 2) * width)
        y1 = int((min_y - h / 2) * height)
        x2 = int((min_x + w / 2) * width)
        y2 = int((min_y + h / 2) * height)
        # print(x1, y1, x2, y2)

        padding_x = max(int(0.02 * width), 30)
        padding_y = max(int(0.02 * height), 30)

        x1_pad = max(0, x1 - padding_x)
        y1_pad = max(0, y1 - padding_y)
        x2_pad = min(width, x2 + padding_x)
        y2_pad = min(height, y2 + padding_y)

        crop_image = image[y1_pad:y2_pad, x1_pad:x2_pad, :]
        crop_image = cv_to_PIL(crop_image)
        if detection_class_names[class_id] == 'table rotated':
            crop_image = crop_image.rotate(270, expand=True)

        crop_images.append(crop_image)

        cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

        label = f'{detection_class_names[class_id]} {score:.2f}'

        lw = max(round(sum(image.shape) / 2 * 0.003), 2)
        fontScale = lw / 3
        thickness = max(lw - 1, 1)
        w_label, h_label = cv2.getTextSize(label, 0, fontScale=fontScale, thickness=thickness)[0]
        cv2.rectangle(image, (x1, y1), (x1 + w_label, y1 - h_label - 3), (0, 0, 255), -1, cv2.LINE_AA)
        cv2.putText(image, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 255, 255), thickness=thickness, lineType=cv2.LINE_AA)

    return crop_images, cv_to_PIL(image)


def ocr(pil_img):
    image = PIL_to_cv(pil_img)
    result = ocr_instance.ocr(image)
    ocr_res = []

    for ps, (text, score) in result[0]:
        x1 = min(p[0] for p in ps)
        y1 = min(p[1] for p in ps)
        x2 = max(p[0] for p in ps)
        y2 = max(p[1] for p in ps)
        word_info = {
            'bbox': [x1, y1, x2, y2],
            'text': text
        }
        ocr_res.append(word_info)

    return ocr_res


def convert_stucture(page_tokens, pil_img, structure_result):
    image = PIL_to_cv(pil_img)

    width = image.shape[1]
    height = image.shape[0]
    # print(width, height)

    bboxes = []
    scores = []
    labels = []
    for idx, result in enumerate(structure_result):
        class_id = int(result[5])
        score = float(result[4])
        min_x = result[0]
        min_y = result[1]
        w = result[2]
        h = result[3]

        x1 = int((min_x - w / 2) * width)
        y1 = int((min_y - h / 2) * height)
        x2 = int((min_x + w / 2) * width)
        y2 = int((min_y + h / 2) * height)
        # print(x1, y1, x2, y2)

        bboxes.append([x1, y1, x2, y2])
        scores.append(score)
        labels.append(class_id)

    table_objects = []
    for bbox, score, label in zip(bboxes, scores, labels):
        table_objects.append({'bbox': bbox, 'score': score, 'label': label})
    # print('table_objects:', table_objects)

    table = {'objects': table_objects, 'page_num': 0}

    table_class_objects = [obj for obj in table_objects if obj['label'] == structure_class_map['table']]
    if len(table_class_objects) > 1:
        table_class_objects = sorted(table_class_objects, key=lambda x: x['score'], reverse=True)
    try:
        table_bbox = list(table_class_objects[0]['bbox'])
    except:
        table_bbox = (0, 0, 1000, 1000)
    # print('table_class_objects:', table_class_objects)
    # print('table_bbox:', table_bbox)

    tmp = Rect(table_bbox)
    for obj in table_objects:
        if structure_class_names[obj['label']] in ('table column', 'table row'):
            if postprocess.iob(obj['bbox'], table_bbox) >= 0.001:
                tmp.include_rect(obj['bbox'])
    table_bbox = (tmp[0], tmp[1], tmp[2], tmp[3])

    tokens_in_table = [token for token in page_tokens if postprocess.iob(token['bbox'], table_bbox) >= 0.001]
    # print('tokens_in_table:', tokens_in_table)

    table_structures, cells, confidence_score = postprocess.objects_to_cells(table, table_objects, tokens_in_table, structure_class_names, structure_class_thresholds)

    return table_structures, cells, confidence_score


def visualize_image(pil_img):
    plt.imshow(pil_img, interpolation='lanczos')
    plt.gcf().set_size_inches(10, 10)
    plt.axis('off')
    img_buf = io.BytesIO()
    plt.savefig(img_buf, bbox_inches='tight', dpi=150)
    plt.close()
    return PIL.Image.open(img_buf)


def visualize_ocr(pil_img, ocr_result):
    plt.imshow(pil_img, interpolation='lanczos')
    plt.gcf().set_size_inches(20, 20)
    ax = plt.gca()

    for idx, result in enumerate(ocr_result):
        bbox = result['bbox']
        text = result['text']
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=2, edgecolor='red', facecolor='none', linestyle='-')
        ax.add_patch(rect)
        ax.text(bbox[0], bbox[1], text, horizontalalignment='left', verticalalignment='bottom', color='blue', fontsize=7)

    plt.xticks([], [])
    plt.yticks([], [])

    plt.gcf().set_size_inches(10, 10)
    plt.axis('off')
    img_buf = io.BytesIO()
    plt.savefig(img_buf, bbox_inches='tight', dpi=150)
    plt.close()

    return PIL.Image.open(img_buf)


def get_bbox_decorations(data_type, label):
    if label == 0:
        if data_type == 'detection':
            return 'brown', 0.05, 3, '//'
        else:
            return 'brown', 0, 3, None
    elif label == 1:
        return 'red', 0.15, 2, None
    elif label == 2:
        return 'blue', 0.15, 2, None
    elif label == 3:
        return 'magenta', 0.2, 3, '//'
    elif label == 4:
        return 'cyan', 0.2, 4, '//'
    elif label == 5:
        return 'green', 0.2, 4, '\\\\'

    return 'gray', 0, 0, None


def visualize_structure(pil_img, structure_result):
    image = PIL_to_cv(pil_img)
    width = image.shape[1]
    height = image.shape[0]
    # print(width, height)

    plt.imshow(pil_img, interpolation='lanczos')
    plt.gcf().set_size_inches(20, 20)
    ax = plt.gca()

    for idx, result in enumerate(structure_result):
        class_id = int(result[5])
        score = float(result[4])
        min_x = result[0]
        min_y = result[1]
        w = result[2]
        h = result[3]

        if score < structure_class_thresholds[structure_class_names[class_id]]:
            continue

        x1 = int((min_x - w / 2) * width)
        y1 = int((min_y - h / 2) * height)
        x2 = int((min_x + w / 2) * width)
        y2 = int((min_y + h / 2) * height)
        # print(x1, y1, x2, y2)
        bbox = [x1, y1, x2, y2]

        color, alpha, linewidth, hatch = get_bbox_decorations('recognition', class_id)
        # Fill
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1],
                                    linewidth=linewidth, alpha=alpha,
                                    edgecolor='none',facecolor=color,
                                    linestyle=None)
        ax.add_patch(rect)
        # Hatch
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1],
                                    linewidth=1, alpha=0.4,
                                    edgecolor=color, facecolor='none',
                                    linestyle='--',hatch=hatch)
        ax.add_patch(rect)
        # Edge
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1],
                                    linewidth=linewidth,
                                    edgecolor=color, facecolor='none',
                                    linestyle='--')
        ax.add_patch(rect)

    plt.xticks([], [])
    plt.yticks([], [])

    legend_elements = []
    for class_name in structure_class_names[:-1]:
        color, alpha, linewidth, hatch = get_bbox_decorations('recognition', structure_class_map[class_name])
        legend_elements.append(
            Patch(facecolor='none', edgecolor=color, linestyle='--', label=class_name, hatch=hatch)
        )

    plt.legend(handles=legend_elements, bbox_to_anchor=(0.5, -0.02), loc='upper center', borderaxespad=0,
                    fontsize=10, ncol=3)
    plt.gcf().set_size_inches(10, 10)
    plt.axis('off')
    img_buf = io.BytesIO()
    plt.savefig(img_buf, bbox_inches='tight', dpi=150)
    plt.close()

    return PIL.Image.open(img_buf)


def visualize_cells(pil_img, cells):
    plt.imshow(pil_img, interpolation='lanczos')
    plt.gcf().set_size_inches(20, 20)
    ax = plt.gca()

    for cell in cells:
        bbox = cell['bbox']

        if cell['header']:
            facecolor = (1, 0, 0.45)
            edgecolor = (1, 0, 0.45)
            alpha = 0.3
            linewidth = 2
            hatch='//////'
        elif cell['subheader']:
            facecolor = (0.95, 0.6, 0.1)
            edgecolor = (0.95, 0.6, 0.1)
            alpha = 0.3
            linewidth = 2
            hatch='//////'
        else:
            facecolor = (0.3, 0.74, 0.8)
            edgecolor = (0.3, 0.7, 0.6)
            alpha = 0.3
            linewidth = 2
            hatch='\\\\\\\\\\\\'

        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=linewidth,
                                    edgecolor='none',facecolor=facecolor, alpha=0.1)
        ax.add_patch(rect)
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=linewidth,
                                    edgecolor=edgecolor,facecolor='none',linestyle='-', alpha=alpha)
        ax.add_patch(rect)
        rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=0,
                                    edgecolor=edgecolor,facecolor='none',linestyle='-', hatch=hatch, alpha=0.2)
        ax.add_patch(rect)

    plt.xticks([], [])
    plt.yticks([], [])

    legend_elements = [Patch(facecolor=(0.3, 0.74, 0.8), edgecolor=(0.3, 0.7, 0.6),
                                label='Data cell', hatch='\\\\\\\\\\\\', alpha=0.3),
                        Patch(facecolor=(1, 0, 0.45), edgecolor=(1, 0, 0.45),
                                label='Column header cell', hatch='//////', alpha=0.3),
                        Patch(facecolor=(0.95, 0.6, 0.1), edgecolor=(0.95, 0.6, 0.1),
                                label='Projected row header cell', hatch='//////', alpha=0.3)]
    plt.legend(handles=legend_elements, bbox_to_anchor=(0.5, -0.02), loc='upper center', borderaxespad=0,
                    fontsize=10, ncol=3)
    plt.gcf().set_size_inches(10, 10)
    plt.axis('off')
    img_buf = io.BytesIO()
    plt.savefig(img_buf, bbox_inches='tight', dpi=150)
    plt.close()

    return PIL.Image.open(img_buf)


# def pytess(cell_pil_img):
#     return ' '.join(pytesseract.image_to_data(cell_pil_img, output_type=Output.DICT, config='-c tessedit_char_blacklist=œ˜â€œï¬â™Ã©œ¢!|”?«“¥ --tessdata-dir tessdata --oem 3 --psm 6')['text']).strip()


# def resize(pil_img, size=1800):
#     length_x, width_y = pil_img.size
#     factor = max(1, size / length_x)
#     size = int(factor * length_x), int(factor * width_y)
#     pil_img = pil_img.resize(size, PIL.Image.ANTIALIAS)
#     return pil_img, factor


# def image_smoothening(img):
#     ret1, th1 = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
#     ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     blur = cv2.GaussianBlur(th2, (1, 1), 0)
#     ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return th3


# def remove_noise_and_smooth(pil_img):
#     img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)
#     filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 3)
#     kernel = np.ones((1, 1), np.uint8)
#     opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
#     closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
#     img = image_smoothening(img)
#     or_image = cv2.bitwise_or(img, closing)
#     pil_img = PIL.Image.fromarray(or_image)
#     return pil_img


# def extract_text_from_cells(pil_img, cells):
#     pil_img, factor = resize(pil_img)
#     #pil_img = remove_noise_and_smooth(pil_img)
#     #display(pil_img)
#     for cell in cells:
#         bbox = [x * factor for x in cell['bbox']]
#         cell_pil_img = pil_img.crop(bbox)
#         #cell_pil_img = remove_noise_and_smooth(cell_pil_img)
#         #cell_pil_img = tess_prep(cell_pil_img)
#         cell['cell text'] = pytess(cell_pil_img)
#     return cells


def extract_text_from_cells(cells, sep=' '):
    for cell in cells:
        spans = cell['spans']
        text = ''
        for span in spans:
            if 'text' in span:
                text += span['text'] + sep
        cell['cell_text'] = text.strip()
    return cells


def cells_to_csv(cells):
    if len(cells) > 0:
        num_columns = max([max(cell['column_nums']) for cell in cells]) + 1
        num_rows = max([max(cell['row_nums']) for cell in cells]) + 1
    else:
        return

    header_cells = [cell for cell in cells if cell['header']]
    if len(header_cells) > 0:
        max_header_row = max([max(cell['row_nums']) for cell in header_cells])
    else:
        max_header_row = -1

    table_array = np.empty([num_rows, num_columns], dtype='object')
    if len(cells) > 0:
        for cell in cells:
            for row_num in cell['row_nums']:
                for column_num in cell['column_nums']:
                    table_array[row_num, column_num] = cell['cell_text']

    header = table_array[:max_header_row+1,:]
    flattened_header = []
    for col in header.transpose():
        flattened_header.append(' | '.join(OrderedDict.fromkeys(col)))
    df = pd.DataFrame(table_array[max_header_row+1:,:], index=None, columns=flattened_header)

    return df, df.to_csv(index=None)


def cells_to_html(cells):
    cells = sorted(cells, key=lambda k: min(k['column_nums']))
    cells = sorted(cells, key=lambda k: min(k['row_nums']))

    table = ET.Element('table')
    current_row = -1

    for cell in cells:
        this_row = min(cell['row_nums'])

        attrib = {}
        colspan = len(cell['column_nums'])
        if colspan > 1:
            attrib['colspan'] = str(colspan)
        rowspan = len(cell['row_nums'])
        if rowspan > 1:
            attrib['rowspan'] = str(rowspan)
        if this_row > current_row:
            current_row = this_row
            if cell['header']:
                cell_tag = 'th'
                row = ET.SubElement(table, 'tr')
            else:
                cell_tag = 'td'
                row = ET.SubElement(table, 'tr')
        tcell = ET.SubElement(row, cell_tag, attrib=attrib)
        tcell.text = cell['cell_text']

    return str(ET.tostring(table, encoding='unicode', short_empty_elements=False))


# def cells_to_html(cells):
#     for cell in cells:
#         cell['column_nums'].sort()
#         cell['row_nums'].sort()
#     n_cols = max(cell['column_nums'][-1] for cell in cells) + 1
#     n_rows = max(cell['row_nums'][-1] for cell in cells) + 1
#     html_code = ''
#     for r in range(n_rows):
#         r_cells = [cell for cell in cells if cell['row_nums'][0] == r]
#         r_cells.sort(key=lambda x: x['column_nums'][0])
#         r_html = ''
#         for cell in r_cells:
#             rowspan = cell['row_nums'][-1] - cell['row_nums'][0] + 1
#             colspan = cell['column_nums'][-1] - cell['column_nums'][0] + 1
#             r_html += f'<td rowspan='{rowspan}' colspan='{colspan}'>{escape(cell['text'])}</td>'
#         html_code += f'<tr>{r_html}</tr>'
#     html_code = '''<html>
#                    <head>
#                    <meta charset='UTF-8'>
#                    <style>
#                    table, th, td {
#                      border: 1px solid black;
#                      font-size: 10px;
#                    }
#                    </style>
#                    </head>
#                    <body>
#                    <table frame='hsides' rules='groups' width='100%%'>
#                      %s
#                    </table>
#                    </body>
#                    </html>''' % html_code
#     soup = bs(html_code)
#     html_code = soup.prettify()
#     return html_code


def cells_to_excel(cells, file_path):

    def int2xlsx(i):
        if i < 26:
            return chr(i + 65)
        return f'{chr(i // 26 + 64)}{chr(i % 26 + 65)}'

    cells = sorted(cells, key=lambda k: min(k['column_nums']))
    cells = sorted(cells, key=lambda k: min(k['row_nums']))

    workbook = xlsxwriter.Workbook(file_path)

    cell_format = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter'}
    )

    worksheet = workbook.add_worksheet(name='Table')

    table_start_index = 0

    for cell in cells:
        start_row = min(cell['row_nums'])
        end_row = max(cell['row_nums'])
        start_col = min(cell['column_nums'])
        end_col = max(cell['column_nums'])
        if start_row == end_row and start_col == end_col:
            worksheet.write(
                table_start_index + start_row,
                start_col,
                cell['cell_text'],
                cell_format,
            )
        else:
            if start_col == end_col and start_row == end_row:
                excel_index = f'{int2xlsx(table_start_index + start_col)}{table_start_index + start_row + 1}'
            else:
                excel_index = f'{int2xlsx(table_start_index + start_col)}{table_start_index + start_row + 1}:{int2xlsx(table_start_index + end_col)}{table_start_index + end_row + 1}'
            worksheet.merge_range(
                excel_index, cell['cell_text'], cell_format
            )

    workbook.close()


def cells_to_data(cells):
    cells = sorted(cells, key=lambda k: min(k['column_nums']))
    cells = sorted(cells, key=lambda k: min(k['row_nums']))

    num_columns = max([max(cell['column_nums']) for cell in cells]) + 1
    num_rows = max([max(cell['row_nums']) for cell in cells]) + 1

    res = [[{'value': '', 'rowSpan': 1, 'colSpan': 1} for i in range(num_columns)] for j in range(num_rows)]

    for cell in cells:
        start_row = min(cell['row_nums'])
        end_row = max(cell['row_nums'])
        start_col = min(cell['column_nums'])
        end_col = max(cell['column_nums'])

        res[start_row][start_col]['value'] = cell['cell_text']
        res[start_row][start_col]['rowSpan'] = end_row - start_row + 1
        res[start_row][start_col]['colSpan'] = end_col - start_col + 1

    return res


def main(pil_img, filename):
    input_path = 'static/input_pics/'
    result_path = 'static/result_pics/'

    if not os.path.exists(input_path):
        os.makedirs(input_path)
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    filename, ext = os.path.splitext(filename)

    pil_img.save(os.path.join(input_path, f'{filename}.png'))

    detection_result = table_detection(pil_img)
    crop_images, vis_det_img = crop_image(pil_img, detection_result)

    vis_det_img.save(os.path.join(result_path, f'{filename}_det.png'))

    res = {
        'input_url': urllib.parse.quote_plus(os.path.join('/static/input_pics/', f'{filename}.png')),
        'num_tables': len(crop_images),
        'vis_det': urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_det.png')),
        'tables': []
    }

    for idx, img in enumerate(crop_images):
        table_dict = {}

        vis_img = visualize_image(img)
        vis_img.save(os.path.join(result_path, f'{filename}_table{idx}.png'))
        table_dict['vis_img'] = urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_table{idx}.png'))
        print(f"# table_dict['vis_img'] = {table_dict['vis_img']}")

        ocr_result = ocr(img)
        vis_ocr_img = visualize_ocr(img, ocr_result)
        vis_ocr_img.save(os.path.join(result_path, f'{filename}_table{idx}_ocr.png'))
        table_dict['vis_ocr_img'] = urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_table{idx}_ocr.png'))
        print(f"# table_dict['vis_ocr_img'] = {table_dict['vis_ocr_img']}")

        structure_result = table_structure(img)
        vis_str_img = visualize_structure(img, structure_result)
        vis_str_img.save(os.path.join(result_path, f'{filename}_table{idx}_str.png'))
        table_dict['vis_str_img'] = urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_table{idx}_str.png'))
        print(f"# table_dict['vis_str_img'] = {table_dict['vis_str_img']}")

        table_structures, cells, confidence_score = convert_stucture(ocr_result, img, structure_result)
        cells = extract_text_from_cells(cells)
        vis_cells_img = visualize_cells(img, cells)
        vis_cells_img.save(os.path.join(result_path, f'{filename}_table{idx}_cells.png'))
        table_dict['vis_cells_img'] = urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_table{idx}_cells.png'))
        print(f"# table_dict['vis_cells_img'] = {table_dict['vis_cells_img']}")

        xlsx_path = os.path.join(result_path, f'{filename}_table{idx}.xlsx')
        cells_to_excel(cells, xlsx_path)
        table_dict['xlsx_url'] = urllib.parse.quote_plus(os.path.join('/static/result_pics/', f'{filename}_table{idx}.xlsx'))
        print(f"table_dict['xlsx_url'] = {table_dict['xlsx_url']}")

        cells_data = cells_to_data(cells)
        table_dict['cells_data'] = cells_data
        print(f"table_dict['cells_data'] = {table_dict['cells_data']}")

        res['tables'].append(table_dict)

    return res
