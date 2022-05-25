from PyQt5.QtWidgets import QLayout, QBoxLayout, QHBoxLayout,  QGridLayout, QMainWindow, QVBoxLayout, QWidget, QMenu, QAction, qApp
from PyQt5 import QtCore

from .base import WidgetControl
from .base import get_widget_factory, BaseUiLinker, WidgetFactory
from typing import List, Tuple, Optional
from pydevmgr_core import BaseDevice, DataLink
from .base_view import DevicesWidgetLinker



class ConfigManager(DevicesWidgetLinker.Config):
    pass


class ManagerWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        top = QWidget()
        bottom = QWidget()
        left = QWidget()
        right = QWidget()
        body = QWidget()
         
        
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        body_layout = QVBoxLayout()


        top.setLayout(top_layout)
        bottom.setLayout(bottom_layout)
        left.setLayout(left_layout)
        right.setLayout(right_layout)
        body.setLayout(body_layout)

        
        main_layout = QGridLayout()
        main = QWidget()
        main.setLayout(main_layout)
        
        main_layout.addWidget( top, 0, 0, 1, 3 )
        main_layout.addWidget( left, 1, 0 )
        main_layout.addWidget( bottom, 2, 0, 1, 3 )
        main_layout.addWidget( right, 1, 2)
        main_layout.addWidget( body, 1, 1)


        
        devices =  DevicesWidgetLinker.Widget()
        body_layout.addWidget(devices)
        
            

        self.setCentralWidget(main)
        
        # main_layout = QVBoxLayout()
        # self.setLayout(main_layout)
        # main_layout.addWidget(self.body)
        
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        
        self.resize(750, 1000)
                
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        fileMenu.addAction(exitAct)
        
        self.viewMenu = QMenu("&View", self)
        menuBar.addMenu(self.viewMenu)
        
        self.menuBar = menuBar
        
        
        self.top = top 
        self.right = right
        self.left = left 
        self.bottom = bottom 
        self.body = body 
        self.main = main 
        self.devices = devices

        self.top_layout = top_layout 
        self.right_layout = right_layout
        self.left_layout = left_layout 
        self.bottom_layout = bottom_layout 
        self.body_layout = body_layout 
        self.main_layout = main_layout 





class ManagerLinker(BaseUiLinker):
    Config = ConfigManager
    Widget =  ManagerWidget
    _widget_view_ctrl = None
    _widget_view = None
    
    class Data(DevicesWidgetLinker.Data):
        pass
    
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    def connect(self, downloader, manager, data = None):
        if data is None:
            data = self.new_data()
        
        self.setup_ui(manager, data)
        
        self._multi_view_ctrl = WidgetControl(
                self._multi_view, 
                downloader, 
                self.list_devices(manager), 
                data
            )
        
        self._multi_view._link(downloader)
        self._link(downloader, DataLink(manager, data), data)
        return self._multi_view_ctrl
    
    def view_changed(self, view_name):
        if self._multi_view_ctrl:
            self._multi_view_ctrl.data.current_view = view_name
            self._multi_view_ctrl.disable()
            self._multi_view_ctrl.enable()
    
    def list_devices(self, manager):
        return list(manager.find( BaseDevice ))

    
    def setup_ui(self, manager, data):
        
        multi_view = DevicesWidgetLinker(widget=self.widget.devices, config=self.config)
        
        multi_view.setup_ui(self.list_devices(manager), data)
        
        self._multi_view = multi_view
                        
        for view_name in self.config.views:
            viewAct = QAction(view_name, self.widget)
            self.widget.viewMenu.addAction(viewAct)

            self.actions.add(self.view_changed, [view_name], feedback=self.feedback).connect_action(viewAct)
                 

    



