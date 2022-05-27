from curses import reset_shell_mode
import os, sys
from flask import Flask, render_template, request
"""
sys.path.insert(1, os.path.abspath('.'))
"""
from src.Archive import Archive
from src.Utilities import Utilities
import src.Constants  as Constants
from src import myConfig

from glob import glob
from io import BytesIO
from zipfile import ZipFile
from flask import send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('search.html')

def download():
    target = os.getcwd() + '/' + "extract"

    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for file in glob(os.path.join(target, '*')):
            zf.write(file, os.path.basename(file))
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        attachment_filename='archive.zip'
    )

@app.route("/search", methods=['GET', 'POST'])
def search():
    resources = []
    Utilities.checkCurrentArchive()
    myArchive = Archive(myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME))
    if request.method == 'POST':
        # check if button btnExtract is pressed
        if request.form['btnExtract'] == 'Extract':
            metadataIds = request.form.getlist('metadataIds')
            if len(metadataIds) >= 1:
                metadatas = myArchive.myDb.getMetadatasByIds(metadataIds)
                myArchive.extractResources(metadatas, os.getcwd()+"/extract")
                return download()
        else:
            filters = dict()
            search = request.form['search']
            if search != "":
                filters = dict(x.split(':') for x in search.split(' ')) 

            resources = myArchive.search(filters)
            #myArchive.saveToExtract(resources)
    return render_template('search.html', resources=resources)
