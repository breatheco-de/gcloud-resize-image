import magic
from PIL import Image
from google.cloud import storage
from io import BytesIO
from flask import abort

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
    data = request.get_json(silent=True)

    print(data)
    if not 'filename' in data:
        return abort(400, 'incorrect filename')

    if not 'bucket' in data:
        return abort(400, 'incorrect bucket')

    if not 'width' in data or not isinstance(data['width'], int):
        return abort(400, 'incorrect width')

    if not 'height' in data or not isinstance(data['height'], int):
        return abort(400, 'incorrect height')

    bucket = data['bucket']
    filename = data['filename']
    width = data['width']
    height = data['height']

    if filename.endswith('-thumbnail'):
        return abort(400, 'can\'t resize a thumbnail')

    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.get_blob(filename)

    with blob.open('rb') as f:
        content = f.read()
        mime = magic.from_buffer(content, mime=True)

        if mime in MIMES_ALLOWED:
            extension = MIMES_ALLOWED[mime]

        else:
            return

        image = Image.open(f)
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
        return 'ok'
