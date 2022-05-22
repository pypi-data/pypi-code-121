from traitlets import TraitType as _TraitType, Any as _Any
import copy
import json

class DataTable(_Any):
    """
        A trait for a graph dictionary
    """

    default_value = []
    info_text = 'a Pandas DataFrame (preferred), dict in format of { col1:[...], col2:[...] }, or list in form of [{col1:val1,col2:val2},{col1:val1,col2:val2}]'

    def validate(self, obj, value):
        if "'pandas.core.frame.DataFrame'" in str(type(value)):
            return copy.deepcopy(json.loads(value.to_json(orient="records")))

        elif "dict" in str(type(value)):
            return copy.deepcopy([dict(zip(value,t)) for t in zip(*value.values())])

        elif "list" in str(type(value)):
            return copy.deepcopy(value)


        self.error(obj, value)
