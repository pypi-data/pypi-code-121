from properties_loader import PropertiesImpl
from properties_loader.interfaces import Properties

_properties: Properties = PropertiesImpl().__dict__
_properties_api_template = _properties['API_TEMPLATE']

# propiedades obligatorias
_jwt_secret_key: str = _properties_api_template['jwt_secret_key']
_path_resources_api: str = _properties_api_template['path_resources_api']

# app_name
if _properties_api_template.get('app_name'):
    _app_name: str = _properties_api_template.get('app_name')
else:
    _app_name: str = 'api'

# jwt_refresh_token_expires
if _properties_api_template.get('jwt_refresh_token_expires'):
    _jwt_refresh_token_expires: int = int(_properties_api_template.get('jwt_refresh_token_expires'))
else:
    _jwt_refresh_token_expires: int = 1

# jwt_access_token_expires
if _properties_api_template.get('jwt_access_token_expires'):
    _jwt_access_token_expires: int = int(_properties_api_template.get('jwt_access_token_expires'))
else:
    _jwt_access_token_expires: int = 1

# propagate_exceptions
if _properties_api_template.get('propagate_exceptions'):
    _propagate_exceptions: bool = bool(_properties_api_template.get('propagate_exceptions'))
else:
    _propagate_exceptions = True

# debug
if _properties_api_template.get('debug') is not None:
    if _properties_api_template.get('debug') == 'False':
        _debug: bool = False
else:
    _debug = True

pass
