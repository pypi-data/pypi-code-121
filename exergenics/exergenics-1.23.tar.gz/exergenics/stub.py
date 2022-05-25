from exergenics import ExergenicsApi
import zipfile
from tempfile import mkdtemp
import requests
import shutil
import os

api = ExergenicsApi("apiteam@exergenics.com", "M3nt4llyF1t", False)

if not api.authenticate():
    exit("couldnt auth")

api.sendCSVToPortal(53)
exit()

'''
# load the jobs that are ready for merging (rawdata_ready::completed) into an array for looping.
readyJobs = []
api.getJobsByPlant("JC-TEST-PLANT-1")
if api.numResults() > 0:
    while api.moreResults():
        readyJobs.append(api.nextResult())

print(readyJobs)
exit()
'''

#set these jobs to now waiting for merged ready to begin.
for i in range(len(readyJobs)):
    api.setStage(readyJobs[i]['jobId'], "merged_ready", "waiting")

# now loop through all these to download and extract data files
for i in range(len(readyJobs)):

    #tell the job scheduler we are "running" this job id
    api.setJobStageRunning(readyJobs[i]['jobId'])

    #get the URL to the datafile from s3 zip (saved from previous stages)
    urlToDataFile = readyJobs[i]['jobData']['zipfile']

    # download the zip file
    r = requests.get(urlToDataFile, allow_redirects=True)
    downloadTempDirectory = mkdtemp()
    fileSaveAs = "{}/{}".format(downloadTempDirectory, "data.zip")
    open(fileSaveAs, 'wb').write(r.content)



    # where to save the zip file locally
    directory_to_extract_to = mkdtemp()

    # extract locally to temp folder
    with zipfile.ZipFile(fileSaveAs, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)

        # get a list of files in this zip
        listOfiles = zip_ref.infolist()

        # get the location of the extracted file on local storage
        for extractedFile in listOfiles:
            # ignore macosx dodgeyness
            if not extractedFile.filename.startswith("__MACOSX"):
                plantDataFile = "{}/{}".format(directory_to_extract_to, extractedFile.filename)


                ####################################
                #### This is a data file to process (merge)
                #### TODO @Yi-Jen
                ####################################
                plantCode = readyJobs[i]['plantCode']
                print(plantDataFile)


        #remove the temp directory and all its files.
        shutil.rmtree(directory_to_extract_to, ignore_errors=True)

        #remove the zip file and directory
        shutil.rmtree(downloadTempDirectory, ignore_errors=True)

        #once here, merged_ready is set to "complete" (to be picked up by next stage handler)
        api.setJobStageComplete(readyJobs[i]['jobId'])
