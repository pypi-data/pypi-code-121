'''File for handling all operations relating to the Address datatype'''

import random
from faker import Faker
from fhir.resources.address import Address


def generateAddress(use: str = 'home') -> dict:
    '''Function for generating a FHIR Address'''

    address_data = {
        'use': use,
        'line': [generateLineAddress()],
        'city': generateCityAddress(),
        'state': generateStateAddress(),
        'postalCode': generatePostalCodeAddress()
    }

    address = Address(**address_data).dict()
    return address


def generateLineAddress():
    '''Function for generating a line in a FHIR Address'''
    fake = Faker()
    return fake.street_address()


def generateCityAddress():
    '''Function for generating a city in a FHIR Address'''
    fake = Faker()
    return fake.city()


def generateStateAddress():
    '''Function for generating a state in a FHIR Address'''
    fake = Faker()
    return fake.state_abbr()


def generatePostalCodeAddress():
    '''Function for generating a postal code in a FHIR Address'''
    rand_str = str(random.randint(1, 99950))
    if len(rand_str) != 5:
        leading_zeros = ''.join(['0' for x in range(0, 5 - len(rand_str))])
        rand_str = leading_zeros + rand_str
    return rand_str
