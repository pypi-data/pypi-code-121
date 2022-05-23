import os
import platform
import shutil
import stat


class FlutterScript(object):

    def __init__(self):
        self.isWindow = platform.system().lower() == 'windows'
        self.osTargetCommand = ''
        if (self.isWindow):
            self.osTargetCommand = 'cd'
        else:
            self.osTargetCommand = 'pwd'

    def readonly_handler(func, path, execinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def execFunc(self, scriptFile, moduleName):
        os.system(
            'git clone git@git.2dfire.net:app/flutter/tools/flutter-script.git')

        print('执行脚本：' + scriptFile)
        print('模块：' + moduleName)
        print('python3 flutter-script/{0} {1}'.format(scriptFile, moduleName))
        os.system(
            'python3 flutter-script/{0} {1}'.format(scriptFile, moduleName))
        if (self.isWindow):
            path = os.popen(self.osTargetCommand).read().split('\n')[0]
            path = path + "\\flutter-script"
            shutil.rmtree(path, ignore_errors=False,
                          onerror=self.readonly_handler)
        else:
            shutil.rmtree(r'flutter-script')
