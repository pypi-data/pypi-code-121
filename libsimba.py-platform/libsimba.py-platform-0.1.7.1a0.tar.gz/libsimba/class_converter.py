from typing import Any
import json


def convert_classes(inputs):
    """
    solidity structs represented as classes will have "class_to_dict_converter" attr
    this function gets called in contract method calls inside simba_contract.py

    Args:
        inputs (dict): dict of {param_name: param_value} form
    """
    for attr_name, attr_value in inputs.items():
        if hasattr(attr_value, "class_to_dict_converter"):
            attr_value.class_to_dict_converter()
            inputs[attr_name] = attr_value.__dict__


class ClassToDictConverter:
    def class_to_dict_converter_helper(
        self, class_dict: dict, attr_name: str, attr_value: Any
    ):
        """
        Recursively convert method inputs from class instances to dicts
        We call this method because when we pass a struct in the API, it expects a dictionary, not a class instance

        Args:
            class_dict (dict): dict formatted version of a class, obtained from classInstance.__dict__
            attr_name (str)): attribute name in our inputs dictionary
            attr_value (Any): value of attribute in inputs dictionary. if this is a class instance with attribute __dict__, then we convert to dict
        """
        if hasattr(attr_value, "__dict__"):
            class_dict[attr_name] = attr_value.__dict__
            for att_name, att_val in class_dict[attr_name].items():
                self.class_to_dict_converter_helper(
                    class_dict[attr_name], att_name, att_val
                )

    def class_to_dict_converter(self):
        for att_name, att_value in self.__dict__.items():
            self.class_to_dict_converter_helper(self.__dict__, att_name, att_value)
