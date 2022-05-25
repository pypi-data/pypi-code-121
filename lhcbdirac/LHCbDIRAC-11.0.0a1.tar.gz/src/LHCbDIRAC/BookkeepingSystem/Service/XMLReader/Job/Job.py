###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""stores the jobs and its parameters."""


class Job(object):
    """Job class."""

    def __init__(self):
        """initialize the class members."""
        self.configuration = None
        self.options = []
        self.parameters = []
        self.inputFiles = []
        self.outputFiles = []
        self.simulationCondition = None
        self.dataTakingCondition = None
        self.jobID = -1
        self.fileName = ""

    def addJobParams(self, jobParams):
        """sets the job parameters."""
        self.parameters += [jobParams]

    def exists(self, jobParam):
        """checks a given job parameter."""
        return any(i.name == jobParam for i in self.parameters)

    def getParam(self, jobParam):
        """returns a job parameter."""
        for i in self.parameters:
            if i.name == jobParam:
                return i

    def removeParam(self, jobParam):
        """removes a job parameter."""
        for i in self.parameters:
            if i.name == jobParam:
                self.parameters.remove(i)

    def addJobInputFiles(self, files):
        """adds the input file to a job."""
        self.inputFiles += [files]

    def addJobOutputFiles(self, files):
        """adds the output files to a job."""
        self.outputFiles += [files]

    def getOutputFileParam(self, paramName):
        """returns the parameters of a output file."""
        for i in self.outputFiles:
            param = i.getParam(paramName)
            if param is not None:
                return param

    def __repr__(self):
        """formats the output of the print command."""
        result = ["JOB: \n"]
        result += [str(self.configuration) + " "]
        for option in self.options:
            result += [str(option)]
        result += ["\n"]
        for param in self.parameters:
            result += [str(param)]
        result += ["\n"]
        for jobinput in self.inputFiles:
            result += [str(jobinput)]
        for output in self.outputFiles:
            result += [str(output)]
        result += ["\n"]
        return "".join(result)

    def writeToXML(self):
        """writes an XML string."""
        string = []
        string += ['<?xml version="1.0" encoding="ISO-8859-1"?>\n']
        string += ['<!DOCTYPE Job SYSTEM "book.dtd">\n']

        string += [str(self.configuration.writeToXML())]
        for param in self.parameters:
            string += [str(param.writeToXML())]

        for inputFile in self.inputFiles:
            string += [str(inputFile.writeToXML())]

        for output in self.outputFiles:
            string += [str(output.writeToXML())]

        if self.simulationCondition:
            string += [str(self.simulationCondition.writeToXML())]

        daq = self.dataTakingCondition
        if daq is not None:
            string += [str(daq.writeToXML())]

        string += ["</Job>"]

        return "".join(string)
