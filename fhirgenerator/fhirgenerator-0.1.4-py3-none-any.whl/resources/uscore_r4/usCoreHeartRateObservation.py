'''File for handling all operations relating to the US Core Heart Rate Observation resource'''

from fhirgenerator.resources.r4.observation import generateObservation


def generateUSCoreHeartRateObservation(detail: dict, patient_id: str, start_date: str, days: str) -> dict:
    '''Generate a US Core Heart Rate Observation'''

    detail['codes'] = [{'system': 'http://loinc.org', 'code': '8867-4'}]
    observation_resource = generateObservation(detail, patient_id, start_date, days)
    observation_resource['meta'] = {'profile': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-heart-rate']}
    observation_resource['category'] = [{"coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "vital-signs",
        "display": "Vital Signs"
    }]}]

    return observation_resource
