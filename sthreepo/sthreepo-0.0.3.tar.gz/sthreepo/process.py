from .repository import Repository

from botocore import session as aws
from datetime import datetime
from hashlib import md5, sha1, sha256
from io import StringIO
from pgpkms import KmsPgpKey
from logging import getLogger

import gzip
import lzma
import zoneinfo

log = getLogger(__name__)

def process(repository, key_id, bucket,
    kms_client=None,
    s3_client=None,
    session=None,
    prefix='repository/',
  ):
  assert isinstance(repository, Repository), 'Wrong repository type'
  assert isinstance(key_id, str), 'The key id must be a string'

  prefix = prefix if prefix.endswith('/') else prefix + '/'

  # Default KMS client if none specified
  if not kms_client:
    log.debug('Creating KMS client')
    if not session: session = aws.get_session()
    kms_client = session.create_client('kms')

  # Default S3 client if none specified
  if not s3_client:
    log.debug('Creating S3 client')
    if not session: session = aws.get_session()
    s3_client = session.create_client('s3')

  # Get our AWS KMS key as a PGP key
  key = KmsPgpKey(key_id, kms_client=kms_client)

  # Prepare the _base_ files (repository keys)
  files = {
    'repository.gpg': (key.to_pgp(armoured=False, kms_client=kms_client), 'application/pgp-keys'),
    'repository.gpg.asc': (key.to_pgp(armoured=True, kms_client=kms_client), 'text/plain; charset=utf-8'),
  }

  # Process every distribution in the repository
  for (distribution, components) in repository.indexes:
    distribution_files = {}

    # Process every component in the distribution
    for component in components:
      log.info('Generating repository files for "%s:%s"' % (distribution, component))

      # Process every architecture in the repository
      for architecture in repository.architectures:
        packages = str(repository.get_packages(distribution, component, architecture)).encode('utf-8')
        packages_gz = gzip.compress(packages)
        packages_xz = lzma.compress(packages)

        # Here are our "Packages" files, with their compressed equivalent
        distribution_files[f'{component}/binary-{architecture}/Packages'] = (packages, 'text/plain; charset=utf-8')
        distribution_files[f'{component}/binary-{architecture}/Packages.gz'] = (packages_gz, 'application/gzip')
        distribution_files[f'{component}/binary-{architecture}/Packages.xz'] = (packages_xz, 'application/x-xz')

        # Prepare the per-component "Release" file
        buffer = StringIO()
        if repository.origin: buffer.write('Origin: %s\n' % (repository.origin))
        if repository.label: buffer.write('Label: %s\n' % (repository.label))
        buffer.write('Archive: %s\n' % (distribution))
        buffer.write('Component: %s\n' % (component))
        buffer.write('Architecture: %s\n' % (architecture))
        buffer.write('Acquire-By-Hash: no\n')

        release = buffer.getvalue().encode('utf-8')
        buffer.close()

        distribution_files[f'{component}/binary-{architecture}/Release'] = (release, 'text/plain; charset=utf-8')

    # We can now prepare the "Release" file for the component
    if distribution_files:
      buffer = StringIO()

      # Generic headers
      if repository.origin: buffer.write('Origin: %s\n' % (repository.origin))
      if repository.label: buffer.write('Label: %s\n' % (repository.label))
      buffer.write('Suite: %s\n' % (distribution))
      buffer.write('Codename: %s\n' % (distribution))
      buffer.write('Components: %s\n' % (' '.join(components)))
      buffer.write('Architectures: %s\n' % (' '.join(repository.architectures)))
      buffer.write('Date: %s\n' % (datetime.now(tz=zoneinfo.ZoneInfo('UTC')).strftime('%a, %d %b %Y %H:%M:%S %Z')))
      buffer.write('Acquire-By-Hash: no\n')

      buffer.write("MD5Sum:\n")
      for name in sorted(distribution_files):
        content, content_type = distribution_files[name]
        digest = md5(content).hexdigest()
        buffer.write(' %s %16d %s\n' % (digest, len(content), name))

      buffer.write("SHA1:\n")
      for name in sorted(distribution_files):
        content, content_type = distribution_files[name]
        digest = sha1(content).hexdigest()
        buffer.write(' %s %16d %s\n' % (digest, len(content), name))

      buffer.write("SHA256:\n")
      for name in sorted(distribution_files):
        content, content_type = distribution_files[name]
        digest = sha256(content).hexdigest()
        buffer.write(' %s %16d %s\n' % (digest, len(content), name))

      release = buffer.getvalue().encode('utf-8')
      buffer.close()

      release_gpg = key.sign(release, armoured=True, kms_client=kms_client)
      inrelease = key.message(release, kms_client=kms_client).encode('utf-8')

      files[f'dists/{distribution}/Release'] = (release, 'text/plain; charset=utf-8')
      files[f'dists/{distribution}/Release.gpg'] = (release_gpg, 'text/plain; charset=utf-8')
      files[f'dists/{distribution}/InRelease'] = (inrelease, 'text/plain; charset=utf-8')

      for name, (content, content_type) in distribution_files.items():
        files[f'dists/{distribution}/{name}'] = (content, content_type)

    # No distribution file, remove files
    else:
      files[f'dists/{distribution}/Release'] = (None, None)
      files[f'dists/{distribution}/Release.gpg'] = (None, None)
      files[f'dists/{distribution}/InRelease'] = (None, None)

  # Now upload...
  for name, (content, content_type) in files.items():
    key = "%s%s" % (prefix, name)
    if content != None:
      log.info('Uploading "s3://%s/%s"' % (bucket, key))
      s3_client.put_object(
        Bucket = bucket,
        Key = key,
        ContentType = content_type,
        Body = content,
      )
    else:
      log.info('Excluding "s3://%s/%s"' % (bucket, key))
      s3_client.delete_object(
        Bucket = bucket,
        Key = key,
      )

  # Return uploaded files
  return files
