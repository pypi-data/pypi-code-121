# coding=utf-8

import subprocess

from flutter_gen.core.command import Command


class RunCommand(Command):
    def __init__(self, document_path: str):
        super(RunCommand, self).__init__()
        if not document_path.startswith('/'):
            document_path = "/" + document_path
        self.document_path = document_path

    def run(self):
        applescript = '''
        tell application "Terminal"
            activate
            do script "cd '%s';flutter_gen watch" in front window
        end tell
        '''
        applescript = applescript % (self.document_path)
        args = [item for x in [
            ("-e", l.strip()) for l in applescript.split('\n') if l.strip() != ''] for item in x]
        proc = subprocess.Popen(["osascript"] + args, stdout=subprocess.PIPE)
        result = proc.stdout.read().strip()
        print(result)
