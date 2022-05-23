import json
import argparse
from pathlib import Path
from utils import generate_users, generate_projects

'''
A script which generates and outputs random test data, into a file used by the performance unit tests
for help run python test_data_generator.py -h
'''

parser = argparse.ArgumentParser(description='generates and outputs random test data, into a file used by the performance unit tests')
parser.add_argument(dest='count', metavar='N', type=int, help='the number of users (and projects) to generate')

args = parser.parse_args()
count = args.count

user_template = {
    'model': 'tests.user',
    'pk': 0,
    'fields': {
        'username': 'john',
        'email': 'jlennon@c.coop',
        'password':'glass onion'
    }
}

project_template = {
    'model': 'tests.project',
    'pk': 0,
    'fields': {
        'status': 'Public',
        'description': 'Test'
    }
}

fixture = generate_users(count, user_template)
fixture = generate_projects(count, project_template, fixture=fixture, production=False)

with open(Path(__file__).parent / "../fixtures/test.json", 'w') as output:
    json.dump(fixture, output)

print(str(count))
