from exergenics import ExergenicsApi
import zipfile
from tempfile import mkdtemp
import requests
import shutil

api = ExergenicsApi("apiteam@exergenics.com", "M3nt4llyF1t", False)

api.authenticate()

# load the jobs that are ready for transforming (headers_ready::completed) into an array for looping.
readyJobs = []
api.getJobs("transformed_ready", "completed")
if api.numResults() > 0:
    while api.moreResults():
        readyJobs.append(api.nextResult())

# set these jobs to now waiting for merged ready to begin.
for i in range(len(readyJobs)):
    api.setStage(readyJobs[i]['jobId'], "modelling_ready", "waiting")

# now loop through all these to download and extract data files
for i in range(len(readyJobs)):
    plantCode = readyJobs[i]['plantCode'];
    api.sendSlackMessage("Plant {} requires modelling on dash.".format(plantCode))
    #ideally, dash interface would be able to tell when modelling began, even if a button needed pushing to start, and then it set the job status to "running".
    #perhaps dash could read the modelling_ready stage and show all jobs in this category for the user to start/continue the modelling
    #regardless of if state is set to running, dash needs to then mark this job as completed status in addition to sending co-eff.
    #the dash interface should allow for this stage to set an error status also, along with an error reason.

