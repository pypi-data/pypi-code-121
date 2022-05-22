from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
)


JIRA_CLOSED_TASK_STATUS_NAME = 'Закрыт'

JIRA_PROJECTS_CONFORMITY = {
    'BOBUH': (
        ProjectEnum.WEB_BB_ACCOUNTING,
    ),
    'BOZIK': (
        ProjectEnum.WEB_BB_SALARY,
    ),
    'BOAIP': (
        ProjectEnum.WEB_BB_ACCOUNTING,
        ProjectEnum.WEB_BB_VEHICLE,
        ProjectEnum.WEB_BB_FOOD,
    ),
}

JIRA_STAND_URL_RE = r'\|URL тестового стенда\|[\s]*([\w\d:\/\-\\.]+)\|'

JIRA_ENT_IDS_RE = (
    r'\|Идентификатор учреждения \(ent_id\)\|[\s]*([\d]+)[\s]*\|'
)


