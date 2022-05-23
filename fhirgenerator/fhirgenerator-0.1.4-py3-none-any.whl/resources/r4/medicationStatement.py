'''File for handling all operations relating to the MedicationStatement resource'''

import uuid
import random
from fhir.resources.medicationstatement import MedicationStatement

from fhirgenerator.helpers.helpers import makeRandomDate
from fhirgenerator.types.dosage import generateDosage


def generateMedicationStatement(resource_detail: dict, patient_id: str, start_date: str, days: int) -> dict:
    '''Generate MedicationStatement resource from resource detail from configuration'''

    ms_id = str(uuid.uuid4())

    medication_cc = random.choice(resource_detail['codes'])

    random_date = makeRandomDate(start_date, days)

    try:
        if 'enumSetList' in resource_detail:
            enum_set_list = resource_detail['enumSetList']
            dosage = generateDosage(enum_set_list=enum_set_list)
        else:
            if 'decimalValue' in resource_detail:
                dosage = generateDosage(min_value=resource_detail['minValue'], max_value=resource_detail['maxValue'], decimal_value=resource_detail['decimalValue'], unit_str=resource_detail['unit'])
            else:
                dosage = generateDosage(min_value=resource_detail['minValue'], max_value=resource_detail['maxValue'], unit_str=resource_detail['unit'])
    except KeyError:
        raise NameError('There was no enumSetList in your configuration and there is no listed unit. Without an enumSetList, you MUST have the unit key in your configuration.')

    ms_data = {
        'id': ms_id,
        'status': 'completed',
        'medicationCodeableConcept': {'coding': [medication_cc]},
        'effectiveDateTime': random_date,
        'subject': {
            'reference': f'Patient/{patient_id}'
        },
        'dosage': [dosage]
    }

    medicationstatement_resource = MedicationStatement(**ms_data).dict()
    return medicationstatement_resource
