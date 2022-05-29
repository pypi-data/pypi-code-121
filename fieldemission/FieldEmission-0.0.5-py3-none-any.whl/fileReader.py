import numpy as np
import re


def ReadDatFile(Filename):
    f = open(Filename)
    lines = f.readlines()
    f.close()
    # Search for header column and create a dictionary for
    cCommentLines = 0
    for iLine in range(0, len(lines)):
        currLine = lines[iLine]
        if currLine.startswith("#"):  # Check for possible header-line
            # Remove distrubing characters
            currLine = re.sub("\t|\#|\ |\n", "", currLine)
            splitLine = currLine.split(",")
            if len(splitLine) > 1:  # Has it at least 2 entries?
                ColumnCount = len(splitLine)  # Get amount of columns
                # Make dictionary and basic numpy-structure
                HeaderColumn = {splitLine[i]: range(ColumnCount)[i] for i in range(ColumnCount)}
                break
    del f

    # Parse data and insert to numpy-array
    data = []
    for iLine in range(0, len(lines)):
        currLine = lines[iLine]
        if currLine.startswith("#"):  # Check if line is a comment
            continue
        currLine = re.sub("\t|\#|\ |\n", "", currLine)
        if currLine == "":  # or empty
            continue

        # Dataline found -> Parse and enter to numpy-array
        split = currLine.split(",")
        if len(split) == ColumnCount:
            for iSplit in range(len(split)):
                split[iSplit] = float(split[iSplit].strip("\t "))
            data.append(split)
    Data = np.array(data)  # Convert list to numpy-array
    return HeaderColumn, Data
