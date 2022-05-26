import os
from pprint import pprint

import projectal
from projectal.enums import Currency, ConstraintType, TaskType

projectal.api_base = os.environ.get('PROJECTAL_URL')
projectal.api_username = os.environ.get('PROJECTAL_USERNAME')
projectal.api_password = os.environ.get('PROJECTAL_PASSWORD')

print('Creating project')
project = projectal.Project.create({
    'name': 'Example Project',
    'fixedCost': 322000,
    'currencyCode': Currency.AUD
})
pprint(project)

print('Creating task with project as holder')
task = projectal.Task.create(project, {
    'name': 'Example Task',
    'constraintType': ConstraintType.ASAP,
    'taskType': TaskType.Task
})
pprint(task)

print('Getting project with tasks')
project = projectal.Project.get(project, links='TASK')
# See 'taskList' in response
pprint(project)

