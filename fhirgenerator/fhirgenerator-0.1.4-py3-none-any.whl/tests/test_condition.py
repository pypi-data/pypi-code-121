'''Testing Cndition generator'''

import orjson
from dateutil import parser
import datetime
from fhirgenerator.resources.r4.condition import generateCondition
from fhirgenerator.helpers.helpers import default


def testConditionGenerator():
    '''Test function for Condition Generator'''
    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    condition_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'Condition':
            condition_resource_details.append(detail)

    for i, detail in enumerate(condition_resource_details):
        created_resource = generateCondition(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'Condition'
        assert created_resource['code']['coding'][0] in detail['codes']
        assert (created_resource['onsetDateTime'] >= parser.parse(config_dict['startDate'])) and (created_resource['onsetDateTime'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'

        with open(f'fhirgenerator/tests/output/test_condition_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
