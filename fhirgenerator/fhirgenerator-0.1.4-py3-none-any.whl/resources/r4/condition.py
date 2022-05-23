'''File for handling all operations relating to the Condition resource'''

import uuid
import random
from fhir.resources.condition import Condition

from fhirgenerator.helpers.helpers import makeRandomDate


def generateCondition(resource_detail: dict, patient_id: str, start_date: str, days: int) -> dict:
    '''Generate Condition Resource from resource detail from configuration'''

    condition_id = str(uuid.uuid4())

    condition_code = random.choice(resource_detail['codes'])

    random_date = makeRandomDate(start_date, days)

    condition_data = {
        'id': condition_id,
        'code': {
            'coding': [
                condition_code
            ]
        },
        'subject': {
            'reference': f'Patient/{patient_id}'
        },
        'onsetDateTime': str(random_date)
    }

    condition_resource = Condition(**condition_data)
    return dict(condition_resource.dict())
