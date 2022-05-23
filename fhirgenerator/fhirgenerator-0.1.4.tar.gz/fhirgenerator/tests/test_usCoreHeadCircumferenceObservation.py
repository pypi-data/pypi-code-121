'''Testing US Core Head Circumference Observation generator'''

import orjson
from dateutil import parser
import datetime
from fhirgenerator.resources.uscore_r4.usCoreHeadCircumferenceObservation import generateUSCoreHeadCircumferenceObservation
from fhirgenerator.helpers.helpers import default


def testUSCoreHeadCircumferenceObservationGenerator():
    '''Test function for US Core Head Circumference Observation Generator'''

    with open('fhirgenerator/tests/input/config_usCore.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    observation_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'USCoreHeadCircumferenceObservation':
            observation_resource_details.append(detail)

    for i, detail in enumerate(observation_resource_details):
        created_resource = generateUSCoreHeadCircumferenceObservation(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'Observation'
        assert created_resource['meta']['profile'] == ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-head-circumference']
        assert created_resource['status'] == 'final'
        assert created_resource['category'] == [{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "vital-signs",
            "display": "Vital Signs"
        }]}]
        assert created_resource['code']['coding'][0] == {'system': 'http://loinc.org', 'code': '9843-4'}
        assert (created_resource['effectiveDateTime'] >= parser.parse(config_dict['startDate'])) and (created_resource['effectiveDateTime'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'
        assert 'value' in created_resource['valueQuantity']
        assert 'unit' in created_resource['valueQuantity']
        assert 'system' in created_resource['valueQuantity']
        assert 'code' in created_resource['valueQuantity']

        with open(f'fhirgenerator/tests/output/test_usCoreHeadCircumferenceObservation_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
