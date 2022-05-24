"""
Utilities for processing simba output to generate the desired Interaction vector
"""

from .configUtil import readVideoData
import os
import csv


def finalizeSimBaOutput(config, simbaFiles, classifier ,destDir = None):
    """
    Generate the final interaction vector
    Input:
        simbaFiles: a list or a directory of path to simba csv output
        classifier: a list of classifer names (e.g. isInteraction)
    """
    videoData = readVideoData(config)

    if type(simbaFiles) is str and os.path.isdir(simbaFiles):
        basepath = simbaFiles
        simbaFiles = os.listdir(simbaFiles)
    else:
        if not type(simbaFiles) is list:
            print("Input simbaFile should be either a list or a directory!")
            return None

    if not destDir:
        destDir = os.path.join(os.getcwd(),"final_result")
    if not os.path.isdir(destDir):
        if not os.path.exists(destDir):
            os.mkdir(destDir)
        else:
            print("Error: {} is a file.".format(destDir))
            exit()

    # get indexes of wanted columns
    wantedColumnNames = set()
    for cl in classifier:
        wantedColumnNames.add("Probability_" + cl)
        wantedColumnNames.add(cl)
    
    wantedColumns = []

    for simbaCSV in simbaFiles:
        if not simbaCSV.split('.')[-1] in {'csv','CSV'}:
            continue
        
        videoID = simbaCSV[4:-4]

        try:
            with open(os.path.join(basepath, simbaCSV)) as csvFile:
                data = list(csv.reader(csvFile))
                index = data[0]
                data = data[1:]
        except FileNotFoundError:
            print("File {} does not exists!".format(simbaCSV))
            continue

        if not wantedColumns:
            wantedColumns = [0]
            for i,name in enumerate(index):
                if name in wantedColumnNames:
                    wantedColumns.append(i)

        # reconstruct a new csv file
        originalVideoFrameCount = int(videoData[videoID]['FrameCount'])
        offset = originalVideoFrameCount - len(data)

        for i in range(len(data)):
            data[i] = [data[i][x] for x in wantedColumns]
            data[i][0] = int(data[i][0]) + offset
        
        index = [index[x] for x in wantedColumns]
        index[0] = "FrameNumber"
        
        csvPath = os.path.join(destDir,"final_"+videoID+".csv") 
        with open(csvPath,"w") as f:
            wr = csv.writer(f)
            wr.writerow(index)
            wr.writerows(data)
        print("Wrote {}.".format(csvPath))
    
    print("Done.")
