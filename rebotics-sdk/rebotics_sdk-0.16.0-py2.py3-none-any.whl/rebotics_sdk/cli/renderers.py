import json
from datetime import datetime

import click
import pytz
from dateutil import parser as dp
from prettytable import PrettyTable


def extract_fields_to_render(d, max_column_length, keys_to_skip, key_prefix=None, depth=0, max_depth=1):
    fields_to_render = []

    if depth > max_depth:
        return []

    for field, value in d.items():
        if field in keys_to_skip:
            continue

        if key_prefix is not None:
            field = '{}.{}'.format(key_prefix, field)

        if not (isinstance(value, list)):
            if isinstance(value, str):
                if len(value) < max_column_length:
                    fields_to_render.append(field)
            elif isinstance(value, int) or isinstance(value, float):
                fields_to_render.append(field)
            elif value is None:
                fields_to_render.append(field)
            elif isinstance(value, dict):
                fields_to_render.extend(
                    extract_fields_to_render(value, max_column_length, keys_to_skip, key_prefix=field)
                )
    return fields_to_render


def format_full_table(results, max_column_length=30, keys_to_skip=None, fields=None):
    if keys_to_skip is None:
        keys_to_skip = []
    if fields is None:
        fields = []

    if fields and keys_to_skip:
        raise ValueError('Can only use either keys_to_skip or either fields, not both.')

    def get_attribute(value, key, default):
        if '.' not in key:
            return value.get(key, default)

        keys = key.split('.')
        acc = value
        for k in keys:
            try:
                acc = acc.get(k, '---')
            except KeyError:
                acc = default
        return acc

    table = PrettyTable()

    if isinstance(results, dict):
        # render it vertically
        table.field_names = ['key', 'value']
        for key, value in results.items():
            table.add_row([key, value])
    else:
        for i, item in enumerate(results):
            if i == 0:
                if fields:
                    table.field_names = fields
                else:
                    table.field_names = extract_fields_to_render(item, max_column_length, keys_to_skip)

            table.add_row([
                get_attribute(item, field, '---') for field in table.field_names
            ])
    click.echo(table)


def format_processing_action_output(processing_actions_list, format_):
    if format_ == 'json':
        click.echo(json.dumps(processing_actions_list, indent=2))
    elif format_ == 'id':
        click.echo(" ".join([str(item['id']) for item in processing_actions_list]))
    else:
        pac = processing_actions_list[0]

        if 'last_requeue' not in pac.keys():
            fields = ['id', 'store_id', 'username', 'status', 'store_planogram_id', 'aisle', 'section', 'created']
        else:
            fields = ['id', 'store_id', 'username', 'status', 'store_planogram_id', 'aisle', 'section', 'created',
                      'last_requeue', 'time_in_queue']

        format_full_table([PacSerializer(x) for x in processing_actions_list], fields=fields)


class PacSerializer(object):
    def __init__(self, data):
        self.data = data
        self.now = datetime.now(pytz.utc)

    def get(self, item, default='---'):
        return self.data.get(item) or getattr(self, item, default)

    @property
    def time_in_queue(self):
        if self.data['status'] not in ['error', 'done', 'interrupted']:
            last_requeue_datetime = self.last_requeue
            if last_requeue_datetime:
                return self.now - last_requeue_datetime

        processing_start_time = self.data.get('processing_start_time')
        processing_finish_time = self.data.get('processing_finish_time')
        if processing_finish_time is None and processing_finish_time is None:
            time_in_queue = 'unknown'
        else:
            start_time = dp.parse(processing_start_time)
            finish_time = dp.parse(processing_finish_time)
            time_in_queue = finish_time - start_time

        return time_in_queue

    @property
    def created(self):
        return dp.parse(self.data['created']).strftime('%c')

    @property
    def username(self):
        u = self.data.get('user')
        if u:
            return u.get('username', 'id')

    @property
    def last_requeue(self):
        d = self.data.get('last_requeue')
        if d is None:
            return None

        return dp.parse(d)

    @property
    def store(self):
        return '#{}'.format(self.data.get('store_id'))
