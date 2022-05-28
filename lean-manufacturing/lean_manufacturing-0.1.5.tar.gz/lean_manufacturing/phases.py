import atexit
import logging
import traceback
from typing import Tuple
from datetime import datetime
from random import sample
from .logging_handler import _MongoHandler

import pymongo


from .statistics import statistics

localdb                             = pymongo.MongoClient('mongodb://localhost:27017')
global_cap                          = 20

log = logging.getLogger('logs')
log.addHandler(_MongoHandler())
log.setLevel(logging.INFO)

def printTypes(*args):
    print_types                     = print(' '.join([str(type(arg).__name__) for arg in args]))

def setup(collection_name: str, one_to_update: dict, decorator_kwargs: dict, function_kwargs: dict) -> Tuple[datetime, int, dict, list, int]:
    started_setup_at                = datetime.now()
    log_started_setup               = log.info('Started setup', extra={'collection': collection_name})
    process_config                  = localdb['monitor']['processes'].find_one(one_to_update)
    batch_size                      = process_config['batch_size'] if 'batch_size' in process_config else sample(range(1,10), 1)[0] * 10

    log_batch_size                  = log.info(f'Working with batch size {batch_size}', extra={'collection': collection_name})

    complemented_kwargs             = function_kwargs | {'config': process_config, 'batch_size': batch_size} if process_config else function_kwargs

    source_db                       = pymongo.MongoClient(decorator_kwargs['supplier_uri']) if 'supplier_uri' in decorator_kwargs else localdb
    db                              = decorator_kwargs['supplier_db'] if 'supplier_db' in decorator_kwargs else 'products'
    collection                      = decorator_kwargs['supplier_collection']
    base_aggregation                = decorator_kwargs['supplier_aggregation'] if 'supplier_aggregation' in decorator_kwargs else []
    supplier_unique                 = decorator_kwargs['supplier_unique_field'] if 'supplier_unique_field' in decorator_kwargs else None

    existing_products               = [document[supplier_unique] for document in list(localdb['products'][collection_name].aggregate([{'$match':{}},{'$project':{supplier_unique:1}}]))] if supplier_unique else []
    unique_aggregation              = base_aggregation

    batch_aggregation               = unique_aggregation + [{'$sample': { 'size': batch_size } }]
    queue_size_aggregation          = unique_aggregation + [{'$count': 'count' }]

    batch_elements                  = list(source_db[db][collection].aggregate(batch_aggregation))
    source_count                    = list(source_db[db][collection].aggregate(queue_size_aggregation))[0]['count']
    sourced_queue                   = result if (result := source_count - len(existing_products)) > 0 else 0
    input                           = [element for element in batch_elements if element[supplier_unique] not in existing_products] if supplier_unique else batch_elements
    batch_queue                     = len(input)

    update_queue_and_products       = localdb['monitor']['processes'].update_one({'collection': collection_name}, {'$set': {'current_batch_size':batch_size, 'queue':sourced_queue, 'products':len(existing_products)}})

    return started_setup_at, batch_size, complemented_kwargs, input, sourced_queue, batch_queue

def process(collection_name, function, input, sourced_queue, batch_queue, complemented_kwargs):
    if batch_queue > 0:
        started_process_at          = datetime.now()
        log_started_process         = log.info('Started process', extra={'collection': collection_name})

        output                      = function(input, **complemented_kwargs)
        products_size               = len(output) if output else 0
        queue_after_processing      = sourced_queue - products_size

        return started_process_at, output, queue_after_processing
    else:
        log_no_queue_for_process    = log.info('No queue for processing', extra={'collection': collection_name})
        return None, None, 0

def pack(collection_name, decorator_kwargs, one_to_update, started_setup_at, batch_size, started_process_at, output, queue_after_processing):
    if output:
        started_packing_at          = datetime.now()
        log_packing                 = log.info('Started packing', extra={'collection': collection_name})
        group_control_by            = f'batch_size_{batch_size}'
        field_control_by            = 'duration_per_product'
        client_unique               = decorator_kwargs['client_unique_field'] if 'client_unique_field' in decorator_kwargs else None

        documents_to_update         = [document for document in output if client_unique in document if type(output) == list] if client_unique else []
        documents_to_insert         = [document for document in output if client_unique not in document if type(output) == list] if client_unique else output

        bulk_update                 = localdb['products'][collection_name].bulk_write([pymongo.UpdateOne({client_unique: document[client_unique]}, {'$set': document}, upsert=True) for document in documents_to_update if documents_to_update]).bulk_api_result if documents_to_update else {'nUpserted':0}
        bulk_insert                 = localdb['products'][collection_name].insert_many(documents_to_insert).inserted_ids if documents_to_insert else []
        log_db_changes              = log.info(f'Updated {bulk_update["nUpserted"]}. Inserted {len(bulk_insert)}.', extra={'collection': collection_name})

        ended_at                    = datetime.now()
        cycle_time                  = ended_at - started_setup_at
        setup_time                  = started_process_at - started_setup_at
        process_time                = started_packing_at - started_process_at
        packing_time                = ended_at - started_packing_at
        chosen_metric_1             = lambda object: object.total_seconds()
        chosen_metric_2             = lambda object: object.total_seconds()
        products_size               = len(output)
        
        turn_worker_off             = localdb['monitor']['processes'].update_one(one_to_update, {
                                    '$set': {
                                        'running': False,
                                        'last_event.last_success': ended_at, 
                                        'last_event.last_setup': started_setup_at,
                                        'last_event.last_process': started_process_at,
                                        'last_event.last_packing': started_packing_at,
                                        'last_duration.batch_size': batch_size,
                                        'last_duration.output': products_size,
                                        'last_duration.last_duration': chosen_metric_1(cycle_time), 
                                        'last_duration.last_duration_per_product': chosen_metric_1(cycle_time) / products_size,
                                        'last_duration.last_setup_duration': chosen_metric_1(setup_time),
                                        'last_duration.last_process_duration': chosen_metric_1(process_time),
                                        'last_duration.last_packing_duration': chosen_metric_1(packing_time)
                                        }, 
                                    '$push': { 
                                        f'history.{group_control_by}': {
                                            'started_at': started_setup_at,
                                            'ended_at': ended_at,
                                            'batch_size': batch_size,
                                            'output': products_size,
                                            'duration': chosen_metric_2(cycle_time), 
                                            'duration_per_product': chosen_metric_2(cycle_time) / products_size,
                                            'setup_duration': chosen_metric_2(setup_time),
                                            'process_duration': chosen_metric_2(process_time),
                                            'packing_duration': chosen_metric_2(packing_time)
                                        }}}, upsert=True)
        cap_history                 = localdb['monitor']['processes'].update_one(one_to_update, {'$push': { f'history.{group_control_by}': { '$each': [], '$slice': -global_cap }}})

    else:
        log_no_product_for_packing  = log.info('No product for packing', extra={'collection': collection_name})
        also_turn_worker_off        = localdb['monitor']['processes'].update_one(one_to_update, { '$set': {'running': False }})
    
    run_statistics                  = statistics(log, localdb, collection_name, one_to_update, batch_size, global_cap, queue_after_processing)

        
def attempt(one_to_update, collection_name):
    def inner_function(subprocess, *subprocess_args, **subprocess_kwargs):
        try:
            return subprocess(*subprocess_args, **subprocess_kwargs)
        except Exception as e:
            error_time              = datetime.now()
            error_message           = f'{type(e).__name__}: {" ".join(e.args)}'
            turn_worker_off         = localdb['monitor']['processes'].update_one(one_to_update, {'$set': {'running': False, 'last_failure': error_time}, '$addToSet': {'errors': {'error_time': error_time, 'phase': subprocess.__name__, 'message': error_message, 'traceback': traceback.format_exc()}}}, upsert=True)
            cap_errors              = localdb['monitor']['processes'].update_one(one_to_update, {'$push': { f'errors': { '$each': [], '$slice': -global_cap }}})
            log_error               = log.error(f'{error_message}', extra={'collection': collection_name})
            raise
    return inner_function

def process_until_completed(value_stream, function, decorator_kwargs, function_kwargs):
    collection_name                 = f'{value_stream}.{function.__name__}'
    one_to_update                   = {'collection': collection_name, 'name': function.__name__, 'value_stream': value_stream}
    turn_process_on                 = localdb['monitor']['processes'].update_one(one_to_update, {'$set': {'running': True}, '$inc': {'current_workers': 1}}, upsert=True)
    turn_process_off                = lambda: localdb['monitor']['processes'].update_one(one_to_update, {'$set': {'running': False}, '$inc': {'current_workers': -1}})
    register_turn_process_off       = atexit.register(turn_process_off)

    started_setup_at, batch_size, complemented_kwargs, input, sourced_queue, batch_queue    = attempt(one_to_update, collection_name)(setup, collection_name, one_to_update, decorator_kwargs, function_kwargs)
    started_process_at, output, queue_after_processing                                      = attempt(one_to_update, collection_name)(process, collection_name, function, input, sourced_queue, batch_queue, complemented_kwargs)
    pack_products                                                                           = attempt(one_to_update, collection_name)(pack, collection_name, decorator_kwargs, one_to_update, started_setup_at, batch_size, started_process_at, output, queue_after_processing)

    if queue_after_processing > 0:
        process_until_completed(value_stream, function, decorator_kwargs, function_kwargs)

