from exergenics import ExergenicsApi
import zipfile
from tempfile import mkdtemp
import requests
import shutil

api = ExergenicsApi("apiteam@exergenics.com", "M3nt4llyF1t", False)

api.authenticate()

# load the jobs that are ready for transforming (headers_ready::completed) into an array for looping.
readyJobs = []
api.getJobs("modelling_ready", "completed")
if api.numResults() > 0:
    while api.moreResults():
        readyJobs.append(api.nextResult())

# set these jobs to now waiting for merged ready to begin.
for i in range(len(readyJobs)):
    api.setStage(readyJobs[i]['jobId'], "validation_ready", "waiting")

# now loop through all these to download and extract data files
for i in range(len(readyJobs)):
    plantCode = readyJobs[i]['plantCode'];
    api.sendSlackMessage("Plant {} requires validation of its modelling.".format(plantCode))

    #dash flow to validate modelling.
    #sets completed or error status at the end.

