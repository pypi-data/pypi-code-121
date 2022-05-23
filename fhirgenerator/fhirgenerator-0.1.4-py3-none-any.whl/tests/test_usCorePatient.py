'''Testing US Core Patient generator'''

import orjson
from fhirgenerator.resources.uscore_r4.usCorePatient import generateUSCorePatient
from fhirgenerator.helpers.helpers import calculateAge, default


def testUSCorePatientGenerator():
    '''Test function for US Core Patient Generator'''
    patient_config = {
        "age": 66,
        "gender": 'F',
        "startDate": '01-01-2022'
    }
    created_resource = generateUSCorePatient(patient_config)

    assert created_resource['resourceType'] == 'Patient'
    assert created_resource['meta']['profile'][0] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient'
    assert created_resource['extension'][0]['url'] in ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity']
    assert created_resource['extension'][1]['url'] in ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity']
    assert created_resource['gender'] == 'female'
    assert calculateAge(created_resource['birthDate'], start=patient_config['startDate']) == patient_config['age']
    assert isinstance(created_resource['name'], list)
    assert isinstance(created_resource['address'], list)
    assert created_resource['identifier'][0]['system'] == 'urn:fhirgen:mrn'
    assert created_resource['identifier'][0]['type']['coding'][0] == {'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'MR'}
    assert len(created_resource['identifier'][0]['value']) == 11

    with open('fhirgenerator/tests/output/test_usCorePatient.json', 'wb') as outfile:
        outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
