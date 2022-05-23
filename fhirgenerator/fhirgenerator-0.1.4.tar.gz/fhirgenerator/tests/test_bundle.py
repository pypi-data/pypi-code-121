'''Testing Patient generator'''

import orjson
from fhirgenerator.resources.r4.bundle import generateBundle
from fhirgenerator.helpers.helpers import default


def testBundleGenerator():
    '''Test function for Bundle Generator'''

    patient_id = '26774-827647-736278-3737646'
    fake_resources = [
        {
            'resourceType': 'Patient',
            'id': patient_id
        },
        {
            'resourceType': 'Observation',
            'id': '73736464647474',
            'status': 'final',
            'code': {'coding': [{'code': '6457-9'}]}
        },
        {
            'resourceType': 'Condition',
            'id': '7373737383838383',
            'subject': {'reference': f'Patient/{patient_id}'}
        },
        {
            'resourceType': 'Observation',
            'id': '7373738929292727',
            'status': 'final',
            'code': {'coding': [{'code': '6467-9'}]}
        },
    ]
    created_resource_collection = generateBundle(fake_resources)
    created_resource_transaction = generateBundle(fake_resources, type='transaction')

    assert created_resource_transaction['type'] == 'transaction'
    assert created_resource_transaction['entry'][0]['resource']['resourceType'] == 'Patient'
    assert created_resource_transaction['entry'][0]['resource']['id'] == patient_id

    assert created_resource_transaction['entry'][1]['resource']['resourceType'] == 'Observation'
    assert created_resource_transaction['entry'][1]['resource']['id'] == '73736464647474'
    assert created_resource_transaction['entry'][1]['resource']['status'] == 'final'
    assert created_resource_transaction['entry'][1]['resource']['code']['coding'][0]['code'] == '6457-9'

    assert created_resource_transaction['entry'][2]['resource']['resourceType'] == 'Condition'
    assert created_resource_transaction['entry'][2]['resource']['id'] == '7373737383838383'
    assert created_resource_transaction['entry'][2]['resource']['subject']['reference'] == f'Patient/{patient_id}'

    assert created_resource_transaction['entry'][3]['resource']['resourceType'] == 'Observation'
    assert created_resource_transaction['entry'][3]['resource']['id'] == '7373738929292727'
    assert created_resource_transaction['entry'][3]['resource']['status'] == 'final'
    assert created_resource_transaction['entry'][3]['resource']['code']['coding'][0]['code'] == '6467-9'

    assert created_resource_transaction['entry'][0]['request']['method'] == 'POST'
    assert created_resource_transaction['entry'][0]['request']['url'] == 'Patient'

    assert created_resource_transaction['entry'][1]['request']['method'] == 'POST'
    assert created_resource_transaction['entry'][1]['request']['url'] == 'Observation'

    assert created_resource_transaction['entry'][2]['request']['method'] == 'POST'
    assert created_resource_transaction['entry'][2]['request']['url'] == 'Condition'

    assert created_resource_transaction['entry'][3]['request']['method'] == 'POST'
    assert created_resource_transaction['entry'][3]['request']['url'] == 'Observation'

    assert created_resource_collection['type'] == 'collection'

    assert created_resource_collection['entry'][0]['resource']['resourceType'] == 'Patient'
    assert created_resource_collection['entry'][0]['resource']['id'] == patient_id

    assert created_resource_collection['entry'][1]['resource']['resourceType'] == 'Observation'
    assert created_resource_collection['entry'][1]['resource']['id'] == '73736464647474'
    assert created_resource_collection['entry'][1]['resource']['status'] == 'final'
    assert created_resource_collection['entry'][1]['resource']['code']['coding'][0]['code'] == '6457-9'

    assert created_resource_collection['entry'][2]['resource']['resourceType'] == 'Condition'
    assert created_resource_collection['entry'][2]['resource']['id'] == '7373737383838383'
    assert created_resource_collection['entry'][2]['resource']['subject']['reference'] == f'Patient/{patient_id}'

    assert created_resource_collection['entry'][3]['resource']['resourceType'] == 'Observation'
    assert created_resource_collection['entry'][3]['resource']['id'] == '7373738929292727'
    assert created_resource_collection['entry'][3]['resource']['status'] == 'final'
    assert created_resource_collection['entry'][3]['resource']['code']['coding'][0]['code'] == '6467-9'

    with open('fhirgenerator/tests/output/test_bundle_transaction.json', 'wb') as outfile:
        outfile.write(orjson.dumps(created_resource_transaction, default=default, option=orjson.OPT_NAIVE_UTC))
    with open('fhirgenerator/tests/output/test_bundle_collection.json', 'wb') as outfile:
        outfile.write(orjson.dumps(created_resource_collection, default=default, option=orjson.OPT_NAIVE_UTC))
