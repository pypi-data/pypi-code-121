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
log.setLevel(logging.DEBUG)

def printTypes(*args):
    print_types                     = print(' '.join([str(type(arg).__name__) for arg in args]))

def setup(collection_name: str, this_process: dict, decorator_kwargs: dict, function_kwargs: dict) -> Tuple[datetime, int, dict, list, int]:
    started_setup_at                = datetime.now()
    log_started_setup               = log.info('Started setup', extra={'collection': collection_name})

    process_local_config            = decorator_kwargs['supplier']
    process_saved_config            = localdb['monitor']['processes'].find_one(this_process)

    batch_size                      = process_saved_config.get('batch_size', sample(range(1,10), 1)[0] * 10)
    log_batch_size                  = log.info(f'Working with batch size {batch_size}', extra={'collection': collection_name})
    complemented_kwargs             = function_kwargs | {'config': process_saved_config, 'batch_size': batch_size} if process_saved_config else function_kwargs

    db                              = pymongo.MongoClient(process_local_config['uri'])[process_local_config['db']] if 'uri' in process_local_config and 'db' in process_local_config else localdb['products']
    collection                      = process_local_config['collection']
    supplier_unique                 = process_local_config['unique']
    base_aggregation                = process_local_config['aggregation'] if 'aggregation' in process_local_config else []

    queue_from_supplier             = [element[supplier_unique] for element in list(db[collection].aggregate(base_aggregation + [{'$project': { '_id': 0, supplier_unique: 1 } }]))]
    local_queue                     = [element[supplier_unique] for element in list(localdb['inventory'][collection_name].aggregate([])) if supplier_unique in element]

    queue_to_add                    = set(queue_from_supplier) - set(local_queue)
    update_queue                    = localdb['inventory'][collection_name].insert_many([{supplier_unique:element} for element in queue_to_add]) if queue_to_add else None

    log_updated_queue               = log.info(f'Found {len(queue_from_supplier)} from supplier. Had {len(local_queue)} locally. Updated {len(queue_to_add)}.', extra={'collection': collection_name})

    queue_size                      = queue[0]['count'] if (queue:= list(localdb['inventory'][collection_name].aggregate([{'$match':{'processed': {'$exists': False}}},{'$count': 'count'}]))) and len(queue) > 0 and 'count' in queue[0] else 0
    processed_queue_size            = queue[0]['count'] if (queue:= list(localdb['inventory'][collection_name].aggregate([{'$match':{'processed': True}},{'$count': 'count'}]))) and len(queue) > 0 and 'count' in queue[0] else 0
    products_size                   = queue[0]['count'] if (queue:= list(localdb['products'][collection_name].aggregate([{'$count': 'count'}]))) and len(queue) > 0 and 'count' in queue[0] else 0
    batch_queue                     = [element[supplier_unique] for element in list(localdb['inventory'][collection_name].aggregate([{'$match':{'processed': {'$exists': False}}}, {'$sample': {'size': batch_size}}])) if supplier_unique in element]
    this_batch                      = {supplier_unique: {'$in': batch_queue}}
    input                           = list(db[collection].aggregate([{'$match': this_batch}]))
    batch_elements_size             = len(input)

    update_queue_and_products       = localdb['monitor']['processes'].update_one({'collection': collection_name}, {'$set': {'current_batch_size':batch_size, 'queue.pending':queue_size, 'queue.processed':processed_queue_size, 'queue.total':queue_size + processed_queue_size}})

    return started_setup_at, batch_size, complemented_kwargs, input, queue_size, batch_elements_size, this_batch

def process(collection_name, function, input, queue_size, batch_elements_size, complemented_kwargs):
    if batch_elements_size > 0:
        started_process_at          = datetime.now()
        log_started_process         = log.info('Started process', extra={'collection': collection_name})

        output                      = function(input, **complemented_kwargs)
        batch_products_size               = len(output) if output else 0
        queue_after_processing      = queue_size - batch_products_size

        return started_process_at, output, queue_after_processing
    else:
        log_no_queue_for_process    = log.info('No queue for processing', extra={'collection': collection_name})
        return None, None, 0

def pack(collection_name, decorator_kwargs, this_process, started_setup_at, batch_size, started_process_at, output, this_batch, queue_after_processing):
    if output:
        started_packing_at          = datetime.now()
        log_packing                 = log.info('Started packing', extra={'collection': collection_name})
        group_control_by            = f'batch_size_{batch_size}'
        client_unique               = decorator_kwargs['client']['unique']
        local_products              = [element[client_unique] for element in list(localdb['products'][collection_name].aggregate([{'$project':{'_id': 0, client_unique: 1}}])) if client_unique in element]
        output_ids                  = [element[client_unique] for element in output]
        output_dict                 = {element[client_unique]:element for element in output}

        new_output_ids              = set(output_ids) - set(local_products)
        new_output                  = [output_dict[id] for id in new_output_ids]

        documents_to_insert         = [document for document in new_output if type(output) == list and document[client_unique] not in local_products]
        bulk_insert                 = localdb['products'][collection_name].insert_many(documents_to_insert).inserted_ids if documents_to_insert else []

        log_db_changes              = log.info(f'Inserted {len(bulk_insert)}.', extra={'collection': collection_name})
        update_inventory            = localdb['inventory'][collection_name].update_many(this_batch, {'$set': {'processed': True}})

        ended_at                    = datetime.now()
        cycle_time                  = ended_at - started_setup_at
        setup_time                  = started_process_at - started_setup_at
        process_time                = started_packing_at - started_process_at
        packing_time                = ended_at - started_packing_at
        chosen_metric_1             = lambda object: object.total_seconds()
        chosen_metric_2             = lambda object: object.total_seconds()
        batch_products_size         = len(output)
        
        turn_worker_off             = localdb['monitor']['processes'].update_one(this_process, {
                                    '$set': {
                                        'running': False,
                                        'products': len(local_products), 
                                        'last_event.last_success': ended_at, 
                                        'last_event.last_setup': started_setup_at,
                                        'last_event.last_process': started_process_at,
                                        'last_event.last_packing': started_packing_at,
                                        'last_duration.batch_size': batch_size,
                                        'last_duration.output': batch_products_size,
                                        'last_duration.last_duration': chosen_metric_1(cycle_time), 
                                        'last_duration.last_duration_per_product': chosen_metric_1(cycle_time) / batch_size,
                                        'last_duration.last_setup_duration': chosen_metric_1(setup_time),
                                        'last_duration.last_process_duration': chosen_metric_1(process_time),
                                        'last_duration.last_packing_duration': chosen_metric_1(packing_time)
                                        }, 
                                    '$push': { 
                                        f'history.{group_control_by}': {
                                            'started_at': started_setup_at,
                                            'ended_at': ended_at,
                                            'batch_size': batch_size,
                                            'output': batch_products_size,
                                            'duration': chosen_metric_2(cycle_time), 
                                            'duration_per_product': chosen_metric_2(cycle_time) / batch_size,
                                            'setup_duration': chosen_metric_2(setup_time),
                                            'process_duration': chosen_metric_2(process_time),
                                            'packing_duration': chosen_metric_2(packing_time)
                                        }}}, upsert=True)
        cap_history                 = localdb['monitor']['processes'].update_one(this_process, {'$push': { f'history.{group_control_by}': { '$each': [], '$slice': -global_cap }}})

    else:
        log_no_product_for_packing  = log.info('No product for packing', extra={'collection': collection_name})
        also_turn_worker_off        = localdb['monitor']['processes'].update_one(this_process, { '$set': {'running': False }})
    
    run_statistics                  = statistics(log, localdb, collection_name, this_process, batch_size, global_cap, queue_after_processing)

        
def attempt(this_process, collection_name):
    def selected_function(subprocess):
        def inner_function(*subprocess_args, **subprocess_kwargs):
            try:
                return subprocess(*subprocess_args, **subprocess_kwargs)
            except Exception as e:
                error_time              = datetime.now()
                error_message           = f'{type(e).__name__}: {" ".join(e.args)}'
                turn_worker_off         = localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': False, 'last_failure': error_time}, '$addToSet': {'errors': {'error_time': error_time, 'phase': subprocess.__name__, 'message': error_message, 'traceback': traceback.format_exc()}}}, upsert=True)
                cap_errors              = localdb['monitor']['processes'].update_one(this_process, {'$push': { f'errors': { '$each': [], '$slice': -global_cap }}})
                log_error               = log.error(f'{error_message}', extra={'collection': collection_name})
                raise
        return inner_function
    return selected_function

def process_until_completed(value_stream, function, decorator_kwargs, function_kwargs):
    collection_name                 = f'{value_stream}.{function.__name__}'
    this_process                   = {'collection': collection_name, 'name': function.__name__, 'value_stream': value_stream}
    turn_process_on                 = localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': True}, '$inc': {'current_workers': 1}}, upsert=True)
    turn_process_off                = lambda: localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': False}, '$inc': {'current_workers': -1}})
    register_turn_process_off       = atexit.register(turn_process_off)

    started_setup_at, batch_size, complemented_kwargs, input, queue_size, batch_elements_size, this_batch       = attempt(this_process, collection_name)(setup)(collection_name, this_process, decorator_kwargs, function_kwargs)
    started_process_at, output, queue_after_processing                                                          = attempt(this_process, collection_name)(process)(collection_name, function, input, queue_size, batch_elements_size, complemented_kwargs)
    pack_products                                                                                               = attempt(this_process, collection_name)(pack)(collection_name, decorator_kwargs, this_process, started_setup_at, batch_size, started_process_at, output, this_batch, queue_after_processing)

    if queue_after_processing > 0:
        turn_process_off()
        process_until_completed(value_stream, function, decorator_kwargs, function_kwargs)

