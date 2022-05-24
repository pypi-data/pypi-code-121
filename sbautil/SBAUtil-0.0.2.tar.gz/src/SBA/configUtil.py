"""
Utilities for manipulating the configuration file
"""

import json
import datetime
import os

'''
Configuration File:
{   
    "Project_Name": 
    "Experimenter":
    "Date": 
    "Videos":
    [   
        {
        "ID": 399
        "start_time": 3
        "FrameCount": 12382
        }
    ]
}
'''

def initConfig(Dirpath,projectName=None,experimenter=None):
    data = {}
    data["Project_Name"] = projectName if projectName else "newProject"
    data["Experimenter"]= experimenter if experimenter else "experimenter1"
    data["Date"] = datetime.now().strftime("%b/%d/%Y")
    data["Videos"]=[]

    jsonPath = os.path.join(Dirpath,"config.json")
    print(jsonPath)
    with open(jsonPath,"w+") as jsonfile:
        json.dump(data,jsonfile)

# add video record to config
def _addVideoRecord(jsonPath,videoID,start_crop_time,originalFrameCount):
    with open(jsonPath,"r+") as jsonfile:
        data = json.load(jsonfile)
        data["Videos"].append({"ID":videoID,"start_time":start_crop_time,"FrameCount":originalFrameCount})            
        jsonfile.truncate(0)
        jsonfile.seek(0)
        json.dump(data,jsonfile)


def readConfig(config):
    data = None
    try:
        with open(config,"r") as jsonfile:
            data = json.load(jsonfile)
    except:
        print("Error in reading config file.")
        exit(1)
    return data

def readVideoData(config):
    """
    Read Config, generate a dictionary containing video Info: 
        {VideoID: {"ID": .., "start_time": .., "FrameCount": ..}}
    """

    videoData = readConfig(config)["Videos"]
    res = {}
    for item in videoData:
        res[item["ID"]] = item

    return res
