from exergenics import ExergenicsApi
import zipfile
from tempfile import mkdtemp
import requests
import shutil

api = ExergenicsApi("apiteam@exergenics.com", "M3nt4llyF1t", False)

api.authenticate()

# load the jobs that are ready for transforming (headers_ready::completed) into an array for looping.
readyJobs = []
api.getJobs("headers_ready", "completed")
if api.numResults() > 0:
    while api.moreResults():
        readyJobs.append(api.nextResult())

# set these jobs to now waiting for merged ready to begin.
for i in range(len(readyJobs)):
    api.setStage(readyJobs[i]['jobId'], "transformed_ready", "waiting")

# now loop through all these to download and extract data files
for i in range(len(readyJobs)):

    # tell the job scheduler we are "running" this job id
    api.setJobStageRunning(readyJobs[i]['jobId'])

    #load config
    plantCode = readyJobs[i]['plantCode']
    mergedTable = readyJobs[i]['jobData']['tablenameMerged']
    headerTable = readyJobs[i]['jobData']['tablenameHeader']
    transformedTable = "{}-transformed".format(plantCode)

    ####################################
    #### TODO @Yi-Jen
    ####################################

    # tell job handler what table was just created
    api.setJobData(readyJobs[i]['jobId'], "tablenameTransformed", transformedTable)

    # once here, headers_ready is set to "complete" (to be picked up by next stage handler)
    api.setJobStageComplete(readyJobs[i]['jobId'])
