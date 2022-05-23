'''File for handling all operations relating to the US Core Laboratory Result Observation resource'''

from fhirgenerator.resources.r4.observation import generateObservation


def generateUSCoreLabResultObservation(detail: dict, patient_id: str, start_date: str, days: str) -> dict:
    '''Generate a US Core Lab Result Observation'''

    observation_resource = generateObservation(detail, patient_id, start_date, days)
    observation_resource['meta'] = {'profile': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab']}
    observation_resource['category'] = [{"coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "laboratory",
        "display": "Laboratory"
    }]}]
    return observation_resource
