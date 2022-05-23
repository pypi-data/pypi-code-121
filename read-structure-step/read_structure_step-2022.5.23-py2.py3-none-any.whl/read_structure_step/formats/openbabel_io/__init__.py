from read_structure_step.formats.registries import register_format_checker  # noqa: F401
from . import obabel  # noqa: F401

# keywords = ['V2000', 'V3000']

# @register_format_checker('.sdf')
# def check_format(file_name):

#     with open(file_name, "r") as f:

#         data = f.read()

#         if any(keyword in data for keyword in keywords):
#             return True
#         else:
#             return False
