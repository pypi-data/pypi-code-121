'''File for handling all operations relating to the Encounter resource'''

import uuid
import random
from fhir.resources.encounter import Encounter

from fhirgenerator.helpers.helpers import makeRandomDate

class_options = [
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'AMB',
        'display': 'ambulatory'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'EMER',
        'display': 'emergency'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'FLD',
        'display': 'field'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'HH',
        'display': 'home health'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'IMP',
        'display': 'inpatient encounter'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'ACUTE',
        'display': 'inpatient acute'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'NONAC',
        'display': 'inpatient non-acute'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'OBSENC',
        'display': 'observation encounter'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'PRENC',
        'display': 'pre-admission'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'SS',
        'display': 'short-stay'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
        'code': 'VR',
        'display': 'virtual'
    }
]


def generateEncounter(resource_detail: dict, patient_id: str, start_date: str, days: int) -> dict:
    '''Generate Encounter resource from resource detail from configuration'''

    encounter_id = str(uuid.uuid4())

    encounter_code = random.choice(resource_detail['codes'])

    if 'class' in resource_detail:
        encounter_class = resource_detail['class']
    else:
        encounter_class = random.choice(class_options)

    random_date = makeRandomDate(start_date, days)

    encounter_data = {
        'id': encounter_id,
        'status': 'finished',
        'class': encounter_class,
        'type': [{'coding': [encounter_code]}],
        'subject': {
            'reference': f'Patient/{patient_id}'
        },
        'period': {
            'start': random_date,
            'end': makeRandomDate(str(random_date), 10)
        }
    }

    encounter_resource = Encounter(**encounter_data).dict()
    return encounter_resource
