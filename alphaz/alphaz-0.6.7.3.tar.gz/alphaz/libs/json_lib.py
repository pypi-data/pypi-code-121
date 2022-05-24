import json
import typing
from flask_sqlalchemy.model import DefaultMeta

from ..models.database.row import Row

def jsonify_database_models(model: DefaultMeta, first=False, relationship: bool = True, disabled_relationships: typing.List[str] = None):
    """Convert a database model structure to json

    Args:
        model (DefaultMeta): database mode structure
        first (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """

    schema = model.get_schema(relationship = relationship, disabled_relationships = disabled_relationships)

    structures = schema()  # schema(many=True) if not first else
    results_json = structures.dump(model)  # TODO: ? wtf why does it works
    return results_json


def jsonify_data(data, string_output: bool = False):
    """Convert any data to a json structure

    Args:
        data ([type]): data to convert

    Returns:
        [type]: data converted as a json structure
    """
    if type(data) == list:
        result = [jsonify_data(x) for x in data]
    elif type(data) == dict:
        result = {jsonify_data(x): jsonify_data(y) for x, y in data.items()}
    elif type(data) == Row:
        result = dict(data)
    else:
        result = data

        if hasattr(data, "schema") or hasattr(data, "get_schema"):
            result = jsonify_database_models(data)
        elif hasattr(data, "_fields"):
            result = {x: data[i] for i, x in enumerate(data._fields)}
    if string_output:
        result = json.dumps(result)
    return result


def load_json(string: str):
    if string is None:
        return None
    if type(string) != str:
        string = str(string)
    string = string.strip()
    
    if len(string) != 0 and string[0] == "{" and string[-1] == "}":
        return json.loads(string)
    if len(string) == 0:
        string = '""'
    string = '{"json":' + string + "}"
    data = json.loads(string)
    return data["json"]
