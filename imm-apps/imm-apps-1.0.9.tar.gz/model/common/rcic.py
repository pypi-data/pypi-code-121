from pydantic import BaseModel

# RCIC
class Rcic(BaseModel):
    first_name:str
    last_name:str
    company:str
    sex:str
    rcic_number:str
    
    @property
    def name(self):
        return self.first_name+' '+self.last_name
    
    