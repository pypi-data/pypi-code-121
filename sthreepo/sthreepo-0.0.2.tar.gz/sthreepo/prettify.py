from botocore import session as aws
from io import StringIO
from html import escape
from textwrap import dedent
from logging import getLogger
from datetime import datetime

import zoneinfo

log = getLogger(__name__)

__ICON = 'data:image/svg+xml;base64,' \
  'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAg' \
  'MTAwIj48dGV4dCB5PSIuOWVtIiBmb250LXNpemU9IjkwIj4mI3gxRjVDNDs8L3RleHQ+PC9zdmc+'

def prettify(bucket, prefix='repository/', s3_client=None, parent=False):
  prefix = prefix if prefix.endswith('/') else prefix + '/'

  log.debug('Generating index for "%s"' % (prefix))

  if not s3_client:
    session = aws.get_session()
    s3_client = session.create_client('s3')

  files = []
  sizes = {}
  dates = {}
  prefixes = []

  params = { 'Bucket': bucket, 'Delimiter': '/', 'Prefix': prefix }

  while True:
    response = s3_client.list_objects_v2(**params)

    for content in response.get('Contents', []):
      file = content['Key'][len(prefix):]
      if file == 'index.html':
        continue
      if file not in files:
        files.append(file)
        sizes[file] = content['Size']
        dates[file] = content['LastModified']

    for common_prefix in response.get('CommonPrefixes', []):
      if common_prefix['Prefix'] not in prefixes:
        prefixes.append(common_prefix['Prefix'])

    if response['IsTruncated']:
      params['ContinuationToken'] = response['NextContinuationToken']
    else:
      break

  buffer = StringIO()
  if parent:
    buffer.write('&#x1F519; <a href="../">../</a>\n')

  for sub_prefix in prefixes:
    buffer.write('&#x1F4C2; <a href="./{0}">{0}</a>\n'.format(
      escape(sub_prefix[len(prefix):])
    ))

  for file in files:
    icon = '&#x1F4E6;' if file.endswith('.deb') else '&#x1F4C4;'
    buffer.write('{0} <a href="./{1}">{1}</a> {2} {3} bytes\n'.format(
      icon,
      file,
      dates[file].strftime('%d-%b-%Y %H:%M:%S').rjust(70 - len(file)),
      '{:,}'.format(sizes[file]).rjust(20),
    ))

  index = buffer.getvalue().strip()
  buffer.close()

  date = datetime.now(tz=zoneinfo.ZoneInfo('UTC')).strftime('%a, %d %b %Y %H:%M:%S %Z')

  content = dedent('''
    <!DOCTYPE html>
    <html>
      <head>
        <title>Index of /{0}</title>
        <link rel="icon" href="{3}">
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400&family=Roboto:wght@400;700&display=swap');
          h1   {{ font-weight: normal; }}
          body {{ font-family: 'Roboto', sans-serif; }}
          pre  {{
            font-family: 'Roboto Mono', monospace;
            border-bottom: 1px solid grey;
            border-top: 1px solid grey;
            margin: 1em 0;
            padding: 1em 0;
          }}
        </style>
      </head>
      <body>
        <h1>Index of <b>/{0}</b></h1>
        <pre>{1}</pre>
        <small>
          Generated with
          <a href="https://github.com/juitnow/sthreepo" target="_blank">sthreepo</a>
          on {2}
        </small>
      </body>
    </html>
    ''').format(escape(prefix), index, escape(date), __ICON)

  body = content.strip().encode('utf-8')
  key = '%sindex.html' % (prefix)

  log.info('Uploading "s3://%s/%s"' % (bucket, key))

  s3_client.put_object(
    Bucket = bucket,
    Key = key,
    Body = body,
    ContentType = 'text/html; charset=utf-8',
  )

  for sub_prefix in prefixes:
    prettify(bucket, prefix=sub_prefix, s3_client=s3_client, parent=True)
