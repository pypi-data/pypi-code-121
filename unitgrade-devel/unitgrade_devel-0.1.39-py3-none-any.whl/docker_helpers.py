import os
import glob
import shutil
import time
import zipfile
import io
import subprocess
import urllib.request

def download_docker_images(destination=None):
    if destination is None:
        destination = os.getcwd()
    if not os.path.exists(destination):
        os.makedirs(destination)

    print('Beginning file download with urllib2...')
    url = 'https://gitlab.compute.dtu.dk/tuhe/unitgrade_private/-/archive/master/unitgrade_private-master.zip?path=docker_images'
    result, headers = urllib.request.urlretrieve(url)

    ex = result +"_extract"
    zf = zipfile.ZipFile(result)
    zf.extractall(path=ex)
    dockers = [f for f in zf.namelist() if f[-1] == "/" and len( [s for s in f if s == "/"] ) == 3]
    for f in dockers: # zf.namelist():
        tmp_dir = ex + "/" + f
        if os.path.isdir(tmp_dir):
            dest = destination +"/"+os.path.basename(tmp_dir[:-1])

            if os.path.isdir(dest):
                print("> Destination for docker image", dest, "exists. Skipping download.")
            else:
                print("> Extracting docker image", os.path.basename(f[:-1]), "to", dest)
                shutil.copytree(tmp_dir, dest)


def compile_docker_image(Dockerfile, tag=None, no_cache=False):
    assert os.path.isfile(Dockerfile)
    base = os.path.dirname(Dockerfile)
    if tag == None:
        tag = os.path.basename(base)
    os.system(f"cd {base} && docker build {'--no-cache' if no_cache else ''} --tag {tag} .")
    return tag


def student_token_file_runner(host_tmp_dir, student_token_file, instructor_grade_script, grade_file_relative_destination):
    """
    This code is used to run student unitgrade tests (i.e., a .token file).
    Use by autolab code.

    It accepts a student .token file which is extracted, the 'correct' instructor grade script is copied
    into it, and it is then run.

    :param Dockerfile_location:
    :param host_tmp_dir:
    :param student_token_file:
    :param ReportClass:
    :param instructor_grade_script:
    :return:
    """
    assert os.path.exists(student_token_file)
    assert os.path.exists(instructor_grade_script)
    from unitgrade_private import load_token
    start = time.time()
    results, _ = load_token(student_token_file)
    sources = results['sources'][0]
    with io.BytesIO(sources['zipfile']) as zb:
        with zipfile.ZipFile(zb) as zip:
            zip.extractall(host_tmp_dir)

    # Done extracting the zip file! Now time to move the (good) report test class into the location.
    gscript = instructor_grade_script
    print(f"{sources['report_relative_location']=}")
    print(f"{sources['name']=}")
    print("Now in docker_helpers.py")
    print(f'{gscript=}')
    print(f'{instructor_grade_script=}')
    gscript_destination = host_tmp_dir + "/" + grade_file_relative_destination
    print(f'{gscript_destination=}')
    shutil.copy(gscript, gscript_destination)
    # Now everything appears very close to being set up and ready to roll!.
    d = os.path.normpath(grade_file_relative_destination).split(os.sep)
    d = d[:-1] + [os.path.basename(instructor_grade_script)[:-3]]
    pycom = ".".join(d)
    """
    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/app python-docker python3 -m cs202courseware.ug2report1_grade
    """
    pycom = "python3 -m " + pycom
    print(f"{pycom=}")
    token_location = host_tmp_dir + "/" + os.path.dirname( grade_file_relative_destination ) + "/*.token"
    elapsed = time.time() - start
    # print("Elapsed time is", elapsed)
    return pycom, host_tmp_dir, token_location


def docker_run_token_file(Dockerfile_location, host_tmp_dir, student_token_file, tag=None, instructor_grade_script=None,
                          fix_user=None,
                          # grade_script_relative_destination_dir=None, # The relative location relative to the top-dir containing the package. Example: irlc/project1
                          xvfb=True):
    """
    xvfb: Control whether to use X-windows. Works on linux. This seems like a good idea when using e.g. gym.

    This thingy works:

    To build the image, run:
    docker build --tag python-docker .

    To run the app run:

    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/app python-docker > output.log

    """
    Dockerfile_location = Dockerfile_location.replace("\\", "/")
    host_tmp_dir = host_tmp_dir.replace("\\", "/")
    student_token_file = student_token_file.replace("\\", "/")

    # A bunch of tests. This is going to be great!
    Dockerfile_location = os.path.abspath(Dockerfile_location)
    assert os.path.exists(Dockerfile_location)

    start = time.time()

    if fix_user is None:
        fix_user = os.name != 'nt'  # On Linux, this should probably be true to avoid problem with edit-rights of docker-created files.

    # with open(student_token_file, 'rb') as f:
    #     results = pickle.load(f)
    from unitgrade_private import load_token
    results, _ = load_token(student_token_file)

    sources = results['sources'][0]

    if os.path.exists(host_tmp_dir):
        shutil.rmtree(host_tmp_dir)

    with io.BytesIO(sources['zipfile']) as zb:
        with zipfile.ZipFile(zb) as zip:
            zip.extractall(host_tmp_dir)
    # Done extracting the zip file! Now time to move the (good) report test class into the location.
    gscript = instructor_grade_script

    # if grade_script_relative_destination_dir is None:
    #     student_grade_script = host_tmp_dir + "/" + sources['report_relative_location']
    # else:
    #     student_grade_script = host_tmp_dir + "/" + grade_script_relative_destination_dir
    # Get relative location from first line of the grade script.
    with open(instructor_grade_script, 'r') as f:
        student_grade_script_dir = os.path.dirname( host_tmp_dir + "/" + f.read().splitlines()[0][1:].strip() )
    print("student_grade_script", student_grade_script_dir)



    student_grade_script_dir = student_grade_script_dir.replace("\\", "/")
    instructor_grade_script = student_grade_script_dir + "/"+os.path.basename(gscript)
    shutil.copy(gscript, instructor_grade_script)

    """
    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/home python-docker python3 -m cs202courseware.ug2report1_grade
    """
    if tag is None:
        dockname = os.path.basename( os.path.dirname(Dockerfile_location) )
    else:
        dockname = tag

    tmp_grade_file =  sources['name'] + "/" + sources['report_relative_location']
    tmp_grade_file = tmp_grade_file.replace("\\", "/")

    # pycom = ".".join( sources['report_module_specification'][:-1] + [os.path.basename(gscript)[:-3],] )
    pycom = ".".join(os.path.relpath(instructor_grade_script, host_tmp_dir)[:-3].split("/"))
    pycom = "python3 -m " + pycom

    if fix_user:
        user_cmd = ' --user "$(id -u):$(id -g)" '
    else:
        user_cmd = ''

    if xvfb:
        user_cmd = " -e DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix " + user_cmd

    tmp_path = os.path.abspath(host_tmp_dir).replace("\\", "/")
    dcom = f"docker run {user_cmd} -v {tmp_path}:/home {dockname} {pycom}"
    cdcom = f"cd {os.path.dirname(Dockerfile_location)}"
    fcom = f"{cdcom}  && {dcom}"
    print("> Running docker command")
    print(fcom)
    init = time.time() - start
    # thtools.execute_command(fcom.split())
    out = subprocess.check_output(fcom, shell=True).decode("utf-8")
    host_tmp_dir +"/" + os.path.dirname(tmp_grade_file) + "/"
    tokens = glob.glob( os.path.dirname(instructor_grade_script) + "/*.token" )
    for t in tokens:
        print("Source image produced token", t)
    elapsed = time.time() - start
    print("Elapsed time is", elapsed, f"({init=} seconds)")
    if len(tokens) != 1:
        print("Wrong number of tokens produced:", len(tokens))
        print(out)
    return tokens[0]
