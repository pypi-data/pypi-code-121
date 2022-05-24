import os
import glob
import shutil
import sys
import subprocess
from unitgrade_private.autolab.autolab import format_autolab_json
from unitgrade_private.docker_helpers import student_token_file_runner
from unitgrade_private import load_token
import time
import unitgrade_private

verbose = False
tag = "[driver_python.py]"

if not verbose:
    print("="*10)
    print(tag, "Starting unitgrade evaluation...")
import unitgrade
print(tag, "Unitgrade version", unitgrade.version.__version__)
print(tag, "Unitgrade-devel version", unitgrade_private.version.__version__)


sys.stderr = sys.stdout
wdir = os.getcwd()

def pfiles():
    print("> Files in dir:")
    for f in glob.glob(wdir + "/*"):
        print(f)
    print("---")

handin_filename = "{{handin_filename}}"
student_token_file = '{{handin_filename if student_should_upload_token else student_token_src_filename}}'
instructor_grade_script = '{{instructor_grade_file}}'
grade_file_relative_destination = "{{grade_file_relative_destination}}"
host_tmp_dir = wdir + "/tmp"
homework_file = "{{homework_file}}"
# homework_file = "{{homework_file}}"
student_should_upload_token = {{student_should_upload_token}} # Add these from template.

if not verbose:
    pfiles()
    print(f"{host_tmp_dir=}")
    print(f"{student_token_file=}")
    print(f"{instructor_grade_script=}")



command, host_tmp_dir, token = student_token_file_runner(host_tmp_dir, student_token_file, instructor_grade_script, grade_file_relative_destination)
# Alternatively. Unzip the .token file of the student (true version). Overwrite the .py file with the one uploaded, then
# run the stuff.
if not student_should_upload_token:
    """ Add the student homework to the right location. """
    print("Moving from", os.path.basename(handin_filename), "to", handin_filename)
    print("file exists?", os.path.isfile(os.path.basename(handin_filename)))
    shutil.move(os.path.basename(handin_filename), host_tmp_dir + "/" + handin_filename)

command = f"cd tmp && {command} --noprogress --autolab"

def rcom(cm):
    rs = subprocess.run(cm, capture_output=True, text=True, shell=True)
    print(rs.stdout)
    if len(rs.stderr) > 0:
        print(tag, "There were errors in executing the file:")
        print(rs.stderr)

start = time.time()
rcom(command)
ls = glob.glob(token)
f = ls[0]
results, _ = load_token(ls[0])

if verbose:
    print(f"{token=}")
    print(results['total'])

format_autolab_json(results)

# if os.path.exists(host_tmp_dir):
#     shutil.rmtree(host_tmp_dir)
# with io.BytesIO(sources['zipfile']) as zb:
#     with zipfile.ZipFile(zb) as zip:
#         zip.extractall(host_tmp_dir
# print("="*10)
# print('{"scores": {"Correctness": 100,  "Problem 1": 4}}')
## Format the scores here.

# sc = [('Total', results['total'][0])] + [(q['title'], q['obtained']) for k, q in results['details'].items()]
# ss = ", ".join([f'"{t}": {s}' for t, s in sc])
# scores = '{"scores": {' + ss + '}}'
# print('{"_presentation": "semantic"}')
# print(scores)

