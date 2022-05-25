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
"""It stores the job related information."""
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.JobConfiguration import JobConfiguration
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.JobOption import JobOption
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.File import File
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.InputFile import InputFile
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.JobParameters import JobParameters
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.Job import Job
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.FileParam import FileParam
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.SimulationConditions import SimulationConditions
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.DataTakingConditions import DataTakingConditions
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Replica.FileReplica import FileReplica
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Replica.ReplicaParam import ReplicaParam
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.Quality import Quality
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.QualityParameters import QualityParameters
from DIRAC import gLogger


class JobReader(object):
    """JobReader class."""

    def readJob(self, doc, fileName):
        """reads and stores the job elements from the file."""
        job = Job()
        job.fileName = fileName
        gLogger.debug("Reading job from" + str(fileName) + "XML!")

        self.__readJobConfigurations(doc, job)
        self.__readJobOptions(doc, job)
        self.__readJobTypeParameters(doc, job)
        self.__readJobInputFiles(doc, job)
        self.__readJobOutputFiles(doc, job)
        self.__readJobSimulationConditions(doc, job)
        self.__readJobDataTakingConditions(doc, job)

        gLogger.debug("Job reading finished successfully!")
        return job

    #############################################################################
    @staticmethod
    def __readJobConfigurations(doc, job):
        """reads and stores the job configurations."""

        conf = JobConfiguration()
        jobElements = doc.getElementsByTagName("Job")
        for node in jobElements:

            name = node.getAttributeNode("ConfigName")
            if name is not None:
                conf.configName = name.value
            else:
                gLogger.error("<ConfigName> XML tag is missing!!")

            version = node.getAttributeNode("ConfigVersion")
            if version is not None:
                conf.configVersion = version.value
            else:
                gLogger.error("<ConfigVersion> XML tag is missing!!")

            date = node.getAttributeNode("Date")
            if date is not None:
                conf.date = date.value
            else:
                gLogger.error("<Date> XML tag is missing!!")

            time = node.getAttributeNode("Time")
            if time is not None:
                conf.time = time.value
            else:
                gLogger.error("<Time> XML tag is missing!!")

        job.configuration = conf

    #############################################################################
    @staticmethod
    def __readJobOptions(doc, job):
        """reads and stores the job option."""
        jobOptions = doc.getElementsByTagName("JobOption")
        for node in jobOptions:
            options = JobOption()
            recipient = node.getAttributeNode("Recipient")
            if recipient is not None:
                options.recipient = recipient.value
            else:
                gLogger.warn("<Recipinet> jobOption XML tag is missing!!")

            name = node.getAttributeNode("Name")
            if name is not None:
                options.name = name.value
            else:
                gLogger.warn("<Name> JobOption XML tag is missing!!")

            value = node.getAttributeNode("Value")
            if value is not None:
                options.value = value.value
            else:
                gLogger.warn("<Value> JobOption XML tag is missing!!")

            job.options += [options]

    #############################################################################
    @staticmethod
    def __readJobTypeParameters(doc, job):
        """reads and stores the job parameters."""

        jobTypeParameters = doc.getElementsByTagName("TypedParameter")

        for node in jobTypeParameters:
            parameters = JobParameters()
            name = node.getAttributeNode("Name")
            if name is not None:
                parameters.name = name.value
            else:
                gLogger.warn("<Name> TypedParameter XML tag is missing!!")

            value = node.getAttributeNode("Value")
            if value is not None:
                parameters.value = value.value
            else:
                gLogger.warn("<Value> TypedParameter XML tag is missing!!")

            nodetype = node.getAttributeNode("Type")
            if nodetype is not None:
                parameters.type = nodetype.value
            else:
                gLogger.warn("<Type> TypedParameter XML tag is missing!!")

            job.addJobParams(parameters)

    ########################################################################
    @staticmethod
    def __readJobInputFiles(doc, job):
        """reads and stores the input files of a job."""
        jobInputFile = doc.getElementsByTagName("InputFile")
        for node in jobInputFile:
            inputFile = InputFile()
            inputFileName = node.getAttributeNode("Name")
            if inputFileName is not None:
                inputFile.name = inputFileName.value
            else:
                gLogger.error("<Name> InputFile XML tag is missing!!")

            job.addJobInputFiles(inputFile)

    ########################################################################
    def __readJobOutputFiles(self, doc, job):
        """reads the jobs output files."""
        jobOutputFiles = doc.getElementsByTagName("OutputFile")
        for node in jobOutputFiles:
            outputFile = File()

            name = node.getAttributeNode("Name")
            if name is not None:
                outputFile.name = name.value
            else:
                gLogger.error("<Name> Outputfile XML tag is missing!!")

            typeName = node.getAttributeNode("TypeName")
            if typeName is not None:
                outputFile.type = typeName.value
            else:
                gLogger.error("<Type> outputfile XML tag is missing!!")

            version = node.getAttributeNode("TypeVersion")
            if version is not None:
                outputFile.version = version.value
            else:
                gLogger.error("<Version> outputfile XML tag is missing!!")

            fileparams = node.getElementsByTagName("Parameter")
            for param in fileparams:
                outputFileParams = FileParam()

                name = param.getAttributeNode("Name")
                if name is not None:
                    outputFileParams.name = name.value
                else:
                    gLogger.error("<Name> outputfile Parameter XML tag is missing!!")

                value = param.getAttributeNode("Value")
                if value is not None:
                    outputFileParams.value = value.value
                else:
                    gLogger.error("<Value> outputfile Parameter XML tag is missing!!")

                outputFile.addFileParam(outputFileParams)
            self.__readFilereplica(doc, outputFile)
            self.__readDataquality(node, outputFile)
            job.addJobOutputFiles(outputFile)

    ########################################################################
    @staticmethod
    def __readFilereplica(doc, outputFile):
        """It creates the replica object and adds to the output file."""
        replicas = doc.getElementsByTagName("Replica")  # I have to check doc ? no node? !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for replica in replicas:
            rep = FileReplica()
            param = ReplicaParam()
            name = replica.getAttributeNode("Name")
            location = replica.getAttributeNode("Location")
            if name is not None:
                param.name = name.value
            if location is not None:
                param.location = location.value
                rep.addParam(param)
            outputFile.replicas += [rep]

    ########################################################################
    @staticmethod
    def __readDataquality(node, outputFile):
        """It reads the data quality information of a given file."""
        qualities = node.getElementsByTagName("Quality")
        for quality in qualities:
            fileQuality = Quality()
            group = quality.getAttributeNode("Group")
            if group is None:
                fileQuality.group = group.value
            else:
                gLogger.warn("<Group> Quality XML tag is missing!!")

            flag = quality.getAttributeNode("Flag")
            if flag is not None:
                fileQuality.flag = flag.value
            else:
                gLogger.warn("<Flag> Quality XML tag is missing!!")

            parameters = quality.getElementsByTagName("Parameter")
            for param in parameters:
                qualityParameters = QualityParameters()
                name = param.getAttributeNode("Name")
                if name is not None:
                    qualityParameters.name = name.value
                else:
                    gLogger.warn("<Name> Quality XML tag is missing!!")

                value = param.getAttributeNode("Value")
                if value is not None:
                    qualityParameters.value = value.value
                else:
                    gLogger.warn("<Value> Quality XML tag is missing!!")

                fileQuality.addParam(qualityParameters)

            outputFile.qualities += [fileQuality]

    ########################################################################
    @staticmethod
    def __readJobSimulationConditions(doc, job):
        """reads and stores the job simulation condition."""
        gLogger.debug("Read Simulation Conditions")
        simcond = doc.getElementsByTagName("SimulationCondition")
        if not simcond:
            gLogger.debug("No Simulation Conditions:")
        elif len(simcond) > 1:
            gLogger.debug("Too many Simulation conditions:", str(simcond))
        else:
            simParam = SimulationConditions()
            node = simcond[0]
            gLogger.debug("Found Simulation conditions:", str(node))
            parameters = node.getElementsByTagName("Parameter")
            for param in parameters:
                name = param.getAttributeNode("Name")
                value = param.getAttributeNode("Value")
                if name is None or value is None:
                    gLogger.warn("<Name>  or <Value> simulation XML tag is missing!!")
                else:
                    simParam.parameters[name.value] = value.value
                    job.simulationCondition = simParam

    ########################################################################
    @staticmethod
    def __readJobDataTakingConditions(doc, job):
        """reads and stores the job data taking conditions."""
        gLogger.debug("Read DataTaking Conditions")
        daqcond = doc.getElementsByTagName("DataTakingConditions")
        if not daqcond:
            gLogger.debug("No Real DataTaking Conditions")
        elif len(daqcond) > 1:
            gLogger.debug("Too many Real DataTaking conditions:", str(daqcond))
        else:
            daqParam = DataTakingConditions()
            node = daqcond[0]
            gLogger.debug("Found Real DataTaking conditions:", str(node))
            parameters = node.getElementsByTagName("Parameter")
            for param in parameters:
                name = param.getAttributeNode("Name")
                value = param.getAttributeNode("Value")
                if name is None or value is None:
                    gLogger.warn("<Name>  or <Value> DataTakingConditions XML tag is missing!!")
                else:
                    daqParam.parameters[name.value] = value.value
                    job.dataTakingCondition = daqParam
