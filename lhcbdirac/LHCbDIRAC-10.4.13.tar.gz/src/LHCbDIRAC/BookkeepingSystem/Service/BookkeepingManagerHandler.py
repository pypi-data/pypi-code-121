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
"""BookkeepingManager service is the front-end to the Bookkeeping database."""
import six

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.Core.Utilities.Decorators import deprecated
from DIRAC.ConfigurationSystem.Client.PathFinder import getServiceSection
from DIRAC.ConfigurationSystem.Client.Helpers import cfgPath
from DIRAC.ConfigurationSystem.Client.Config import gConfig


from LHCbDIRAC.BookkeepingSystem.DB.OracleBookkeepingDB import OracleBookkeepingDB
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.XMLFilesReaderManager import XMLFilesReaderManager
from LHCbDIRAC.BookkeepingSystem.Client import JEncoder
from LHCbDIRAC.BookkeepingSystem.DB.Utilities import checkEnoughBKArguments

# pylint: disable=invalid-name


default = "ALL"


class BookkeepingManagerHandler(RequestHandler):

    """Bookkeeping Service class.

    It serves the requests made the users by using the BookkeepingClient.
    """

    @classmethod
    def initializeHandler(cls, serviceInfoDict):
        """Initializes the variables used to identify queries, which are not
        containing enough conditions."""

        cls.bkkDB = OracleBookkeepingDB()
        cls.xmlReader = XMLFilesReaderManager()
        cls.__eventTypeCache = {}

        bkkSection = getServiceSection("Bookkeeping", "BookkeepingManager")
        if not bkkSection:
            cls.email = "lhcb-bookkeeping@cern.ch"
            cls.forceExecution = False
        else:
            cls.email = gConfig.getValue(cfgPath(bkkSection, "Email"), "lhcb-bookkeeping@cern.ch")
            cls.forceExecution = gConfig.getValue(cfgPath(bkkSection, "ForceExecution"), False)
        gLogger.info("Email used to track queries: %s forceExecution" % cls.email, cls.forceExecution)
        return S_OK()

    #############################################################################
    types_sendXMLBookkeepingReport = [six.string_types]

    def export_sendXMLBookkeepingReport(self, xml):
        """This method is used to upload an xml report which is produced after when
        the job successfully finished. The input parameter 'xml' is a string which
        contains various information (metadata) about the finished job in the Grid
        in an XML format.

        :param str xml: bookkeeping report
        """
        retVal = self.xmlReader.readXMLfromString(xml)
        if not retVal["OK"]:
            self.log.error("Issue reading XML", retVal["Message"])
        elif retVal["Value"] == "":
            return S_OK("The send bookkeeping finished successfully!")
        return retVal

    #############################################################################
    types_getAvailableSteps = [dict]

    @classmethod
    def export_getAvailableSteps(cls, in_dict):
        """It returns all the available steps which corresponds to a given
        conditions.

        The in_dict contains the following conditions: StartDate, StepId,
        InputFileTypes, OutputFileTypes,     ApplicationName,
        ApplicationVersion, OptionFiles, DDDB, CONDDB, ExtraPackages,
        Visible, ProcessingPass, Usable, RuntimeProjects, DQTag,
        OptionsFormat, StartItem, MaxItem
        """
        return cls.bkkDB.getAvailableSteps(in_dict)

    #############################################################################
    types_getRuntimeProjects = [dict]

    @classmethod
    def export_getRuntimeProjects(cls, in_dict):
        """It returns a runtime project for a given step.

        The input parameter is a in_dictionary which has only one key StepId
        """
        return cls.bkkDB.getRuntimeProjects(in_dict)

    #############################################################################
    types_getStepInputFiles = [int]

    @classmethod
    def export_getStepInputFiles(cls, stepId):
        """It returns the input files for a given step."""
        retVal = cls.bkkDB.getStepInputFiles(stepId)
        if not retVal["OK"]:
            return retVal

        records = [list(record) for record in retVal["Value"]]
        return S_OK({"ParameterNames": ["FileType", "Visible"], "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_setStepInputFiles = [int, list]

    @classmethod
    def export_setStepInputFiles(cls, stepid, files):
        """It is used to set input file types to a Step."""
        return cls.bkkDB.setStepInputFiles(stepid, files)

    #############################################################################
    types_setStepOutputFiles = [int, list]

    @classmethod
    def export_setStepOutputFiles(cls, stepid, files):
        """It is used to set output file types to a Step."""
        return cls.bkkDB.setStepOutputFiles(stepid, files)

    #############################################################################
    types_getStepOutputFiles = [int]

    @classmethod
    def export_getStepOutputFiles(cls, stepId):
        """It returns the output file types for a given Step."""
        retVal = cls.bkkDB.getStepOutputFiles(stepId)
        if not retVal["OK"]:
            return retVal

        records = []
        parameters = ["FileType", "Visible"]
        for record in retVal["Value"]:
            records += [list(record)]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getAvailableFileTypes = []

    @classmethod
    def export_getAvailableFileTypes(
        cls,
    ):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getAvailableFileTypes()

    #############################################################################
    types_insertFileTypes = [six.string_types, six.string_types, six.string_types]

    @classmethod
    def export_insertFileTypes(cls, ftype, desc, fileType):
        """It is used to register a file type. It has the following input
        parameters:

        :param str ftype: file type; for example: COOL.DST
        :param str desc: a short description which describes the file content
        :paran str fileType: the file format such as ROOT, POOL_ROOT, etc.
        """
        return cls.bkkDB.insertFileTypes(ftype, desc, fileType)

    #############################################################################
    types_insertStep = [dict]

    @classmethod
    def export_insertStep(cls, in_dict):
        """It used to insert a step to the Bookkeeping Metadata Catalogue. The
        imput parameter is a dictionary which contains the steps attributes. For
        example: Dictionary format:

        {'Step': {'ApplicationName': 'DaVinci',
        'Usable': 'Yes',
        'StepId': '',
        'ApplicationVersion': 'v29r1', 'ext-comp-1273':
        'CHARM.MDST (Charm micro dst)', 'ExtraPackages': '', 'StepName': 'davinci prb2',
        'ProcessingPass': 'WG-Coool', 'ext-comp-1264': 'CHARM.DST (Charm stream)', 'Visible': 'Y', 'DDDB': '',
        'OptionFiles': '', 'CONDDB': ''}, 'OutputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.MDST'}],
        'InputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.DST'}],'RuntimeProjects':[{StepId:13878}]}
        """
        return cls.bkkDB.insertStep(in_dict)

    #############################################################################
    types_deleteStep = [int]

    @classmethod
    def export_deleteStep(cls, stepid):
        """It used to delete a given step."""
        return cls.bkkDB.deleteStep(stepid)

    #############################################################################
    types_deleteStepContainer = [int]

    @classmethod
    def export_deleteStepContainer(cls, stepid):
        """It used to delete a given step."""
        return cls.bkkDB.deleteStepContainer(stepid)

    #############################################################################
    types_updateStep = [dict]

    @classmethod
    def export_updateStep(cls, in_dict):
        """It is used to modify the step attributes."""
        return cls.bkkDB.updateStep(in_dict)

    ##############################################################################
    types_getAvailableConfigNames = []

    @classmethod
    def export_getAvailableConfigNames(cls):
        """It returns all the available configuration names which are used."""
        retVal = cls.bkkDB.getAvailableConfigNames()
        if not retVal["OK"]:
            return retVal

        records = [list(record) for record in retVal["Value"]]
        return S_OK({"ParameterNames": ["Configuration Name"], "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getConfigVersions = [dict]

    @classmethod
    def export_getConfigVersions(cls, in_dict):
        """It returns all the available configuration version for a given
        condition.

        Input parameter is a dictionary which has the following key: 'ConfigName'
        For example: in_dict = {'ConfigName':'MC'}
        """
        configName = in_dict.get("ConfigName", default)
        retVal = cls.bkkDB.getConfigVersions(configName)
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = ["Configuration Version"]
        for record in retVal["Value"]:
            records += [list(record)]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getConditions = [dict]

    @classmethod
    def export_getConditions(cls, in_dict):
        """It returns all the available conditions for a given conditions.

        Input parameter is a dictionary which has the following keys: 'ConfigName', 'ConfigVersion', 'EventType'
        For example: in_dict = {'ConfigName':'MC','ConfigVersion':'MC10'}
        """
        result = S_ERROR()
        ok = True
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))

        if "EventTypeId" in in_dict:
            gLogger.verbose("EventTypeId will be not accepted! Please change it to EventType")

        retVal = cls.bkkDB.getConditions(configName, configVersion, evt)
        if retVal["OK"]:
            values = retVal["Value"]
            sim_parameters = [
                "SimId",
                "Description",
                "BeamCondition",
                "BeamEnergy",
                "Generator",
                "MagneticField",
                "DetectorCondition",
                "Luminosity",
                "G4settings",
            ]
            daq_parameters = [
                "DaqperiodId",
                "Description",
                "BeamCondition",
                "BeanEnergy",
                "MagneticField",
                "VELO",
                "IT",
                "TT",
                "OT",
                "RICH1",
                "RICH2",
                "SPD_PRS",
                "ECAL",
                "HCAL",
                "MUON",
                "L0",
                "HLT",
                "VeloPosition",
            ]
            sim_records = []
            daq_records = []

            if len(values) > 0:
                for record in values:
                    if record[0] is not None:
                        sim_records += [
                            [
                                record[0],
                                record[2],
                                record[3],
                                record[4],
                                record[5],
                                record[6],
                                record[7],
                                record[8],
                                record[9],
                            ]
                        ]
                    elif record[1] is not None:
                        daq_records += [
                            [
                                record[1],
                                record[10],
                                record[11],
                                record[12],
                                record[13],
                                record[14],
                                record[15],
                                record[16],
                                record[17],
                                record[18],
                                record[19],
                                record[20],
                                record[21],
                                record[22],
                                record[23],
                                record[24],
                                record[25],
                                record[26],
                            ]
                        ]
                    else:
                        result = S_ERROR("Condition does not existis!")
                        ok = False
            if ok:
                result = S_OK(
                    [
                        {"ParameterNames": sim_parameters, "Records": sim_records, "TotalRecords": len(sim_records)},
                        {"ParameterNames": daq_parameters, "Records": daq_records, "TotalRecords": len(daq_records)},
                    ]
                )
        else:
            result = retVal

        return result

    #############################################################################
    types_getProcessingPass = [dict, six.string_types]

    @classmethod
    def export_getProcessingPass(cls, in_dict, path=None):
        """It returns the processing pass for a given conditions.

        Input parameter is a dictionary and a path (string) which has the following keys:
        'ConfigName', 'ConfigVersion', 'ConditionDescription','Production', 'RunNumber', 'EventType'
        This method is used to recursively browse the processing pass.
        To start the browsing you have to define the path as a root: path = '/'
        Note: it returns a list with two dictionary. First dictionary contains the processing passes
        while the second dictionary contains the event types.
        """
        if path is None:
            path = "/"
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        prod = in_dict.get("Production", default)
        runnb = in_dict.get("RunNumber", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        return cls.bkkDB.getProcessingPass(configName, configVersion, conddescription, runnb, prod, evt, path)

    #############################################################################
    types_getProductions = [dict]

    @classmethod
    def export_getProductions(cls, in_dict):
        """It returns the productions for a given conditions.

        Input parameter is a dictionary which has the following keys:
        'ConfigName', 'ConfigVersion', 'ConditionDescription',
        'EventType','ProcessingPass'
        """
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        ftype = in_dict.get("FileType", default)
        visible = in_dict.get("Visible", "Y")
        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        retVal = cls.bkkDB.getProductions(
            configName, configVersion, conddescription, processing, evt, visible, ftype, replicaFlag
        )
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = ["Production/RunNumber"]
        for record in retVal["Value"]:
            records += [[record[0]]]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getFileTypes = [dict]

    @classmethod
    def export_getFileTypes(cls, in_dict):
        """It returns the file types for a given conditions.

        Input parameter is a dictionary which has the following keys:
        'ConfigName', 'ConfigVersion', 'ConditionDescription', 'EventType','ProcessingPass','Production','RunNumber'
        """
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        runnb = in_dict.get("RunNumber", default)
        visible = in_dict.get("Visible", "Y")
        replicaflag = in_dict.get("ReplicaFlag", "Yes")

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        retVal = cls.bkkDB.getFileTypes(
            configName, configVersion, conddescription, processing, evt, runnb, production, visible, replicaflag
        )
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = ["FileTypes"]
        for record in retVal["Value"]:
            records += [[record[0]]]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    def transfer_toClient(self, parameters, token, fileHelper):
        """This method used to transfer data using a file.

        Currently two client methods are using this function: getFiles,
        getFilesWithMetadata
        """
        result = S_OK()
        in_dict = JEncoder.loads(parameters)
        gLogger.verbose("The following dictionary received:", "%s" % in_dict)
        methodName = in_dict.get("MethodName", default)
        if methodName == "getFiles":
            retVal = self.__getFiles(in_dict)
        else:
            retVal = self.__getFilesWithMetadata(in_dict)

        fileString = JEncoder.dumps(retVal)

        retVal = fileHelper.stringToNetwork(fileString)
        if retVal["OK"]:
            gLogger.debug("Sent files for", "%s of size %d" % (in_dict, len(fileString)))
        else:
            gLogger.error("Failed to send files:", "%s" % in_dict)
            result = retVal
        return result

    #############################################################################
    @classmethod
    @checkEnoughBKArguments
    def __getFiles(cls, in_dict):
        """It returns a list of files."""
        simdesc = in_dict.get("SimulationConditions", default)
        datataking = in_dict.get("DataTakingConditions", default)
        procPass = in_dict.get("ProcessingPass", default)
        ftype = in_dict.get("FileType", default)
        evt = in_dict.get("EventType", default)
        configname = in_dict.get("ConfigName", default)
        configversion = in_dict.get("ConfigVersion", default)
        prod = in_dict.get("Production", in_dict.get("ProductionID", default))
        flag = in_dict.get("DataQuality", in_dict.get("DataQualityFlag", default))
        startd = in_dict.get("StartDate", None)
        endd = in_dict.get("EndDate", None)
        nbofevents = in_dict.get("NbOfEvents", False)
        startRunID = in_dict.get("StartRun", None)
        endRunID = in_dict.get("EndRun", None)
        runNbs = in_dict.get("RunNumber", in_dict.get("RunNumbers", []))
        if not isinstance(runNbs, list):
            runNbs = [runNbs]
        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        visible = in_dict.get("Visible", default)
        filesize = in_dict.get("FileSize", False)
        tck = in_dict.get("TCK", [])
        jobStart = in_dict.get("JobStartDate", None)
        jobEnd = in_dict.get("JobEndDate", None)

        if "ProductionID" in in_dict:
            gLogger.verbose("ProductionID will be removed. It will changed to Production")

        if "DataQualityFlag" in in_dict:
            gLogger.verbose("DataQualityFlag will be removed. It will changed to DataQuality")

        if "RunNumbers" in in_dict:
            gLogger.verbose("RunNumbers will be removed. It will changed to RunNumbers")

        result = []
        retVal = cls.bkkDB.getFiles(
            simdesc,
            datataking,
            procPass,
            ftype,
            evt,
            configname,
            configversion,
            prod,
            flag,
            startd,
            endd,
            nbofevents,
            startRunID,
            endRunID,
            runNbs,
            replicaFlag,
            visible,
            filesize,
            tck,
            jobStart,
            jobEnd,
        )
        if not retVal["OK"]:
            result = retVal
        else:
            values = retVal["Value"]
            for i in values:
                result += [i[0]]
            result = S_OK(result)

        return result

    #############################################################################
    @classmethod
    @checkEnoughBKArguments
    def __getFilesWithMetadata(cls, in_dict):
        """It returns the files with their metadata."""
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        filetype = in_dict.get("FileType", default)
        quality = in_dict.get("DataQuality", in_dict.get("Quality", default))
        visible = in_dict.get("Visible", "Y")
        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        startDate = in_dict.get("StartDate", None)
        endDate = in_dict.get("EndDate", None)
        runnumbers = in_dict.get("RunNumber", in_dict.get("RunNumbers", []))
        startRunID = in_dict.get("StartRun", None)
        endRunID = in_dict.get("EndRun", None)
        tcks = in_dict.get("TCK")
        jobStart = in_dict.get("JobStartDate", None)
        jobEnd = in_dict.get("JobEndDate", None)

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        if "Quality" in in_dict:
            gLogger.verbose("The Quality has to be replaced by DataQuality!")

        retVal = cls.bkkDB.getFilesWithMetadata(
            configName,
            configVersion,
            conddescription,
            processing,
            evt,
            production,
            filetype,
            quality,
            visible,
            replicaFlag,
            startDate,
            endDate,
            runnumbers,
            startRunID,
            endRunID,
            tcks,
            jobStart,
            jobEnd,
        )
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = [
            "FileName",
            "EventStat",
            "FileSize",
            "CreationDate",
            "JobStart",
            "JobEnd",
            "WorkerNode",
            "FileType",
            "RunNumber",
            "FillNumber",
            "FullStat",
            "DataqualityFlag",
            "EventInputStat",
            "TotalLuminosity",
            "Luminosity",
            "InstLuminosity",
            "TCK",
            "GUID",
            "ADLER32",
            "EventType",
            "MD5SUM",
            "VisibilityFlag",
            "JobId",
            "GotReplica",
            "InsertTimeStamp",
        ]
        for record in retVal["Value"]:
            records += [
                [
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    record[7],
                    record[8],
                    record[9],
                    record[10],
                    record[11],
                    record[12],
                    record[13],
                    record[14],
                    record[15],
                    record[16],
                    record[17],
                    record[18],
                    record[19],
                    record[20],
                    record[21],
                    record[22],
                    record[23],
                    record[24],
                ]
            ]
        return {"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)}

    #############################################################################
    types_getFilesSummary = [dict]

    @checkEnoughBKArguments
    def export_getFilesSummary(self, in_dict):
        """It returns sumary for a given data set.

        Input parameter is a dictionary which has the following keys:
        'ConfigName', 'ConfigVersion', 'ConditionDescription', 'EventType',
        'ProcessingPass','Production','RunNumber', 'FileType', DataQuality
        """
        gLogger.debug("Input:", "%s" % in_dict)

        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        condDescription = in_dict.get("ConditionDescription", default)
        processingPass = in_dict.get("ProcessingPass", default)
        eventType = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        fileType = in_dict.get("FileType", default)
        dataQuality = in_dict.get("DataQuality", in_dict.get("Quality", default))
        startRun = in_dict.get("StartRun", None)
        endRun = in_dict.get("EndRun", None)
        visible = in_dict.get("Visible", "Y")
        startDate = in_dict.get("StartDate", None)
        endDate = in_dict.get("EndDate", None)
        runNumbers = in_dict.get("RunNumber", in_dict.get("RunNumbers", []))
        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        tcks = in_dict.get("TCK")
        jobStart = in_dict.get("JobStartDate", None)
        jobEnd = in_dict.get("JobEndDate", None)

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        if "Quality" in in_dict:
            gLogger.verbose("The Quality has to be replaced by DataQuality!")

        retVal = self.bkkDB.getFilesSummary(
            configName=configName,
            configVersion=configVersion,
            conditionDescription=condDescription,
            processingPass=processingPass,
            eventType=eventType,
            production=production,
            fileType=fileType,
            dataQuality=dataQuality,
            startRun=startRun,
            endRun=endRun,
            visible=visible,
            startDate=startDate,
            endDate=endDate,
            runNumbers=runNumbers,
            replicaFlag=replicaFlag,
            tcks=tcks,
            jobStart=jobStart,
            jobEnd=jobEnd,
        )
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = ["NbofFiles", "NumberOfEvents", "FileSize", "Luminosity", "InstLuminosity"]
        for record in retVal["Value"]:
            records += [[record[0], record[1], record[2], record[3], record[4]]]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getLimitedFiles = [dict]

    @classmethod
    def export_getLimitedFiles(cls, in_dict):
        """It returns a chunk of files.

        This method is equivalent to the getFiles.
        """
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        filetype = in_dict.get("FileType", default)
        quality = in_dict.get("DataQuality", in_dict.get("Quality", default))
        runnb = in_dict.get("RunNumbers", in_dict.get("RunNumber", default))
        start = in_dict.get("StartItem", 0)
        maxValue = in_dict.get("MaxItem", 10)

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        if "Quality" in in_dict:
            gLogger.verbose("The Quality has to be replaced by DataQuality!")

        retVal = cls.bkkDB.getLimitedFiles(
            configName,
            configVersion,
            conddescription,
            processing,
            evt,
            production,
            filetype,
            quality,
            runnb,
            start,
            maxValue,
        )
        if not retVal["OK"]:
            return retVal
        records = []
        parameters = [
            "Name",
            "EventStat",
            "FileSize",
            "CreationDate",
            "JobStart",
            "JobEnd",
            "WorkerNode",
            "FileType",
            "EventType",
            "RunNumber",
            "FillNumber",
            "FullStat",
            "DataqualityFlag",
            "EventInputStat",
            "TotalLuminosity",
            "Luminosity",
            "InstLuminosity",
            "TCK",
            "WNMJFHS06",
            "HLT2TCK",
            "NumberOfProcessors",
        ]
        for record in retVal["Value"]:
            records += [
                [
                    record[0],
                    record[1],
                    record[2],
                    str(record[3]),
                    str(record[4]),
                    str(record[5]),
                    record[6],
                    record[7],
                    record[8],
                    record[9],
                    record[10],
                    record[11],
                    record[12],
                    record[13],
                    record[14],
                    record[15],
                    record[16],
                    record[17],
                ]
            ]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

    #############################################################################
    types_getAvailableDataQuality = []

    @classmethod
    def export_getAvailableDataQuality(cls):
        """it returns all the available data quality flags."""
        return cls.bkkDB.getAvailableDataQuality()

    #############################################################################
    types_getAvailableProductions = []

    @classmethod
    def export_getAvailableProductions(cls):
        """It returns all the available productions which have associated file with
        replica flag yes."""
        return cls.bkkDB.getAvailableProductions()

    #############################################################################
    types_getAvailableRuns = []

    @classmethod
    def export_getAvailableRuns(cls):
        """It returns all the available runs which have associated files with
        reploica flag yes."""
        return cls.bkkDB.getAvailableRuns()

    #############################################################################
    types_getAvailableEventTypes = []

    @classmethod
    def export_getAvailableEventTypes(cls):
        """It returns all the available event types."""
        return cls.bkkDB.getAvailableEventTypes()

    #############################################################################
    types_getMoreProductionInformations = [int]

    @classmethod
    def export_getMoreProductionInformations(cls, prodid):
        """It returns inforation about a production."""
        return cls.bkkDB.getMoreProductionInformations(prodid)

    #############################################################################
    types_getJobInfo = [six.string_types]

    @classmethod
    def export_getJobInfo(cls, lfn):
        """It returns the job metadata information for a given lfn produced by this
        job."""
        return cls.bkkDB.getJobInfo(lfn)

    #############################################################################
    types_bulkJobInfo = [dict]

    @classmethod
    def export_bulkJobInfo(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.bulkJobInfo(lfns)

    #############################################################################
    types_getJobInformation = [dict]

    @classmethod
    def export_getJobInformation(cls, in_dict):
        """It returns the job metadata information for a given lfn produced by this
        job."""
        return cls.bkkDB.getJobInformation(in_dict)

    #############################################################################
    types_getRunNumber = [six.string_types]

    @classmethod
    def export_getRunNumber(cls, lfn):
        """It returns the run number for a given lfn!"""
        return cls.bkkDB.getRunNumber(lfn)

    #############################################################################
    types_getRunNbAndTck = [six.string_types]

    @classmethod
    def export_getRunNbAndTck(cls, lfn):
        """It returns the run number and tck for a given LFN."""
        return cls.bkkDB.getRunNbAndTck(lfn)

    #############################################################################
    types_getProductionFiles = [six.integer_types, six.string_types]

    @classmethod
    def export_getProductionFiles(cls, prod, fileType, replica=default):
        """It returns files and their metadata for a given production, file type
        and replica."""
        return cls.bkkDB.getProductionFiles(prod, fileType, replica)

    #############################################################################
    types_getProductionFilesBulk = [list, six.string_types]

    @classmethod
    def export_getProductionFilesBulk(cls, prods, fileType, replica=default):
        """It returns files and their metadata for list of productions, file type
        and replica."""
        return cls.bkkDB.getProductionFilesBulk(prods, fileType, replica)

    #############################################################################
    types_getAvailableRunNumbers = []

    def export_getAvailableRunNumbers(self):
        """more info in the BookkeepingClient.py."""
        return self.export_getAvailableRuns()

    #############################################################################
    types_getRunFiles = [int]

    @classmethod
    def export_getRunFiles(cls, runid):
        """It returns all the files and their metadata for a given run number!"""
        return cls.bkkDB.getRunFiles(runid)

    #############################################################################
    types_updateFileMetaData = [six.string_types, dict]

    @classmethod
    def export_updateFileMetaData(cls, filename, fileAttr):
        """This method used to modify files metadata.

        Input parametes is a stirng (filename) and a dictionary (fileAttr)
        with the file attributes. {'GUID':34826386286382,'EventStat':222222}
        """
        return cls.bkkDB.updateFileMetaData(filename, fileAttr)

    #############################################################################
    types_renameFile = [six.string_types, six.string_types]

    @classmethod
    def export_renameFile(cls, oldLFN, newLFN):
        """It allows to change the name of a file which is in the Bookkeeping
        Metadata Catalogue."""
        return cls.bkkDB.renameFile(oldLFN, newLFN)

    #############################################################################
    types_getProductionProcessingPassID = [six.integer_types]

    @classmethod
    def export_getProductionProcessingPassID(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionProcessingPassID(prodid)

    #############################################################################
    types_getProductionProcessingPass = [six.integer_types]

    @classmethod
    def export_getProductionProcessingPass(cls, prodid):
        """It returns the processing pass for a given production."""
        return cls.bkkDB.getProductionProcessingPass(prodid)

    #############################################################################
    types_insertTag = [dict]

    @classmethod
    def export_insertTag(cls, values):
        """It used to register tags (CONDB, DDDB, etc) to the database.

        The input parameter is dictionary: {'TagName':'Value'}
        """
        successfull = {}
        faild = {}

        for i in values:
            tags = values[i]
            for tag in tags:
                retVal = cls.bkkDB.existsTag(i, tag)
                if retVal["OK"] and not retVal["Value"]:
                    retVal = cls.bkkDB.insertTag(i, tag)
                    if not retVal["OK"]:
                        faild[tag] = i
                    else:
                        successfull[tag] = i
                else:
                    faild[tag] = i
        return S_OK({"Successfull": successfull, "Faild": faild})

    #############################################################################
    types_setFileDataQuality = [list, six.string_types]

    @classmethod
    def export_setFileDataQuality(cls, lfns, flag):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.setFileDataQuality(lfns, flag)

    #############################################################################
    types_setRunAndProcessingPassDataQuality = [six.integer_types, six.string_types, six.string_types]

    @classmethod
    def export_setRunAndProcessingPassDataQuality(cls, runNB, procpass, flag):
        """It sets the data quality to a run which belong to a given processing
        pass.

        This method insert a new row to the runquality table. This value
        used to set the data quality flag to a given run files which
        processed by a given processing pass.
        """
        return cls.bkkDB.setRunAndProcessingPassDataQuality(runNB, procpass, flag)

    #############################################################################
    types_setRunDataQuality = [int, six.string_types]

    @classmethod
    def export_setRunDataQuality(cls, runNb, flag):
        """It sets the data quality for a given run!

        The input parameter is the run number and a data quality flag.
        """
        return cls.bkkDB.setRunDataQuality(runNb, flag)

    #############################################################################
    types_setQualityRun = [int, six.string_types]

    @classmethod
    def export_setQualityRun(cls, runNb, flag):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.setRunDataQuality(runNb, flag)

    #############################################################################
    types_setProductionDataQuality = [int, six.string_types]

    @classmethod
    def export_setProductionDataQuality(cls, prod, flag):
        """It sets the data quality for a given production!"""
        return cls.bkkDB.setProductionDataQuality(prod, flag)

    #############################################################################
    types_getFileAncestors = [list, int, bool]

    @classmethod
    def export_getFileAncestors(cls, lfns, depth=None, replica=None):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileAncestors(lfns, depth, replica)

    #############################################################################
    types_getAllAncestors = [list, int]

    @classmethod
    def export_getAllAncestors(cls, lfns, depth):
        """more info in the BookkeepingClient.py."""
        retVal = cls.bkkDB.getFileAncestors(lfns, depth, False)
        if not retVal["OK"]:
            return retVal
        values = retVal["Value"]
        for key, value in values["Successful"].items():
            values["Successful"][key] = [i["FileName"] for i in value]
        return S_OK(values)

    #############################################################################
    types_getAncestors = [list, int]

    @classmethod
    def export_getAncestors(cls, lfns, depth):
        """Get the ancestors for a list of LFNs in input"""
        retVal = cls.bkkDB.getFileAncestors(lfns, depth, True)
        if not retVal["OK"]:
            return retVal
        values = retVal["Value"]
        for key, value in values["Successful"].items():
            values["Successful"][key] = [i["FileName"] for i in value]
        return S_OK(values)

    #############################################################################
    types_getAllAncestorsWithFileMetaData = [list, int]

    @classmethod
    def export_getAllAncestorsWithFileMetaData(cls, lfns, depth):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileAncestors(lfns, depth, False)

    #############################################################################
    types_getAllDescendents = [list, int, int, bool]

    @classmethod
    def export_getAllDescendents(cls, lfn, depth=0, production=0, checkreplica=False):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileDescendents(lfn, depth, production, checkreplica)

    #############################################################################
    types_getDescendents = [list, int]

    def export_getDescendents(self, lfn, depth):
        """more info in the BookkeepingClient.py."""
        return self.export_getFileDescendants(lfn, depth)

    #############################################################################
    types_getFileDescendents = [list, int, int, bool]

    @classmethod
    def export_getFileDescendents(cls, lfn, depth, production=0, checkreplica=True):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileDescendents(lfn, depth, production, checkreplica)

    #############################################################################
    types_getFileDescendants = [list, int, int, bool]

    def export_getFileDescendants(self, lfn, depth, production=0, checkreplica=True):
        """more info in the BookkeepingClient.py."""
        return self.export_getFileDescendents(lfn, depth, production, checkreplica)

    #############################################################################
    types_checkfile = [six.string_types]

    @classmethod
    def export_checkfile(cls, fileName):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.checkfile(fileName)

    #############################################################################
    types_checkFileTypeAndVersion = [six.string_types, six.string_types]

    @classmethod
    def export_checkFileTypeAndVersion(cls, ftype, version):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.checkFileTypeAndVersion(ftype, version)

    #############################################################################
    types_checkEventType = [six.integer_types]

    @classmethod
    def export_checkEventType(cls, eventTypeId):
        """more info in the BookkeepingClient.py."""
        if eventTypeId not in cls.__eventTypeCache:
            retVal = cls.bkkDB.checkEventType(eventTypeId)
            if not retVal["OK"]:
                return retVal
            cls.__eventTypeCache[eventTypeId] = retVal

        return cls.__eventTypeCache[eventTypeId]

    #############################################################################
    types_insertSimConditions = [dict]

    @classmethod
    def export_insertSimConditions(cls, in_dict):
        """It inserts a simulation condition to the Bookkeeping Metadata
        catalogue."""
        return cls.bkkDB.insertSimConditions(in_dict)

    #############################################################################
    types_getSimConditions = []

    @classmethod
    def export_getSimConditions(cls):
        """It returns all the simulation conditions which are in the Bookkeeping
        Metadata catalogue."""
        return cls.bkkDB.getSimConditions()

    #############################################################################
    types_removeReplica = [six.string_types]

    @classmethod
    def export_removeReplica(cls, fileName):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.removeReplica(fileName)

    #############################################################################
    types_getFileMetadata = [list]

    @classmethod
    def export_getFileMetadata(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileMetadata(lfns)

    #############################################################################
    types_getFilesInformations = [list]

    @classmethod
    def export_getFilesInformations(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileMetadata(lfns)

    #############################################################################
    types_getFileMetaDataForUsers = [list]

    @classmethod
    def export_getFileMetaDataForUsers(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileMetaDataForWeb(lfns)

    #############################################################################
    types_getFileMetaDataForWeb = [list]

    @classmethod
    def export_getFileMetaDataForWeb(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileMetaDataForWeb(lfns)

    #############################################################################
    types_getProductionFilesForUsers = [int, dict, dict, six.integer_types, six.integer_types]

    @classmethod
    def export_getProductionFilesForUsers(cls, prod, ftype, sortDict, startItem, maxitems):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionFilesForWeb(prod, ftype, sortDict, startItem, maxitems)

    #############################################################################
    types_getProductionFilesForWeb = [six.integer_types, dict, dict, six.integer_types, six.integer_types]

    @classmethod
    def export_getProductionFilesWeb(cls, prod, ftype, sortDict, startItem, maxitems):
        """It returns files and their metadata information for a given
        production."""
        return cls.bkkDB.getProductionFilesForWeb(prod, ftype, sortDict, startItem, maxitems)

    #############################################################################
    types_exists = [list]

    @classmethod
    def export_exists(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.exists(lfns)

    #############################################################################
    types_addReplica = [list]

    @classmethod
    def export_addReplica(cls, fileName):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.addReplica(fileName)

    #############################################################################
    types_getRunInformations = [six.integer_types]

    @classmethod
    def export_getRunInformations(cls, runnb):
        """It returns run information and statistics."""
        return cls.bkkDB.getRunInformations(runnb)

    #############################################################################
    types_getRunInformation = [dict]

    @classmethod
    def export_getRunInformation(cls, runnb):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getRunInformation(runnb)

    #############################################################################
    types_getFileCreationLog = [six.string_types]

    @classmethod
    def export_getFileCreationLog(cls, lfn):
        """For a given file returns the log files of the job which created it."""
        return cls.bkkDB.getFileCreationLog(lfn)

    #############################################################################
    types_getLogfile = [six.string_types]

    @classmethod
    def export_getLogfile(cls, lfn):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileCreationLog(lfn)

    #############################################################################
    types_insertEventType = [six.integer_types, six.string_types, six.string_types]

    @classmethod
    def export_insertEventType(cls, evid, desc, primary):
        """It inserts an event type to the Bookkeeping Metadata catalogue."""
        retVal = cls.bkkDB.checkEventType(evid)
        if not retVal["OK"]:  # meaning the event type is not already inserted
            retVal = cls.bkkDB.insertEventTypes(evid, desc, primary)
            if not retVal["OK"]:
                return retVal
            return S_OK(str(evid) + " event type added successfully!")
        return S_OK(str(evid) + " event type exists")

    #############################################################################
    types_addEventType = [six.integer_types, six.string_types, six.string_types]

    def export_addEventType(self, evid, desc, primary):
        """more info in the BookkeepingClient.py."""
        return self.export_insertEventType(evid, desc, primary)

    #############################################################################
    types_updateEventType = [six.integer_types, six.string_types, six.string_types]

    @classmethod
    def export_updateEventType(cls, evid, desc, primary):
        """It can used to modify an existing event type."""

        retVal = cls.bkkDB.checkEventType(evid)
        if not retVal["OK"]:
            return S_ERROR(str(evid) + " event type is missing in the BKK database!")

        retVal = cls.bkkDB.updateEventType(evid, desc, primary)
        if not retVal["OK"]:
            return retVal
        return S_OK(str(evid) + " event type updated successfully!")

    #############################################################################
    types_addFiles = [list]

    @classmethod
    def export_addFiles(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.addReplica(lfns)

    #############################################################################
    types_removeFiles = [list]

    @classmethod
    def export_removeFiles(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.removeReplica(lfns)

    #############################################################################
    types_getProductionSummary = [dict]

    @classmethod
    def export_getProductionSummary(cls, in_dict):
        """It can used to count the number of events for a given dataset."""

        cName = in_dict.get("ConfigName", default)
        cVersion = in_dict.get("ConfigVersion", default)
        production = in_dict.get("Production", default)
        simdesc = in_dict.get("ConditionDescription", default)
        pgroup = in_dict.get("ProcessingPass", default)
        ftype = in_dict.get("FileType", default)
        evttype = in_dict.get("EventType", default)
        return cls.bkkDB.getProductionSummary(cName, cVersion, simdesc, pgroup, production, ftype, evttype)

    #############################################################################
    types_getProductionInformation = [six.integer_types]

    def export_getProductionInformation(self, prodid):
        """It returns statistics (data processing phases, number of events, etc.) for a given production"""

        nbjobs = None
        nbOfFiles = None
        nbOfEvents = None
        prodinfos = None

        value = self.bkkDB.getProductionNbOfJobs(prodid)
        if value["OK"]:
            nbjobs = value["Value"]

        value = self.bkkDB.getProductionNbOfFiles(prodid)
        if value["OK"]:
            nbOfFiles = value["Value"]

        value = self.bkkDB.getProductionNbOfEvents(prodid)
        if value["OK"]:
            nbOfEvents = value["Value"]

        value = self.bkkDB.getConfigsAndEvtType(prodid)
        if value["OK"]:
            prodinfos = value["Value"]

        path = "/"

        if not prodinfos:
            self.log.error("No Configs/Event type for production", prodid)
            return S_ERROR("No Configs/Event type")

        cname = prodinfos[0][0]
        cversion = prodinfos[0][1]
        path += cname + "/" + cversion + "/"

        res = self.bkkDB.getProductionSimulationCond(prodid)
        if not res["OK"]:
            return res
        path += res["Value"]

        res = self.bkkDB.getProductionProcessingPass(prodid)
        if not res["OK"]:
            return res
        path += res["Value"]
        prefix = "\n" + path

        # FIXME: I think this will crash due to iterating over None if cls.bkkDB.getProductionNbOfEvents(prodid) fails.
        # FIXME: I also have no idea what i is. At at glance I thought it was an integer but its being indexed?
        # FIXME: Why only index 0 and 2? The docstring of getProductionNbOfEvents should probably be fixed.
        for i in nbOfEvents:
            path += prefix + "/" + str(i[2]) + "/" + i[0]
        result = {
            "Production information": prodinfos,
            "Number of jobs": nbjobs,
            "Number of files": nbOfFiles,
            "Number of events": nbOfEvents,
            "Path": path,
        }
        return S_OK(result)

    #############################################################################
    types_getFileHistory = [six.string_types]

    @classmethod
    def export_getFileHistory(cls, lfn):
        """It returns all the information about a file."""
        retVal = cls.bkkDB.getFileHistory(lfn)
        result = {}
        records = []
        if retVal["OK"]:
            values = retVal["Value"]
            parameterNames = [
                "FileId",
                "FileName",
                "ADLER32",
                "CreationDate",
                "EventStat",
                "Eventtype",
                "Gotreplica",
                "GUI",
                "JobId",
                "md5sum",
                "FileSize",
                "FullStat",
                "Dataquality",
                "FileInsertDate",
                "Luminosity",
                "InstLuminosity",
            ]
            counter = 0
            for record in values:
                value = [
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    record[7],
                    record[8],
                    record[9],
                    record[10],
                    record[11],
                    record[12],
                    record[13],
                    record[14],
                    record[15],
                ]
                records += [value]
                counter += 1
            result = {"ParameterNames": parameterNames, "Records": records, "TotalRecords": counter}
        else:
            result = S_ERROR(retVal["Message"])
        return S_OK(result)

    #############################################################################
    types_getJobsNb = [six.integer_types]

    @classmethod
    @deprecated("Use getProductionNbOfJobs")
    def export_getJobsNb(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionNbOfJobs(prodid)

    #############################################################################
    types_getProductionNbOfJobs = [six.integer_types]

    @classmethod
    def export_getProductionNbOfJobs(cls, prodid):
        """It returns the number of jobs for a given production."""
        return cls.bkkDB.getProductionNbOfJobs(prodid)

    #############################################################################
    types_getNumberOfEvents = [six.integer_types]

    @classmethod
    @deprecated("Use getProductionNbOfEvents")
    def export_getNumberOfEvents(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionNbOfEvents(prodid)

    #############################################################################
    types_getProductionNbOfEvents = [six.integer_types]

    @classmethod
    def export_getProductionNbOfEvents(cls, prodid):
        """It returns the number of events for a given production."""
        return cls.bkkDB.getProductionNbOfEvents(prodid)

    #############################################################################
    types_getSizeOfFiles = [six.integer_types]

    @classmethod
    @deprecated("Use getProductionSizeOfFiles")
    def export_getSizeOfFiles(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionSizeOfFiles(prodid)

    #############################################################################
    types_getProductionSizeOfFiles = [six.integer_types]

    @classmethod
    def export_getProductionSizeOfFiles(cls, prodid):
        """It returns the size of files for a given production."""
        return cls.bkkDB.getProductionSizeOfFiles(prodid)

    #############################################################################
    types_getNbOfFiles = [six.integer_types]

    @classmethod
    @deprecated("Use getProductionNbOfFiles")
    def export_getNbOfFiles(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionNbOfFiles(prodid)

    #############################################################################
    types_getProductionNbOfFiles = [six.integer_types]

    @classmethod
    def export_getProductionNbOfFiles(cls, prodid):
        """It returns the number of files produced by a given production."""
        return cls.bkkDB.getProductionNbOfFiles(prodid)

    #############################################################################
    types_getNbOfJobsBySites = [six.integer_types]

    @classmethod
    def export_getNbOfJobsBySites(cls, prodid):
        """It returns the number of jobs executed at different sites for a given
        production."""
        return cls.bkkDB.getNbOfJobsBySites(prodid)

    #############################################################################
    types_getAvailableTags = []

    @classmethod
    def export_getAvailableTags(cls):
        """It returns the available database tags."""
        return cls.bkkDB.getAvailableTags()

    #############################################################################
    types_getProcessedEvents = [six.integer_types]

    @classmethod
    @deprecated("Use getProductionProcessedEvents")
    def export_getProcessedEvents(cls, prodid):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getProductionProcessedEvents(prodid)

    #############################################################################
    types_getProductionProcessedEvents = [six.integer_types]

    @classmethod
    def export_getProductionProcessedEvents(cls, prodid):
        """it returns the number of events processed for a given production."""
        gLogger.debug("getProductionProcessedEvents->Production:", "%d " % prodid)
        return cls.bkkDB.getProductionProcessedEvents(prodid)

    #############################################################################
    types_getRunsForAGivenPeriod = [dict]

    @classmethod
    def export_getRunsForAGivenPeriod(cls, in_dict):
        """It returns the available runs between a period.

        Input parameters:
        AllowOutsideRuns: If it is true, it only returns the runs which finished before EndDate.
        StartDate: the run start period
        EndDate: the run end period
        CheckRunStatus: if it is true, it check the run is processed or not processed.
        """
        return cls.bkkDB.getRunsForAGivenPeriod(in_dict)

    #############################################################################
    types_getProductionsFromView = [dict]

    @classmethod
    @deprecated("Useless?")
    def export_getProductionsFromView(cls, in_dict):
        """It returns the productions from the bookkeeping view for a given
        processing pass and run number.

        Input parameters: RunNumber ProcessingPass
        """
        # FIXME: might be a useless method
        return cls.bkkDB.getProductionsFromView(in_dict)

    #############################################################################
    types_getRunFilesDataQuality = [list]

    @classmethod
    def export_getRunFilesDataQuality(cls, runs):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getRunFilesDataQuality(runs)

    #############################################################################
    types_setFilesInvisible = [list]

    @classmethod
    def export_setFilesInvisible(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.setFilesInvisible(lfns)

    #############################################################################
    types_setFilesVisible = [list]

    @classmethod
    def export_setFilesVisible(cls, lfns):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.setFilesVisible(lfns)

    #############################################################################
    types_getRunAndProcessingPassDataQuality = [six.integer_types, six.integer_types]

    @classmethod
    def export_getRunAndProcessingPassDataQuality(cls, runnb, processing):
        """It returns the data quality flag for a given run and processing pass."""
        return cls.bkkDB.getRunAndProcessingPassDataQuality(runnb, processing)

    #############################################################################
    types_getAvailableConfigurations = []

    @classmethod
    def export_getAvailableConfigurations(cls):
        """It returns the available configurations."""
        return cls.bkkDB.getAvailableConfigurations()

    #############################################################################
    types_getRunProcessingPass = [six.integer_types]

    @classmethod
    def export_getRunProcessingPass(cls, runnumber):
        """it returns the run number for a given run."""
        return cls.bkkDB.getRunProcessingPass(runnumber)

    #############################################################################
    types_getProductionFilesStatus = [int, list]

    @classmethod
    def export_getProductionFilesStatus(cls, productionid=None, lfns=None):
        """It returns the file status in the bkk for a given production or a list
        of lfns."""
        if not lfns:
            lfns = []
        return cls.bkkDB.getProductionFilesStatus(productionid, lfns)

    #############################################################################
    types_getFiles = [dict]

    @classmethod
    def export_getFiles(cls, values):
        """more info in the BookkeepingClient.py."""

        simdesc = values.get("SimulationConditions", default)
        datataking = values.get("DataTakingConditions", default)
        procPass = values.get("ProcessingPass", default)
        ftype = values.get("FileType", default)
        evt = values.get("EventType", 0)
        configname = values.get("ConfigName", default)
        configversion = values.get("ConfigVersion", default)
        prod = values.get("Production", values.get("ProductionID", default))
        flag = values.get("DataQuality", values.get("DataQualityFlag", default))
        startd = values.get("StartDate", None)
        endd = values.get("EndDate", None)
        nbofevents = values.get("NbOfEvents", False)
        startRunID = values.get("StartRun", None)
        endRunID = values.get("EndRun", None)
        runNbs = values.get("RunNumber", values.get("RunNumbers", []))
        if not isinstance(runNbs, list):
            runNbs = [runNbs]
        replicaFlag = values.get("ReplicaFlag", "Yes")
        visible = values.get("Visible", default)
        filesize = values.get("FileSize", False)
        tck = values.get("TCK")
        jobStart = values.get("JobStartDate", None)
        jobEnd = values.get("JobEndDate", None)

        if "ProductionID" in values:
            gLogger.verbose("ProductionID will be removed. It will changed to Production")

        if "DataQualityFlag" in values:
            gLogger.verbose("DataQualityFlag will be removed. It will changed to DataQuality")

        if "RunNumbers" in values:
            gLogger.verbose("RunNumbers will be removed. It will changed to RunNumbers")

        result = []
        retVal = cls.bkkDB.getFiles(
            simdesc,
            datataking,
            procPass,
            ftype,
            evt,
            configname,
            configversion,
            prod,
            flag,
            startd,
            endd,
            nbofevents,
            startRunID,
            endRunID,
            runNbs,
            replicaFlag,
            visible,
            filesize,
            tck,
            jobStart,
            jobEnd,
        )
        if not retVal["OK"]:
            return retVal
        values = retVal["Value"]
        for i in values:
            result += [i[0]]

        return S_OK(result)

    #############################################################################
    types_getFilesWithGivenDataSetsForUsers = [dict]

    def export_getFilesWithGivenDataSetsForUsers(self, values):
        """more info in the BookkeepingClient.py."""
        return self.export_getVisibleFilesWithMetadata(values)

    #############################################################################
    types_getVisibleFilesWithMetadata = [dict]

    @classmethod
    def export_getVisibleFilesWithMetadata(cls, in_dict):
        """It returns a list of files with metadata for a given condition."""

        conddescription = in_dict.get("SimulationConditions", in_dict.get("DataTakingConditions", default))
        procPass = in_dict.get("ProcessingPass", default)
        ftype = in_dict.get("FileType", default)
        evt = in_dict.get("EventType", default)
        configname = in_dict.get("ConfigName", default)
        configversion = in_dict.get("ConfigVersion", default)
        prod = in_dict.get("Production", in_dict.get("ProductionID", default))
        dqflag = in_dict.get("DataQuality", in_dict.get("DataQualityFlag", default))
        startd = in_dict.get("StartDate", None)
        endd = in_dict.get("EndDate", None)
        startRunID = in_dict.get("StartRun", None)
        endRunID = in_dict.get("EndRun", None)
        runNbs = in_dict.get("RunNumber", in_dict.get("RunNumbers", []))
        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        tck = in_dict.get("TCK", [])
        visible = in_dict.get("Visible", "Y")
        jobStart = in_dict.get("JobStartDate", None)
        jobEnd = in_dict.get("JobEndDate", None)

        if ftype == default:
            return S_ERROR("FileType is missing!")

        if "ProductionID" in in_dict:
            gLogger.verbose("ProductionID will be removed. It will changed to Production")

        if "DataQualityFlag" in in_dict:
            gLogger.verbose("DataQualityFlag will be removed. It will changed to DataQuality")

        if "RunNumbers" in in_dict:
            gLogger.verbose("RunNumbers will be removed. It will changed to RunNumbers")

        gLogger.debug("getVisibleFilesWithMetadata->", "%s" % in_dict)
        result = {}
        retVal = cls.bkkDB.getFilesWithMetadata(
            configName=configname,
            configVersion=configversion,
            conddescription=conddescription,
            processing=procPass,
            evt=evt,
            production=prod,
            filetype=ftype,
            quality=dqflag,
            visible=visible,
            replicaflag=replicaFlag,
            startDate=startd,
            endDate=endd,
            runnumbers=runNbs,
            startRunID=startRunID,
            endRunID=endRunID,
            tcks=tck,
            jobStart=jobStart,
            jobEnd=jobEnd,
        )

        summary = 0

        parameters = [
            "FileName",
            "EventStat",
            "FileSize",
            "CreationDate",
            "JobStart",
            "JobEnd",
            "WorkerNode",
            "FileType",
            "RunNumber",
            "FillNumber",
            "FullStat",
            "DataqualityFlag",
            "EventInputStat",
            "TotalLuminosity",
            "Luminosity",
            "InstLuminosity",
            "TCK",
            "GUID",
            "ADLER32",
            "EventType",
            "MD5SUM",
            "VisibilityFlag",
            "JobId",
            "GotReplica",
            "InsertTimeStamp",
        ]

        if not retVal["OK"]:
            return retVal

        values = retVal["Value"]
        nbfiles = 0
        nbevents = 0
        evinput = 0
        fsize = 0
        tLumi = 0
        lumi = 0
        ilumi = 0
        for i in values:
            nbfiles = nbfiles + 1
            row = dict(zip(parameters, i))
            if row["EventStat"] is not None:
                nbevents += row["EventStat"]
            if row["EventInputStat"] is not None:
                evinput += row["EventInputStat"]
            if row["FileSize"] is not None:
                fsize += row["FileSize"]
            if row["TotalLuminosity"] is not None:
                tLumi += row["TotalLuminosity"]
            if row["Luminosity"] is not None:
                lumi += row["Luminosity"]
            if row["InstLuminosity"] is not None:
                ilumi += row["InstLuminosity"]
            result[row["FileName"]] = {
                "EventStat": row["EventStat"],
                "EventInputStat": row["EventInputStat"],
                "Runnumber": row["RunNumber"],
                "Fillnumber": row["FillNumber"],
                "FileSize": row["FileSize"],
                "TotalLuminosity": row["TotalLuminosity"],
                "Luminosity": row["Luminosity"],
                "InstLuminosity": row["InstLuminosity"],
                "TCK": row["TCK"],
            }
        if nbfiles > 0:
            summary = {
                "Number Of Files": nbfiles,
                "Number of Events": nbevents,
                "EventInputStat": evinput,
                "FileSize": fsize / 1000000000.0,
                "TotalLuminosity": tLumi,
                "Luminosity": lumi,
                "InstLuminosity": ilumi,
            }
        return S_OK({"LFNs": result, "Summary": summary})

    #############################################################################
    types_addProduction = [dict]

    @classmethod
    def export_addProduction(cls, infos):
        """It is used to register a production in the bkk.

        Input parameters:
        SimulationConditions
        DataTakingConditions
        Steps: the step which is used to process data for a given production.
        Production:
        InputProductionTotalProcessingPass: it is a path of the input data processing pass
        """

        gLogger.debug("Registering:", infos)
        simcond = infos.get("SimulationConditions", None)
        daqdesc = infos.get("DataTakingConditions", None)
        production = None

        if simcond is None and daqdesc is None:
            return S_ERROR("SimulationConditions and DataTakingConditions are both missing!")

        if "Steps" not in infos:
            return S_ERROR("Missing Steps!")
        if "Production" not in infos:
            return S_ERROR("Production is missing!")
        if "EventType" not in infos:
            return S_ERROR("EventType is missing!")

        steps = infos["Steps"]
        inputProdTotalProcessingPass = ""
        production = infos["Production"]
        inputProdTotalProcessingPass = infos.get("InputProductionTotalProcessingPass", "")
        configName = infos.get("ConfigName")
        configVersion = infos.get("ConfigVersion")
        eventType = infos.get("EventType")
        return cls.bkkDB.addProduction(
            production=production,
            simcond=simcond,
            daq=daqdesc,
            steps=steps,
            inputproc=inputProdTotalProcessingPass,
            configName=configName,
            configVersion=configVersion,
            eventType=eventType,
        )

    #############################################################################
    types_getEventTypes = [dict]

    @classmethod
    def export_getEventTypes(cls, in_dict):
        """It returns the available event types for a given configuration name and
        configuration version.

        Input parameters: ConfigName, ConfigVersion, Production
        """

        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        production = in_dict.get("Production", default)
        return cls.bkkDB.getEventTypes(configName, configVersion, production)

    #############################################################################
    types_getProcessingPassSteps = [dict]

    @classmethod
    def export_getProcessingPassSteps(cls, in_dict):
        """It returns the steps for a given stepname, processing pass and
        production."""
        stepname = in_dict.get("StepName", default)
        cond = in_dict.get("ConditionDescription", default)
        procpass = in_dict.get("ProcessingPass", default)

        return cls.bkkDB.getProcessingPassSteps(procpass, cond, stepname)

    #############################################################################
    types_getProductionProcessingPassSteps = [dict]

    @classmethod
    def export_getProductionProcessingPassSteps(cls, in_dict):
        """it returns the steps for a given production."""

        if "Production" in in_dict:
            return cls.bkkDB.getProductionProcessingPassSteps(in_dict["Production"])
        return S_ERROR("The Production dictionary key is missing!!!")

    #############################################################################
    types_getProductionOutputFiles = [dict]

    @deprecated("Use getProductionOutputFileTypes")
    def export_getProductionOutputFiles(self, in_dict):
        """more info in the BookkeepingClient.py."""

        return self.export_getProductionOutputFileTypes(in_dict)

    #############################################################################
    types_getProductionOutputFileTypes = [dict]

    @classmethod
    def export_getProductionOutputFileTypes(cls, in_dict):
        """It returns the output file types which produced by a given
        production."""

        production = in_dict.get("Production", default)
        stepid = in_dict.get("StepId", default)

        if production != default:
            return cls.bkkDB.getProductionOutputFileTypes(production, stepid)
        return S_ERROR("The Production dictionary key is missing!!!")

    #############################################################################
    types_getRunQuality = [six.string_types, six.string_types]

    @deprecated("Use getRunWithProcessingPassAndDataQuality")
    def export_getRunQuality(self, procpass, flag=default):
        """more info in the BookkeepingClient.py."""

        return self.export_getRunWithProcessingPassAndDataQuality(procpass, flag)

    #############################################################################
    types_getRunWithProcessingPassAndDataQuality = [six.string_types, six.string_types]

    @classmethod
    def export_getRunWithProcessingPassAndDataQuality(cls, procpass, flag=default):
        """It returns the run number for a given processing pass and a flag from
        the run quality table."""
        return cls.bkkDB.getRunWithProcessingPassAndDataQuality(procpass, flag)

    #############################################################################
    types_getRuns = [dict]

    @classmethod
    def export_getRuns(cls, in_dict):
        """It returns the runs for a given configuration name and version.

        Input parameters:
        """
        cName = in_dict.get("ConfigName", default)
        cVersion = in_dict.get("ConfigVersion", default)
        if cName != default and cVersion != default:
            return cls.bkkDB.getRuns(cName, cVersion)
        return S_ERROR("The configuration name and version have to be defined!")

    #############################################################################
    types_getRunProcPass = [dict]

    def export_getRunProcPass(self, in_dict):
        """more info in the BookkeepingClient.py."""
        return self.export_getRunAndProcessingPass(in_dict)

    #############################################################################
    types_getRunAndProcessingPass = [dict]

    @classmethod
    def export_getRunAndProcessingPass(cls, in_dict):
        """It returns all the processing pass and run number for a given run."""
        run = in_dict.get("RunNumber", default)
        if run != default:
            return cls.bkkDB.getRunAndProcessingPass(run)
        return S_ERROR("The run number has to be specified!")

    #############################################################################
    types_getProcessingPassId = [six.string_types]

    @classmethod
    def export_getProcessingPassId(cls, fullpath):
        """It returns the ProcessingPassId for a given path.

        this method should not used!
        """
        return cls.bkkDB.getProcessingPassId(fullpath)

    #############################################################################
    types_getRunNbFiles = [dict]

    @deprecated("Use getNbOfRawFiles")
    def export_getRunNbFiles(self, in_dict):
        """more info in the BookkeepingClient.py."""
        return self.export_getNbOfRawFiles(in_dict)

    #############################################################################
    types_getNbOfRawFiles = [dict]

    @classmethod
    def export_getNbOfRawFiles(cls, in_dict):
        """It counts the raw files for a given run and (or) event type."""

        runnb = in_dict.get("RunNumber", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        replicaFlag = in_dict.get("ReplicaFlag", "Yes")
        visible = in_dict.get("Visible", "Y")
        isFinished = in_dict.get("Finished", "ALL")
        if runnb == default and evt == default:
            return S_ERROR("Run number or event type must be given!")
        retVal = cls.bkkDB.getNbOfRawFiles(runnb, evt, replicaFlag, visible, isFinished)
        if not retVal["OK"]:
            return retVal
        return S_OK(retVal["Value"][0][0])

    #############################################################################
    types_getTypeVersion = [list]

    def export_getTypeVersion(self, lfn):
        """more info in the BookkeepingClient.py."""
        return self.export_getFileTypeVersion(lfn)

    #############################################################################
    types_getFileTypeVersion = [list]

    @classmethod
    def export_getFileTypeVersion(cls, lfn):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getFileTypeVersion(lfn)

    #############################################################################
    types_getTCKs = [dict]

    @classmethod
    def export_getTCKs(cls, in_dict):
        """It returns the tcks for a given data set."""
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        filetype = in_dict.get("FileType", default)
        quality = in_dict.get("DataQuality", in_dict.get("Quality", default))
        runnb = in_dict.get("RunNumber", default)
        if "Quality" in in_dict:
            gLogger.verbose("The Quality has to be replaced by DataQuality!")

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        retVal = cls.bkkDB.getTCKs(
            configName, configVersion, conddescription, processing, evt, production, filetype, quality, runnb
        )
        if not retVal["OK"]:
            return retVal
        return S_OK([record[0] for record in retVal["Value"]])

    #############################################################################
    types_getAvailableTcks = [dict]

    def export_getAvailableTcks(self, in_dict):
        """more info in the BookkeepingClient.py."""
        return self.export_getTCKs(in_dict)

    #############################################################################
    types_getSteps = [six.integer_types]

    @classmethod
    def export_getSteps(cls, prodID):
        """get list of steps used in a production"""
        return cls.bkkDB.getSteps(prodID)

    #############################################################################
    types_getStepsMetadata = [dict]

    @classmethod
    def export_getStepsMetadata(cls, in_dict):
        """It returns the step(s) which is produced  a given dataset."""
        gLogger.debug("getStepsMetadata", "%s" % in_dict)
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        cond = in_dict.get("ConditionDescription", default)
        procpass = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
        production = in_dict.get("Production", default)
        filetype = in_dict.get("FileType", default)
        runnb = in_dict.get("RunNumber", default)

        if "EventTypeId" in in_dict:
            gLogger.verbose("The EventTypeId has to be replaced by EventType!")

        if "Quality" in in_dict:
            gLogger.verbose("The Quality has to be replaced by DataQuality!")

        return cls.bkkDB.getStepsMetadata(configName, configVersion, cond, procpass, evt, production, filetype, runnb)

    #############################################################################
    types_getDirectoryMetadata_new = [list]

    @classmethod
    @deprecated("Use getDirectoryMetadata")
    def export_getDirectoryMetadata_new(cls, lfn):
        """more info in the BookkeepingClient.py."""
        return cls.bkkDB.getDirectoryMetadata(lfn)

        #############################################################################

    types_getDirectoryMetadata = [list]

    @classmethod
    def export_getDirectoryMetadata(cls, lfn):
        """more info in the BookkeepingClient.py."""
        gLogger.verbose("Getting the metadata for:", "%s" % lfn)
        return cls.bkkDB.getDirectoryMetadata(lfn)

    #############################################################################
    types_getFilesForGUID = [six.string_types]

    @classmethod
    def export_getFilesForGUID(cls, guid):
        """It returns a file for a given GUID."""
        return cls.bkkDB.getFilesForGUID(guid)

    #############################################################################
    types_getRunsGroupedByDataTaking = []

    @classmethod
    def export_getRunsGroupedByDataTaking(cls):
        """It returns all the run numbers grouped by the data taking
        description."""
        return cls.bkkDB.getRunsGroupedByDataTaking()

    #############################################################################
    types_getListOfFills = [dict]

    @classmethod
    def export_getListOfFills(cls, in_dict):
        """It returns a list of FILL numbers for a given Configuration name,
        Configuration version and data taking description."""
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        return cls.bkkDB.getListOfFills(configName, configVersion, conddescription)

    #############################################################################
    types_getRunsForFill = [six.integer_types]

    @classmethod
    def export_getRunsForFill(cls, fillid):
        """It returns a list of runs for a given FILL."""
        return cls.bkkDB.getRunsForFill(fillid)

    #############################################################################
    types_getListOfRuns = [dict]

    @classmethod
    def export_getListOfRuns(cls, in_dict):
        """It returns a list of runs for a given conditions.

        Input parameter is a dictionary which has the following keys:
        'ConfigName', 'ConfigVersion', 'ConditionDescription',
        'EventType','ProcessingPass'
        """
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)
        conddescription = in_dict.get("ConditionDescription", default)
        processing = in_dict.get("ProcessingPass", default)
        evt = in_dict.get("EventType", default)
        quality = in_dict.get("DataQuality", default)

        retVal = cls.bkkDB.getListOfRuns(configName, configVersion, conddescription, processing, evt, quality)
        if not retVal["OK"]:
            return retVal
        return S_OK([i[0] for i in retVal["Value"]])

    #############################################################################
    types_getSimulationConditions = [dict]

    @classmethod
    def export_getSimulationConditions(cls, in_dict):
        """It returns a list of simulation conditions for a given conditions."""
        return cls.bkkDB.getSimulationConditions(in_dict)

    #############################################################################
    types_updateSimulationConditions = [dict]

    @classmethod
    def export_updateSimulationConditions(cls, in_dict):
        """It updates a given simulation condition."""
        return cls.bkkDB.updateSimulationConditions(in_dict)

    #############################################################################
    types_deleteSimulationConditions = [six.integer_types]

    @classmethod
    def export_deleteSimulationConditions(cls, simid):
        """deletes a given simulation conditions."""
        return cls.bkkDB.deleteSimulationConditions(simid)

    #############################################################################
    types_getProductionSummaryFromView = [dict]

    @classmethod
    def export_getProductionSummaryFromView(cls, in_dict):
        """it returns a summary for a given condition."""
        return cls.bkkDB.getProductionSummaryFromView(in_dict)

    types_getJobInputOutputFiles = [list]

    @classmethod
    def export_getJobInputOutputFiles(cls, diracjobids):
        """It returns the input and output files for a given DIRAC jobid."""
        return cls.bkkDB.getJobInputOutputFiles(diracjobids)

    types_setRunOnlineFinished = [six.integer_types]

    @classmethod
    def export_setRunOnlineFinished(cls, runnumber):
        """It is used to set the run finished..."""
        return cls.bkkDB.setRunStatusFinished(runnumber, "Y")

    types_setRunOnlineNotFinished = [six.integer_types]

    @classmethod
    def export_setRunOnlineNotFinished(cls, runnumber):
        """You can set the runs not finished."""
        return cls.bkkDB.setRunStatusFinished(runnumber, "N")

    types_getRunStatus = [list]

    @classmethod
    def export_getRunStatus(cls, runnumbers):
        """it returns the status of the runs."""
        return cls.bkkDB.getRunStatus(runnumbers)

    types_bulkupdateFileMetaData = [dict]

    @classmethod
    def export_bulkupdateFileMetaData(cls, lfnswithmeta):
        """It updates the file metadata."""
        return cls.bkkDB.bulkupdateFileMetaData(lfnswithmeta)

    types_fixRunLuminosity = [list]

    @classmethod
    def export_fixRunLuminosity(cls, runnumbers):
        return cls.bkkDB.fixRunLuminosity(runnumbers)

    #############################################################################
    types_getProductionProducedEvents = [six.integer_types]

    @classmethod
    def export_getProductionProducedEvents(cls, prodid):
        """it returns the number of events producced for a given production."""
        gLogger.debug("Retrieving the number of processed event for production", prodid)
        return cls.bkkDB.getProductionProducedEvents(prodid)

    #############################################################################
    types_bulkinsertEventType = [list]

    @classmethod
    def export_bulkinsertEventType(cls, eventtypes):
        """It inserts a list of event types to the db.

        :param eventtypes: it is a list of event types. For example, the list elements are the following

          .. code-block:: python

            {'EVTTYPEID': '12265021',
             'DESCRIPTION': 'Bu_D0pipipi,Kpi-withf2=DecProdCut_pCut1600MeV',
             'PRIMARY': '[B+ -> (D~0 -> K+ pi-) pi+ pi- pi+]cc'}


        :return: S_ERROR S_OK({'Failed':[],'Successful':[]})
        """
        return cls.bkkDB.bulkinsertEventType(eventtypes)

    #############################################################################
    types_bulkupdateEventType = [list]

    @classmethod
    def export_bulkupdateEventType(cls, eventtypes):
        """It updates a list of event types which are exist in the db.

        :param list eventtypes: it is a list of event types. For example: the list elements are the following:

          .. code-block:: python

          {'EVTTYPEID': '12265021',
          'DESCRIPTION': 'Bu_D0pipipi,Kpi-withf2=DecProdCut_pCut1600MeV',
          'PRIMARY': '[B+ -> (D~0 -> K+ pi-) pi+ pi- pi+]cc'}

        :return: S_ERROR S_OK({'Failed':[],'Successful':[]})
        """
        return cls.bkkDB.bulkupdateEventType(eventtypes)

    #############################################################################
    types_getRunConfigurationsAndDataTakingCondition = [six.integer_types]

    @classmethod
    def export_getRunConfigurationsAndDataTakingCondition(cls, runnumber):
        """It returns minimal information for a given run.

        :param: int runnumber
        :return: S_OK()/S_ERROR ConfigName, ConfigVersion and DataTakingDescription
        """
        return cls.bkkDB.getRunConfigurationsAndDataTakingCondition(runnumber)

    types_deleteCertificationData = []

    @classmethod
    def export_deleteCertificationData(cls):
        """It destroy the data used by the integration test."""
        return cls.bkkDB.deleteCertificationData()

    types_updateProductionOutputfiles = []

    @classmethod
    def export_updateProductionOutputfiles(cls):
        """It is used to trigger an update of the productionoutputfiles table."""
        return cls.bkkDB.updateProductionOutputfiles()

    types_getAvailableTagsFromSteps = []

    @classmethod
    def export_getAvailableTagsFromSteps(cls):
        """It returns the all used datatbase tags: DDDB, CondDB, DQTag."""
        return cls.bkkDB.getAvailableTagsFromSteps()
