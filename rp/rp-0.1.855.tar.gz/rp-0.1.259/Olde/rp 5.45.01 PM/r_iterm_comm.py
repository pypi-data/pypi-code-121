# Getting variables to be shared between modules can be difficult.
# This class exists to that modules from r.py can talk to modules in the rp_ptpython package.
# Essentially, this class is th middle-man. The other modules will both read and write to this module.
globa=[]
last_assignable_comm=None
pseudo_terminal_level=0
realtime_display_string="oijijoijo"
rp_evaluator=lambda x:None
rp_evaluator_mem=None
current_input_text=""
rp_VARS_display=""
python_input_buffers={}