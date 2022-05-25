from pydantic import BaseModel, root_validator  
from typing import List, Dict
from collections import OrderedDict

class PositionsConfig(BaseModel):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    posnames : List = []
    tolerance: float = 1.0
    positions: Dict = OrderedDict()  # adding a dictionary for positions. Presfered than leaving it as extra 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:        
        extra = 'allow' # needed for the poses 
        validate_assignment = True
    @root_validator()
    def collect_positions(cls, values):     
        """ collectect the positions from the extras """ 
        positions = values['positions']
        for name in values['posnames']:
            if name not in positions:
                try:
                    positions[name] = float( values[name] ) 
                except (KeyError, TypeError):
                    raise ValueError(f'posname {name!r} is not defined or not a float')   
        return values 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        d = {'posnames': self.posnames, 'tolerance':self.tolerance}
        for p in self.posnames:
            d[p] = self.positions[p]
        return d
# ################################  


