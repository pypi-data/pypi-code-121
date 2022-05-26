from .translation_dictionary import translation
from .type_utils import str2bool


class Property:
    
    def __init__(self, name, type=str, help='', default=None, choices=None, required=False, *args, **kw) -> None:
        
        # Remove all dashes from name
        while name[0] == "-":
            name = name[1:]
        self.name = name

        self.description = help
        self.type = type
        self.default = default
        self.choices = choices
        self.required = required

    def print(self):

        print("#####################")
        print("Name: " + self.name)
        print("Description: ", self.description)
        print("Type: ", translation['type'][self.type])
        print("Default: ", self.default)
