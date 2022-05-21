from socket import gethostname, gethostbyname_ex, create_connection
from requests import get
from datetime import datetime
from random import randint
from os import listdir, remove, chdir, path, getcwd
from platform import system, platform, python_version
from colorama import Fore, Back, Style
from colorama import init
from pathlib import Path
import pmanager


def pre_fill_module_files(module_name: str) -> None:
    """

    pre-fill the two module files to ease the user experience in module creation

    """

    xml_file = open(f"pmanager/modules/{module_name}.xml", "w")
    py_file = open(f"pmanager/modules/{module_name}.py", "w")

    # pre-fill basic xml
    xml_file.write(
        f"<template>\n<folder path=\"{module_name}\">\n\n</folder>\n</template>")
    xml_file.close()

    # pre-fill basic python script
    script = """
from pmanager.res import *
from os import mkdir,path
from xml.etree import ElementTree as ET


def recursive(root,path):
    for item in root:

        if item.tag == "folder":
            sub_path = item.attrib['path']
            print(f"folder : {path}{sub_path}")
            mkdir(f"{path}{sub_path}")
            recursive(item,f"{path}{sub_path}/")

            
        elif item.tag == "file":
            fname = item.attrib['name']
            print(f"file : {path}{fname}")
            with open((path+fname),"w") as f:
                f.write(item.text)
                f.close()


def initialize(project_name):
    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    if not path.exists(dirpath):
            mkdir(dirpath)
        
    module_name = path.basename(__file__).replace(".py","")

    root = ET.parse(f"pmanager/modules/{module_name}.xml",).getroot()

    recursive(root,dirpath+"/")
    
    """

    py_file.write(script)
    py_file.close()


def sanitize_for_xml(string):
    """
        " to  &quot;
        ' to  &apos;
        < to  &lt;
        > to  &gt;
        & to  &amp;
    """

    return string.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;").replace("'", "&apos;").replace("\"", "&quot;")


def notify_update():
    """
    request the lastest version number of the project to pypi
    and notify the user if his version is outdated

    """

    # make a bunch of condition to not spam the user if he just don't have internet
    # or pypi is offline
    if check_internet():
        r = get("https://pypi.org/pypi/projects-manager/json")
        if r.status_code == 200:
            if str(pmanager.__version__) != str(r.json()['info']['version']):
                pwarn(
                    "A new version of pmanager is available, to update it just type 'pip install --upgrade projects_manager'")


def check_internet():
    """
    a simple function to check if an internet connection is available
    :return: True if connected, else it returns false
    """
    try:
        create_connection(("1.1.1.1", 53), 2)
        return True
    except:
        return False


def is_available(website, port=None):
    """
    a simple function to check if a website/server is available
    :param: website is a string where you put the website url/ip
    :param: port is an optionnal argument where you can specify a port
    :return: True if available, else it returns false
    """
    if port != None:
        try:
            create_connection((website, port), 2)
            return True
        except:
            return False
    else:
        try:
            create_connection((website, 80), 2)
            return True
        except:
            return False


def get_os_name():
    """
    :return: the os name
    """
    return str(system())


def get_full_os_name():
    """
    :return: the full os name
    """
    return str(platform())


def get_python_version():
    """
    :return: the python version you are using
    """
    return str(python_version())


def get_file_number_of_lines(fname):
    """
    :param: fname is a string containing the path to the file you want to count the lines
    :return: the number of line of the file
    """
    with open(f"{getcwd()}/{fname}") as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def get_file_size(fname):
    """
    :param: fname is a string containing the path to the file you want to get the size
    :return: a string containing the size of the file in Megabytes
    """
    byte = int(path.getsize(f"{getcwd()}/{fname}"))
    return f"{byte/1000000}"


def perror(str, time=False):
    """
    :param: time is set to false by default, set to true it display the time with the message
    :param: str is just a string where you put your message
    This function display a error-style custom and colored error message
    """
    init()
    if time:
        print(f"{Fore.RED}{get_time()} [x] {str} {Fore.WHITE}")
    else:
        print(f"{Fore.RED}[x] {str} {Fore.WHITE}")


def pwarn(str, time=False):
    """
    :param: time is set to false by default, set to true it display the time with the message
    :param: str is just a string where you put your message
    This function display a warning-style custom and colored warning message
    """
    init()
    if time:
        print(f"{Fore.YELLOW}{get_time()} [!] {str} {Fore.WHITE}")
    else:
        print(f"{Fore.YELLOW}[!] {str} {Fore.WHITE}")


def pinfo(str, time=False):
    """
    :param: time is set to false by default, set to true it display the time with the message
    :param: str is just a string where you put your message
    This function display a info-style custom and colored info message
    """
    init()
    if time:
        print(f"{Fore.BLUE}{get_time()} [+] {str} {Fore.WHITE}")
    else:
        print(f"{Fore.BLUE}[+] {str} {Fore.WHITE}")


def psuccess(str, time=False):
    """
    :param: time is set to false by default, set to true it display the time with the message
    :param: str is just a string where you put your message
    This function display a success-style custom and colored success message
    """
    init()
    if time:
        print(f"{Fore.GREEN}{get_time()} [v] {str} {Fore.WHITE}")
    else:
        print(f"{Fore.GREEN}[v] {str} {Fore.WHITE}")


def get_private_ips():
    """
    :return: a list of all private IP addresses liked to your machine (may be vm) 
    """
    return gethostbyname_ex(gethostname())[:2]


def get_public_ip():
    """
    :return: a string containing your public ip
    """
    return get('https://api.ipify.org').text


def get_hostname():
    """
    :return: a string containing the hostname
    """
    return gethostname()


def get_time():
    """
    :return: a string containing the time
    """
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def get_date():
    """
    :return: a string containing today's date
    """
    today = datetime.today()
    return today.strftime("%d/%m/%Y")


def write_temp_file(purpose, content, append=True):
    """
    :param: purpose is a string where you specify an idea of what you are putting in the temp file
    :param: content is a string where you put the content of the temp file
    :param: append is a boolean set to True by default to open the temp file in append mode or not
    write the specified string on a random named temp file
    """
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(str(randint(0, 99999999999))+purpose+".res", mode) as f:
        f.write(content)
        f.close()


def read_temp_file(purpose):
    """
    :param: purpose is a string  where ypu specify an idea of what you have put in the temp file
    :return: a string containing the content of the temp file or False if the file for this purpose don't exist
    """
    found = False
    for file in listdir():
        if (purpose in file) and (".res" in file):
            found = True
            with open(file) as f:
                content = f.read()
                f.close()

    if not found:
        return False
    else:
        return content


def clear_temp_files():
    """
    delete all temporary files created by write_temp_file
    """
    for file in listdir():
        if (".res" in file):
            remove(file)


def auto_chdir_to_file_root():
    """
    a function to make sure that the program is writing/reading at his root 
    (need to put res file in a folder)
    """
    chdir(path.abspath(__file__).replace("res.py", ""))
    chdir("..")


def get_home_dir_path():
    """
    :return: a string containing the path to the home directory of the curent user
    """

    return str(Path.home())


TEMPLATE = """

<!doctype html>
<html>

<head>
  <meta charset="UTF-8">
  <title>Directory Contents</title>
  <script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
</head>

<body>

  <div id="container">
  
    <h1>Directory Contents</h1>
    
    <table class="sortable">
      <thead>
        <tr>
          <th>Filename</th>
          <th>Size <small>(bytes)</small>(click to sort)</th>
          <th>Date Modified</th>
        </tr>
      </thead>
      <tbody>

        {%for file in files%}
        <tr class="file">
            <td sorttable_customkey="{{file['size']}}"><a href="/display_file?path={{file['path']}}" class="name">{{file['name']}}</a></td>
            <td sorttable_customkey="{{file['size']}}"><a href="/display_file?path={{file['path']}}"</a>{{file['size']}}</td>
            <td sorttable_customkey="{{file['size']}}"><a href="/display_file?path={{file['path']}}"</a>{{file['date']}}</td>
        </tr>
        {%endfor%}
      </tbody>
    </table>
  
    <h2></h2>
    
  </div>
  <style>
  * {
  padding:0;
  margin:0;
}

body {
  color: #333;
  font: 14px Sans-Serif;
  padding: 50px;
  background: #eee;
}

h1 {
  text-align: center;
  padding: 20px 0 12px 0;
  margin: 0;
}

h2 {
  font-size: 16px;
  text-align: center;
  padding: 0 0 12px 0; 
}

#container {
  box-shadow: 0 5px 10px -5px rgba(0,0,0,0.5);
  position: relative;
  background: white; 
}

table {
  background-color: #F3F3F3;
  border-collapse: collapse;
  width: 100%;
  margin: 15px 0;
}

th {
  background-color: #FE4902;
  color: #FFF;
  cursor: pointer;
  padding: 5px 10px;
}

th small {
  font-size: 9px; 
}

td, th {
  text-align: left;
}

a {
  text-decoration: none;
}

td a {
  color: #663300;
  display: block;
  padding: 5px 10px;
}

th a {
  padding-left: 0
}

td:first-of-type a {
  background: url(./.images/file.png) no-repeat 10px 50%;
  padding-left: 35px;
}

th:first-of-type {
  padding-left: 35px;
}

td:not(:first-of-type) a {
  background-image: none !important;
} 

tr:nth-of-type(odd) {
  background-color: #E6E6E6;
}

tr:hover td {
  background-color:#CACACA;
}

tr:hover td a {
  color: #000;
}

/* icons for file types (icons by famfamfam) */

/* images */
table tr td:first-of-type a[href$=".jpg"], 
table tr td:first-of-type a[href$=".png"], 
table tr td:first-of-type a[href$=".gif"], 
table tr td:first-of-type a[href$=".svg"], 
table tr td:first-of-type a[href$=".jpeg"] {
  background-image: url(./.images/image.png);
}

/* zips */
table tr td:first-of-type a[href$=".zip"] {
  background-image: url(./.images/zip.png);
}

/* css */
table tr td:first-of-type a[href$=".css"] {
  background-image: url(./.images/css.png);
}

/* docs */
table tr td:first-of-type a[href$=".doc"],
table tr td:first-of-type a[href$=".docx"],
table tr td:first-of-type a[href$=".ppt"],
table tr td:first-of-type a[href$=".pptx"],
table tr td:first-of-type a[href$=".pps"],
table tr td:first-of-type a[href$=".ppsx"],
table tr td:first-of-type a[href$=".xls"],
table tr td:first-of-type a[href$=".xlsx"] {
  background-image: url(./.images/office.png)
}

/* videos */
table tr td:first-of-type a[href$=".avi"], 
table tr td:first-of-type a[href$=".wmv"], 
table tr td:first-of-type a[href$=".mp4"], 
table tr td:first-of-type a[href$=".mov"], 
table tr td:first-of-type a[href$=".m4a"] {
  background-image: url(./.images/video.png);
}

/* audio */
table tr td:first-of-type a[href$=".mp3"], 
table tr td:first-of-type a[href$=".ogg"], 
table tr td:first-of-type a[href$=".aac"], 
table tr td:first-of-type a[href$=".wma"] {
  background-image: url(./.images/audio.png);
}

/* web pages */
table tr td:first-of-type a[href$=".html"],
table tr td:first-of-type a[href$=".htm"],
table tr td:first-of-type a[href$=".xml"] {
  background-image: url(./.images/xml.png);
}

table tr td:first-of-type a[href$=".php"] {
  background-image: url(./.images/php.png);
}

table tr td:first-of-type a[href$=".js"] {
  background-image: url(./.images/script.png);
}

/* directories */
table tr.dir td:first-of-type a {
  background-image: url(./.images/folder.png);
}
  
  </style>
</body>

</html>
"""
