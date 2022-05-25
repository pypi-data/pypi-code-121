from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from .io import find_ui
from pydevmgr_elt import Motor, DataLink

from pydevmgr_core_qt import record_widget_factory, InputOutputs, get_style, STYLE
from .elt_device_cfg import EltDeviceCfg
import math 

class MotorCfgData(EltDeviceCfg.Data):
    CfgData = Motor.Data.CfgData
    
    cfg: CfgData = CfgData()     



def link_init_action():
    pass
        
def float_nan(t):
    try:
        return float(t)
    except (ValueError, TypeError):
        return None

def int_nan(t):
    try:
        return int(t)
    except (ValueError, TypeError):
        return None    

def b2t(b):
    return "[X]" if b else "[_]"

def switch_style(w,b):
    style = STYLE.SIMILAR if b else STYLE.DIFFERENT
    w.setStyleSheet(get_style(style))


class InitSeq(InputOutputs.Base):
    def __init__(self, action_enum,  input_action, input_value1, input_value2, output):
        def set_input(action, value1, value2):
            input_action.setCurrentIndex(action)
            input_value1.setText(f"{value1}")
            input_value2.setText(f"{value2}")  
            
        def get():

            try:
                v1 = float(input_value1.text())
            except (TypeError, ValueError):
                v1 = math.nan
            
            try:
                v2 = float(input_value1.text())
            except (TypeError, ValueError):
                v2 = math.nan
 

            a = input_action.currentIndex()          
            return (a, v1, v2)
        
        def set(action, value1, value2):
            action_txt = action_enum(action).name            
            output.setText(f"{action_txt:>13} {value1:.3f} {value2:.3f}")
            
            switch_style(output, self.get() == (action, value1, value2))        
        super().__init__(set_input, set, get)   
            

class MotorCfgUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('motor_cfg_frame.ui'), self)    
        
            
class MotorCfg(EltDeviceCfg):
    Widget = MotorCfgUi
    Data = MotorCfgData
        
    first_update = True
    
    def feedback(self, er, msg):
        # a feedback would be nice 
        pass 
    
    def init_vars(self):
        ws = self.widget
        get = lambda a: getattr(self.widget,a)
        
        self.outputs.name = self.outputs.Str( ws.name )
        
        self.io.keys = {}
        for k in ["brake", "low_brake", "check_inpos", "low_inpos",
            "active_low_lstop", "active_low_lhw", "active_low_ref", "active_low_index",
            "active_low_uhw", "active_low_ustop", "exec_pre_init", "exec_post_init",
            "exec_pre_move", "exec_post_move", "disable",  "lock"]: 
            
            self.io.keys[k]  = self.io.Bool(get("in_"+k),get(k))
        
        for k in ["min_pos", "max_pos", "lock_pos", "lock_tolerance", "backlash"]:
            self.io.keys[k]  = self.io.Float(get("in_"+k), get(k))
        
        for k in ["tout_init", "tout_move", "tout_switch"]:
            self.io.keys[k]  = self.io.Int(get("in_"+k), get(k))
            
        
        self.io.keys['axis_type'] = self.io.Enum(Motor.AXIS_TYPE, self.widget.in_axis_type, self.widget.axis_type)
        
        self.io.sequences = {}
        names = [a.name for a in Motor.INITSEQ]
        for i in range(1,11):
            wa = get(f"init{i}_action")
            wa.addItems(names)
            self.io.sequences[i] = InitSeq(Motor.INITSEQ, 
                                           wa,
                                           get(f"init{i}_value1"),
                                           get(f"init{i}_value2"),
                                           get(f"init{i}_actual"), 
                                           )
                                                           
    def update(self, data) -> None:
        """ update the gui from the attached structure data """
        super().update(data)
        
        cfg = data.cfg
        
        if self.first_update:
            self.edit_all(data.cfg)            
            self.first_update = False
        
        for k, v in self.io.keys.items():
            v.set( getattr(cfg, k) )
        
        for i,s in self.io.sequences.items():
            s.set( getattr(cfg, f"init_seq{i}_action"), 
                                      getattr(cfg, f"init_seq{i}_value1"), 
                                      getattr(cfg, f"init_seq{i}_value2"), 
                                      )
        
    
    def setup_ui(self, motor, data):
        super().setup_ui(motor, data)
        
        self.outputs.name.set( data.name or motor.key )
        
        configure = self.actions.add( lambda : self.configure_motor(motor))
        configure.connect_button(self.widget.in_upload_to)
        
        
        def upload_data():
            data = self.new_data()
            
            #download(DataLink(motor.cfg, cfg))
            DataLink(motor, data).download()
            self.edit_all(data.cfg)
            self.update(data)
        upload_data = self.actions.add(upload_data)
        upload_data.connect_button(self.widget.in_download_from)
        
        
        def upload_data_from_config():
            data = self.new_data()
            cfg = data.cfg
            
            dl = DataLink(motor.cfg, cfg)
            nodes = motor.get_configuration()
                        
            dl.download_from_nodes(nodes)                        
            self.edit_all(cfg)
            self.update(data)
        upload_data_from_config = self.actions.add(upload_data_from_config)
        upload_data_from_config.connect_button(self.widget.in_from_config_file)
                 
        self.first_update = True

            
    #####################################################
    def edit_all(self, cfg):
        for k, v in self.io.keys.items():
            v.set_input( getattr(cfg, k) )
        
        for i,s in self.io.sequences.items():
            s.set_input( getattr(cfg, f"init_seq{i}_action"), 
                         getattr(cfg, f"init_seq{i}_value1"), 
                         getattr(cfg, f"init_seq{i}_value2") )
        
        self.widget.repaint()
        
     
    def configure_motor(self, motor: Motor) -> None:
        """ Configure the motor to what is eddited on the GUI """
        data = self.new_data()
        cfg = data.cfg
        dl = DataLink(motor.cfg, cfg)
        dl.download() # load all server values first 
        # Then update the data to what is defined in the GUI
        
        for k, v in self.io.keys.items():
            setattr(cfg, k, v.get())
        
        for i,s in self.io.sequences.items():
            a,v1,v2 = s.get()
            setattr(cfg, f"init_seq{i}_action", a )
            setattr(cfg, f"init_seq{i}_value1", v1)
            setattr(cfg, f"init_seq{i}_value2", v2)
                
        dl.upload()                
        
record_widget_factory("cfg", "Motor", MotorCfg)        
    
        
        
        
            
        
      
