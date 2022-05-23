import json
import argparse
from pathlib import Path
from datetime import datetime
from utils import generate_users, generate_projects

'''
A script which generates and outputs random production data, into a parameterised file (csv), which can be used as
a Django fixture or imported into a live database
e.g. python manage.py loaddata fixture.json
for help run python prod_data_generator.py -h
'''

# starting from offset ensures that existing users etc are not disturbed
parser = argparse.ArgumentParser(description='generates and outputs random test data, into a file used by the performance unit tests')
parser.add_argument(dest='count', metavar='N', type=int, help='the number of users (and projects) to generate')
parser.add_argument('--offset', dest='offset', type=int, default=100, help='an offset to start primary keys at (should be larger than the largest pre-existing project/user primary key)')
parser.add_argument('-f', dest='file_dest', type=str, default="../fixtures/live.json", help='the file destination to write to')

args = parser.parse_args()
count = args.count
OFFSET = args.offset

user_template = {
    'model': 'djangoldp_account.ldpuser',
    'pk': 0,
    'fields': {
        'username': 'john',
        'email': 'jlennon@c.coop',
        'password':'glass onion'
    }
}

project_template = {
    'model': 'djangoldp_project.project',
    'pk': 0,
    'fields': {
        'description': 'Test',
        'status': 'Public',
        'creationDate': str(datetime.date(datetime.now()))
    }
}

fixture = generate_users(count, user_template, offset=OFFSET)
fixture = generate_projects(count, project_template, fixture=fixture, offset=OFFSET)

with open(Path(__file__).parent / args.file_dest, 'w') as output:
    json.dump(fixture, output)

print(str(count))
