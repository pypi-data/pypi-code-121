from bdaserviceutils import get_cmd_arg

def input_or_output(name):
    if get_cmd_arg("assets.dataset.input." + name) is not None:
        return "input"
    return "output"

def get_dataset_property(name, prop=None):
    dir = input_or_output(name)
    
    arg = "assets.dataset." + dir + "." + name 
    
    if prop is not None:
        arg += "." + prop
    
    return get_cmd_arg(arg)
