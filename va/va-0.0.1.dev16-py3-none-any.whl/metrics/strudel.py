import subprocess
import sys
import os
from distutils.spawn import find_executable
import timeit
import time


def create_folder(output_path):
    """
        create strudel output folder inside va directory

    :return: model related path of strudel folder
    """

    fullname = '{}'.format(output_path)

    if not os.path.isdir(fullname):
        os.mkdir(fullname, mode=0o777)
    else:
        print('{} is exist'.format(fullname))


def run_monitored_job(command, work_dir):
    """
    Submits a job to the queue system and waits until it finishes
    :param command: Bsub command
    :param work_dir: directory where the job will be run
    """
    command = command.split()
    # Submit job to the queue ang get the job id
    out = str(subprocess.check_output(command, cwd=work_dir))
    job_id = out.split('<')[1].split('>')[0]
    while True:
        # Check the job status every 20 seconds
        try:
            out1 = str(subprocess.check_output(["bjobs", "-a", "-noheader", job_id]))
            status = out1.split()[2]
        except subprocess.CalledProcessError:
            continue
        if status == 'DONE' or status == 'EXIT':
            break
        elif 'not found' in out1:
            break
        else:
            time.sleep(20)


def run_strudel(full_modelpath, full_mappath, motif_libpath, output_path, platform=None):
    """
        full_modelpath: full path of the model with name
        full_mappath: full path of the map with name
        motif_libpath: full path of the motif lib for its resolution
        output_path: output directory
    :return:
    """

    start = timeit.default_timer()
    create_folder(output_path)
    num_processors = int(os.cpu_count() / 2)
    bsub_bin = find_executable('bsub')
    strudel_cmd = 'strudel_mapMotifValidation.py -p {} -m {} -l {} -o {} -np {}'.format(full_modelpath,
                                                                                            full_mappath, motif_libpath,
                                                                                            output_path, num_processors)
    if platform == 'emdb' and bsub_bin:
        strudel_cmd = 'bsub -e {}/strudel_stderr.txt -o {}/strudel_stdout.txt -n 8 -M 26G ' \
                      'strudel_mapMotifValidation.py -p {} -m {} -l {} -o {} -np 8 -log ' \
                      '{}/strudel.log -r -rs'.format(output_path,
                                              output_path,
                                              full_modelpath,
                                              full_mappath,
                                              motif_libpath,
                                              output_path, output_path)
    errlist = []
    print(strudel_cmd)
    try:
        # run_monitored_job(strudel_cmd, output_path)
        # subprocess.check_call(strudel_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
        #                                 cwd=output_path)
        process = subprocess.Popen(strudel_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                                   cwd=output_path)
        # out = subprocess.check_output(strudel_cmd.split(), stderr=subprocess.STDOUT, shell=True, cwd=output_path)
        # print(out)

        output = process.communicate('n\n')[0]
        errstrudelscore = 'error'
        if sys.version_info[0] >= 3:
            for item in output.decode('utf-8').split('\n'):
                print(item)
                if errstrudelscore in item.lower():
                    errline = item.strip()
                    errlist.append(errline)
                    assert errstrudelscore not in output.decode('utf-8'), errline

        else:
            for item in output.split('\n'):
                print(item)
                if errstrudelscore in item.lower():
                    errline = item.strip()
                    errlist.append(errline)
                    assert errstrudelscore not in output.decode('utf-8'), errline

        end = timeit.default_timer()
        print('Strudel time: %s' % (end - start))
        print('------------------------------------')
    except:
        end = timeit.default_timer()
        err = 'Strudel error: {}'.format(sys.exc_info()[1])
        errlist.append(err)
        sys.stderr.write(err + '\n')
        print('Strudel time: %s' % (end - start))
        print('------------------------------------')


    # If needed here will do the post processing of strudel score
    # posts_trudlescore()

    return errlist


def strudel_tojson(self):
    """
        Process strudel score related files

    :return:
    """

    pass
