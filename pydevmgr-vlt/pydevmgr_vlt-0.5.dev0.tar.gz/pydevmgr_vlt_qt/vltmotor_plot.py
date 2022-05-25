
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from .io import find_ui
from pydevmgr_core import NodeVar
from .elt_device_ctrl import EltDeviceCtrl
from pydevmgr_core_qt import record_widget_factory, BaseUiLinker
from pydevmgr_core.nodes import Time , DequeList
from pydantic import Field
import pyqtgraph as pg
import numpy as np 
from enum import IntEnum

#####
# Define all the data used at fron-end 
# The NodeVar annotation indicate that the data will be taken from a device node see `pydevmgr.DataLink`


# create a node returning the unix  time 
time = Time('time')


plot_nodes = [time, "pos_actual", "pos_error", "vel_actual"]

class MotorPlotStatData(EltDeviceCtrl.Data.StatData):
    # DeviceStatData contain state, substate, error code and txt information 
    # Add here all NodeVar needed for the motor GUI   
    
    pos_actual: NodeVar[float] = 0.0
    pos_error: NodeVar[float]  = 0.0
    plot_data: NodeVar[list] = Field([], node=DequeList.prop('plot_data' , nodes=plot_nodes, trigger_index=-1))


###
# Example of use:
#  data = MotorCtrlData()
#  dl = DataLink(motor, data)
#  dl.update() # update data from server(s)
#  print(data.stat.pos_actual, data.stat.pos_error) 
class MotorPlotData(EltDeviceCtrl.Data):
    StatData = MotorPlotStatData
    stat: StatData = StatData()


# We create a widget holding the two plots 
class MotorPlotWidget(QWidget):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
                
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # plots
        g_layout = QHBoxLayout()
        plots = {
          'pos' :       pg.PlotWidget(title='Position'), 
          'pos_error' : pg.PlotWidget(title='Error'), 
        }
        g_layout.addWidget(plots['pos'])
        g_layout.addWidget(plots['pos_error'])        
        layout.addLayout(g_layout)
        
        # a Clear button 
        clear_button = QPushButton()
        clear_button.setText('Clear')
        layout.addWidget(clear_button)
        
        self.clear_button = clear_button
        self.plots = plots





    
class MotorPlot(BaseUiLinker):
    # A widget constructor for default widget 
    Widget = MotorPlotWidget
    # A data constructor 
    Data = MotorPlotData
    
    # Basicaly 3 methods needs to be implemented 
    # - .init_vars() :  build the variable handler function to their type and widget
    # - .update(data) :   update widget with new data 
    # - .connect_device(device, data) : this is where commands has to be connected to widget buttons etc...
    start_time = None 
    def init_vars(self):
        super().init_vars()
        self.outputs.plots = self.widget.plots

    def update(self, data: MotorPlotData) -> None:
        """ Update the widget (the plots in our case) """
        plotdata = np.asarray(data.stat.plot_data)
        
        if len(plotdata):
            if self.start_time is None:
                self.start_time = min(plotdata[:,0])
                
            p = self.outputs.plots['pos']
            p.clear()        
            p.plot(plotdata[:,0]- self.start_time, plotdata[:,1])
            
            p = self.outputs.plots['pos_error']
            p.clear()        
            p.plot(plotdata[:,0]- self.start_time, plotdata[:,2])
 
    
      
    def connect_device(self, device, data):

        def clear_plotdata():
            self.start_time = None
            data.stat.plotdata.clear()
            self.outputs.plots['pos'].clear()
            self.outputs.plots['pos_error'].clear()
        
         # we could also do self.widget.clear_button.clicked.connect(clear_plotdata)
         # but the actions object allow to collect all widget connection and unlink them properly 
         # when the window is closed for instance
        self.actions.add(clear_plotdata).connect_button(self.widget.clear_button)           


record_widget_factory("plot", "Motor", MotorPlot)

