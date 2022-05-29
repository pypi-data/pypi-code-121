import inspect
from types import FunctionType


class LeapInspect:
    @staticmethod
    def get_classes(cls, filterbyparents=None):
        """

        :param cls:
        :return:
        [
            {
                name: x
                class: x
                parents: []
            }
        ]
        """
        classes = []
        for c in inspect.getmembers(cls, predicate=inspect.isclass):
            if '__module__' not in c[1].__dict__:
                print('')
                continue
            cls_dict = {
                'name': c[0],
                'class': c[1],
                'parents': c[1].__dict__['__module__'].split('.')
            }
            if 'meta' in cls_dict['parents']: continue

            if len(set(filterbyparents) - set(cls_dict['parents'])) == len(set(filterbyparents)):
                classes.append(cls_dict)

        return classes

    @staticmethod
    def get_type(func, pval):
        dtype_map = {'int': ['int', 'Integer', 'number'], 'float': ['float'], 'str': ['string', 'str'],
                     'name': ['name'], 'tuple': ["tuple", "Tuple"]}
        if pval.default != inspect._empty:
            return str(type(pval.default)).split('\'')[1]
        # TODO: comment out due to missing CallableMeta type in python 3.8, if an error occurs from this section consider
        # finding the right way to write this if in python 3.8
        # if isinstance(pval.annotation, CallableMeta):
        #     return Callable
        if pval.annotation is str:
            return str
        _type = 'None'
        doc_str = func.__dict__.get('__doc__')
        if doc_str is not None:
            for line in doc_str.split('\n'):
                if ' {}:'.format(pval.name) in line[0:len(pval.name) + 10]:
                    # _type = line.split(': ')[1].split(',')[0].split(' ')[0]
                    for t, vals in dtype_map.items():
                        if True in list(val in line for val in vals):
                            _type = t
                    break
        return _type

    @staticmethod
    def get_function_args(func):
        args = {}
        if isinstance(func, FunctionType):
            parameters = inspect.signature(func).parameters
        else:
            parameters = inspect.signature(func.__init__).parameters
        for p, pval in parameters.items():
            if p in ['kwargs']:
                continue
            _type = LeapInspect.get_type(func, pval)
            args[pval.name] = \
                {
                    'name': pval.name,
                    'isdefault': pval.default != inspect._empty,
                    'default_val': pval.default if pval.default != inspect._empty else None,
                    'type': _type,
                }
        return args
