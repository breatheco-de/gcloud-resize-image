import magic
from PIL import Image
from google.cloud import storage
from io import BytesIO
from flask import abort, jsonify, make_response

# you can add new mimes from here https://www.sitepoint.com/mime-types-complete-list/
# name of formats https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
MIMES_ALLOWED = {
    # 'mime': 'format',
    'image/gif': 'gif',
    'image/x-icon': 'ico',
    'image/jpeg': 'jpeg',
    # 'image/svg+xml': 'svg', not have sense resize a svg
    # 'image/tiff': 'tiff', don't work
    'image/webp': 'webp',
    'image/png': 'png',
}


def resize(request):
    data = request.get_json(force=True)

    print(data)
    if not 'filename' in data:
        return make_response(jsonify({'message': 'Incorrect filename', 'status_code': 400}), 400)

    if not 'bucket' in data:
        return make_response(jsonify({'message': 'Incorrect bucket', 'status_code': 400}), 400)

    if (not 'width' in data or not data['width']) and (not 'height' in data or not data['height']):
        return make_response(jsonify({'message': 'Incorrect width or height', 'status_code': 400}), 400)

    bucket = data['bucket']
    filename = data['filename']
    width = int(data['width']) if 'width' in data and data['width'] else None
    height = int(data['height']) if 'height' in data and data['height'] else None

    if filename.endswith('-thumbnail'):
        return make_response(jsonify({'message': 'Can\'t resize a thumbnail', 'status_code': 200}), 200)

    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.get_blob(filename)

    with blob.open('rb') as f:
        content = f.read()
        mime = magic.from_buffer(content, mime=True)

        if mime in MIMES_ALLOWED:
            extension = MIMES_ALLOWED[mime]

        else:
            return make_response(jsonify({'message': 'File type not allowed', 'status_code': 400}), 400)

        image = Image.open(f)
        current_width, current_height = image.size

        # Aspect ratio
        width_divide_by_height = current_width / current_height
        height_divide_by_width = current_height / current_width

        if width and not height:
            height = round(width * height_divide_by_width)

        elif not width and height:
            width = round(height * width_divide_by_height)

        size = (width, height)
        image = image.resize(size)
        filename = f'{filename}-{width}x{height}'

    with BytesIO() as output:
        image.save(output, format=extension)
        contents = output.getvalue()

        content = output.read()

        blob = bucket.blob(filename)
        blob.upload_from_string(contents)

        print(f'{filename} was generated')
        return make_response(jsonify({
            'message': 'Ok',
            'status_code': 200,
            'width': width,
            'height': height,
        }), 200)
