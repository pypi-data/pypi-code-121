from botocore import session as aws
from getopt import getopt, GetoptError
from textwrap import dedent
from uuid import uuid4

import json
import logging
import os
import sys

from .package import Package
from .prettify import prettify
from .process import process
from .repository import Repository

# ==============================================================================

log = logging.getLogger('sthreepo')
log.setLevel(logging.INFO)

root_log = logging.getLogger()

formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

root_log.addHandler(handler)

# ==============================================================================

def __help():
  cmd = os.getenv('PGP_KMS_ARGV0', sys.argv[0])
  cmd = 'python3 -m sthreepo' if cmd == __file__ else cmd

  sys.exit(dedent('''
    Usage: {cmd} [options] <package.deb>

    Options:
      -b, --bucket=<name>   The AWS bucket name of the repository.
      -c, --create-index=distribution:component
                            Create a new index in the repository.
      -d, --default-index=distribution:component
                            Set the default index for the repository.
      -i, --index=distribution:component
                            Use the specified index for the new package.
      -k, --key=<id>        The ID, ARN, or alias of the key to use.
      -l, --label=<label>   Set the label for the repository.
      -n, --name=<name>     The name of the repository (default: "repository").
      -o, --origin=<origin> Set the origin for the repository.
      -v, --verbose         Be more verbose.
          --invalidate-cloudfront=<distribution-id>
                            Invalidate all CloudFront caches for the distribution
                            with the specified ID.

    Environment Variables:
      STHREEPO_BUCKET         The AWS bucket name of the repository.
      STHREEPO_KEY            The default ID, ARN or alias of the KMS key to use.
      STHREEPO_CLOUDFRONT_ID  The CloudFront Distribution ID for invalidating caches.
  '''.format(cmd = cmd)))

# ==============================================================================

if __name__ == '__main__':
  key_id = os.environ.get('STHREEPO_KEY')
  bucket = os.environ.get('STHREEPO_BUCKET')
  invalidate = os.environ.get('STHREEPO_CLOUDFRONT_ID')
  name = 'repository'
  label = None
  origin = None
  create_index = []
  default_index = None
  package_index = []
  verbose = False

  try:
    (options, rest) = getopt(sys.argv[1:], 'hb:l:n:o:k:c:d:i:v', [
      'bucket=', 'label=', 'origin=', 'key=', 'create-index=', 'default-index=',
      'name=', 'index=', 'invalidate-cloudfront=', 'help', 'verbose'
    ])

    for key, value in options:
      if key in [ '-h', '--help' ]:
        __help()
      elif key in [ '-b', '--bucket' ]:
        bucket = value
      elif key in [ '-c' , '--create-index' ]:
        create_index.append(value)
      elif key in [ '-d' , '--default-index' ]:
        default_index = value
      elif key in [ '-i' , '--index' ]:
        package_index.append(value)
      elif key in [ '-k' , '--key' ]:
        key_id = value
      elif key in [ '-l', '--label' ]:
        label = value
      elif key in [ '-n', '--name' ]:
        name = value
      elif key in [ '-o' , '--origin' ]:
        origin = value
      elif key in [ '-v' , '--verbose' ]:
        verbose = True
      elif key in [ '--invalidate-cloudfront' ]:
        invalidate = value

  except GetoptError as error:
    sys.exit('Error: %s' % (error))

  if verbose:
    log.setLevel(logging.DEBUG)
    root_log.setLevel(logging.INFO)

  if not key_id:
    sys.exit('Error: no key ID specified')

  if not bucket:
    sys.exit('Error: no bucket name specified')

  # Initialize our AWS session and clients
  session = aws.get_session()
  kms_client = session.create_client('kms')
  s3_client = session.create_client('s3')

  # State file and prefix
  state = '%s.json' % (name)
  prefix = '%s/' % (name)

  # Get the initial state of the repository
  repository = None
  try:
    response = s3_client.get_object(
      Bucket = bucket,
      Key = state,
    )
    log.info('Repository state found in s3://%s/%s' % (bucket, state))
    data = json.loads(response['Body'].read().decode('utf-8'))
    repository = Repository(
      data = data if data else {},
      default_index = default_index,
      origin = origin,
      label = label,
    )

  except s3_client.exceptions.NoSuchKey:
    log.info('Repository state not found, creating...')
    repository = Repository(
      default_index = default_index,
      origin = origin,
      label = label,
    )

  assert repository, 'Huh? No repository???'

  # Update base repository fields
  for index in create_index: repository.add_index(index)
  if default_index: repository.default_index = default_index
  if origin: repository.origin = origin
  if label: repository.label = label

  # Add all packages we were told to add
  for filename in rest:
    package = Package(filename)
    repository.add_package(package)
    for index in package_index:
      repository.add_package(package, index=index)
    package_key = '%s/%s' % (name, package.filename)

    # Upload the package...
    log.info('Uploading "s3://%s/%s"' % (bucket, package_key))
    params = {
      'Bucket': bucket,
      'Key': package_key,
      'Body': open(filename, 'rb'),
      'ContentType': 'application/vnd.debian.binary-package',
    }

    if package_index:
      params['Metadata'] = { 'sthreepo-indexes': ','.join(package_index)}

    s3_client.put_object(** params)

  # Process release files and upload to S3
  process(
    repository = repository,
    key_id = key_id,
    bucket = bucket,
    kms_client = kms_client,
    s3_client = s3_client,
    prefix = prefix,
  )

  prettify(
    bucket = bucket,
    prefix = prefix,
    s3_client = s3_client,
  )

  # Upload repository to S3
  log.info('Uploading "s3://%s/%s"' % (bucket, state))
  s3_client.put_object(
    Bucket = bucket,
    Key = state,
    Body = json.dumps(repository).encode('utf-8'),
    ContentType = 'application/json; charset=utf-8',
  )

  # Invalidate CloudFront
  if invalidate:
    log.debug('Creating cache invalidation (id=%s)' % (invalidate))
    cloudfront_client = session.create_client('cloudfront')

    response = cloudfront_client.create_invalidation(
      DistributionId = invalidate,
      InvalidationBatch = {
        'CallerReference': str(uuid4()),
        'Paths': {
          'Quantity': 1,
          'Items': [ '/*' ],
        },
      },
    )

    log.info('Invalidation %s created' % (response['Invalidation']['Id']))
