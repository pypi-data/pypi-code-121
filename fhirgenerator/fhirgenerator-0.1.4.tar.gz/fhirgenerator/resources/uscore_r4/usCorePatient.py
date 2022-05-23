'''File for handling all operations relating to the US Core Patient resource'''

import random
from fhirgenerator.resources.r4.patient import generatePatient
from fhir.resources.extension import Extension

race_choices = [
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '1002-5',
        'display': 'American Indian or Alaska Native'
    },
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2028-9',
        'display': 'Asian'
    },
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2054-5',
        'display': 'Black or African American'
    },
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2076-8',
        'display': 'Native Hawaiian or Other Pacific Islander'
    },
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2106-3',
        'display': 'White'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor',
        'code': 'UNK',
        'display': 'unknown'
    },
    {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor',
        'code': 'ASKU',
        'display': 'asked but unknown'
    }
]

ethicity_choices = [
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2135-2',
        'display': 'Hispanic or Latino'
    },
    {
        'system': 'urn:oid:2.16.840.1.113883.6.238',
        'code': '2186-5',
        'display': 'Not Hispanic or Latino'
    }
]


def generateUSCorePatient(config: dict) -> dict:
    '''Generate Patient Resource'''
    patient_resource = generatePatient(config)
    patient_resource['meta'] = {'profile': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient']}
    patient_resource['extension'] = [generateUSCoreRaceExtension(), generateUSCoreEthnicityExtension()]
    return patient_resource


def generateUSCoreRaceExtension() -> dict:
    '''Generate US Core Race Extension'''
    race_choice = random.choice(race_choices)

    us_core_race_ext_data = {
        'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
        'extension': [
            {
                'url': 'ombCategory',
                'valueCoding': race_choice
            },
            {
                'url': 'text',
                'valueString': race_choice['display']
            }
        ]
    }

    us_core_race_extension = Extension(**us_core_race_ext_data)

    return dict(us_core_race_extension.dict())


def generateUSCoreEthnicityExtension() -> dict:
    '''Generate US Core Ethnicity Extension'''
    ethnicity_choice = random.choice(ethicity_choices)

    us_core_ethnicity_ext_data = {
        'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity',
        'extension': [
            {
                'url': 'ombCategory',
                'valueCoding': ethnicity_choice
            },
            {
                'url': 'text',
                'valueString': ethnicity_choice['display']
            }
        ]
    }

    us_core_ethnicity_extension = Extension(**us_core_ethnicity_ext_data)

    return dict(us_core_ethnicity_extension.dict())
