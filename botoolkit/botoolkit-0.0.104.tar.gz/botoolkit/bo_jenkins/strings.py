JENKINS_JOB_DESCRIPTION_PARSING_ERROR = (
    'Jenkins job "{job_name}" contains wring description "{job_description}". '
    'Please verify and fix it. Description format is "<stand_url>, '
    '<project_name>, ветка <branch>".'
)

WRONG_JENKINS_URL = (
    'Error! Please check --jenkins_url. Value must be correct URL.'
)

EMPTY_JENKINS_URL_ERROR = (
    'Error! Please set --jenkins_url. Value must be correct URL.'
)

EMPTY_JENKINS_USERNAME_ERROR = (
    'Error! Please set --jenkins_username.'
)

EMPTY_JENKINS_PASSWORD_ERROR = (
    'Error! Please set --jenkins_password.'
)

STAND_URL_IS_NOT_URL_ERROR = 'Error! Please check stand_url.'

STAND_WITH_SAME_URL_UNAVAILABLE_OR_NOT_FOUND = (
    'Error! Stand with same url is unavailable or not found.'
)
