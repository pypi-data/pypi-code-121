from typing import Optional, Union, List, Dict

import ROOT

class Sample:
    
    def __init__(self):
        self.process = ""
        self.input_file = ""
        self.norm_factors = []
        self.shape_factors = []
        self.syst_groups = []
        self.expected = ROOT.RooArgSet()
        self.model_name = ""
        self.norm_name = ""
        self.share_pdf_group = ""
        
    def is_equal(self, other:Union[str, "Sample"]):
        if isinstance(other, str):
            return self.process == other
        elif isinstance(other, type(self)):
            return self.process == other.process
        else:
            raise TypeError(f"cannot compare object of type {type(other)} with "
                            "object of type Sample")
    def get_tag_name(self) -> str:
        is_shared_pdf = self.share_pdf_group != ""
        if is_shared_pdf:
            tag_name = self.share_pdf_group
        else:
            tag_name = self.process
        return tag_name