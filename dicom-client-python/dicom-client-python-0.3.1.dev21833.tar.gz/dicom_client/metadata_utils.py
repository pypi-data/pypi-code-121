# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

""" Utility functions """
import os
from pathlib import Path
import pydicom

# -------------------------------------------------
def left(sourcestring, amount):
    """ Extract the leftmost characters """
    return sourcestring[:amount]


# -------------------------------------------------
def right(sourcestring, amount):
    """ Extract the rightmost characters """
    return sourcestring[-amount:]


# -------------------------------------------------
def mid(sourcestring, offset, amount):
    """ Extracts some middle characters """
    return sourcestring[offset : offset + amount]


# -------------------------------------------------
def rename_files():
    """ Rename files based on metadata """
    files = list(Path(".").rglob("./dcmfiles3/*.dcm"))
    for file in files:
        metadata = pydicom.filereader.dcmread(file)
        patient_id = right(metadata.PatientID, 4)
        study_id = right(metadata.StudyInstanceUID, 4)
        series_id = right(metadata.SeriesInstanceUID, 4)
        instance_id = right(metadata.SOPInstanceUID, 4)
        newfn = (
            os.path.dirname(file)
            + "/"
            + patient_id
            + "_"
            + study_id
            + "_"
            + series_id
            + "_"
            + instance_id
            + ".dcm"
        )
        os.rename(file, newfn)


# -------------------------------------------------
def showdata():
    """ Display DCM metadata"""
    files = list(Path(".").rglob("./dcmfiles3/*.dcm"))
    for file in files:
        print(file)
        metadata = pydicom.filereader.dcmread(file)
        print("Patient ID = " + metadata.PatientID)
        print("Study ID = " + metadata.StudyInstanceUID)
        print("Series ID = " + metadata.SeriesInstanceUID)
        print("SOP Instance  ID = " + metadata.SOPInstanceUID)
        print("=========================================")


# -------------------------------------------------
def writecsv():
    """ Right out metadata to separated list """
    files = list(Path(".").rglob("./dcmfiles3/*.dcm"))
    with open("/mnt/c/temp/csvfile.csv", "w") as file:
        file.write("Patient, Study, Series, Instance\n")
        for file in files:
            metadata = pydicom.filereader.dcmread(file)
            result = (
                metadata.PatientID
                + ","
                + metadata.StudyInstanceUID
                + ","
                + metadata.SeriesInstanceUID
                + ","
                + metadata.SOPInstanceUID
                + "\n"
            )
            file.write(result)
