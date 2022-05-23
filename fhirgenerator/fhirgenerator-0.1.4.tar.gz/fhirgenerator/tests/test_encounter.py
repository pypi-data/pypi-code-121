'''Testing Encounter generator'''

import orjson
from dateutil import parser
import datetime
from fhirgenerator.resources.r4.encounter import generateEncounter, class_options
from fhirgenerator.helpers.helpers import default


def testEncounterGenerator():
    '''Test function for Encounter Generator'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    encounter_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'Encounter':
            encounter_resource_details.append(detail)

    for i, detail in enumerate(encounter_resource_details):
        created_resource = generateEncounter(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'Encounter'
        assert created_resource['status'] == 'finished'
        assert created_resource['class'] in class_options
        assert created_resource['type'][0]['coding'][0] in detail['codes']
        assert (created_resource['period']['start'] >= parser.parse(config_dict['startDate'])) and (created_resource['period']['start'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'

        with open(f'fhirgenerator/tests/output/test_encounter_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
