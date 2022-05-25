from pydevmgr_core_qt import ManagerLinker
from PyQt5.QtWidgets import  QMenu, QAction, QLabel
from typing import Optional, List
from pydevmgr_core import NodeVar


class EltManagerWidget(ManagerLinker.Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actionMenu = QMenu("&Action", self)
        self.menuBar.addMenu(self.actionMenu)
        self.state = QLabel()
        self.top_layout.addWidget(self.state)
        self.rpc_feedback = QLabel()
        self.top_layout.addWidget(self.rpc_feedback)
        
        self.state.setMaximumHeight(30)
        self.rpc_feedback.setMaximumHeight(30)

    def list_devices(self, manager):
        # overwrite the function so it returns oonly the Elt Manager devices defined inside the devices property
        return manager.devices
 
class EltManagerStatData(ManagerLinker.Data):
    state: NodeVar[int] = 0
    state_txt: NodeVar[str] =  ""
    state_group: NodeVar[int] = 0
   
class EltManagerData(ManagerLinker.Data):
     StatData = EltManagerStatData 
     stat: StatData = StatData()


class EltManagerLinker(ManagerLinker):
    Widget = EltManagerWidget
    Data = EltManagerData 
    class Config(ManagerLinker.Config):
        alt_dev_type: Optional[List[str]] = ['Elt'] # not found device widget will fall back to the Elt Base

    def init_vars(self):
        # these shall get stat data
        self.outputs.state    = self.outputs.Code(self.widget.state )
        self.outputs.rpc_feedback = self.outputs.Feedback(self.widget.rpc_feedback)           
                        
    def feedback(self, er, msg=''):
        self.outputs.rpc_feedback.set((er, msg))       
        
    def update(self, data) -> None:
        """ update the ui from the data structure """
        stat = data.stat
                                
        self.outputs.state.set( (stat.state, stat.state_txt, stat.state_group) )
         

    def setup_ui(self, manager, data):
        super().setup_ui(manager, data)
        
        action_list = [
         ("INIT",   manager.init,   []), 
         ("ENABLE", manager.enable, []),
         ("DISABLE",manager.disable,[]),
         ("RESET",  manager.reset,  []), 
         ("---",  None,  []),
         ("CONFIGURE", manager.configure, []),
         ("---",  None,  []),
         ("CHECK ALL", manager.unignore_all, []),
         ("UNCHECK ALL", manager.ignore_all, []),
        ]
        for name,func,inputs in action_list:
            if name == "---":
                self.widget.actionMenu.addSeparator()
                continue
            act = QAction(name, self.widget)
            self.widget.actionMenu.addAction(act)
            self.actions.add(func, inputs, feedback=self.feedback).connect_action(act)
        



