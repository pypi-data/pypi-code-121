import json
from decimal import Decimal
import botocore
import os
import boto3
import time
import re
from pypers.core.interfaces.db import secretsdb
import datetime

dynamo_type_mapping = {
    str: 'S'
}


class DbBase:

    def __init__(self, *args, **kwargs):
        if kwargs.get('config', None):
            self.config = kwargs.get('config')
        end_point_var_name = kwargs.get('endpoint', '')
        mocker = kwargs.get('mocker', None)
        if os.environ.get(end_point_var_name, None):
            endpoint_url = os.environ[end_point_var_name]
        else:
            endpoint_url = None
        if endpoint_url is None:
            self.can_autoscale = True
        else:
            self.can_autoscale = False
        if os.environ.get("GITHUB_TOKEN", None):
            self.dynamodb = mocker
            self.dynamodb_client = mocker
            self.dynamodb_scaling = mocker
        else:
            self.dynamodb = boto3.resource('dynamodb',
                                           endpoint_url=endpoint_url)
            self.dynamodb_client = boto3.client('dynamodb',
                                                endpoint_url=endpoint_url)
            self.dynamodb_scaling = boto3.client('application-autoscaling',
                                                 endpoint_url=endpoint_url)

        self.sm = secretsdb.get_secrets()
        self.create_pypers_config_schema()

    def _set_auto_scaling(self, min_rcu, min_wcu, max_rcu, max_wcu, indexes=[]):
        if not self.can_autoscale:
            return
        self.dynamodb_scaling.register_scalable_target(
            ServiceNamespace="dynamodb",
            ResourceId="table/{}".format(self.config['name']),
            ScalableDimension="dynamodb:table:WriteCapacityUnits",
            MinCapacity=min_wcu,
            MaxCapacity=max_wcu)
        self.dynamodb_scaling.register_scalable_target(
            ServiceNamespace="dynamodb",
            ResourceId="table/{}".format(self.config['name']),
            ScalableDimension="dynamodb:table:ReadCapacityUnits",
            MinCapacity=min_rcu,
            MaxCapacity=max_rcu)

        for index_name in indexes:
            self.dynamodb_scaling.register_scalable_target(
                ServiceNamespace="dynamodb",
                ResourceId="table/{table_name}/index/{index_name}".format(table_name=self.config['name'],
                                                                          index_name=index_name),
                ScalableDimension="dynamodb:index:WriteCapacityUnits",
                MinCapacity=min_wcu,
                MaxCapacity=max_wcu)
            self.dynamodb_scaling.register_scalable_target(
                ServiceNamespace="dynamodb",
                ResourceId="table/{table_name}/index/{index_name}".format(table_name=self.config['name'],
                                                                          index_name=index_name),
                ScalableDimension="dynamodb:index:ReadCapacityUnits",
                MinCapacity=min_rcu,
                MaxCapacity=max_rcu)

    def create_pypers_config_schema(self):
        key_schema = []
        attribute_definitions = []
        seen_atributes = []
        for index in self.config['indexes'][0]:
            key_schema.append({
                'AttributeName': index['name'],
                'KeyType': 'HASH' if index['primary_index'] else 'RANGE'
            })
            seen_atributes.append(index['name'])
            attribute_definitions.append({
                'AttributeName': index['name'],
                'AttributeType': dynamo_type_mapping.get(index['type'], 'S')
            })

        rcu = self.config.get('read', 5)
        wcu = self.config.get('write', 5)
        gcu_schema = []
        if len(self.config['indexes']) > 1:
            gcu_schema = []
            for sec_index in self.config['indexes'][1:]:
                tmp_key_schema = []
                name = self.config['name']
                for index in sec_index:
                    tmp_key_schema.append({
                        'AttributeName': index['name'],
                        'KeyType': 'HASH' if index['primary_index'] else 'RANGE'
                    })
                    if index['name'] not in seen_atributes:
                        seen_atributes.append(index['name'])
                        attribute_definitions.append({
                            'AttributeName': index['name'],
                            'AttributeType': dynamo_type_mapping.get(index['type'], 'S')
                        })
                    name = "%s_%s" % (name, index['name'])
                gcu_schema.append(
                    {
                        'IndexName': name,
                        'KeySchema': tmp_key_schema,
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': rcu,
                            'WriteCapacityUnits': wcu
                        }
                    })
        is_new_created = False
        try:
            # Create table and create GSI
            create_table_args = {
                'TableName': self.config['name'],
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': rcu,
                    'WriteCapacityUnits': wcu
                }
            }
            if gcu_schema:
                create_table_args['GlobalSecondaryIndexes'] = gcu_schema
            table = self.dynamodb.create_table(
                **create_table_args
            )
            is_new_created = True
        except self.dynamodb.meta.client.exceptions.ResourceInUseException as e:
            table = self.dynamodb.Table(self.config['name'])
        except Exception as e:
            raise e
        table.meta.client.get_waiter('table_exists').wait(
            TableName=self.config['name'])
        if is_new_created:
            # Set ttl
            if self.config.get('ttl', None):
                _ = self.dynamodb_client.update_time_to_live(
                    TableName=self.config['name'],
                    TimeToLiveSpecification={
                        'Enabled': True,
                        'AttributeName': 'gbd_ttl'
                    }
                )
            # Autoscale
            if self.config.get('max_write', None) or self.config.get('max_read', None):
                self._set_auto_scaling(rcu, wcu, self.config.get('max_read', rcu + 1),
                                       self.config.get('max_write', wcu + 1),
                                       indexes=[f['IndexName'] for f in gcu_schema])
        self.table = table

    def set_ttl(self):
        if self.config.get('ttl', None):
            week = datetime.datetime.today() + datetime.timedelta(days=self.config['ttl'])
            expiry_date_time = int(time.mktime(week.timetuple()))
        return expiry_date_time

    def create_new_run_for_pipeline(self, run_id, collection, cfg):
        raise NotImplementedError()

    def create_step_config(self, run_id, collection, step, cfg, keys_on_disk,
                           sub_step=None):
        raise NotImplementedError()

    def get_run_id_config(self, run_id, collection):
        raise NotImplementedError()

    def get_step_config(self, run_id, collection, step_name, sub_step=None):
        raise NotImplementedError()

    def has_step_config_changed(self, run_id, collection, step_name,
                                sub_step=None):
        raise NotImplementedError()

    def reset_step_output(self, run_id, collection, step_name, sub_step=None):
        raise NotImplementedError()

    def has_step_run(self, run_id, collection, step_name, sub_step=None):
        raise NotImplementedError()

    def set_step_output(self, run_id, collection, step_name, output,
                        sub_step=None):
        raise NotImplementedError()

    def removeEmptyString(self, dic, without_replace=False):
        if without_replace:
            return json.loads(json.dumps(dic).replace('""', 'null'))
        return self.replace_sys_env(json.loads(json.dumps(dic).replace('""', 'null')))

    def replace_sys_env(self, obj):
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.replace_sys_env(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = self.replace_sys_env(obj[k])
            return obj
        else:
            if isinstance(obj, str):
                obj = self.sm.key_from_value(obj)
            return obj

    def replace_decimals(self, obj):
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = self.replace_decimals(obj[k])
            return obj
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            if isinstance(obj, str):
                res = self.replace_sys_variable(obj, skip_escaped=True)
                return res
            return obj

    def replace_to_decimals(self, root):
        if isinstance(root, list):
            for i in range(len(root)):
                root[i] = self.replace_to_decimals(root[i])
            return root
        elif isinstance(root, dict):
            for k in root.keys():
                root[k] = self.replace_to_decimals(root[k])
            return root
        elif isinstance(root, float):
            return Decimal(str(root))
        return root

    def replace_sys_variable(self, path, default=None, skip_escaped=False):
        """Expand environment variables of form $var and ${var}.
               If parameter 'skip_escaped' is True, all escaped variable references
               (i.e. preceded by backslashes) are skipped.
               Unknown variables are set to 'default'. If 'default' is None,
               they are left unchanged.
        """
        def replace_var(m):
            m = m.group(0)[2:-1]
            return self.sm.get(m)
        reVar = r'\${(.*)}'
        return re.sub(reVar, replace_var, path)

    def dict_same(self, dict_1, dict_2):
        """Compare two dictionaries recursively
        """
        err = False
        if isinstance(dict_1, list) and isinstance(dict_2, list):
            if len(dict_1) != len(dict_2):
                err = True
            else:
                for i in range(0, len(dict_1)):
                    err = err or self.dict_same(dict_1[i], dict_2[i])
        elif isinstance(dict_1, dict) and isinstance(dict_2, dict):
            for k in dict_1.keys():
                if k not in dict_2.keys():
                    err = True
                else:
                    err = err or self.dict_same(dict_1[k], dict_2[k])
            for k in dict_2.keys():
                if k not in dict_1.keys():
                    err = True
        else:
            if dict_1 != dict_2:
                err = True
        return err

    RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                        'ThrottlingException',
                        'ConditionalCheckFailedException')

    def try_retry(self, caller, *args, **kwargs):
        retry = 0
        while True:
            try:
                return caller(*args, **kwargs)
            except botocore.exceptions.ClientError as e:
                # Ignore the ConditionalCheckFailedException, bubble up
                # other exceptions.
                if e.response['Error']['Code'] in self.RETRY_EXCEPTIONS:
                    time.sleep(2 ** retry)
                    retry += 1
                    if retry == 10:
                        raise
                else:
                    raise
