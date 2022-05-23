'''File for handling US Core Resource Generation'''

from fhirgenerator.resources.uscore_r4.usCoreBMIObservation import generateUSCoreBMIObservation
from fhirgenerator.resources.uscore_r4.usCoreBodyHeightObservation import generateUSCoreBodyHeightObservation
from fhirgenerator.resources.uscore_r4.usCoreBodyTemperatureObservation import generateUSCoreBodyTemperatureObservation
from fhirgenerator.resources.uscore_r4.usCoreBodyWeightObservation import generateUSCoreBodyWeightObservation
from fhirgenerator.resources.uscore_r4.usCoreCondition import generateUSCoreCondition
from fhirgenerator.resources.uscore_r4.usCoreHeadCircumferenceObservation import generateUSCoreHeadCircumferenceObservation
from fhirgenerator.resources.uscore_r4.usCoreHeartRateObservation import generateUSCoreHeartRateObservation
from fhirgenerator.resources.uscore_r4.usCoreLabResultObservation import generateUSCoreLabResultObservation
from fhirgenerator.resources.uscore_r4.usCoreLocation import generateUSCoreLocation


def handleUSCore(resource_detail: dict, patient_id: str, start_date: str, days: str) -> dict:
    '''Function to handle US Core resource generation'''

    resource_type = resource_detail['fhirResource']
    match resource_type:
        case 'USCoreCondition':
            return_resource = generateUSCoreCondition(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreLabResultObservation':
            return_resource = generateUSCoreLabResultObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreBMIObservation':
            return_resource = generateUSCoreBMIObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreHeadCircumferenceObservation':
            return_resource = generateUSCoreHeadCircumferenceObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreBodyHeightObservation':
            return_resource = generateUSCoreBodyHeightObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreBodyWeightObservation':
            return_resource = generateUSCoreBodyWeightObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreBodyTemperatureObservation':
            return_resource = generateUSCoreBodyTemperatureObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreHeartRateObservation':
            return_resource = generateUSCoreHeartRateObservation(detail=resource_detail, patient_id=patient_id, start_date=start_date, days=days)
        case 'USCoreLocation':
            return_resource = generateUSCoreLocation()

    return return_resource
