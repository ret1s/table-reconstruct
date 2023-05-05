from flask import Flask, request, jsonify, current_app
from io import BytesIO
from PIL import Image
import core


app = Flask(__name__)


@app.route('/api/upload', methods=['POST'])
def upload():
    data = {}
    try:
        file = request.files['image']
        filename = file.filename
        print(f'# Uploading file {filename}')
        file_bytes = file.read()
        file_content = BytesIO(file_bytes).read()
        print(f'# Received file content: {file_content[:100]}')

        img = Image.open(BytesIO(file_bytes))
        result = core.main(img, filename)
        print(f'# main() return result: {result}')

        data['result'] = result
        data['status'] = 1

    except Exception as e:
        print(f"Couldn't upload file {e}")
        data['status'] = 0

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
