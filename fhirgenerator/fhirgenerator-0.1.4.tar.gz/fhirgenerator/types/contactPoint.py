'''File for handling all operations relating to the ContactPoint datatype'''

import random
from faker import Faker
from fhir.resources.contactpoint import ContactPoint


def generateContactPoint(system: str = 'phone') -> dict:
    '''Function for generating a FHIR ContactPoint'''

    fake = Faker()

    contact_point_data = {
        'system': system,
        'use': random.choice(['home', 'work', 'mobile'])
    }

    if system == 'phone':
        contact_point_data['value'] = fake.phone_number()
    elif system == 'email':
        contact_point_data['value'] = fake.free_email()

    contact_point = ContactPoint(**contact_point_data).dict()

    return contact_point
