'''Testing MedicationStatement generator'''

import orjson
import pytest
from dateutil import parser
import datetime
from fhirgenerator.resources.r4.medicationStatement import generateMedicationStatement
from fhirgenerator.helpers.helpers import default


def testMedicationStatementGenerator():
    '''Test function for MedicationStatement Generator'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    ms_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'MedicationStatement':
            ms_resource_details.append(detail)

    for i, detail in enumerate(ms_resource_details):
        created_resource = generateMedicationStatement(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'MedicationStatement'
        assert created_resource['status'] == 'completed'
        assert created_resource['medicationCodeableConcept']['coding'][0] in detail['codes']
        assert (created_resource['effectiveDateTime'] >= parser.parse(config_dict['startDate'])) and (created_resource['effectiveDateTime'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'

        dose_quantity = created_resource['dosage'][0]['doseAndRate'][0]['doseQuantity']
        if 'enumSetList' in detail:
            enum_set_list = detail['enumSetList']
            assert str(dose_quantity['value']) + ' ' + dose_quantity['system'] + '^' + dose_quantity['code'] + '^' + dose_quantity['unit'] in enum_set_list
        else:
            assert dose_quantity['value'] <= detail['maxValue'] and dose_quantity['value'] >= detail['minValue']
            test_system, test_code, test_unit = detail['unit'].split('^')
            assert dose_quantity['system'] == test_system
            assert dose_quantity['code'] == test_code
            assert dose_quantity['unit'] == test_unit

        with open(f'fhirgenerator/tests/output/test_medicationStatement_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))


def testMedicationStatementWithError():
    '''Test function for MedicationStatement Generator that should raise a NameError'''

    patient_id = '26774-827647-736278-3737646'

    detail = {
        "fhirResource": "MedicationStatement",
        "codes": [
            {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "18631"},
            {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "3640"},
            {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "8698"}
        ],
        "minValue": 3,
        "maxValue": 7,
        "minOccurrencesPerCycle": 1,
        "maxOccurrencesPerCycle": 8,
        "cycleLengthInDays": 365
    }
    with pytest.raises(NameError):
        generateMedicationStatement(detail, patient_id, '01-01-2022', 365)
