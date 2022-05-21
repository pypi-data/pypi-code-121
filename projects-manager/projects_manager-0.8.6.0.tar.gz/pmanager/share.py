from flask import Flask, render_template, send_from_directory,send_file,request,redirect,flash,jsonify
from os import mkdir, path, walk, getcwd
from pmanager.res import *
import pathlib
from datetime import datetime
from mimetypes import guess_type

#init flask app
app = Flask(__name__)

@app.route('/')
def list_directory():

    if not path.exists("pmanager/templates"):
        mkdir("pmanager/templates")

    with open("pmanager/templates/index.html","w") as f:
        f.write(TEMPLATE)
        f.close()

    dirpath = read_temp_file("dirpath")

    files = []
    for e in walk(dirpath):
        for f in e[2]:
            subf = e[0].replace(dirpath,"",1)
            files.append({"name":subf+"/"+f,"path":e[0]+"/"+f,"size":path.getsize(e[0]+"/"+f),"date":datetime.fromtimestamp(pathlib.Path(e[0]+"/"+f).stat().st_mtime).strftime("%H:%M:%S")})


    return render_template("index.html",files=[{"name": file['name'],"path": file['path'],"size":file['size'],"date":file['date']} for file in files])


@app.route("/display_file")
def display_file():
    try:
        path = request.args.get("path")
        with open(path,"rb") as f:
            ctt = f.read()
            f.close()
        try:
            ctt = ctt.decode("utf-8")
            ctt = """<link rel="stylesheet"
      href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.1.0/styles/default.min.css">
<script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.1.0/highlight.min.js"></script> <script>hljs.highlightAll();</script> <pre><code>""" + ctt + "</code></pre>"
        except:
            pass

        return ctt if read_temp_file("dirpath") in path else jsonify({"error":"forbiden access"})

    except :
        return jsonify({"error":"unable to read file"})

def initialize(namespace):

    project_name = namespace.project_name[0]

    #get project full path
    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    write_temp_file("dirpath",dirpath,append=False)

    #check if the project exists
    if not path.exists(dirpath):
        perror("This project does not exists")
        return
    



    pinfo(f"running web IDE on :\n {dirpath}")

    #loop until a correct port is typed or a keyboardInterrupt occurs
    while True:
        try:
            port = int(input("Select which port you want to run the web IDE\n-->"))
            break
        except Exception as e:
            if e.__class__.__name__ == "KeyboardInterrupt":
                return
            else:
                pwarn("Port must be an integer, retry now ;)\n")


    #run web server
    app.run(host="0.0.0.0",port=port)