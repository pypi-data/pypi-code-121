from typing import Optional, Union, List, Dict

class Systematic:
    def __init__(self):
        self.name = ""
        self.domain = ""
        self.process = ""
        self.whereto = ""
        self.constr_term = ""
        self.nominal = 0.
        self.beta = 0.
        self.errorlo = None
        self.errorhi = None
    def is_equal(self, other:"Systematic"):
        return (self.name == other.name) and (self.process == other.process) and (self.whereto == other.whereto)