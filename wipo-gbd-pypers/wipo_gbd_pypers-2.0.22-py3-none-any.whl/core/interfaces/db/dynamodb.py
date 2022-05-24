from pypers.core.interfaces.db.base import DbBase
from pypers.core.interfaces.config.pypers_schema_db import PYPERS_RUN_CONFIG, \
    PYPERS_LOGS, PYPERS_CONFIG, PYPES_ERRORS, PYPERS_SEEN_STEPS, \
    PYPERS_DONE_ARCHIVE, PYPERS_PRE_PROD, PYPERS_TRIGGER, PYPERS_INDEXING_CONFIG, \
    PYPERS_RUN_CONFIG_STEPS, PYPERS_PRE_PROD_HISTORY, PYPERS_ENTITY, PYPERS_OPERATIONS
from pypers.utils import utils as ut
from collections import OrderedDict
from boto3.dynamodb.conditions import Attr, Key
import os
from datetime import datetime
from pypers.core.interfaces.db.test import MockDB, MockDBConfig, MockDBLogger
import socket
import json
from random import seed
from random import randint

DEBUG = os.environ.get("GBD_DEV", False)


class DynamoDBInterface(DbBase):
    """COnfiguration runtime manager"""

    def __init__(self):
        self.config = PYPERS_RUN_CONFIG
        self.step_config = DynamoDBSteps()
        super(DynamoDBInterface, self).__init__(endpoint='DYDB_URL',
                                                mocker=MockDB())

    def create_new_run_for_pipeline(self, run_id, collection, cfg):
        cfg = self.removeEmptyString(cfg)
        cfg['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        cfg = self.replace_to_decimals(cfg)
        existing_steps = self.step_config.get_all_steps(run_id, collection)
        with self.step_config.table.batch_writer() as batch:
            for item in existing_steps:
                batch.delete_item(Key={'runid_collection': item['runid_collection'],
                                       'step_name': item['step_name']})
        self.table.put_item(Item={
            'runid': run_id,
            'collection': collection,
            'pipeline_configuration': cfg,
            'gbd_ttl': self.set_ttl(),
            'version': 0
        })

    def get_pipeline_config(self, run_id, collection):
        if not run_id or not collection:
            return {}
        response = self.table.get_item(Key={
            'runid': run_id,
            'collection': collection})
        return self.replace_decimals(
            response.get('Item', {})).get('pipeline_configuration', {}).get('config', {}).get('pipeline', {})

    def get_running_steps(self, run_id, collection):
        to_return = []
        existing_steps = self.step_config.get_all_steps(run_id, collection)
        for item in existing_steps:
            if item['payload'].get('output', {}).get('status', None) == "RUNNING":
                to_return.append(item['step_name'])
        return to_return

    def create_step_config(self, run_id, collection, step, cfg, keys_on_disk, sub_step=None):
        return self.step_config.create_step_config(run_id, collection, step, cfg, keys_on_disk, sub_step=sub_step)

    def get_run_id_config(self, run_id, collection):
        response = self.table.get_item(Key={
            'runid': run_id,
            'collection': collection})
        pipeline = self.replace_decimals(response.get('Item', None))
        if pipeline:
            pipeline['steps_config'] = {}
            all_steps = self.step_config.get_all_steps(run_id, collection)
            for step in all_steps:
                step_name = step['step_name']
                sub_step = None
                if '_' in step_name:
                    tmp = step_name.split('_')
                    step_name = tmp[0]
                    sub_step = tmp[1]
                if step_name not in pipeline['steps_config'].keys():
                    pipeline['steps_config'][step_name] = {
                        'sub_steps': {}
                    }
                if sub_step:
                    pipeline['steps_config'][step_name]['sub_steps'][sub_step] = step.get('payload', {})
                else:
                    pipeline['steps_config'][step_name].update(step.get('payload', {}))
        return pipeline

    def get_step_config(self, run_id, collection, step_name, sub_step=None):
        return self.step_config.get_step_config(run_id, collection, step_name, sub_step=sub_step)

    def has_step_config_changed(self, run_id, collection, step_name,
                                sub_step=None):
        return self.step_config.has_step_config_changed(run_id, collection, step_name, sub_step=sub_step)

    def log_report(self, run_id, collection, key, report):
        return self.try_retry(self._log_report, run_id, collection, key, report)

    def _log_report(self, run_id, collection, key, report):
        report = self.replace_to_decimals(report)
        pipeline = self.get_run_id_config(run_id, collection)
        self.table.update_item(
            Key={
                'runid': run_id,
                'collection': collection
            },
            UpdateExpression='SET report_%s = :val1 ADD version :inc' % key,
            ConditionExpression=Attr('version').eq(pipeline.get('version')),
            ExpressionAttributeValues={
                ':val1': report,
                ':inc': 1
            }
        )

    def get_report(self, run_id, collection, key):
        pipeline = self.get_run_id_config(run_id, collection)
        return self.replace_decimals(pipeline.get('report_%s' % key, {}))


    def update_process_report(self, run_id, collection, report):
        if report:
            return self.try_retry(self._update_process_report,
                                  run_id, collection, report)

    def _update_process_report(self, run_id, collection, report):
        pipeline = self.get_run_id_config(run_id, collection)
        db_report = pipeline.get('process_report', [])
        db_report.extend(report)
        db_report = self.replace_to_decimals(db_report)
        self.table.update_item(
            Key={
                'runid': run_id,
                'collection': collection
            },
            UpdateExpression='SET process_report = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(pipeline.get('version')),
            ExpressionAttributeValues={
                ':val1': db_report,
                ':inc': 1
            }
        )

    def reset_step_output(self, run_id, collection, step_name, sub_step=None):
        return self.step_config.reset_step_output(run_id, collection, step_name, sub_step=sub_step)

    def has_step_run(self, run_id, collection, step_name, sub_step=None):
        return self.step_config.has_step_run(run_id, collection, step_name, sub_step=sub_step)

    def set_step_output(self, run_id, collection, step_name, output,
                        sub_step=None):
        return self.step_config.set_step_output(run_id, collection, step_name, output, sub_step=sub_step)


class DynamoDBSteps(DbBase):
    """COnfiguration runtime manager"""

    def __init__(self):
        self.config = PYPERS_RUN_CONFIG_STEPS
        super(DynamoDBSteps, self).__init__(endpoint='DYDB_URL',
                                                mocker=MockDB())

    def create_step_config(self, run_id, collection, step, cfg, keys_on_disk, sub_step=None):
        cfg = self.removeEmptyString(cfg, without_replace=True)
        cfg = self.replace_to_decimals(cfg)
        cfg['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_dir = cfg.get('meta', {}).get('pipeline', {}).get('output_dir', '')
        results_path = os.path.join(output_dir, '%s_%s_input.json' % (step, sub_step))
        on_disk = {}
        for key in keys_on_disk:
            on_disk[key] = cfg.pop(key, {})
        with open(results_path, 'w') as f:
            json.dump(on_disk, f)
        cfg['_prev_path'] = results_path
        return self.try_retry(self._create_step_config, run_id, collection, step, cfg,
                              sub_step=sub_step)

    def _create_step_config(self, run_id, collection, step, cfg, sub_step=None):
        key = self._get_keys(run_id, collection, step, sub_step=sub_step)
        step_db = self.get_step(run_id, collection, step, sub_step=sub_step)
        step_config = step_db.get('payload', {})

        if step_config.get('config', None):
            current_config = step_config.get('config')
            config_changed = ut.DictDiffer(OrderedDict(current_config),
                                           OrderedDict(cfg))
        else:
            config_changed = True
        if config_changed:
            update = {
                'output': {
                    'status': "RUNNING"
                },
                'config': cfg,
                'config_changed': config_changed
            }
            step_config.update(update)
        step_config = self.removeEmptyString(step_config)
        step_config = self.replace_to_decimals(step_config)

        if not sub_step:
            response = self.table.query(
                KeyConditionExpression='runid_collection = :runid AND begins_with(step_name, :tag)',
                ExpressionAttributeValues={
                    ':runid': key['runid_collection'],
                    ':tag': '%s_' % key['step_name']
                }
            )
            with self.table.batch_writer() as batch:
                for item in response['Items']:
                    batch.delete_item(Key={'runid_collection': item['runid_collection'],
                                           'step_name': item['step_name']})
        self.table.update_item(
            Key=key,
            UpdateExpression='SET payload = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(step_db.get('version')),
            ExpressionAttributeValues={
                ':val1': step_config,
                ':inc': 1
            }
        )

    def _get_keys(self, run_id, collection, step_name, sub_step=None):
        key_colection = "%s_%s" % (run_id, collection)
        key_step = step_name
        if sub_step:
            key_step = "%s_%s" % (step_name, sub_step)
        return {
            'runid_collection': key_colection,
            'step_name': key_step}

    def get_all_steps(self, run_id, collection):
        response = self.table.query(
            KeyConditionExpression='runid_collection = :runid',
            ExpressionAttributeValues={
                ':runid': "%s_%s" % (run_id, collection),
            }
        )
        results = self.replace_decimals(response.get('Items', []))
        for result in results:
            outputs = result.get('payload', {}).get('output', {}).get('_prev_path', None)
            if outputs and os.path.exists(outputs):
                with open(outputs, 'r') as f:
                    result.get('payload', {}).get('output', {})['results'] = json.load(f)
        return results

    def get_step(self, run_id, collection, step_name, sub_step=None):
        key = self._get_keys(run_id, collection, step_name, sub_step=sub_step)
        response = self.table.get_item(Key=key)
        if response.get('Item', None) is None:
            self.table.put_item(Item={
                'runid_collection': key['runid_collection'],
                'step_name': key['step_name'],
                'payload': {},
                'gbd_ttl': self.set_ttl(),
                'version': 0
            })
            response = self.table.get_item(Key=key)
        result = self.replace_decimals(response.get('Item', None))
        return result

    def get_step_config(self, run_id, collection, step_name, sub_step=None):
        step = self.get_step(run_id, collection, step_name, sub_step=sub_step)
        value = step.get('payload', {}).get('config', None)
        if value and value.get('_prev_path', None) and value['_prev_path']:
            if os.path.exists(value['_prev_path']):
                with open(value['_prev_path'], 'r') as f:
                    inputs_on_disk = json.load(f)
                    value.update(inputs_on_disk)
                    value['values_on_disk'] = list(inputs_on_disk.keys())
        return self.replace_decimals(value)

    def has_step_config_changed(self, run_id, collection, step_name,
                                sub_step=None):
        step = self.get_step(run_id, collection, step_name, sub_step=sub_step)
        return step.get('payload', {}).get('config_changed', True)

    def reset_step_output(self, run_id, collection, step_name, sub_step=None):
        return self.try_retry(self._reset_step_output, run_id, collection, step_name,
                              sub_step=sub_step)

    def _reset_step_output(self, run_id, collection, step_name, sub_step=None):
        key = self._get_keys(run_id, collection, step_name, sub_step=sub_step)
        step = self.get_step(run_id, collection, step_name, sub_step=sub_step)
        steps_config = step.get('payload', {})
        steps_config['output'] = {}
        steps_config = self.removeEmptyString(steps_config)
        steps_config = self.replace_to_decimals(steps_config)
        self.table.update_item(
            Key=key,
            UpdateExpression='SET payload = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(step.get('version')),
            ExpressionAttributeValues={
                ':val1': steps_config,
                ':inc': 1
            }
        )

    def has_step_run(self, run_id, collection, step_name, sub_step=None):
        step = self.get_step(run_id, collection, step_name, sub_step=sub_step)
        return len(step.get('payload', {}).get('output', {})) != 0

    def set_step_output(self, run_id, collection, step_name, output,
                        sub_step=None):
        return self.try_retry(self._set_step_output, run_id, collection, step_name, output,
                              sub_step=sub_step)

    def _set_step_output(self, run_id, collection, step_name, output,
                         sub_step=None):
        key = self._get_keys(run_id, collection, step_name, sub_step=sub_step)
        step = self.get_step(run_id, collection, step_name, sub_step=sub_step)
        steps_config = step.get('payload', {})
        if step_name != 'notify' and step_name != 'clean':
            output_dir = output.get('results', {}).get(
                'meta', {}).get('pipeline', {}).get('output_dir', '')
            if output_dir != '':
                results_path = os.path.join(output_dir, '%s_%s_output.json' % (step_name, sub_step))
                output['_prev_path'] = results_path
                resuls = output.get('results', {})
                with open(results_path, 'w') as f:
                    json.dump(resuls, f)
                if not os.path.exists(results_path):
                    raise Exception("Retry writing of output_file")
                output.pop('results', {})
            if sub_step and output['status'] != 'SUCCEEDED':
                self.set_step_output(run_id, collection, step_name, {'status': output['status']})
        steps_config['output'] = output
        steps_config['output_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        steps_config = self.removeEmptyString(steps_config)
        steps_config = self.replace_to_decimals(steps_config)
        self.table.update_item(
            Key=key,
            UpdateExpression='SET payload = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(step.get('version')),
            ExpressionAttributeValues={
                ':val1': steps_config,
                ':inc': 1
            }
        )


class DynamoDbLogger(DbBase):
    """DB logger"""

    def __init__(self):
        self.config = PYPERS_LOGS
        seed(1)
        super(DynamoDbLogger, self).__init__(endpoint='DYDB_URL',
                                             mocker=MockDBLogger())

    def log_entry(self, run_id, collection, message, step=None, sub_step=None,
                  position=None, file=None, type_log=None, reset=False):
        message = str(message)
        log_line = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': type_log,
            'step': step,
            'sub_step': sub_step,
            'message': message,
            'file': file,
            'position': position,
            'hostname': socket.gethostname()
        }
        if DEBUG:
            print("[%s][%s-%s-%s][%s:%s] %s" % (
                log_line['timestamp'],
                log_line['type'],
                log_line['step'],
                log_line['sub_step'],
                log_line['file'],
                log_line['position'],
                log_line['message']
            ))
        if DEBUG or type_log not in ['INFO', 'DEBUG']:
            return self.try_retry(self._log_entry, run_id, collection, log_line, reset=reset)

    def _log_entry(self, run_id, collection, log_line, reset=False):
        key = "%s_%s" % (run_id, collection)
        logs = self.replace_to_decimals(log_line)
        self.table.put_item(Item={
            'runid_collection': key,
            'log_time': '%s_%s' % (log_line['timestamp'], randint(0, 1000)),
            'l_type': log_line['type'],
            'step': log_line['step'],
            'payload': logs,
            'gbd_ttl': self.set_ttl(),
            'version': 0
        })

class DynamoDbConfig(DbBase):
    """Configuration (pipelines password,etc)"""

    def __init__(self):
        self.config = PYPERS_CONFIG
        super(DynamoDbConfig, self).__init__(endpoint='DYDB_URL',
                                             mocker=MockDBConfig())

    def get_configuration(self, config_name):
        if '_' in config_name:
            config_name = config_name.split('_')[0]
        response = self.table.get_item(Key={'name': config_name})
        return self.replace_decimals(response['Item'].get('json', None))


class DynamoErrorDB(DbBase):
    """Persist errors"""

    def __init__(self):
        self.config = PYPES_ERRORS
        super(DynamoErrorDB, self).__init__(endpoint='DYDB_URL',
                                            mocker=MockDB())

    def send_error(self, run_id, collection, original_message, error_trace):
        self.table.put_item(Item={
            'runid': run_id,
            'collection': collection,
            'original_message': original_message,
            'error_trace': error_trace,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })


class DynamoSeenSteps(DbBase):
    """Persist errors"""

    def __init__(self):
        self.config = PYPERS_SEEN_STEPS
        super(DynamoSeenSteps, self).__init__(endpoint='DYDB_URL',
                                              mocker=MockDB())

    def reset_history(self, run_id, collection):
        return self.try_retry(self._reset, run_id, collection)

    def reset_step(self, run_id, collection, step):
        return self.try_retry(self._reset_step, run_id, collection, step)

    def step_visited(self, run_id, collection, step, sub_step=None):
        return self.try_retry(self._handle_step, run_id, collection, step,
                              sub_step=sub_step)

    def _reset(self, run_id, collection):
        response = self.table.get_item(Key={
            'runid': run_id,
            'collection': collection}).get('Item', {})
        if not len(response.get('history', [])):
            self.table.put_item(Item={
                'runid': run_id,
                'collection': collection,
                'gbd_ttl': self.set_ttl(),
                'history': [],
                'version': 0
            })
        history = []
        self.table.update_item(
            Key={
                'runid': run_id,
                'collection': collection
            },
            UpdateExpression='SET history = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(
                response.get('version', 0)),
            ExpressionAttributeValues={
                ':val1': history,
                ':inc': 1
            }
        )

    def _reset_step(self, run_id, collection, step_name):
        response = self.table.get_item(Key={
            'runid': run_id,
            'collection': collection}).get('Item', {})
        if not len(response.get('history', [])):
            self.table.put_item(Item={
                'runid': run_id,
                'collection': collection,
                'gbd_ttl': self.set_ttl(),
                'history': [],
                'version': 0
            })
        history = []
        for k in response.get('history', []):
            if step_name not in k:
                history.append(k)
        self.table.update_item(
            Key={
                'runid': run_id,
                'collection': collection
            },
            UpdateExpression='SET history = :val1 ADD version :inc',
            ConditionExpression=Attr('version').eq(
                response.get('version', 0)),
            ExpressionAttributeValues={
                ':val1': history,
                ':inc': 1
            }
        )

    def _handle_step(self, run_id, collection, step, sub_step=None):
        response = self.table.get_item(Key={
            'runid': run_id,
            'collection': collection}).get('Item', {})
        if not len(response.get('history', [])):
            self.table.put_item(Item={
                'runid': run_id,
                'collection': collection,
                'gbd_ttl': self.set_ttl(),
                'history': [],
                'version': 0
            })

        history = response.get('history', [])
        id_step_index = "%s_%s" % (step, sub_step)
        if id_step_index not in history:
            history.append(id_step_index)
            history = self.replace_to_decimals(history)
            self.table.update_item(
                Key={
                    'runid': run_id,
                    'collection': collection
                },
                UpdateExpression='SET history = :val1 ADD version :inc',
                ConditionExpression=Attr('version').eq(
                    response.get('version', 0)),
                ExpressionAttributeValues={
                    ':val1': history,
                    ':inc': 1
                }
            )
            return False
        else:
            return True


class DynamoIndexingConfig(DbBase):
    """Persist errors"""

    def __init__(self):
        self.config = PYPERS_INDEXING_CONFIG
        super(DynamoIndexingConfig, self).__init__(endpoint='DYDB_URL',
                                             mocker=MockDB())

    def get_config(self, uid):
        response = self.table.get_item(Key={
            'uid': uid}).get('Item', {})
        return self.replace_decimals(response.get('conf', {}))


class DynamoDoneFile(DbBase):
    """Persist errors"""

    def __init__(self):
        self.config = PYPERS_DONE_ARCHIVE
        super(DynamoDoneFile, self).__init__(endpoint='DYDB_URL',
                                             mocker=MockDB())

    def update_done(self, collection, run_id, archives, should_reset=False):
        self.try_retry(self._update_done, collection, run_id, archives, should_reset)

    def _update_done(self, collection, run_id, archives, should_reset):
        if should_reset:
            elements = self.get_done(collection)
            with self.table.batch_writer() as writer:
                for element in elements:
                    self.try_retry(writer.delete_item, Key={
                            'gbd_collection': element['gbd_collection'],
                            'archive_name': element['archive_name']
                        })
        with self.table.batch_writer() as writer:
            for archive in archives:
                data = {
                    'gbd_collection': collection,
                    'archive_name': archive,
                    'run_id': run_id,
                    'process_date': datetime.now().strftime('%Y-%m-%d')
                }
                self.try_retry(writer.put_item, Item=data)

    def get_done(self, collection):

        response = self.table.query(
            KeyConditionExpression='gbd_collection = :collection',
            ExpressionAttributeValues={
                ':collection': collection,
            }).get('Items', {})
        return response


class DynamoPreProdHistory(DbBase):

    def __init__(self):
        self.config = PYPERS_PRE_PROD_HISTORY
        super(DynamoPreProdHistory, self).__init__(
            endpoint='DYDB_URL', mocker=MockDB())


    def get_document(self, collection, appnum, time):
        response = self.table.get_item(Key={
            'collection_appnum': "%s_%s" % (collection, appnum),
            'office_extraction_date': time}).get('Item', {})
        return self.replace_decimals(response)

    def put_items(self, items):
        with self.table.batch_writer() as writer:
            for item in items:
                with open(item, 'r') as f:
                    data = self.replace_to_decimals(json.load(f))
                self.try_retry(writer.put_item, Item=data)

class DynamoPreProd(DbBase):

    def __init__(self):
        self.config = PYPERS_PRE_PROD
        super(DynamoPreProd, self).__init__(endpoint='DYDB_URL',
                                            mocker=MockDB())

    def put_items(self, items):
        with self.table.batch_writer() as writer:
            for item in items:
                with open(item, 'r') as f:
                    data = self.replace_to_decimals(json.load(f))
                self.try_retry(writer.put_item, Item=data)

    def get_documents(self, prefix, run_id, collection=None, one_page=False):
        if run_id:
            args = {
                'IndexName': "%s_%s_%s" % (self.config['name'], 'latest_run_id', 'st13'),
                'KeyConditionExpression': 'latest_run_id = :runid AND begins_with(st13, :st13)',
                'ExpressionAttributeValues': {
                    ':runid': run_id,
                    ':st13': prefix
                }
            }
        elif collection:
            args = {
                'IndexName': "%s_%s_%s" % (self.config['name'], 'gbd_collection', 'st13'),
                'KeyConditionExpression': 'gbd_collection = :collection AND begins_with(st13, :st13)',
                'ExpressionAttributeValues': {
                    ':collection': collection,
                    ':st13': prefix
                }
            }
        else:
            raise Exception("Please provide a run_id or a collection")
        counter = 1
        while True:
            response = self.table.query(**args)
            print("Processing page %s" % counter)
            counter += 1
            for item in response["Items"]:
                yield self.replace_decimals(item)
            try:
                args["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            except KeyError as e:
                break
            if one_page:
                break

    def get_document(self, appnum, run_id=None):
        if run_id:
            response = self.get_documents(appnum, run_id, one_page=True)
            if len(response) > 0:
                response = response[0]
        else:
            response = self.table.get_item(Key={'st13': appnum}).get('Item', {})
        return self.replace_decimals(response)


class DynamoTrigger(DbBase):

    def __init__(self):
        self.config = PYPERS_TRIGGER
        super(DynamoTrigger, self).__init__(endpoint='DYDB_URL',
                                            mocker=MockDB())

    def read_config(self, name):
        response = self.table.get_item(Key={
            'name': name}).get('Item', {})
        return response.get('config', [])


class DynamoDailyOperations(DbBase):

    def __init__(self):
        self.config = PYPERS_OPERATIONS
        super(DynamoDailyOperations, self).__init__(
            endpoint='DYDB_URL', mocker=MockDB())

    def create_run(self, run_id, collections=[]):
        with self.table.batch_writer() as writer:
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            for collection in collections:
                item = {
                    'run_id': run_id,
                    'collection': collection,
                    'start_time': start_time,
                    'pipeline_status': 'RUNNING',
                    'end_time': None
                }
                self.try_retry(writer.put_item, Item=item)

    def completed(self, run_id, collection, success=True):
        status = "SUCCESS" if success else 'FAILED'
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.table.update_item(
            Key={
                'run_id': run_id,
                'collection': collection
            },
            UpdateExpression='SET pipeline_status = :val1',
            ExpressionAttributeValues={
                ':val1': status,
            })
        self.table.update_item(
            Key={
                'run_id': run_id,
                'collection': collection
            },
            UpdateExpression='SET end_time = :val1',
            ExpressionAttributeValues={
                ':val1': end_time,
            })

    def get_run(self, run_id):
        response = self.table.query(
            KeyConditionExpression='run_id = :runid ',
            ExpressionAttributeValues={
                ':runid': run_id,
            }).get('Items', [])
        return response

class DynamoEntity(DbBase):

    def __init__(self):
        self.config = PYPERS_ENTITY
        super(DynamoEntity, self).__init__(endpoint='DYDB_URL',
                                           mocker=MockDB())

    def put_items(self, items):
        failed_items = []
        with self.table.batch_writer() as writer:
            for item in items:
                with open(item, 'r') as f:
                    data = self.replace_to_decimals(json.load(f))
                try:
                    self.try_retry(writer.put_item, Item=data)
                except:
                    failed_items.append(item)
        return failed_items

    def get_document(self, collection, appnum, e_type="APP"):
        response = self.table.get_item(Key={
            'entity_id': "%s.%s.%s" % (collection, e_type, appnum)}).get('Item', {})
        return self.replace_decimals(response)

    def delete_items(self, collection, appnums, e_type="APP"):
        with self.table.batch_writer() as batch:
            for item in appnums:
                batch.delete_item(Key={
                    'entity_id': "%s.%s.%s" % (collection, e_type, item)})
