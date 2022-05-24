from .package import Package
from .packages import Packages
from .pydpkg import Dpkg

from functools import cmp_to_key
from io import StringIO
from logging import getLogger

import re

log = getLogger(__name__)

class Repository(dict):
  def __init__(self, data={}, origin=None, label=None, default_index=None, keep_old=1):
    dict.__init__(self)

    # Here we want to _reconstruct_ the repository structure, rather than
    # copying it from the data... This makes sure validations run properly.
    self['indexes'] = self.__indexes = {}
    self['packages'] = self.__packages = {}
    self['architectures'] = self.__architectures = []

    # Reconstruct packages
    if 'packages' in data:
      for key, package in data['packages'].items():
        self.add_package(Package(data=package), verbose=False)

    # Reconstruct indexes
    if 'indexes' in data:
      for distribution, components in data['indexes'].items():
        for component, package_keys in components.items():
          index = '%s:%s' % (distribution, component)
          self.add_index(index)

          # Add all packages to the index
          for package_key in package_keys:
            self.add_package(self.__packages[package_key], index, verbose=False)

    # Architectures are automatically regenerated, so add label and origin,
    # defaulting them to the value specified in the constructor parameters
    if label: data['label'] = label
    if origin: data['origin'] = origin
    if keep_old: data['keep_old'] = keep_old
    if default_index: data['default_index'] = default_index

    if 'label' in data: self['label'] = data['label']
    if 'origin' in data: self['origin'] = data['origin']

    if 'default_index' in data:
      self['default_index'] = data['default_index']
      self.add_index(self.default_index)

    # Log
    log.debug('Repository instance created (%s packages)' % (len(self.__packages)))


  def add_index(self, index):
    assert re.match('^[\w-]+:[\w-]+$', index), 'Invalid index name "%s" (must be "distribution:component")' % (index)

    (distribution, component) = __parse_index(index)

    if not distribution in self.__indexes:
      log.debug('Adding distribution "%s"' % (distribution))
      self.__indexes[distribution] = dict()

    if not component in self.__indexes[distribution]:
      log.debug('Adding component "%s" for distribution "%s"' % (component, distribution))
      self.__indexes[distribution][component] = list()


  def add_architecture(self, architecture):
    if architecture == 'all': return

    assert re.match('^[\w-]+$', architecture), 'Invalid architecture "%s"' % (architecture)

    if not architecture in self.__architectures:
      log.debug('Adding architecture "%s"' % (architecture))
      self.__architectures.append(architecture)


  def add_package(self, package, index=None, verbose=True):
    assert isinstance(package, Package), 'Invalid Package (must be <class Package>)'

    key = package.key

    if key in self.__packages:
      assert self.__packages[key].sha256 == package.sha256, 'Package "%s" already added with different hash' % (key)
    else:
      if verbose: log.info('Adding package "%s" to repository' % (key))
      self.__packages[key] = package
      self.add_architecture(package.architecture)

    if not index: return

    (distribution, component) = __parse_index(index)

    assert distribution in self.__indexes, 'Unknown distribution "%s"' % (distribution)
    assert component in self.__indexes[distribution], 'Unknown component "%s" for distribution "%s"' % (component, distribution)

    if not key in self.__indexes[distribution][component]:
      if verbose: log.info('Adding package "%s" to index "%s:%s"' % (key, distribution, component))
      self.__indexes[distribution][component].append(key)

  #=============================================================================

  @property
  def origin(self):
    return self.get('origin')

  @origin.setter
  def origin(self, value):
    if value:
      self['origin'] = value
    else:
      self.pop('origin', None)

  @origin.deleter
  def origin(self):
    self.pop('origin', None)

  #=============================================================================

  @property
  def label(self):
    return self.get('label')

  @label.setter
  def label(self, value):
    if value:
      self['label'] = value
    else:
      self.pop('label', None)

  @label.deleter
  def label(self):
    self.pop('label', None)

  #=============================================================================

  @property
  def keep_old(self):
    return self.get('keep_old', 1)

  @keep_old.setter
  def keep_old(self, value):
    value = int(value)
    assert value >= 1, 'Invalid "keep_old" value "%s"' % (value)
    if value > 1:
      self['keep_old'] = value
    else:
      self.pop('keep_old', None)

  @keep_old.deleter
  def keep_old(self):
    self.pop('keep_old', None)

  #=============================================================================

  @property
  def default_index(self):
    return self.get('default_index')

  @default_index.setter
  def default_index(self, value):
    if value:
      self.add_index(value)
      self['default_index'] = value
    else:
      self.pop('default_index', None)

  @default_index.deleter
  def default_index(self):
    self.pop('default_index', None)

  #=============================================================================

  @property
  def architectures(self):
    return self.__architectures.copy()

  #=============================================================================

  @property
  def indexes(self):
    indexes = []

    for distribution in sorted(self.__indexes):
      components = sorted(self.__indexes[distribution])
      indexes.append((distribution, components))
    return indexes

  #=============================================================================

  def get_packages(self, distribution, component, architecture, keep_old=None):
    assert architecture in self.__architectures, 'Unknown architecture "%s"' % (architecture)
    assert distribution in self.__indexes, 'Unknown distribution "%s"' % (distribution)
    assert component in self.__indexes[distribution], 'Unknown component "%s" for distribution "%s"' % (component, distribution)

    if not keep_old: keep_old = self.keep_old

    filtered = {}

    for key in self.__indexes[distribution][component]:
      assert key in self.__packages, 'Package "%s" missing' % (key)
      package = self.__packages[key]
      if package.architecture in [ architecture, 'all' ]:
        versions = filtered.setdefault(package.name, [])
        versions.append(package)

    packages = Packages()

    for name in sorted(filtered):
      versions = filtered[name]
      versions.sort(key = cmp_to_key(lambda p1, p2: Dpkg.compare_versions(p2.version, p1.version)))
      packages.extend(versions[:keep_old])

    return packages


# ==============================================================================

def _Repository__parse_index(index):
    assert re.match('^[\w-]+:[\w-]+$', index), 'Invalid index name "%s" (must be "distribution:component")' % index
    return index.split(':')
