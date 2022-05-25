""" a Yaml loader for pydevmgr used to provide some custom functionalities :

!math constructor to evaluate some mathematical expression 
!include to include a nested yaml file 

"""
import yaml 
from yaml import ScalarNode, MappingNode, SequenceNode
from py_expression_eval import Parser 
import os


CFGPATH = 'CFGPATH'  # name of the environment variable listing config dictionaries 

INCLUDE_KEY = 'include_files'
INCLUDE_TAG = '!include'
MATH_TAG = '!math'

math_parser  = Parser()
del Parser


def find_config(file_name):
    """ find a config file and return its absolute path 
    
    Args:
        file_name (str): config file name. Should be inside one of the path defined by the $CFGPATH 
        environment variable. Alternatively the file_name can be an abosolute path       
    """
    path_list = os.environ.get(CFGPATH , '.').split(':')
    for directory in path_list[::-1]:
        path = os.path.join(directory, file_name)
        if os.path.exists(path):
            return  path
    raise ValueError('coud not find config file %r in any of %s'%(file_name, path_list))


class PydevmgrLoader(yaml.CLoader):
    """ yaml loader with the !include constructor 
    
    !include constructor can be built a scalar string (file path) or a mapping 
    
    - if a file path : it shall be a a yaml configuration file, it is loaded and included in place 
    - if a mapping : the files to include shall be in a includes list of files path 
    the contents of files (which shall be a mapping) are included inside the mapping a value  
    inside the last file will erase the previous one. Ultimatly the values can be overwriten 
    by in the current mapping 
    
    Exemple
    -------

    ---
    name : test
    config: !include path/to/config.yml
    

    --- 
    name: test 
    config: !include
     include_files: [path/to/config1.yml, path/to/config2.yml]
     overwriten_key: 34.5 
    
    """
    find_config = staticmethod(find_config)
   	


def include_constructor(loader, node):

    if isinstance(node, ScalarNode):

        with open(find_config(loader.construct_scalar(node)), 'r') as f:
            return yaml.load(f, PydevmgrLoader)

    
    elif  isinstance(node, MappingNode):
        data = loader.construct_mapping(node)
        try:
            data.pop(INCLUDE_KEY)
        except KeyError:
            return data 
    
        files = _find_includes(loader, node) 
        for file in files[::-1]:
            with open(find_config(file), 'r') as f:
                src = yaml.load(f, PydevmgrLoader)
                if not isinstance(src, dict):
                    raise ValueError("included file inside a mapping is expected to be a mapping")
                _merge_dictionary(data, src)		

        return data		

    else:
        raise ValueError("Bad argument for !include flag constructor")	



def math_constructor(loader, node):
    return math_parser.parse(loader.construct_scalar(node)).evaluate({})

    # filename = os.path.join(self._root, self.construct_scalar(node))

    # with open(filename, 'r') as f:
    #     return yaml.load(f, Loader)    
    # return     

PydevmgrLoader.add_constructor(INCLUDE_TAG, include_constructor)
PydevmgrLoader.add_constructor(MATH_TAG, math_constructor)


def _find_includes(loader, node):

    for k,v in node.value:
        if isinstance(k, ScalarNode) and k.value == INCLUDE_KEY:
            if isinstance(v, ScalarNode):				
                return [loader.construct_scalar(v)]
            if isinstance(v, SequenceNode):
                return loader.construct_sequence(v) 
            else:
                raise ValueError(f"Bad argument for {INCLUDE_KEY!r} constructor")
    return []	


def _merge_dictionary(dst, src):
    stack = [(dst, src)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if isinstance(current_src[key], dict) and isinstance(current_dst[key], dict) :
                    stack.append((current_dst[key], current_src[key]))
                #else:
                #    current_dst[key] = current_src[key]
    




#Loader = yaml.SafeLoader




if __name__ == "__main__":

    includes = [
("test_include1.yml", 
"""---
ctrl:
    min: 0
    max: 10
    velocity: 3

"""),

("test_include2.yml",
"""---
ctrl:
    velocity: 5.0
"""), 


("test_include3.yml",
"""ctrl: !include test_include4.yml
"""),

("test_include4.yml",
"""---
min: -180
max:  180
velocity: 1
"""),

]



    root = """---
motor1: !include 
    include_files: [test_include1.yml, test_include2.yml]
    name: This is a test of the include fonctionality 
    ctrl:
        max: 5

motor2: !include test_include3.yml
x: !math 3+5
y: !math sin(PI/2.0)
"""
    #print( MyModel.parse_obj(yaml.load(t)) )



    tmp_dir = os.path.join('/', 'tmp')
    os.environ[CFGPATH] = tmp_dir
    for file, txt in includes:
        with open( os.path.join(tmp_dir , file), 'w') as g:
            g.write(txt)

    
    obj1 = yaml.load(root, Loader=PydevmgrLoader)
    assert obj1['motor1']['ctrl']['min'] == 0 
    assert obj1['motor1']['ctrl']['max'] == 5
    assert obj1['motor1']['ctrl']['velocity'] == 5.0
    assert obj1['motor2']['ctrl']['velocity'] == 1.0
    assert obj1['x'] == 8
    assert obj1['y'] == 1.0

    obj2 = yaml.load("!include test_include1.yml", Loader=PydevmgrLoader)
    assert obj2['ctrl']['min'] == 0 
    print("OK")




