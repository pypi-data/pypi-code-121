import os
import subprocess

def run():
    subprocess.Popen(['pythonw', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'launch_script.py')]).wait()

if __name__ == '__main__':
    run()
