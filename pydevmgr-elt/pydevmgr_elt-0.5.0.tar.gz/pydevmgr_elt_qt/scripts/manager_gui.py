#! /usr/bin/env python
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys, os
from pydevmgr_elt import Downloader, open_elt_manager
from pydevmgr_elt_qt  import EltManagerLinker
from pydevmgr_core_qt import io
from pydevmgr_core import io as pio
import yaml


usage = "pydevmgr_gui relative/path/to/manager.yml [path/to/manager_gui.yml]"

# if len(sys.argv)!=2:
#     print(usage)
#     sys.exit(1)


default_ui_cfg = """
ctrl: # all devices in more complete control widget 
    size: [800,500]
    setup:
        - device: "*"
          layout: ly_devices
          widget_kind: "ctrl"

line: # all devices in one line control widget 
    setup:
        - device: "*"
          layout: ly_devices
          widget_kind: "line"
"""


mgr = None
def app_main():
    global mgr
    ui_cfg = None 
    curent_view = None
    if len(sys.argv)<3: 
        file_body, _ = os.path.splitext(sys.argv[1])
        

        for ext in ('_ui.yml', 'ui.yaml'):
            try:
                ui_cfg = io.load_config(file_body+ext)
            except (IOError, ValueError):
                pass


    else:
        ui_cfg = io.load_config(sys.argv[2])
            
    if len(sys.argv)>3:
        current_view = sys.argv[3]

    if ui_cfg is None:
        ui_cfg = yaml.load(default_ui_cfg)
        
        
        
    mgr = open_elt_manager(sys.argv[1], '')
    
    mgr.connect()
    #mgr.configure() # configure through OPC-UA all the devices !!!!!!!
    
    downloader = Downloader()
    

    app = QApplication(sys.argv)
    
    linker = EltManagerLinker(config=ui_cfg)
    data = linker.new_data(current_view="main")

    
    ctrl = linker.connect(downloader, mgr, data)
        
    linker.widget.show()
    
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    
    timer.start(200)
    return app.exec_()

def main():
    global mgr
    exit_code = 1
    if len(sys.argv)<2:
        print(usage)
        print("\nManager file found in $CFGPATH:")
        for f,r in pio.explore_config("Manager"):
            print(f"    {f}    inside {r}")
        return 1
    
    try:
        exit_code = app_main()
    except Exception as e:
        if mgr:        
            mgr.disconnect()
        raise e
    else:
        mgr.disconnect()
        sys.exit(exit_code)

if __name__ == '__main__':
    main()

