'''Testing Location generator'''

import orjson
from fhirgenerator.resources.r4.location import generateLocation
from fhirgenerator.helpers.helpers import default
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint


def testLocationGenerator():
    '''Test function for Location Generator'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    location_resource_details = []
    for detail in config_dict['resourceDetails']:
        if detail['fhirResource'] == 'Location':
            location_resource_details.append(detail)

    for i, detail in enumerate(location_resource_details):

        created_resource = generateLocation()

        assert created_resource['resourceType'] == 'Location'
        assert created_resource['status'] == 'active'

        assert isinstance(Address(**created_resource['address']), Address)
        assert isinstance(ContactPoint(**created_resource['telecom'][0]), ContactPoint)

        with open(f'fhirgenerator/tests/output/test_location_{i}.json', 'wb') as outfile:
            outfile.write(orjson.dumps(created_resource, default=default, option=orjson.OPT_NAIVE_UTC))
