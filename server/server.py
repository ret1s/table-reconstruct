from flask import Flask, request, jsonify, current_app
from io import BytesIO
from PIL import Image
import os
import urllib.parse
from app import main


app = Flask(__name__)


@app.route('/api/upload', methods=['POST'])
def upload():
    d = {}
    try:
        file = request.files['image']
        filename = file.filename
        print(f"Uploading file {filename}")
        file_bytes = file.read()
        file_content = BytesIO(file_bytes).read()
        print(file_content[:100])

        picture_path = os.path.join(current_app.root_path, 'static/input_pics', filename)
        img = Image.open(BytesIO(file_bytes))
        img.save(picture_path)

        result_path = os.path.join(current_app.root_path, 'static/result_pics', filename)
        cells_img, html = main(picture_path)
        cells_img.save(result_path)

        d['url'] = urllib.parse.quote_plus('/static/result_pics/' + filename)
        d['status'] = 1
        print(d)

    except Exception as e:
        print(f"Couldn't upload file {e}")
        d['status'] = 0

    return jsonify(d)


if __name__ == '__main__':
    app.run(debug=True)
