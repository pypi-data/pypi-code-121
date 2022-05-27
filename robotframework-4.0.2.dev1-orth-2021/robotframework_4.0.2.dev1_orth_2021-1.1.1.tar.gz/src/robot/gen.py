#!/usr/bin/env python

USAGE = '''
Robot Framework is open source software released under Apache License 2.0. Its
copyrights are owned and development supported by Nokia Solutions and Networks.
For more information about the framework see http://robotframework.org/.

Options
=======
 -d --outputdir dir       Where to create output files. The default is the
                          directory where tests are run from and the given path
 -L --loglevel level      Threshold level for logging. Available levels: TRACE,
                          DEBUG, INFO (default), WARN, NONE (no logging). Use
                          syntax `LOGLEVEL:DEFAULT` to define the default
                          visible log level in log files.
                          Examples: --loglevel DEBUG
                                    --loglevel DEBUG:INFO
 -h -? --help             Print usage instructions.
 --version                Print version information.
'''
import sys
import os
import shutil

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot.conf import RobotSettings
from robot.utils import Application, unic
from robot.parsing import get_model
from robot.output import LOGGER
from robot.running.builder.orthogonalizers import OrthogonalTestGenerator


class OrthGen(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(1,),
                             env_options='ORTHGEN_OPTIONS', logger=LOGGER)
        self.settings = None
        self.output_dir = None
        self.process_curdir = True


    def _get_curdir(self, source):
        if not self.process_curdir:
            return None
        return os.path.dirname(source).replace('\\', '\\\\')

    def _get_source(self, source):
        return source

    def main(self, datasources, **options):
        global every_file, out_dir
        datasources = "".join(datasources)
        print("需要正交的目录或文件为:" + datasources)

        settings = RobotSettings(options)

        output_dir = settings['OutputDir']
        print("正交后文件输出目录为:" + output_dir)
        output_dir_name = output_dir.split("/")[len(output_dir.split("/")) - 1]
        LOGGER.info('Settings:\n%s' % unic(self.settings))

        if(os.path.isdir(datasources)):
            # os.system(f'cp -R {datasources} {output_dir}')
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                os.makedirs(output_dir)
            else:
                os.makedirs(output_dir)

            scanAll = ScanFile(datasources)
            all_files = scanAll.scan_files()
            for every_file in all_files:
                external_dir_name = datasources.split("/")[len(datasources.split("/")) - 1]
                file_name = every_file.split("/")[len(every_file.split("/")) - 1]
                other_path = every_file.replace(datasources, "")
                other_path_no_filename = other_path[::-1].replace(file_name[::-1], ""[::-1],1)[::-1]
                # out_dir = output_dir + "/" + external_dir_name + other_path
                out_dir = output_dir + "/" + external_dir_name + other_path_no_filename
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                shutil.copy(every_file, out_dir)

            scan_postfix = ScanFile(datasources,postfix=".robot")
            files = scan_postfix.scan_files()
            for file in files:
                # print(file)
                if output_dir_name in str(file):
                    continue
                print(file + " 文件正交中...")

                external_dir_name = datasources.split("/")[len(datasources.split("/"))-1]
                other_path = file.replace(datasources,"")
                out_dir = output_dir + "/" + external_dir_name + other_path

                size = os.path.getsize(file)
                if size == 0:
                    continue

                model = get_model(file, data_only=True,
                                  curdir=self._get_curdir(file))
                OrthogonalTestGenerator(out_dir, None, model)
                print(file + " 文件正交结束...")
        else:

            print(datasources + " 文件正交中...")

            datasourcesFile=datasources.split("/")[len(datasources.split("/"))-1]

            model = get_model(datasources, data_only=True,
                              curdir=self._get_curdir(output_dir + "/" + datasourcesFile))
            checkModel = "Testcase" in  str(model.sections) and "Orthogonal" in str(model.sections)

            if checkModel:
                print("The corrent model was not obtained.Please check the content format of the file.")
                sys.exit()
            OrthogonalTestGenerator(output_dir, datasourcesFile, model)

            print(datasources + " 文件正交结束...")

    def _get_curdir(self, source):
        if not self.process_curdir:
            return None
        return os.path.dirname(source).replace('\\', '\\\\')

    def validate(self, options, arguments):
        return self._filter_options_without_value(options), arguments

    def _filter_options_without_value(self, options):   #FILTER NULL VALUE
        # return dict((name, value) for name, value in options.items()
        return dict((name, value) for name, value in list(options.items())
                    if value not in (None, []))


class ScanFile(object):
    def __init__(self,directory,postfix=None):
        self.directory = directory
        self.postfix = postfix

    def scan_files(self):
        files_list = []
        for dirpath,dirnames,filenames in os.walk(self.directory):
            for special_file in filenames:
                if self.postfix:
                    if special_file.endswith(self.postfix):
                        files_list.append(os.path.join(dirpath,special_file))
                else:
                    files_list.append(os.path.join(dirpath,special_file))
        return files_list

def run_gen_cli(arguments):
    """Command line execution entry point for running tests.

    :param arguments: Command line arguments as a list of strings.

    For programmatic usage the :func:`run` function is typically better. It has
    a better API for that usage and does not call :func:`sys.exit` like this
    function.

    Example::

        from robot import run_cli

        run_cli(['--include', 'tag', 'path/to/tests.html'])
    """
    OrthGen().execute_cli(arguments)

if __name__ == '__main__':
    run_gen_cli(sys.argv[1:])
