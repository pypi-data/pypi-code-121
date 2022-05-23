'''Testing Main function'''

import orjson
import datetime
from dateutil import parser
from fhirgenerator.main import generateResources
from fhirgenerator.helpers.helpers import default


def testMain():
    '''Testing function for main.py'''

    with open('fhirgenerator/tests/input/config.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    output_collection_bundle = generateResources(config_dict=config_dict, bundle_type='collection')
    output_trans_bundle = generateResources(config_dict=config_dict, bundle_type='transaction')

    with open('fhirgenerator/tests/output/test_main_transaction.json', 'wb') as outfile:
        outfile.write(orjson.dumps(output_trans_bundle, default=default, option=orjson.OPT_NAIVE_UTC))
    with open('fhirgenerator/tests/output/test_main_collection.json', 'wb') as outfile:
        outfile.write(orjson.dumps(output_collection_bundle, default=default, option=orjson.OPT_NAIVE_UTC))

    patient_list_collection = list(filter(lambda entry: entry['resource']['resourceType'] == 'Patient', output_collection_bundle['entry']))
    patient_list_transaction = list(filter(lambda entry: entry['resource']['resourceType'] == 'Patient', output_trans_bundle['entry']))

    observation_list_collection = list(filter(lambda entry: entry['resource']['resourceType'] == 'Observation', output_collection_bundle['entry']))
    observation_list_transaction = list(filter(lambda entry: entry['resource']['resourceType'] == 'Observation', output_trans_bundle['entry']))

    observation_dates_collection = [resource['resource']['effectiveDateTime'] for resource in observation_list_collection]
    observation_dates_transaction = [resource['resource']['effectiveDateTime'] for resource in observation_list_transaction]

    condition_list_collection = list(filter(lambda entry: entry['resource']['resourceType'] == 'Condition', output_collection_bundle['entry']))
    condition_list_transaction = list(filter(lambda entry: entry['resource']['resourceType'] == 'Condition', output_trans_bundle['entry']))

    condition_dates_collection = [resource['resource']['onsetDateTime'] for resource in condition_list_collection]
    condition_dates_transaction = [resource['resource']['onsetDateTime'] for resource in condition_list_transaction]

    obs_mins = [detail['minOccurrencesPerCycle'] if detail['fhirResource'] == 'Observation' else 0 for detail in config_dict['resourceDetails']]
    obs_maxs = [detail['maxOccurrencesPerCycle'] if detail['fhirResource'] == 'Observation' else 0 for detail in config_dict['resourceDetails']]
    min_num_of_observations = config_dict['numberPatients'] * sum(obs_mins)
    max_num_of_observations = config_dict['numberPatients'] * sum(obs_maxs)

    con_mins = [detail['minOccurrencesPerCycle'] if detail['fhirResource'] == 'Condition' else 0 for detail in config_dict['resourceDetails']]
    con_maxs = [detail['maxOccurrencesPerCycle'] if detail['fhirResource'] == 'Condition' else 0 for detail in config_dict['resourceDetails']]
    min_num_of_conditions = config_dict['numberPatients'] * sum(con_mins)
    max_num_of_conditions = config_dict['numberPatients'] * sum(con_maxs)

    start_date = parser.parse(config_dict['startDate'])
    end_date = start_date + datetime.timedelta(days=config_dict['days'])

    obs_dates_in_range_collection = [date_time >= start_date and date_time <= end_date for date_time in observation_dates_collection]
    obs_dates_in_range_transaction = [date_time >= start_date and date_time <= end_date for date_time in observation_dates_transaction]

    con_dates_in_range_collection = [date_time >= start_date and date_time <= end_date for date_time in condition_dates_collection]
    con_dates_in_range_transaction = [date_time >= start_date and date_time <= end_date for date_time in condition_dates_transaction]

    assert len(patient_list_collection) == config_dict['numberPatients']
    assert len(observation_list_collection) >= min_num_of_observations and len(observation_list_collection) <= max_num_of_observations
    assert all(obs_dates_in_range_collection)
    assert len(condition_list_collection) >= min_num_of_conditions and len(condition_list_collection) <= max_num_of_conditions
    assert all(con_dates_in_range_collection)

    assert len(patient_list_transaction) == config_dict['numberPatients']
    assert len(observation_list_transaction) >= min_num_of_observations and len(observation_list_transaction) <= max_num_of_observations
    assert all(obs_dates_in_range_transaction)
    assert len(condition_list_transaction) >= min_num_of_conditions and len(condition_list_transaction) <= max_num_of_conditions
    assert all(con_dates_in_range_transaction)


def testMainUSCore():
    '''Testing function for generateResources with US Core Config'''

    with open('fhirgenerator/tests/input/config_usCore.json', 'rb') as infile:
        config_dict = orjson.loads(infile.read())

    output_collection_bundle = generateResources(config_dict=config_dict, bundle_type='collection')
    output_trans_bundle = generateResources(config_dict=config_dict, bundle_type='transaction')

    with open('fhirgenerator/tests/output/test_main_uscore_transaction.json', 'wb') as outfile:
        outfile.write(orjson.dumps(output_trans_bundle, default=default, option=orjson.OPT_NAIVE_UTC))
    with open('fhirgenerator/tests/output/test_main_uscore_collection.json', 'wb') as outfile:
        outfile.write(orjson.dumps(output_collection_bundle, default=default, option=orjson.OPT_NAIVE_UTC))

    patient_list_collection = list(filter(lambda entry: entry['resource']['resourceType'] == 'Patient', output_collection_bundle['entry']))
    patient_list_transaction = list(filter(lambda entry: entry['resource']['resourceType'] == 'Patient', output_trans_bundle['entry']))

    assert len(patient_list_collection) == config_dict['numberPatients']
    assert len(patient_list_transaction) == config_dict['numberPatients']
    # TODO: Add more assertions for US Core Bundles
