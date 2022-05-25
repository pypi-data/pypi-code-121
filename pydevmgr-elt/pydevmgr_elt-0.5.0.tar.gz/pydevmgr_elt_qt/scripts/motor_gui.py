
from pydevmgr_elt import Motor, Downloader, NodeVar,  open_elt_device
from pydevmgr_core.nodes import Time, DequeList
from pydevmgr_elt_qt import MotorCtrl, MotorCfg

from pydevmgr_core_qt import BaseUiLinker
from pydevmgr_core import io

from pydantic import BaseModel, Field
from PyQt5 import  QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QMainWindow, QAction, qApp, QMenu
import numpy as np

import pyqtgraph as pg
import sys


usage = "pydevmgr_motor_gui relative/path/to/motor.yml"


#  ____    _  _____  _      __  __  ___  ____  _____ _     
# |  _ \  / \|_   _|/ \    |  \/  |/ _ \|  _ \| ____| |    
# | | | |/ _ \ | | / _ \   | |\/| | | | | | | |  _| | |    
# | |_| / ___ \| |/ ___ \  | |  | | |_| | |_| | |___| |___ 
# |____/_/   \_\_/_/   \_\ |_|  |_|\___/|____/|_____|_____|
############################################################
                                                         

# create a node returning the unix  time 
time = Time('time')


class MotorPlotStatData(BaseModel):
    """ a Data Model defining what we need for the plot widget """
    substate_txt : NodeVar[int] = 0
    plotdata: NodeVar[list] = Field([], node=DequeList.prop('plotdata', [time, 'pos_actual', 'pos_error', 'is_moving'], maxlen=100, trigger_index=-1)) 
    
class MotorPlotData(BaseModel):
    StatData = MotorPlotStatData
    stat: StatData = StatData()

#  ____  _     ___ _____  __        _____ ____   ____ _____ _____ 
# |  _ \| |   / _ \_   _| \ \      / /_ _|  _ \ / ___| ____|_   _|
# | |_) | |  | | | || |    \ \ /\ / / | || | | | |  _|  _|   | |  
# |  __/| |__| |_| || |     \ V  V /  | || |_| | |_| | |___  | |  
# |_|   |_____\___/ |_|      \_/\_/  |___|____/ \____|_____| |_|  
##################################################################
    
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
    Data = MotorPlotData   # constructor for Data 
    Widget = MotorPlotWidget # constructor for the default Widget 
    start_time = None
    def init_vars(self):
        # the goal of init vars is to collect, grap the outputs and inputs information 
        # of the widget 
        self.outputs.plots = self.widget.plots
        
    def update(self, data: MotorPlotData) -> None:
        """ Update the widget (the plots in our case) """
        plotdata = np.asarray(data.stat.plotdata)
        
        if len(plotdata):
            if self.start_time is None:
                self.start_time = min(plotdata[:,0])
                
            p = self.outputs.plots['pos']
            p.clear()        
            p.plot(plotdata[:,0]- self.start_time, plotdata[:,1])
            
            p = self.outputs.plots['pos_error']
            p.clear()        
            p.plot(plotdata[:,0]- self.start_time, plotdata[:,2])
    
    # a connect_device is only needed when one have to set inputs action 
    # like button .. etc ... in this case the only action is clear (which is actually not related 
    #   to the device but the data)
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
        
    
#   ____ _   _ ___ 
#  / ___| | | |_ _|
# | |  _| | | || | 
# | |_| | |_| || | 
#  \____|\___/|___|
#################### 

def app_main(motor):
    """ main gui window accepting a motor device instance 
    
    the motor shall be connected
    """
    
    downloader = Downloader()
    app = QApplication(sys.argv)
    
    main = QMainWindow()
    
    main_widget = QWidget()
    main.setCentralWidget(main_widget)
    
    main_layout = QHBoxLayout()
    main_widget.setLayout(main_layout)
    
    
    # Initialize tab screen
    tabs = QTabWidget()
    tab_ctrl   = QWidget()
    tab_config = QWidget()
    #tabs.resize(300,200)
        
    # Add tabs
    tabs.addTab(tab_ctrl  ,"Control")
    tabs.addTab(tab_config,"Config")
    
    
    layout_ctrl = QVBoxLayout()
    tab_ctrl.setLayout(layout_ctrl)
    
    layout_config = QVBoxLayout()
    tab_config.setLayout(layout_config)
    
    # Build a MotorCtrl and connect it to the downloader and motor         
    motor_ctrl = MotorCtrl().connect(downloader, motor)
    layout_ctrl.addWidget(motor_ctrl.widget)
    
    motor_plot = MotorPlot().connect(downloader, motor)
    layout_ctrl.addWidget(motor_plot.widget)
    
    motor_cfg = MotorCfg().connect(downloader, motor)
    layout_config.addWidget(motor_cfg.widget)
    
    #main_layout.addWidget(left_widget)
    main_layout.addWidget(tabs)
    
    #menuBar = main.menuBar()
    fileMenu = QMenu("&File", main)
    
    exitAct = QAction('&Exit', main)
    exitAct.setShortcut('Ctrl+Q')
    exitAct.setStatusTip('Exit application')
    exitAct.triggered.connect(qApp.quit)
    
    fileMenu.addAction(exitAct)
    main.show()
            
    # To refresh the gui we need a timer and connect the download method 
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    # 10Hz GUI is nice
    timer.start(100)
        
    return app.exec_()

motor = None
def main():
    global motor 
    if len(sys.argv)<2:
        print(usage)
        print("\nManager file found in $CFGPATH:")
        for f,r in io.explore_config("Motor"):
            print(f"    {f}    inside {r}")
        return 1
    
    motor = open_elt_device(sys.argv[1])
    motor.connect()
    
    try:
        exit_code = app_main(motor)
    except Exception as e:
        if motor:        
            motor.disconnect()
        raise e
    else:
        motor.disconnect()
        sys.exit(exit_code)
    
        
if __name__ == "__main__":
    main()
