import json
import os
from time import sleep
import jinja2
from snprocess.qc.model import plink
import http.server
import shutil


def make_bed(inDir, inFile):
    """Convert SNP file to binary format. Return name of binary file."""
    inFileLink = inDir + inFile
    plink(" --file {} --make-bed --out {}".format(inFileLink, inFileLink))


def md(output_path, context, path):
    # load the template environment
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path + "/templates"),
        autoescape=jinja2.select_autoescape(['html', 'xml']), )

    # get the template
    temp = template_env.get_template("report_template.html")

    # render the html report template
    output_path.write_text(temp.render(context))


def printdict(d: dict) -> str:
    """print a dict in a json-like format"""
    outstr = ""
    for item in d.keys():
        outstr += "\t" + item + ": " + str(d[item]) + "\n"
    return outstr.rstrip("\n")


def clean():
    """Remove unnecesary files produced by QC."""
    shutil.rmtree("tmp")


def run(outdir, server_class=http.server.HTTPServer, handler_class=http.server.SimpleHTTPRequestHandler):
    """Run an http server to display info."""
    OKGREEN = '\033[92m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

    # set working directory to outdir
    os.chdir(outdir)
    
    server_address = ('', 8008)
    httpd = server_class(server_address, handler_class)
    print(OKGREEN + BOLD + "SNProcess will start the http server. Cancel with CTRL+C\nStarting in 3 seconds..." + ENDC)
    sleep(3)
    print("http://localhost:8008")
    httpd.serve_forever()
