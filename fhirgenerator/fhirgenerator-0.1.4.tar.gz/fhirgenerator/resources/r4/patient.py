'''File for handling all operations relating to the Patient resource'''

import uuid
import random
import datetime
from dateutil import parser
from fhir.resources.patient import Patient
from fhirgenerator.types.contactPoint import generateContactPoint

from fhirgenerator.types.humanName import generateName
from fhirgenerator.types.address import generateAddress
from fhirgenerator.types.identifier import generateMRNIdentifier, generateSSNIdentifier

gender_map = {
    'M': 'male',
    'F': 'female',
    'O': 'other',
    'U': 'unknown'
}

marital_status = [
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "A",
        "display": "Annulled"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "D",
        "display": "Divorced"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "I",
        "display": "Interlocutory"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "L",
        "display": "Legally Separated"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "M",
        "display": "Married"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "P",
        "display": "Polygamous"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "S",
        "display": "Never Married"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "T",
        "display": "Domestic partner"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "U",
        "display": "unmarried"
    },
    {
        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
        "code": "W",
        "display": "Widowed"
    }
]


def generateBirthDateFromAge(age: int, startDate: str) -> str:
    '''Generate a random birthday that matches the given age'''
    start = parser.parse(startDate)
    random_number_of_days = random.randrange(365)
    birthdate = datetime.date(start.year - age - 1, start.month, start.day) + datetime.timedelta(days=random_number_of_days)
    return str(birthdate)


def generatePatient(configuration: dict) -> dict:
    '''Generate Patient Resource'''

    patient_id = str(uuid.uuid4())
    patient_data = {
        'id': patient_id,
        'identifier': [generateMRNIdentifier(), generateSSNIdentifier()],
        'name': [generateName(gender=configuration['gender'], use='official')],
        'address': [generateAddress(use='home')],
        'telecom': [generateContactPoint(system='phone')],
        'gender': gender_map[configuration['gender'].upper()],
        'birthDate': generateBirthDateFromAge(configuration['age'], configuration['startDate']),
        'maritalStatus': {'coding': [random.choice(marital_status)]}
    }

    # Handles if a Patient will have a usual or maiden name
    if random.choices([True, False], weights=[40, 60]):  # 40% chance of having a maiden name
        patient_data['name'].append(generateName(gender=configuration['gender'], use='maiden'))
    elif random.choices([True, False], weights=[60, 40]):  # 60% chance of having a usual name
        patient_data['name'].append(generateName(gender=configuration['gender'], use='usual'))

    # Handles if a Patient will have an old address
    if random.choices([True, False], weights=[25, 75]):
        patient_data['address'].append(generateAddress(use='old'))

    # Handles if a Patient will have an email address
    if random.choices([True, False], weights=[90, 10]):
        patient_data['telecom'].append(generateContactPoint(system='email'))

    patient_resource = Patient(**patient_data).dict()
    return patient_resource
