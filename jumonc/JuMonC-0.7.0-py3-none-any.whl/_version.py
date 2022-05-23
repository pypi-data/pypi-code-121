# Module version stage suffix map
_specifier_ = {'alpha': 'a', 'beta': 'b', 'candidate': 'rc', 'final': ''}


# Module version
version_info = (0, 7, 0, 'final', 0)

version_end = '' if version_info[3] == 'final' else _specifier_[version_info[3]]+str(version_info[4])
__version__ = f'{version_info[0]}.{version_info[1]}.{version_info[2]}{version_end}' 


# REST-API version
REST_version_info = (1, 0, 1, 'beta', 0)

REST_version_end = '' if REST_version_info[3] == 'final' else _specifier_[REST_version_info[3]]+str(REST_version_info[4])
__REST_version__ = f'{REST_version_info[0]}.{REST_version_info[1]}.{REST_version_info[2]}{REST_version_end}' 


# DB version
DB_version_info = (1, 0, 0, 'final', 0)

DB_version_end = '' if DB_version_info[3] == 'final' else _specifier_[DB_version_info[3]]+str(DB_version_info[4])
__DB_version__ = f'{DB_version_info[0]}.{DB_version_info[1]}.{DB_version_info[2]}{DB_version_end}' 
