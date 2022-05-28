

import os

guistate = os.environ.get("DLClight", default="False")

# if module is executed directly (i.e. `python -m openlabcluster.__init__`) launch straight into the GUI
if guistate == "False":  # or not guistate:
    print("Starting GUI...")
    import openlabcluster

    openlabcluster.launch_dlc()
else:
    print("You are in DLClight mode, GUI cannot be started.")
