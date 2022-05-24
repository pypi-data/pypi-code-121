from io import StringIO
from .pydpkg import Dpkg

import re
from logging import getLogger

log = getLogger(__name__)

# ==============================================================================

class Package(dict):
  def __init__(self, filename=None, data={}):
    if filename:
      log.debug('Reading package from "%s"' % (filename))
      data.update(__readDpkg(filename))

    for key in __MANDATORY_FIELDS:
      if key not in data:
        raise AssertionError('Missing mandatory field "%s"' % key)

    dict.__init__(self, data)

  def __str__(self):
    buffer = StringIO()
    for key, value in self.items():
      buffer.write('%s: %s\n' % (key, value))
    string = buffer.getvalue()
    buffer.close()
    return string

  @property
  def name(self):
    return self['Package']

  @property
  def version(self):
    return self['Version']

  @property
  def architecture(self):
    return self['Architecture']

  @property
  def key(self):
    return f'{self.name}_{self.version}_{self.architecture}'

  @property
  def filename(self):
    return self['Filename']

  @property
  def sha256(self):
    return self['SHA256']

# ==============================================================================

# Mandatory fields that MUST be present in the package
_Package__MANDATORY_FIELDS = [
  'Package',
  'Architecture',
  'Description',
  # Those are our own
  'Filename',
  'Size',
  'MD5sum',
  'SHA1',
  'SHA256',
]

# Multiline fields NOT to be cleaned up
__MULTILINE_FIELDS = [
  'description',
  'changes',
  'files',
  'checksums-sha1',
  'checksums-sha256',
  'package-list',
]

# Cleanup field value (normalize spaces)
def __cleanup(key, value):
  return value \
    if key.lower() in __MULTILINE_FIELDS \
    else re.sub('\s+', ' ', value).strip()

# Read a DPKG file and return its fields
def _Package__readDpkg(filename):
  package = Dpkg(filename)

  name = package['package']
  version = package.version
  prefix = name[:4] if name.startswith('lib') else name[0]
  filename = f'pool/{prefix}/{name}_{package.version}_{package.architecture}.deb'

  return { k: __cleanup(k, v) for k, v in package.headers.items() } | {
    'Filename': filename,
    'Size': package.filesize,
    'MD5sum': package.md5,
    'SHA1': package.sha1,
    'SHA256': package.sha256,
  }
