'''Command line functionality for package to generate new Python files for extending this package'''

import argparse
import os


def main():
    '''
    Command line function to generate new Python files for extending this package
    example usage: fhirgenerator new profile observation ObservationCauseOfDeathCondition
    '''
    parser = argparse.ArgumentParser(prog='fhirgenerator_make_new_profile')
    parser.add_argument('action', help='Only supports new at this time')
    parser.add_argument('type', help='Only supports profile at this time')
    parser.add_argument('resource_type', help='name of resource template you want to generate')
    parser.add_argument('profile_name', help='name of profile you want to generate')

    args = parser.parse_args()

    assert args.action == 'new'
    assert args.type == 'profile'

    resource_type = args.resource_type
    profile_name = args.profile_name
    output_file_text = f'''from fhirgenerator.resources.r4.{resource_type.lower()} import generate{resource_type.capitalize()}
from fhir.resources.{resource_type.lower()} import {resource_type.capitalize()}


def generate{profile_name[:1].upper() + profile_name[1:]}(resource_detail, patient_id, start_date, days):
    # Pre-built template using the fhirgenerator command line tool

    {resource_type.lower()} = {{}}

    # START CODE

    # END CODE
    {resource_type.lower()} = generate{resource_type.capitalize()}(resource_detail, patient_id, start_date, days)

    {resource_type.lower()} = {resource_type.capitalize()}(**{resource_type.lower()}).dict()
    return {resource_type.lower()}
'''

    if os.path.isfile(f'generate{profile_name}.py'):
        overwrite = input('File already exists. Overwrite (Y/n)? ')
        if overwrite.lower() == 'y':
            with open(f'generate{profile_name}.py', 'w') as outfile:
                outfile.write(output_file_text)
            print(f'Saved new Profile file at generate{profile_name}.py')
        else:
            print('File not saved')
    else:
        with open(f'generate{profile_name}.py', 'w') as outfile:
            outfile.write(output_file_text)
        print(f'Saved new Profile file at generate{profile_name}.py')
