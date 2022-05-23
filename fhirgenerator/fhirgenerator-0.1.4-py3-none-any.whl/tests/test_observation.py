'''Testing Observation generator'''

import orjson
from dateutil import parser
import datetime
from fhirgenerator.resources.r4.observation import generateObservation
from fhirgenerator.helpers.helpers import default


def testObservationGenerator():
    '''Test function for Observation Generator'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    patient_id = '26774-827647-736278-3737646'

    observation_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'Observation':
            observation_resource_details.append(detail)

    for i, detail in enumerate(observation_resource_details):

        if 'enumSetList' in detail:
            enum_set_list = detail['enumSetList']
            if 'value' in enum_set_list[0]:
                value_x_type = 'Quantity'
            elif 'coding' in enum_set_list[0]:
                value_x_type = 'CodeableConcept'
            elif len(enum_set_list[0].split(':')) > 1:
                value_x_type = 'Ratio'
            else:
                value_x_type = 'String'
        elif 'decimalValue' in detail:
            value_x_type = 'Quantity'
        elif 'minValue' in detail:
            value_x_type = 'Integer'
        elif 'dateRange' in detail:
            value_x_type = 'DateTime'
        else:
            value_x_type = 'None'

        created_resource = generateObservation(detail, patient_id, config_dict['startDate'], config_dict['days'])

        assert created_resource['resourceType'] == 'Observation'
        assert created_resource['status'] == 'final'
        assert created_resource['code']['coding'][0] in detail['codes']
        assert (created_resource['effectiveDateTime'] >= parser.parse(config_dict['startDate'])) and (created_resource['effectiveDateTime'] <= parser.parse(config_dict['startDate']) + datetime.timedelta(days=config_dict['days']))
        assert created_resource['subject']['reference'] == f'Patient/{patient_id}'

        match value_x_type:
            case 'Ratio':
                assert str(created_resource['valueRatio']['numerator']['value']) + ':' + str(created_resource['valueRatio']['denominator']['value']) in detail['enumSetList']
            case 'CodeableConcept':
                assert created_resource['valueCodeableConcept'] in detail['enumSetList']
            case 'Quantity':
                if 'enumSetList' in detail:
                    assert created_resource['valueQuantity'] in detail['enumSetList']
                else:
                    assert created_resource['valueQuantity']['value'] <= detail['maxValue'] and created_resource['valueQuantity']['value'] >= detail['minValue']
                    if 'unit' in detail:
                        test_system, test_code, test_unit = detail['unit'].split('^')
                        assert created_resource['valueQuantity']['system'] == test_system
                        assert created_resource['valueQuantity']['code'] == test_code
                        assert created_resource['valueQuantity']['unit'] == test_unit
            case 'String':
                assert created_resource['valueString'] in detail['enumSetList']
            case 'Integer':
                if 'enumSetList' in detail:
                    assert created_resource['valueInteger'] in detail['enumSetList']
                else:
                    assert created_resource['valueInteger'] <= detail['maxValue'] and created_resource['valueInteger'] >= detail['minValue']
            case 'DateTime':
                assert created_resource['valueDateTime'] >= created_resource['effectiveDateTime'] + datetime.timedelta(days=detail["dateRange"][0])
                assert created_resource['valueDateTime'] <= created_resource['effectiveDateTime'] + datetime.timedelta(days=detail["dateRange"][1])
            case 'None':
                assert 'valueRatio' not in created_resource
                assert 'valueCodeableConcept' not in created_resource
                assert 'valueQuantity' not in created_resource
                assert 'valueString' not in created_resource
                assert 'valueInteger' not in created_resource

        with open(f'fhirgenerator/tests/output/test_observation_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))


def testObservationComponentGenerator():
    '''Test Observation Component Generator'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    resource_details = {
        "fhirResource": "Observation",
        "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure"],
        "codes": [
            {"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel with all children optional"}
        ],
        "minOccurrencesPerCycle": 1,
        "maxOccurrencesPerCycle": 1,
        "cycleLengthInDays": 365,
        "components": [
            {
                "codes": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}],
                "minValue": 105,
                "maxValue": 135,
                "unit": "http://unitsofmeasure.org^mm[Hg]^mmHg"
            },
            {
                "codes": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}],
                "minValue": 65,
                "maxValue": 95,
                "unit": "http://unitsofmeasure.org^mm[Hg]^mmHg"
            }
        ]
    }

    patient_id = '26774-827647-736278-3737646'

    created_resource = generateObservation(resource_details, patient_id, config_dict['startDate'], config_dict['days'])

    with open('fhirgenerator/tests/output/test_observation_component.json', 'wb') as outfile:
        outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))


# TODO: write more observation tests for all possible value[x] that the package supports
