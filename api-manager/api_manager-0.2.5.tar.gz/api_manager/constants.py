import re
from enum import Enum
from typing import List


class Project(Enum):
    ALMS = 'alms'
    LABS = 'labs'


class APIState(Enum):
    """
    API response state

    Some of responses contains response state:
    1 - means success
    2 - means error
    """
    SUCCESS = 1
    FAILED = 2


class HttpActions(Enum):
    POST = 'created'
    PUT = 'updated'
    PATCH = 'updated'
    DELETE = 'deleted'


class Entities(Enum):
    ACTIVITY = 'Activity'
    GROUP = 'Group'
    GROUP_USER = 'GroupUser'
    LMS_USER = 'Lms user'
    OAUTH1_CREDENTIALS = 'Oauth1 credentials'
    OBJECTIVE = 'Objective'
    OBJECTIVE_ACCESS = 'Objective access'
    OBJECTIVE_WORKFLOW = 'Objective workflow'
    PERMISSION = 'Permission'
    ROLE = 'Role'
    ROLE_PATTERN = 'Role pattern'
    ROLE_PATTERN_PERMISSION = 'Role pattern permission'
    USER_ROLE = 'User role'
    USER = 'User'
    TENANT = 'Tenant'
    TENANT_SETTING = 'TenantSetting'
    RESOURCE_LIBRARIES = 'Resource libraries'
    GRADING_SCALE = 'Grading scale'

    @classmethod
    def to_human_readable(cls, entity: 'Entities') -> str:
        entity_as_list: List[str] = re.findall('[A-Z][^A-Z]*', entity.value)
        return ' '.join(entity_as_list)
