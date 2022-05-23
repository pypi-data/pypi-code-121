"""
A system to facilitate pre-submission checks in submission tools.

Submitters can implement Validator plugins by inheriting from Validator, in order to check for
things like paths, suitable hardware, cameras, and so on.

Typically, a validation runner will be set up in each submitter's source code to discover and run
all Validator plugins.

"""

import re


def split_camel(name):
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', name)

class ValidationError(Exception):
    pass

class Validator(object):

    def __init__(self, submitter):
        """
        Base class, creates a Validator and initializes storage for errors, warnings, and info messages.

        Arguments:

        * **`submitter`** -- The submitter object, such as a ConductorRender node in Maya, or a
          dialog in Cinema4D. This can be useful for checking submitter settings, but is not always
          needed. 

        ???+ example
            ``` python

            from ciocore.validator import Validator

            class ValidateCheckSomething(Validator):
                def run(self, layername):
                    
                    okay = get_some_value_from_the_scene()
                    if not okay:
                        self.add_warning("There was an issue with a value on layer {}.".format(layername))
            ```

        """
        self._submitter = submitter
        self.errors = set()
        self.warnings = set()
        self.notices = set()

    def add_error(self, msg):
        self.errors.add("[{}]:\n{}".format(self.title(), msg))

    def add_warning(self, msg):
        self.warnings.add("[{}]:\n{}".format(self.title(), msg))

    def add_notice(self, msg):
        self.notices.add("[{}]:\n{}".format(self.title(), msg))

    def run(self, layername):
        raise NotImplementedError

    @classmethod
    def plugins(cls):
        class_names = []
        sub_classes = []
        
        # Avoid a subclass from being added twice - which can happen during a reload()
        for sub_class in cls.__subclasses__():
            if sub_class.__name__ not in class_names:
                sub_classes.append(sub_class)
                class_names.append(sub_class.__name__)
        
        return sub_classes

    @classmethod
    def title(cls):
        return split_camel(cls.__name__)
