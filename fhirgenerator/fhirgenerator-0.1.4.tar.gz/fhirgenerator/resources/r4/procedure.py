'''File for handling all operations relating to the Procedure resource'''

import uuid
import random
from fhir.resources.procedure import Procedure

from fhirgenerator.helpers.helpers import makeRandomDate


def generateProcedure(resource_detail: dict, patient_id: str, start_date: str, days: int) -> dict:
    '''Generate Procedure resource from resource detail from configuration'''

    procedure_id = str(uuid.uuid4())

    procedure_code = random.choice(resource_detail['codes'])

    random_date = makeRandomDate(start_date, days)

    procedure_data = {
        'id': procedure_id,
        'code': {
            'coding': [
                procedure_code
            ]
        },
        'status': 'completed',
        'subject': {
            'reference': f'Patient/{patient_id}'
        },
        'performedDateTime': random_date
    }

    procedure_resource = Procedure(**procedure_data).dict()
    return procedure_resource
