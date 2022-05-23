'''File for handling all operations relating to the US Core Body Height Observation resource'''

from fhirgenerator.resources.r4.observation import generateObservation


def generateUSCoreBodyHeightObservation(detail: dict, patient_id: str, start_date: str, days: str) -> dict:
    '''Generate a US Core Body Height Observation'''

    detail['codes'] = [{'system': 'http://loinc.org', 'code': '8302-2'}]
    observation_resource = generateObservation(detail, patient_id, start_date, days)
    observation_resource['meta'] = {'profile': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-body-height']}
    observation_resource['category'] = [{"coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "vital-signs",
        "display": "Vital Signs"
    }]}]

    return observation_resource
