#!/usr/bin/python

class Assign:
    @staticmethod
    def doc_(doc):
        return f'# {doc}\n'

    @staticmethod
    def int_(key, value):
        return f'{key} = {value}\n'

    @staticmethod
    def str_(key, value=""):
        return f'{key} = \"{value}\"\n'

    @staticmethod
    def list_(key, value=""):
        return f'{key} = [{value}]\n'

    @staticmethod
    def dict_(key):
        return f'{key} = {{}}\n'

    @staticmethod
    def none_(key):
        return f'{key} = None\n'

    @staticmethod
    def line_():
        return "\n"

    @staticmethod
    def dict_list(dict_config):
        result_str = ""
        for key, list_value in dict_config.items():
            _ = "\n    ".join( map(lambda x:f'"{x.strip()}",', [*map(str, list_value)] ) )
            value = f'[\n    {_}\n]\n'
            result_str += f'{key} = {value}'+ "\n"
        return result_str