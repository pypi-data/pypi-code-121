from pydantic import BaseModel, validator
from typing import List
from enum import Enum 



##### ############
# Sequence
class INITSEQ(int, Enum):
    END = 0
    FIND_INDEX = 1
    FIND_REF_LE = 2
    FIND_REF_UE = 3
    FIND_LHW = 4
    FIND_UHW = 5

    DELAY = 6
    MOVE_ABS = 7
    MOVE_REL = 8
    CALIB_ABS = 9
    CALIB_REL = 10
    CALIB_SWITCH = 11

for E,v1,v2 in [
    ( INITSEQ.END,  "", "" ),
    ( INITSEQ.FIND_INDEX, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_REF_LE, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_REF_UE, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_LHW, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_UHW, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.DELAY, "Delay [ms]", "" ),
    ( INITSEQ.MOVE_ABS, "Vel", "Pos" ),
    ( INITSEQ.MOVE_REL, "Vel", "Pos" ),
    ( INITSEQ.CALIB_ABS, "Pos", "" ),
    ( INITSEQ.CALIB_REL, "Pos", "" ),
    ( INITSEQ.CALIB_SWITCH, "Pos", "" ),
]:
    setattr(E, "var1", v1)
    setattr(E, "var2", v2)
del E,v1,v2



# ################################        
    
class SeqStepConfig(BaseModel):
    """ Data  Model for step configuration """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    index: int =  0    
    value1: float = 0.0
    value2: float = 0.0
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:                
        validate_assignment = True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        return self.dict(exclude={"index"})
# ################################

class InitialisationConfig(BaseModel):
    """ Config Model for the initialisation sequence """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    sequence : List[str] = []
    END          : SeqStepConfig = SeqStepConfig(index=0) 
    FIND_INDEX   : SeqStepConfig = SeqStepConfig(index=1)
    FIND_REF_LE  : SeqStepConfig = SeqStepConfig(index=2)
    FIND_REF_UE  : SeqStepConfig = SeqStepConfig(index=3)
    FIND_LHW     : SeqStepConfig = SeqStepConfig(index=4)
    FIND_UHW     : SeqStepConfig = SeqStepConfig(index=5)  
    DELAY        : SeqStepConfig = SeqStepConfig(index=6)
    MOVE_ABS     : SeqStepConfig = SeqStepConfig(index=7)
    MOVE_REL     : SeqStepConfig = SeqStepConfig(index=8)
    CALIB_ABS    : SeqStepConfig = SeqStepConfig(index=9)
    CALIB_REL    : SeqStepConfig = SeqStepConfig(index=10)
    CALIB_SWITCH : SeqStepConfig = SeqStepConfig(index=11)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:                
        validate_assignment = True        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @validator('END', 'FIND_INDEX', 'FIND_REF_LE', 'FIND_REF_UE', 'FIND_LHW', 'FIND_UHW', 
               'DELAY', 'MOVE_ABS', 'MOVE_REL', 'CALIB_ABS', 'CALIB_REL' , 'CALIB_SWITCH')
    def force_index(cls, v, field):
        """ need to write the index """        
        v.index = getattr(INITSEQ, field.name)
        return v

    @validator('sequence')
    def validate_initialisation(cls,sequence):   
        """ Validate the list of sequence """ 
        for s in sequence:
            try:
                cls.__fields__[s]
            except KeyError:
                raise ValueError(f'unknown sequence step named {s!r}')
        return sequence
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        d = {'sequence':self.sequence}
        for seq in self.sequence:
            d[seq] = getattr(self, seq).cfgdict()            
        return d
# ################################



def init_sequence_to_cfg(initialisation, INITSEQ=INITSEQ):
    """ from a config initialisation dict return a dictionary of key/value for .cfg interface """            
    
    
    # set the init sequence    
    cfg_dict = {} 
    
    init_dict = initialisation.dict(exclude_none=True, exclude_unset=True)
    if not "sequence" in init_dict:        
        return cfg_dict
    
    # reset all sequence variable
    for i in range(1,11):
        cfg_dict["init_seq{}_action".format(i)] = INITSEQ.END.value
        cfg_dict["init_seq{}_value1".format(i)] = 0.0
        cfg_dict["init_seq{}_value2".format(i)] = 0.0
        
    for stepnum, step_name in enumerate(initialisation.sequence, start=1):
        step = getattr(initialisation, step_name)
        cfg_dict["init_seq%d_action"%stepnum] = step.index
        cfg_dict["init_seq%d_value1"%stepnum] = step.value1
        cfg_dict["init_seq%d_value2"%stepnum] = step.value2    
    return cfg_dict

