import os
from subprocess import PIPE, Popen
from platform import system, processor
import sys
import ctypes

STABLE_VERSION = "101.0.4951.41"

OS = system().lower()
PROCESSOR = processor().lower()

FILE = None
WINDOWS_FILE = "chromedriver_win32.zip"
MAC_FILE = "chromedriver_mac64.zip"
MAC_M1_FILE = "chromedriver_mac64_m1.zip"
LINUX_FILE = "chromedriver_linux64.zip"

if(OS == "windows"):
    FILE = WINDOWS_FILE
if(OS == "darwin"):
    FILE = MAC_FILE
if(OS == "darwin" and PROCESSOR == "arm"):
    FILE = MAC_M1_FILE
if(OS == "linux"):
    FILE = LINUX_FILE

if(FILE is None):
    print("OS not supported. Please report as issue at: https://github.com/tezz-io/selenium-chromedriver")
    exit(1)

LINK = f"https://chromedriver.storage.googleapis.com/{STABLE_VERSION}/{FILE}"
FILE_NAME = FILE.split(".")[0]
CURR_DIR = os.getcwd()

LINUX_OR_MAC_CMD = f"""
sudo rm -rf chromedriver.zip chromedriver /usr/bin/chromedriver 
curl {LINK} --output chromedriver.zip
unzip chromedriver.zip
sudo mv chromedriver /usr/bin/chromedriver
rm -rf chromedriver.zip chromedriver
"""

WINDOWS_CMD = f"""
Write-Output "Getting Ready for installing chromedriver..."
if (Test-Path {CURR_DIR}\\{FILE_NAME}) {{
    Remove-Item -Recurse {CURR_DIR}\\{FILE_NAME}
}}
if (Test-Path {CURR_DIR}\\{FILE}) {{
    Remove-Item {CURR_DIR}\\{FILE}
}}
if (Test-Path C:\\Windows\\chromedriver.exe) {{
    Remove-Item C:\\Windows\\chromedriver.exe
}}
Write-Output "Downloading {FILE}..."
Invoke-WebRequest {LINK} -OutFile {CURR_DIR}\\{FILE}
Write-Output "Unzipping {FILE}..."
Expand-Archive {CURR_DIR}\\{FILE} -Destination {CURR_DIR}\\{FILE_NAME}
Write-Output "Adding chromedriver.exe to PATH..."
Move-Item -Path {CURR_DIR}\\{FILE_NAME}\\chromedriver.exe -Destination C:\\Windows\\chromedriver.exe
Write-Output "Cleaning up..."
Remove-Item -Recurse {CURR_DIR}\\{FILE_NAME}
Remove-Item {CURR_DIR}\\{FILE}
"""

# `Set-ExecutionPolicy RemoteSigned` for windows

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except:
        return False

if(OS == "windows"):
    if ctypes.windll.shell32.IsUserAnAdmin() == 1:
        Popen(["powershell.exe", WINDOWS_CMD]).wait()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
else:
    Popen(LINUX_OR_MAC_CMD, shell=True).wait()

from time import sleep
sleep(1)

print("Successfully installed chromedriver...")
