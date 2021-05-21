import magic, logging
from PIL import Image
from google.cloud import storage
from io import BytesIO


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


def thumbnails(event, context):
    print(event)
    if not 'name' in event or not 'bucket' in event:
        return

    BUCKET_NAME = event['bucket']
    filename = event['name']

    if filename.endswith('-thumbnail'):
        return

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
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

        filename = f'{filename}-thumbnail'

    with BytesIO() as output:
        image.save(output, format=extension)
        contents = output.getvalue()

        content = output.read()

        blob = bucket.blob(filename)
        blob.upload_from_string(contents)

        print(f'{filename} was generated')
