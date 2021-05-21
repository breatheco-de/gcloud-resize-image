#!/bin/env python
import os
import sys


if __name__ == '__main__':
    SERVICE_NAME = os.getenv('SERVICE_NAME', '')
    BUCKET_NAME = os.getenv('BUCKET_NAME', '')
    GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    GOOGLE_CLOUD_SERVICE_ACCOUNT = os.getenv('GOOGLE_CLOUD_SERVICE_ACCOUNT', '')

    exit_code = os.system('pip freeze > requirements.txt')
    command = ' '.join([
        f'gcloud functions deploy {SERVICE_NAME}',
        f'--entry-point thumbnails',
        f'--runtime python39',
        f'--memory 256MB',
        f'--service-account {GOOGLE_CLOUD_SERVICE_ACCOUNT}',
        f'--source .',
        f'--trigger-resource={BUCKET_NAME}',
        f'--trigger-event=google.storage.object.finalize',
        f'--project {GOOGLE_CLOUD_PROJECT_ID}',
    ])

    exit_code = os.system(command)

    # python don't return 256
    if exit_code:
        sys.exit(1)
