# Getting variables to be shared between modules can be difficult.
# This class exists to that modules from r.py can talk to modules in the rp_ptpython package.
# Essentially, this class is th middle-man. The other modules will both read and write to this module.
globa=[]
last_assignable_comm=None
pseudo_terminal_level=0
rp_evaluator=lambda x:None
current_input_text=""
rp_pt_VARS=""
python_input_buffers={}# str ⟶ str
rp_evaluator_mem=None
buffy_the_buffer_buffalo=None# Set by key bindings and read by layout
parenthesized_line=""
try_eval_mem_text=""