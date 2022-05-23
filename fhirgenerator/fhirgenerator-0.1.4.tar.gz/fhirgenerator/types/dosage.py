'''File for handling all operations relating to the Dosage datatype'''

import random


def generateDosage(enum_set_list: list = [], min_value: int = 0, max_value: int = 0, decimal_value: int = 0, unit_str: str = '') -> dict:
    '''Generate a Dosage for a MedicationStatement'''
    if enum_set_list:
        dose_quantity_full = random.choice(enum_set_list)
        value, unit_string = dose_quantity_full.split(' ')
        dose_quantity_system, dose_quantity_code, dose_quantity_unit = unit_string.split('^')
        dose_quantity = {
            'value': value,
            'system': dose_quantity_system,
            'code': dose_quantity_code,
            'unit': dose_quantity_unit
        }
    else:
        if not unit_str:
            raise NameError('There was no enumSetList in your configuration and there is no listed unit. Without an enumSetList, you MUST have the unit key in your configuration')
        if decimal_value:
            system, code, unit = unit_str.split('^')
            dose_quantity = {
                'value': round(random.uniform(min_value, max_value), decimal_value),
                'system': system,
                'code': code,
                'unit': unit
            }
        else:
            system, code, unit = unit_str.split('^')
            dose_quantity = {
                'value': round(random.uniform(min_value, max_value)),
                'system': system,
                'code': code,
                'unit': unit
            }

    dosage_dict = {
        'doseAndRate': [{
            'doseQuantity': dose_quantity
        }]
    }
    return dosage_dict
