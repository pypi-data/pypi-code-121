import decimal
import json
from collections import OrderedDict

import humps
import yaml


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def dump_json(obj) -> str:
    return json.dumps(obj, cls=DecimalEncoder)


def _decimal_representer(dumper, obj: decimal.Decimal):
    return dumper.represent_scalar(u'!decimal.Decimal', str(obj))


def _noop(self, *args, **kw):
    """
    Noop function, used to disable yaml tag emitter for log printing
    """
    pass


class Literal(str):
    pass


class Quoted(str):
    pass


def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')


def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


yaml.add_representer(Quoted, quoted_presenter)
yaml.add_representer(OrderedDict, ordered_dict_presenter)
yaml.add_representer(Literal, literal_presenter)
yaml.add_representer(decimal.Decimal, _decimal_representer)


def dump_yaml(obj) -> str:
    tag_processor = yaml.emitter.Emitter.process_tag
    yaml.emitter.Emitter.process_tag = _noop
    yaml_dump = yaml.dump(obj, default_flow_style=False, indent=2, width=1024)
    yaml.emitter.Emitter.process_tag = tag_processor
    return yaml_dump


def dump_camelized_yaml(payload):
    """
    Transform snake_case to camelCase and dump as a yaml document.
    """
    return dump_yaml(OrderedDict(humps.camelize(payload))).rstrip()


def update_and_normalize(dump_data, process_listener, api_call_function, normalize):
    payloads = yaml.full_load(dump_data)
    results = []
    for data_item in payloads['data']:
        item_id = data_item['id']
        payload = {'data': data_item}
        result = api_call_function(item_id, payload)
        if process_listener:
            process_listener(item_id)
        results.append(result.body['data'])

    results = normalize(results)

    updated = {
        'version': 1,
        'data': results,
    }

    return dump_yaml(updated)


def format_logs(logs, output_format):
    if output_format == 'json':
        return dump_json(logs)
    else:
        return dump_yaml(logs)


def wrap_records(data):
    return {
        'version': 1,
        'data': data,
    }