'''File for handling all operations relating to the US Core Condition resource'''

from fhirgenerator.resources.r4.condition import generateCondition


def generateUSCoreCondition(detail: dict, patient_id: str, start_date: str, days: str):
    '''Generate a US Core Condition'''

    condition_resource = generateCondition(detail, patient_id, start_date, days)
    condition_resource['meta'] = {'profile': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition']}
    condition_resource['clinicalStatus'] = {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical', 'code': 'active', 'display': 'Active'}]}
    condition_resource['category'] = [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-category', 'code': 'problem-list-item'}]}]
    return condition_resource
