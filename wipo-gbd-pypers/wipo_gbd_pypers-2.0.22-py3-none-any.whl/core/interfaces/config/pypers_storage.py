import os

region = os.environ.get('AWS_DEFAULT_REGION', 'eu-central-1')
u_id = os.environ.get('AWS_ACCOUNTID', 'n')
prefix = 'gbd-assets-%s-%s-%s' % ("%s", region, u_id)

ARCHIVES_BUCKET = prefix % 'archives'
RAW_IMAGES_BUCKET = prefix % 'imgs-ori'
IMAGES_BUCKET = prefix % 'imgs-gbd'
RAW_DOCUMENTS = prefix % 'docs-ori'
GBD_DOCUMENTS = prefix % 'docs-gbd'
IDX_BUCKET = prefix % 'idx-files'
