from .node import Node
import importlib
from .utils import is_object, is_objects_list, is_var, is_list, is_config, is_from
from . import config as config
from . import variables as variables
import copy
import os

__all__ = ["Config", "SingleObject", "ObjectsList", "Parameters"]


class Config(Node, dict):

    def __init__(self, name, config_dict, parent=None, path=None):
        object.__setattr__(self, "_xpipe_path", path)
        Node.__init__(self, name, config_dict, parent)

    def _xpipe_check_valid(self, name, config_dict):
        if not isinstance(name, str) or name != "__root__":
            super(Config, self)._xpipe_check_valid(name, config_dict)
        return True

    def _xpipe_construct(self, name, sub_config):
        from_node = None

        for name, sub_config in sub_config.items():
            node = construct(name, sub_config, parent=self)
            
            if isinstance(node, FromIncludes):
                if from_node is not None:
                    raise Exception("Only one !from per node is allowed")
                from_node = node
            else:
                dict.__setitem__(self, name, node)
        
        if from_node is not None:
            r = config.merge(from_node.includes, self)
            dict.clear(self)
            dict.update(self, r)

    def _xpipe_to_yaml(self, n_indents=0):
        r = []
        for key, value in self.items():
            el = "  " * n_indents
            el += f"{key}: "
            if not isinstance(value, variables.Variable):
                el += "\n"
            el += f"{value._xpipe_to_yaml(n_indents=n_indents + 1)}"
            r += [el]
        joiner = "\n\n" if self._xpipe_name == "__root__" else "\n"
        return joiner.join(r)

    def _xpipe_to_dict(self):
        return { k: v._xpipe_to_dict() for k, v in self.items() }
    
    def __getattribute__(self, prop: str):
        try:
            return dict.__getitem__(self, prop)
        except KeyError:
            pass

        try: 
            return object.__getattribute__(self, prop)
        except:
            raise AttributeError(f"'{self._xpipe_name}' ({self.__class__.__name__}) does not have an attribute '{prop}'")

    def __setattr__(self, key, value):
        dict.__setitem__(self, key, value)

    def __getitem__(self, prop):
        if dict.__contains__(self, prop):
            return dict.__getitem__(self, prop)
        else:
            raise AttributeError(f"'{self._xpipe_name}' ({self.__class__.__name__}) does not have an attribute '{prop}'")
    
    def __repr__(self) -> str:
        return f"Config(len={len(self)})"
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        copy_instance = cls.__new__(cls)
        memo[id(self)] = copy_instance # Add the object to memo to avoid infinite recursion (the object is referenced by its children)

        dict_values = set(self.keys()) 
        attributes_name = set(self.__dict__.keys()) - dict_values

        # copy attributes
        for name in attributes_name:
            attr_value = object.__getattribute__(self, name)
            copied_attr_value = copy.deepcopy(attr_value, memo)
            object.__setattr__(copy_instance, name, copied_attr_value)

        # copy dict
        for name in dict_values:
            dict_value = dict.__getitem__(self, name)
            copied_dict_value = copy.deepcopy(dict_value, memo)
            dict.__setitem__(copy_instance, name, copied_dict_value)

        return copy_instance

    def __hash__(self) -> int:
        return hash(id(self))


class IncludedConfig(Config):

    def __init__(self, name, config_dict, parent=None, path=None):
        base_path = config.get_base(parent)._xpipe_path or "" if parent is not None else ""
        base_path = os.path.dirname(base_path)
        conf = config_dict.load(base_path)
        super(IncludedConfig, self).__init__(name, conf, parent, path=path)
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, IncludedConfig): 
            raise Exception(f"Cannot compare {self.__class__} and {o.__class__}")
        return self._xpipe_path == o._xpipe_path

    def __hash__(self) -> int:
        return hash(id(self))

    def __repr__(self) -> str:
        return f"IncludedConfig(len={len(self)}, path={self._xpipe_path})"


class Parameters(Config):
    """Create parameters of an object from a dict 'param_dict' of format 
    { 
    object_param_name: {class_name: obj_param_dict},
    variable_param_name: value,
    objects_list_param_name: [class_name: obj_param_dict, ...]
    }

    Args:
        param_dict (dict): Dictionary of the parameters
    """

    def __init__(self, class_name, param_dict, parent=None):
        super(Parameters, self).__init__(class_name, param_dict, parent)
        
    def _xpipe_construct(self, class_name, params_dict):
        super(Parameters, self)._xpipe_construct(class_name, params_dict)

    def _xpipe_check_valid(self, class_name, param_dict):
        return True

    def __repr__(self) -> str:
        return f"Parameters({len(self)})"

    def unwarp(self):
        return {param_name: (param_value() if not isinstance(param_value, Config) else param_value) for param_name, param_value in self.items()}


class IncludedParameters(Parameters):

    def __init__(self, class_name, param_dict, parent=None):
        base_path = config.get_base(parent)._xpipe_path or "" if parent is not None else ""
        base_path = os.path.dirname(base_path)
        conf = param_dict.load(base_path)
        super(IncludedParameters, self).__init__(class_name, conf, parent)
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, IncludedParameters): 
            raise Exception(f"Cannot compare {self.__class__} and {o.__class__}")
        return self._xpipe_path == o._xpipe_path
    
    def __hash__(self) -> int:
        return hash(id(self))


class FromIncludes(Node):

    def __init__(self, name, config_dict, parent=None):
        super(FromIncludes, self).__init__(name, config_dict, parent)
    
    def _xpipe_check_valid(self, name, config_dict):
        
        if not isinstance(config_dict, list):
            raise Exception(f"{name} must be a list")
        
        for include in config_dict:
            if not isinstance(include, variables.Include):
                raise Exception(f"{name} must be a list of includes")
        
        return True

    def _xpipe_construct(self, name, config_dict):
        self.includes = config.merge(*[construct("", sub_config_dict, parent=self) for sub_config_dict in config_dict], inplace=True)


class List(Node, list):

    def __init__(self, name, config_dict, parent=None):
        super(List, self).__init__(name, config_dict, parent)
    
    def _xpipe_construct(self, name, config_dict):
        for i, element in enumerate(config_dict):
            var_name = f"{name}[{i}]"
            constructed_el = construct(var_name, element, parent=self)
            self.append(constructed_el)

    def _xpipe_check_valid(self, name, config_dict):
        return True

    def _xpipe_to_dict(self):
        return [el._xpipe_to_dict() if isinstance(el, Node) else el for el in self]

    def _xpipe_to_yaml(self, n_indents=0):
        r = ""
        
        for el in self:
            indents = "  " * (n_indents + 1)
            yaml_el = el._xpipe_to_yaml(n_indents = n_indents + 2) if isinstance(el, Node) else el
            if isinstance(el, Config) or isinstance(el, ObjectsList) or isinstance(el, List):
                yaml_el = f"\n{yaml_el}"
            if isinstance(el, SingleObject):
                yaml_el = yaml_el.lstrip()
            r += f"{indents}- {yaml_el}\n"
        return r

    def __getitem__(self, index):
        from .variables import Variable
        element = list.__getitem__(self, index)
        if isinstance(element, Variable):
            return element()
        else:
            return element

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __hash__(self) -> int:
        return hash(id(self))
        
    def __call__(self):
        return [el for el in self]

    def __repr__(self) -> str:
        return f"[{', '.join(map(lambda x: str(x), self))}]"
    

class SingleObject(Node):
    """Allow the instantiation of an object defined in a yaml configuration file.

    Args:
        name (str): Name of the object
        config_dict (dict): A dictionary defining the object (class name and parameters).
    """

    def __init__(self, name, config_dict, parent=None):
        super(SingleObject, self).__init__(name, config_dict, parent)

    def _xpipe_check_valid(self, name, config_dict):
        return True

    def _xpipe_construct(self, name, config_dict):
        obj, self._params = list(config_dict.items())[0]
        self._class_name = obj.class_name
        split_index = len(self._class_name) - self._class_name[::-1].index(".") # Get index of the last point
        self._module, self._class_name = self._class_name[:split_index-1], self._class_name[split_index:]
        if not isinstance(self._params, variables.Include):
            self._params = Parameters(self._class_name, self._params, parent=self)
        else:
            self._params = IncludedParameters(self._class_name, self._params, parent=self)

    def _xpipe_to_yaml(self, n_indents=0):
        indents = "  " * (n_indents)
        r = f"{indents}{variables.SingleObjectTag.yaml_tag} {self._module}.{self._class_name}:\n"
        r += self._params._xpipe_to_yaml(n_indents=n_indents + 1)
        return r

    def _xpipe_to_dict(self):
        return {
            f"{variables.SingleObjectTag.yaml_tag} {self._module}.{self._class_name}": self._params._xpipe_to_dict()
        }
        
    def __call__(self, **args):
        module = importlib.import_module(self._module)
        class_object = getattr(module, self._class_name)
        params = self._params.unwarp()
        return class_object(**params, **args)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SingleObject): 
            raise Exception(f"Cannot compare {self.__class__} and {o.__class__}")
        return self._class_name == o._class_name and self._params == o._params

    def __hash__(self) -> int:
        return hash(id(self))

    def __repr__(self) -> str:
        return f"SingleObject(name={self._class_name})"


class ObjectsList(List):
    """Create a list of SingleObject from a yaml configuration file.

    Args:
        name (str): Name of the list of objects
        config_dict (list<dict>): A list of dictionaries which defines the objects list.
    """
    
    def __init__(self, name, config_dict, parent=None):
        super(ObjectsList, self).__init__(name, config_dict, parent)

    def _xpipe_check_valid(self, name, config_dict): 
        super(ObjectsList, self)._xpipe_check_valid(name, config_dict)

    def __call__(self, **args):
        return [obj(**args) for obj in self]


def get_node_type(name, conf):
    """Detect the object that can build the tree

    Args:
        conf (dict): The configuration dictionary

    Returns:
        Node | Variable: The object type
    """
    if isinstance(conf, variables.Variable):
        # Return the builder class defined by the variable or None if none is needed
        builder_name = getattr(conf.__class__, "builder_class_name", None)
        return globals()[builder_name] if builder_name is not None else None

    builder_checkers = [
        (FromIncludes, is_from),
        (SingleObject, is_object),
        (ObjectsList, is_objects_list),
        (List, is_list), 
        (variables.Variable, is_var),
        (Config, is_config)
    ]
    for node_type, can_build in builder_checkers:
        if can_build(name, conf):
            return node_type
    raise Exception(f"Configuration cannot be parsed: {conf}")


def construct(name, config_dict, parent=None):
    """Build a tree from a dictionary

    Args:
        name (str): Name of the node
        config_dict (dict): The dictionary

    Returns:
        Node | Variable: The build tree element
    """
    NodeType = get_node_type(name, config_dict)
    try:
        if NodeType is not None: 
            node = NodeType(name, config_dict, parent)
        else: 
            # Node is already built by a yaml tag
            node = config_dict
            node.set_parent(parent)
            node.set_name(name)
    except Exception as e:
        raise ValueError(f"Error while building {name}, {NodeType}") from e
    return node