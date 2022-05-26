from properties_loader import PropertiesImpl
from properties_loader.interfaces import Properties
from cleandev_framework.inmutables import _PropertiesGroups
from cleandev_framework.inmutables import _PropertiesParams

_properties: Properties = PropertiesImpl().__dict__

_properties_bd: dict = _properties[_PropertiesGroups.BD_CORE]
_parent_package_model = _properties_bd[_PropertiesParams.PATH_MODULE_SCHEMA]
_properties_cleandev_framework: dict = _properties[_PropertiesGroups.CLEANDEV_FRAMEWORK]

if _properties_cleandev_framework is None:
    _camel_case_enabled = 'false'
else:
    _camel_case_enabled: str = str(_properties_cleandev_framework[_PropertiesParams.CAMEL_CASE_ENABLED])
