from TDhelper.MagicCls.MagicMeta import MagicMeta
from TDhelper.MagicCls.FieldsType import FieldType
import json

class model(metaclass=MagicMeta):
    def __init__(self, source, convertType="json"):
        assert source, "params source is None."
        try:
            if isinstance(source,str):
                if convertType.lower()=="xml":
                    # add code, conver xml data to json.
                    pass
                elif convertType.lower()=="json":
                    source= json.loads(source)
                else:
                    raise Exception("conver_type must set xml or json.")
            self.Meta.source = source if isinstance(source, list) else [source]
            self.Meta.convert_type = convertType
            self.__instance__()
        except Exception as e:
            raise e

    class Meta:
        """
        class meta set
        - source: create class source.
        - convert_type: convert type, default json.
        """

        source = None
        convert_type = "json"


def createCls(cls_name, mapping: dict, source, convert_type="json"):
    '''
    running time dynamic create class.
    
    Args:
        cls_name: <str>, class name.
        mapping: <dict>, mapping setting.
        source: <object>, data source(json or xml).
        convert_type: <str>, default value 'json', can set value <'json','xml'>.
    Return:
        <class:cls_name> object.
    '''
    dct = {}
    for n, v in mapping.items():
        if len(v) == 1:
            dct[n] = FieldType(v[0], n)
        elif len(v) == 2:
            dct[n] = FieldType(v[0], v[1])
        else:
            raise "mapping format is error, example: {field:[type,mapping_field]}, if field is same of mapping_field then can not be set 'mapping_field'."
    dct["__init__"] = __init__
    return type(cls_name, (model,), dct)(source, convert_type)

def __init__(self, source, convert_type="json"):
    model.__init__(self, source, convert_type)
