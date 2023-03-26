import PIL
import numpy as np
import torch
from collections import defaultdict

import cv2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.utils.visualization import visualize_page

import pytesseract
from pytesseract import Output

from bs4 import BeautifulSoup as bs
from html import escape

import sys, json

import postprocess


ocr_predictor = ocr_predictor('db_resnet50', 'crnn_vgg16_bn', pretrained=True)
structure_model = torch.hub.load('ultralytics/yolov5', 'custom', 'weights/structure_wts.pt', force_reload=True)
imgsz = 640

structure_class_names = [
    'table', 'table column', 'table row', 'table column header',
    'table projected row header', 'table spanning cell', 'no object'
]
structure_class_map = {k: v for v, k in enumerate(structure_class_names)}
structure_class_thresholds = {
    "table": 0.5,
    "table column": 0.5,
    "table row": 0.5,
    "table column header": 0.25,
    "table projected row header": 0.25,
    "table spanning cell": 0.25,
    "no object": 10
}


def PIL_to_cv(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR) 


def cv_to_PIL(cv_img):
    return PIL.Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


def table_structure(filename):
    pil_img = PIL.Image.open(filename)
    image = PIL_to_cv(pil_img)
    pred = structure_model(image, size=imgsz)
    pred = pred.xywhn[0]
    result = pred.cpu().numpy()
    return result


def ocr(filename):
    doc = DocumentFile.from_images(filename)
    result = ocr_predictor(doc).export()
    result = result['pages'][0]
    H, W = result['dimensions']
    ocr_res = []
    for block in result['blocks']:
        for line in block['lines']:
            for word in line['words']:
                bbox = word['geometry']
                word_info = {
                    'bbox': [int(bbox[0][0] * W), int(bbox[0][1] * H), int(bbox[1][0] * W), int(bbox[1][1] * H)],
                    'text': word['value']
                }
                ocr_res.append(word_info)
    return ocr_res


def convert_stucture(page_tokens, filename, structure_result):
    pil_img = PIL.Image.open(filename)
    image = PIL_to_cv(pil_img)

    width = image.shape[1]
    height = image.shape[0]
    # print(width, height)
    
    bboxes = []
    scores = []
    labels = []
    for i, result in enumerate(structure_result):
        class_id = int(result[5])
        score = float(result[4])
        min_x = result[0]
        min_y = result[1]
        w = result[2]
        h = result[3]
        
        x1 = int((min_x-w/2)*width)
        y1 = int((min_y-h/2)*height)
        x2 = int((min_x+w/2)*width)
        y2 = int((min_y+h/2)*height)
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
        table_bbox = (0,0,1000,1000)
    # print('table_class_objects:', table_class_objects)
    # print('table_bbox:', table_bbox)
    
    tokens_in_table = [token for token in page_tokens if postprocess.iob(token['bbox'], table_bbox) >= 0.5]
    # print('tokens_in_table:', tokens_in_table)
    
    table_structures, cells, confidence_score = postprocess.objects_to_cells(table, table_objects, tokens_in_table, structure_class_names, structure_class_thresholds)
    
    return table_structures, cells, confidence_score


def visualize_cells(filename, cells):    
    pil_img = PIL.Image.open(filename)
    image = PIL_to_cv(pil_img)
    for i, cell in enumerate(cells):
        bbox = cell['bbox']
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])
        cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 255, 0))
    return cv_to_PIL(image)


def pytess(cell_pil_img):
    return ' '.join(pytesseract.image_to_data(cell_pil_img, output_type=Output.DICT, config='-c tessedit_char_blacklist=œ˜â€œï¬â™Ã©œ¢!|”?«“¥ --tessdata-dir tessdata --oem 3 --psm 6')['text']).strip()


def resize(pil_img, size=1800):
    length_x, width_y = pil_img.size
    factor = max(1, size / length_x)
    size = int(factor * length_x), int(factor * width_y)
    pil_img = pil_img.resize(size, PIL.Image.ANTIALIAS)
    return pil_img, factor


def image_smoothening(img):
    ret1, th1 = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
    ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(th2, (1, 1), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th3


def remove_noise_and_smooth(pil_img):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)
    filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 3)
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    img = image_smoothening(img)
    or_image = cv2.bitwise_or(img, closing)
    pil_img = PIL.Image.fromarray(or_image)
    return pil_img


def extract_text_from_cells(filename, cells):
    pil_img = PIL.Image.open(filename)
    pil_img, factor = resize(pil_img)
    #pil_img = remove_noise_and_smooth(pil_img)
    #display(pil_img)
    for cell in cells:
        bbox = [x * factor for x in cell['bbox']]
        cell_pil_img = pil_img.crop(bbox)
        #cell_pil_img = remove_noise_and_smooth(cell_pil_img)
        #cell_pil_img = tess_prep(cell_pil_img)        
        cell['text'] = pytess(cell_pil_img)
    return cells


def cells_to_html(cells):
    for cell in cells:
        cell['column_nums'].sort()
        cell['row_nums'].sort()
    n_cols = max(cell['column_nums'][-1] for cell in cells) + 1
    n_rows = max(cell['row_nums'][-1] for cell in cells) + 1
    html_code = ''
    for r in range(n_rows):
        r_cells = [cell for cell in cells if cell['row_nums'][0] == r]
        r_cells.sort(key=lambda x: x['column_nums'][0])
        r_html = ''
        for cell in r_cells:
            rowspan = cell['row_nums'][-1] - cell['row_nums'][0] + 1
            colspan = cell['column_nums'][-1] - cell['column_nums'][0] + 1
            r_html += f'<td rowspan="{rowspan}" colspan="{colspan}">{escape(cell["text"])}</td>'
        html_code += f'<tr>{r_html}</tr>'
    html_code = '''<html>
                   <head>
                   <meta charset="UTF-8">
                   <style>
                   table, th, td {
                     border: 1px solid black;
                     font-size: 10px;
                   }
                   </style>
                   </head>
                   <body>
                   <table frame="hsides" rules="groups" width="100%%">
                     %s
                   </table>
                   </body>
                   </html>''' % html_code
    soup = bs(html_code)
    html_code = soup.prettify()
    return html_code


def main(filename):    
    print(filename)
    ocr_res = ocr(filename)
    structure_result = table_structure(filename)

    table_structures, cells, confidence_score = convert_stucture(ocr_res, filename, structure_result)
    cells_img = visualize_cells(filename, cells)

    cells = extract_text_from_cells(filename, cells)
    html_code = cells_to_html(cells)

    return cells_img, html_code
