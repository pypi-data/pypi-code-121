from math import ceil
import pandas as pd
import os
import json
from datetime import datetime

from tables import HDF5ExtError

from .configUtil import _addVideoRecord

import pandas as pd

import cv2

def scanH5files(h5files):
    '''
    For each videoID:
    returns a tuple: 
        Critical frame: the frame where two mice are present(with no NAN)
        Number of frames: the number of frames in the original video
        path to the h5file
    Input:
        h5files: a list of paths or the directory
    '''
    res = {}
    basepath = ""
    if type(h5files) is str and os.path.isdir(h5files):
        basepath = h5files
        h5files = os.listdir(h5files)
    else:
        if not type(h5files) is list:
            print("Input h5files is a list!")
            return res

    for h5file in h5files:
        try:
            data = pd.read_hdf(os.path.join(basepath,h5file))
        except FileNotFoundError:
            print("File {} does not exists!".format(h5file))
            continue
        except HDF5ExtError:
            continue

        # check data, get the critical frame
        crtFrame = 0
        
        numFrames = len(data.index)
        for i in range(len(data.index)):
            if not data.iloc[i].isnull().any():
                crtFrame = i
                break
        videoID = h5file[:os.path.basename(h5file).find("DLC")]
        res[videoID] = (crtFrame, numFrames, os.path.join(basepath,h5file))

    return res

def getFrameCount(h5file):
    '''
    returns the number of frames based on the DLC result h5file
    returns -1 if error
    '''
    try:
        data = pd.read_hdf(h5file)
        return len(data.index)

    except FileNotFoundError:
        print("File {} does not exist".format(h5file))
        return -1
    except HDF5ExtError:
        print("HDF5ExtError")
        return -1

def _modifyH5(h5filePath, h5destPath, newvideopath):
    cap = cv2.VideoCapture(newvideopath)
    framenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    crtframe = getFrameCount(h5filePath) - framenum
    
    df = pd.read_hdf(h5filePath)
    df.drop(df[df.index<crtframe].index, inplace=True)

    df = df.reset_index(drop=True)

    df.to_hdf(h5destPath,key="df_with_missing", mode= "w")
    

def batch_dynamic_cropVideo(config,videos,h5files,videoType="avi",destDir=None,dontCut=False):
    '''
    Main function for dynamic cutting videos: 
    1. extract the portion in the video where two mice are present based on DLC h5file
    2. Modify the DLC h5 output so that the new h5 files match the cut videos. 
    3. Record video information in the configuration file
    '''
    if not dontCut and os.system("ffmpeg -h") != 0:
        print("Please install ffmpeg!")
        exit()
    
    if not destDir:
        destDir = os.path.join(os.getcwd(),"preprocessed")
    if not os.path.isdir(destDir):
        if not os.path.exists(destDir):
            os.mkdir(destDir)
        else:
            print("Error: {} is a file.".format(destDir))
            exit()

    H5DestDir = os.path.join(destDir,"newH5")
    videosDestDir = os.path.join(destDir, "preprocessed_videos")

    try:
        os.mkdir(H5DestDir)
    except FileExistsError:
        pass
    try:
        os.mkdir(videosDestDir)
    except FileExistsError:
        pass
        
    scanned_dict = scanH5files(h5files)
    videopath = os.path.join(videos)
    videos = os.listdir(videos)
    
    for video in videos:
        cap = cv2.VideoCapture(os.path.join(videopath,video))
        if not cap.isOpened():
            print(video," is not a valid video file. Skipped...")
            continue
        fps = int(cap.get(cv2.CAP_PROP_FPS))


        videoID = video.split(".")[0]
        if videoID in scanned_dict:
            crtFrame, numFrame, h5filePath = scanned_dict[videoID]
            start_crop_time = ceil(crtFrame / fps)
            
            destpath = os.path.join(videosDestDir,"cut_"+video)
            if not dontCut:
                ret = os.system("ffmpeg -i {} -ss {} -c copy {}".format(os.path.join(videopath,video), start_crop_time,destpath))

            if dontCut or ret == 0:
                _addVideoRecord(config,videoID,start_crop_time,numFrame)

            # modify the corresponding h5 file
            h5destPath = os.path.join(H5DestDir,"cut_"+ os.path.basename(h5filePath))
            _modifyH5(h5filePath, h5destPath, destpath)

    

    print("Done.")
