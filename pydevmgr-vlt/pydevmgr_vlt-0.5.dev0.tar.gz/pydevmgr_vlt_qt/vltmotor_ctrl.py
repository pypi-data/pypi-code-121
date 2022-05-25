from PyQt5 import uic
from PyQt5.QtWidgets import QFrame

from .io import find_ui
from pydevmgr_core import NodeVar
from .vltdevice_ctrl import VltDeviceCtrl
from pydevmgr_core_qt import record_widget_factory

from enum import IntEnum

#####
# Define all the data used at fron-end 
# The NodeVar annotation indicate that the data will be taken from a device node see `pydevmgr.DataLink`

class VltMotorCtrlStatData(VltDeviceCtrl.Data.StatData):
    # DeviceStatData contain state, substate, error code and txt information 
    # Add here all NodeVar needed for the motor GUI    
    pos_actual: NodeVar[float] = 0.0
    pos_target: NodeVar[float] = 0.0
    vel_actual: NodeVar[float] = 0.0
    pos_name: NodeVar[str] = ""
    state: NodeVar[int] = 0
    state_txt : NodeVar[str] = ""

###
# Example of use:
#  data = MotorCtrlData()
#  dl = DataLink(motor, data)
#  dl.update() # update data from server(s)
#  print(data.stat.pos_actual, data.stat.pos_error) 
class VltMotorCtrlData(VltDeviceCtrl.Data):
    StatData = VltMotorCtrlStatData
    stat: StatData = StatData()

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

# The UI is an empty shell all inteligence is settled by MotorCtrlLink
class VltMotorCtrlUi(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('vltmotor_ctrl_frame.ui'), self)

    
class VltMotorCtrl(VltDeviceCtrl):
    # A widget constructor for default widget 
    Widget = VltMotorCtrlUi
    # A data constructor 
    Data = VltMotorCtrlData
    
    # Basicaly 3 methods needs to be implemented 
    # - .init_vars() :  build the variable handler function to their type and widget
    # - .update(data) :   update widget with new data 
    # - .connect_device(device, data) : this is where commands has to be connected to widget buttons etc...
    
    def init_vars(self):
        super().init_vars()
        
        # Add an interface between the widget and the variable to set/get 
        # the goal is to give basic functionality to the variable (.get ) wihtout having to care 
        # on the widget type. It is expected that the .Float will handled any suitable widgets
        # however so far only a few widget are handled and this can involved function to usage
        # It is okay to also use the widget directly, the goal of these layer is not to interface all
        # widget capabilities but only some basic ones.
        # outputs/inputs are instances of Inputs/Outputs and can be use to collect constructors
        # and instances of widget interfaces. 
        self.outputs.pos_actual = self.outputs.Float(self.widget.pos_actual, fmt="%.3f")
        self.outputs.pos_target = self.outputs.Float(self.widget.pos_target, fmt="%.3f")
        self.outputs.vel_actual = self.outputs.Float(self.widget.vel_actual, fmt="%.3f")
        
        self.outputs.pos_name = self.outputs.Str(self.widget.posname)
        
        self.outputs.pos_error = self.outputs.Float(self.widget.pos_error, fmt="%.3f")
        self.outputs.state = self.outputs.Code(self.widget.state)

        self.inputs.velocity   = self.inputs.Float(self.widget.input_velocity, default=1.0)
        self.inputs.pos_target = self.inputs.Float(self.widget.input_pos_target)
        self.inputs.move_mode  = self.inputs.Enum(MOVE_MODE , self.widget.move_mode, default=MOVE_MODE.ABSOLUTE)     
     
    def update(self, data):
        super().update(data)
        # data as returned by self.new_data()
        stat = data.stat 
        
        if self.widget.move_mode.currentIndex()==MOVE_MODE.VELOCITY: # VELOCITY
            self.widget.input_pos_target.setEnabled(False)
        else:
            self.widget.input_pos_target.setEnabled(True)
        
        # this will update the widget labels underneath          
        self.outputs.state.set( (stat.state, stat.state_txt ) )
        self.outputs.pos_actual.set(stat.pos_actual)
        self.outputs.pos_error.set(stat.pos_actual - stat.pos_target)
        self.outputs.pos_target.set(stat.pos_target)
        self.outputs.vel_actual.set(stat.vel_actual)

        self.outputs.pos_name.set(stat.pos_name)
    
    
    def setup_ui(self,motor, data):
        # super shall take care of state and substate         
        super().setup_ui(motor, data)
                                
        # init some input fields to default, only if the device is connected         
        if motor.is_connected():
            self.inputs.velocity.set_input(motor.cfg.velocity.get())
        
        # self.actions is an instance of Actions and shall be used to implement any action
        # it is important to use actions.add instead of directly Action() as some individual action 
        # need a proper global setup when connected to a widget (e.g. connect_item)
        # The possibilities of action connection type is still reduced but should grows in the future
                
        # Stop button calls motor.stop without argument feedback(er, txt) is called in case of exception            
        self.actions.add( motor.stop, feedback=self.feedback).connect_button(self.widget.stop)
        
        # MOVE button 
        # define a move function to handled inputs comming from movement type, pos and velocity                               
        def move(mode, pos, vel):
            if mode == MOVE_MODE.ABSOLUTE:
                motor.move_abs(pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                motor.move_rel(pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                motor.move_vel(vel)
        
        move = self.actions.add(
                      move, 
                      # if a function (like bellow) it is called at run time to get the value
                      # if an exception occurs feedback is called and move function is not 
                      [self.inputs.move_mode.get, self.inputs.pos_target.get, self.inputs.velocity.get], 
                      feedback = self.feedback
                      )
        move.connect_button(self.widget.move)
   
        # A dropdown menu allows to move directly by position name 
        wm = self.widget.move_by_posname
        wm.clear()
        wm.addItem('')
        reset = lambda : wm.setCurrentIndex(0) # put always the first empty item after an action 
        
        for i,posname in enumerate(motor.config.positions.posnames, start=wm.count()):
            action = self.actions.add( 
                                       motor.move_name, [posname, self.inputs.velocity.get], 
                                       after=reset, feedback = self.feedback
                                    )
            wm.addItem(posname)
            action.connect_item(wm, i)



    def setup_actions(self, device, data):
        super().setup_actions(device, data)
        

                                           
record_widget_factory("ctrl", "VltMotor", VltMotorCtrl)

