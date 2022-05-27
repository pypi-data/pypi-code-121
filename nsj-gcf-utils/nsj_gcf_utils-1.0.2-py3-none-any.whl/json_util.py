import copy
import datetime
import json
import re
import uuid
import decimal

# JSON DUMPS


def convert_to_dumps(data):
    if data == None:
        return None

    data_copy = copy.copy(data)

    if isinstance(data_copy, datetime.datetime):
        return data_copy.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(data_copy, datetime.date):
        return data_copy.strftime('%Y-%m-%d')
    elif isinstance(data_copy, uuid.UUID):
        return str(data_copy)
    elif isinstance(data_copy, decimal.Decimal):
        return float(data_copy)
    elif isinstance(data_copy, dict):
        for key in data_copy.keys():
            data_copy[key] = convert_to_dumps(data_copy[key])
        return data_copy
    elif isinstance(data_copy, list):
        for idx in range(0, len(data_copy)):
            data_copy[idx] = convert_to_dumps(data_copy[idx])

        return data_copy
    elif isinstance(data_copy, str) or isinstance(data_copy, int) or isinstance(data_copy, float) or isinstance(data_copy, bool):
        return data_copy
    elif isinstance(data_copy, object):
        to_dict_method = getattr(data_copy, 'to_dict', None)
        if to_dict_method is not None and callable(to_dict_method):
            dict_attrs = data_copy.to_dict()
        else:
            attrs_fields = [k for k in data_copy.__dict__ if not callable(
                getattr(data_copy, k, None))]
            dict_attrs = {k: data_copy.__dict__[k] for k in attrs_fields}

        return convert_to_dumps(dict_attrs)
    else:
        return data_copy


def json_dumps(data, ensure_ascii=True, convert_before_dump=True):
    """
    Retorna a representação em json (string) do objeto recebido no parâmetro "data".

    É importante destacar que este método está preparado para as seguintes transformações:
    - datetime.datetime => '%Y-%m-%dT%H:%M:%S'
    - datetime.date => '%Y-%m-%d'
    - uuid.UUID => str(uuid.UUID)
    - Decimal => float

    Além disso, objetos (que não sejam de tipos primitivos, como str, float e bool), são
    tratados como dicionários, tendo todos os seus atributos considerados como chaves do json.

    Adicionalmente, se um objeto implementar um método "to_dict", a representação, em dicionário,
    desse objeto será obtida por meio da invocação deste método, antes da transformação do mesmo
    em json (permitindo customizar o modo como um objeto é serializado em json).
    """
    if convert_before_dump:
        data_copy = convert_to_dumps(data)
    else:
        data_copy = data

    return json.dumps(data_copy, ensure_ascii=ensure_ascii)


# JSON LOADS
def _loads_datetime_uuid(value):
    if not isinstance(value, str):
        return value

    matcher_datetime = re.compile(
        '^(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)$')
    matcher_date = re.compile('^(\d\d\d\d)-(\d\d)-(\d\d)$')
    matcher_uuid = re.compile(
        '^[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$')

    match_datetime = matcher_datetime.search(value)
    match_date = matcher_date.search(value)
    match_uuid = matcher_uuid.search(value)

    if match_datetime:
        ano = int(match_datetime.group(1))
        mes = int(match_datetime.group(2))
        dia = int(match_datetime.group(3))
        hora = int(match_datetime.group(4))
        minuto = int(match_datetime.group(5))
        segundo = int(match_datetime.group(6))

        return datetime.datetime(year=ano, month=mes, day=dia, hour=hora, minute=minuto, second=segundo)
    elif match_date:
        ano = int(match_date.group(1))
        mes = int(match_date.group(2))
        dia = int(match_date.group(3))

        return datetime.date(year=ano, month=mes, day=dia)
    elif match_uuid:
        return uuid.UUID(value)
    else:
        return value


def _internal_loads(data):
    if isinstance(data, dict):
        for key in data.keys():
            data[key] = _internal_loads(data[key])
        return data

    elif isinstance(data, list):
        vector = []
        for item in data:
            vector.append(_internal_loads(item))
        return vector

    else:
        return _loads_datetime_uuid(data)


def _loads_to_class(load_data, model_class=None):
    if isinstance(load_data, list):
        return [_loads_to_class(item, model_class) for item in load_data]
    elif isinstance(load_data, dict):
        obj = model_class()
        for k in load_data:
            if hasattr(obj, k):
                setattr(obj, k, load_data[k])
        return obj
    else:
        return model_class()


def json_loads(str_json: str, model_class=None):
    """
    Interpreta a string json recebida no parâmetro "str_json", retornando:
    - Um dicionário ou uma lista de dicionários (se o parâmetro "model_class" for nulo)
    - Um objeto do tipo model_class, ou uma lista desses objetos, atribuido o valor
    das chaves correspondentes no json, para cada atributo com mesmo nome, no objeto.

    É importante destacar que este método está preparado para as seguintes transformações:
    - '%Y-%m-%dT%H:%M:%S' => datetime.datetime
    - '%Y-%m-%d' => datetime.date
    """

    if isinstance(str_json, str):
        data = json.loads(str_json)
    else:
        data = str_json

    load_data = _internal_loads(data)

    if model_class is None or (not isinstance(load_data, dict) and not isinstance(load_data, list)):
        return load_data
    else:
        return _loads_to_class(load_data, model_class)
