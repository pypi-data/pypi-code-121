import os
from unitgrade_private.version import __version__
from unitgrade_private.hidden_gather_upload import load_token, save_token
from unitgrade_private.plagiarism.mossit import unpack_sources_from_token
from unitgrade_private.hidden_create_files import setup_grade_file_report

# def cache_write(object, file_name, verbose=True):
#     assert False
#     dn = os.path.dirname(file_name)
#     if not os.path.exists(dn):
#         os.mkdir(dn)
#     if verbose: print("Writing cache...", file_name)
#     with open(file_name, 'wb', ) as f:
#         compress_pickle.dump(object, f, compression="lzma")
#     if verbose: print("Done!")
#
#
# def cache_exists(file_name):
#     assert False
#     return os.path.exists(file_name)
#
#
# def cache_read(file_name):
#     assert False
#     if os.path.exists(file_name):
#         with open(file_name, 'rb') as f:
#             return compress_pickle.load(f, compression="lzma")
#     else:
#         return None

