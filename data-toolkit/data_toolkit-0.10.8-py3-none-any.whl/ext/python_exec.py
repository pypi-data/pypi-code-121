import pandas as pd
import swifter # ==0.289
import os, sys, io
import subprocess as sp

def execute(command: str, filt_cond: str, directory=''):
    '''
    Runs a python `command` on filenames that pass -f
    filt_cond: filter all files in in this directory and below by this expression.
    command: E.g.
    `dt py 'f"mv {x} real_A/ "' -f "real_A"`
    '''
    df = get_files_as_pd(directory)

    # import ipdb; ipdb.set_trace()

    target_files = pd.Series(filter(lambda x: filt_cond in x, df.full_path.values))
    target_fcn = lambda x: os.system(eval(command))
    target_files.swifter.apply(lambda x: target_fcn(x))


def get_files_as_pd(directory):
    '''
    directory: `str` of full_path

    Gets all files from recursive directories and returns this as
    a `DataFrame`
    '''
    # TODO: find a way to print STDOUT and STDERR as a print statement
    try:
        proc = str(sp.check_output(f'find {directory}* -type f',
                                    shell=True,stderr=sp.PIPE))[2:]
    except sp.CalledProcessError as e:
        print(f'Error {e} Possibly incorrect path.')
        raise AssertionError
    df = pd.DataFrame(str(proc).split('\\n')[:-1] )
    df.columns = ['full_path']

    level_paths = df.full_path.str.split('/',expand=True)
    df = pd.concat([df, level_paths], axis=1)
    return df

