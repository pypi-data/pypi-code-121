'''Testing US Core Condition generator'''

import orjson
from dateutil import parser
import datetime
from fhirgenerator.resources.uscore_r4.usCoreCondition import generateUSCoreCondition
from fhirgenerator.helpers.helpers import default


def testUSCoreConditionGenerator():
    '''Test function for US Core Condition Generator'''
    with open('fhirgenerator/tests/input/config_usCore.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    condition_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'USCoreCondition':
            condition_resource_details.append(detail)

    for i, detail in enumerate(condition_resource_details):
        created_resource = generateUSCoreCondition(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'Condition'
        assert created_resource['meta']['profile'][0] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition'
        assert created_resource['clinicalStatus'] == {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical', 'code': 'active', 'display': 'Active'}]}
        assert created_resource['category'] == [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-category', 'code': 'problem-list-item'}]}]
        assert created_resource['code']['coding'][0] in detail['codes']
        assert (created_resource['onsetDateTime'] >= parser.parse(config_dict['startDate'])) and (created_resource['onsetDateTime'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'

        with open(f'fhirgenerator/tests/output/test_usCoreCondition_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
