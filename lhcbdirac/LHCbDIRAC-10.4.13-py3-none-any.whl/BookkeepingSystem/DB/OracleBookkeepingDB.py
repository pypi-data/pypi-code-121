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
"""Queries creation."""
import datetime
import re
import six

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Config import gConfig
from DIRAC.ConfigurationSystem.Client.PathFinder import getDatabaseSection
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.Core.Utilities.Decorators import deprecated
from LHCbDIRAC.BookkeepingSystem.DB.OracleDB import OracleDB

global default
default = "ALL"


class OracleBookkeepingDB(object):
    """This class provides all the methods which manipulate the database."""

    #############################################################################

    def __init__(self):
        """c'tor."""
        self.log = gLogger.getSubLogger("OracleBookkeepingDB")
        self.cs_path = getDatabaseSection("Bookkeeping", "BookkeepingDB")

        self.dbHost = ""
        result = gConfig.getOption(self.cs_path + "/LHCbDIRACBookkeepingTNS")
        if not result["OK"]:
            self.log.error("Failed to get the configuration parameters: LHCbDIRACBookkeepingTNS")
            return
        self.dbHost = result["Value"]

        self.dbUser = ""
        result = gConfig.getOption(self.cs_path + "/LHCbDIRACBookkeepingUser")
        if not result["OK"]:
            self.log.error("Failed to get the configuration parameters: LHCbDIRACBookkeepingUser")
            return
        self.dbUser = result["Value"]

        self.dbPass = ""
        result = gConfig.getOption(self.cs_path + "/LHCbDIRACBookkeepingPassword")
        if not result["OK"]:
            self.log.error("Failed to get the configuration parameters: LHCbDIRACBookkeepingPassword")
            return
        self.dbPass = result["Value"]

        self.dbServer = ""
        result = gConfig.getOption(self.cs_path + "/LHCbDIRACBookkeepingServer")
        if not result["OK"]:
            self.log.error("Failed to get the configuration parameters: LHCbDIRACBookkeepingServer")
            return
        self.dbServer = result["Value"]

        self.dbW_ = OracleDB(self.dbServer, self.dbPass, self.dbHost)
        self.dbR_ = OracleDB(self.dbUser, self.dbPass, self.dbHost)

    #############################################################################
    def getAvailableSteps(self, in_dict):
        """For retrieving a list of steps for a given condition.

        :param dict in_dict: contains step conditions
        :retrun: list of steps
        """
        start = 0
        maximum = 10
        paging = False
        retVal = None
        fileTypefilter = None

        condition = ""
        tables = "steps s, steps r, runtimeprojects rr "
        isMulticore = in_dict.get("isMulticore", default)
        if isMulticore.upper() != default:
            if isMulticore.upper() in ["Y", "N"]:
                condition += " and s.isMulticore='%s'" % (isMulticore)
            else:
                return S_ERROR("isMulticore is not Y or N!")
        if in_dict:
            infiletypes = in_dict.get("InputFileTypes", default)
            outfiletypes = in_dict.get("OutputFileTypes", default)
            matching = in_dict.get("Equal", "YES")

            if isinstance(matching, bool):
                if matching:
                    matching = "YES"
                else:
                    matching = "NO"
            elif matching.upper() not in ["YES", "NO"]:
                return S_ERROR("Wrong Equal value!")

            if infiletypes != default or outfiletypes != default:
                if isinstance(infiletypes, six.string_types):
                    infiletypes = []
                if isinstance(outfiletypes, six.string_types):
                    outfiletypes = []
                infiletypes.sort()
                outfiletypes.sort()
                values = "lists( "
                for i in infiletypes:
                    values += "'%s'," % (i)
                inp = values[:-1] + ")"

                values = "lists( "
                for i in outfiletypes:
                    values += "'%s'," % (i)
                out = values[:-1] + ")"

                fileTypefilter = (
                    " table(BOOKKEEPINGORACLEDB.getStepsForFiletypes(%s, %s, '%s')) s \
                                   "
                    % (inp, out, matching.upper())
                )

            startDate = in_dict.get("StartDate", default)
            if startDate != default:
                condition += " and s.inserttimestamps >= TO_TIMESTAMP (' %s ' ,'YYYY-MM-DD HH24:MI:SS')" % (startDate)

            stepId = in_dict.get("StepId", default)
            if stepId != default:
                if isinstance(stepId, (six.string_types + six.integer_types)):
                    condition += " and s.stepid= %s" % (str(stepId))
                elif isinstance(stepId, (list, tuple)):
                    condition += "and s.stepid in (%s)" % ",".join(str(sid) for sid in stepId)
                else:
                    return S_ERROR("Wrong StepId")

            stepName = in_dict.get("StepName", default)
            if stepName != default:
                if isinstance(stepName, six.string_types):
                    condition += " and s.stepname='%s'" % (stepName)
                elif isinstance(stepName, list):
                    values = " and ("
                    for i in stepName:
                        values += " s.stepname='%s' or " % (i)
                    condition += values[:-3] + ")"

            appName = in_dict.get("ApplicationName", default)
            if appName != default:
                if isinstance(appName, six.string_types):
                    condition += " and s.applicationName='%s'" % (appName)
                elif isinstance(appName, list):
                    values = " and ("
                    for i in appName:
                        values += " s.applicationName='%s' or " % (i)
                    condition += values[:-3] + ")"

            appVersion = in_dict.get("ApplicationVersion", default)
            if appVersion != default:
                if isinstance(appVersion, six.string_types):
                    condition += " and s.applicationversion='%s'" % (appVersion)
                elif isinstance(appVersion, list):
                    values = " and ("
                    for i in appVersion:
                        values += " s.applicationversion='%s' or " % (i)
                    condition += values[:-3] + ")"

            optFile = in_dict.get("OptionFiles", default)
            if optFile != default:
                if isinstance(optFile, six.string_types):
                    condition += " and s.optionfiles='%s'" % (optFile)
                elif isinstance(optFile, list):
                    values = " and ("
                    for i in optFile:
                        values += " s.optionfiles='%s' or " % (i)
                    condition += values[:-3] + ")"

            dddb = in_dict.get("DDDB", default)
            if dddb != default:
                if isinstance(dddb, six.string_types):
                    condition += " and s.dddb='%s'" % (dddb)
                elif isinstance(dddb, list):
                    values = " and ("
                    for i in dddb:
                        values += " s.dddb='%s' or " % (i)
                    condition += values[:-3] + ")"

            conddb = in_dict.get("CONDDB", default)
            if conddb != default:
                if isinstance(conddb, six.string_types):
                    condition += " and s.conddb='%s'" % (conddb)
                elif isinstance(conddb, list):
                    values = " and ("
                    for i in conddb:
                        values += " s.conddb='%s' or " % (i)
                    condition += values[:-3] + ")"

            extraP = in_dict.get("ExtraPackages", default)
            if extraP != default:
                if isinstance(extraP, six.string_types):
                    condition += " and s.extrapackages='%s'" % (extraP)
                elif isinstance(extraP, list):
                    values = " and ("
                    for i in extraP:
                        values += " s.extrapackages='%s' or " % (i)
                    condition += values + ")"

            visible = in_dict.get("Visible", default)
            if visible != default:
                if isinstance(visible, six.string_types):
                    condition += " and s.visible='%s'" % (visible)
                elif isinstance(visible, list):
                    values = " and ("
                    for i in visible:
                        values += " s.visible='%s' or " % (i)
                    condition += values[:-3] + ")"

            procPass = in_dict.get("ProcessingPass", default)
            if procPass != default:
                if isinstance(procPass, six.string_types):
                    condition += " and s.processingpass like'%%%s%%'" % (procPass)
                elif isinstance(procPass, list):
                    values = " and ("
                    for i in procPass:
                        values += " s.processingpass like '%%%s%%' or " % (i)
                    condition += values[:-3] + ")"

            usable = in_dict.get("Usable", default)
            if usable != default:
                if isinstance(usable, six.string_types):
                    condition += " and s.usable='%s'" % (usable)
                elif isinstance(usable, list):
                    values = " and ("
                    for i in usable:
                        values += " s.usable='%s' or " % (i)
                    condition += values[:-3] + ")"

            runtimeProject = in_dict.get("RuntimeProjects", default)
            if runtimeProject != default:
                condition += " and s.runtimeProject=%d" % (runtimeProject)

            dqtag = in_dict.get("DQTag", default)
            if dqtag != default:
                if isinstance(dqtag, six.string_types):
                    condition += " and s.dqtag='%s'" % (dqtag)
                elif isinstance(dqtag, list):
                    values = " and ("
                    for i in dqtag:
                        values += "  s.dqtag='%s' or " % (i)
                    condition += values[:-3] + ")"

            optsf = in_dict.get("OptionsFormat", default)
            if optsf != default:
                if isinstance(optsf, six.string_types):
                    condition += " and s.optionsFormat='%s'" % (optsf)
                elif isinstance(optsf, list):
                    values = " and ("
                    for i in optsf:
                        values += " s.optionsFormat='%s' or " % (i)
                    condition += values[:-3] + ")"

            sysconfig = in_dict.get("SystemConfig", default)
            if sysconfig != default:
                condition += " and s.systemconfig='%s'" % sysconfig

            mcTck = in_dict.get("mcTCK", default)
            if mcTck != default:
                condition += " and s.mcTCK='%s'" % mcTck

            start = in_dict.get("StartItem", default)
            maximum = in_dict.get("MaxItem", default)

            if start != default and maximum != default:
                paging = True

            sort = in_dict.get("Sort", default)
            if sort != default:
                condition += "Order by "
                order = sort.get("Order", "Asc")
                if order.upper() not in ["ASC", "DESC"]:
                    return S_ERROR("wrong sorting order!")
                items = sort.get("Items", default)
                if isinstance(items, list):
                    order = ""
                    for item in items:
                        order += "s.%s," % (item)
                    condition += " %s %s" % (order[:-1], order)
                elif isinstance(items, six.string_types):
                    condition += " s.%s %s" % (items, order)
                else:
                    return S_ERROR("SortItems is not properly defined!")
            else:
                condition += " order by s.inserttimestamps desc"
            if fileTypefilter:
                if paging:
                    command = (
                        " select sstepid, sname, sapplicationname, sapplicationversion, soptionfiles, \
                    sdddb, sconddb, sextrapackages, svisible, sprocessingpass, susable, \
                    sdqtag, soptsf, smulti, ssysconfig, smcTck, \
                     rsstepid, rsname, rsapplicationname, rsapplicationversion, rsoptionfiles, rsdddb, \
                     rsconddb, rsextrapackages, rsvisible, rsprocessingpass, rsusable, \
                     rdqtag, roptsf, rmulti, rsysconfig, rmcTck from \
  ( select ROWNUM r , sstepid, sname, sapplicationname, sapplicationversion, soptionfiles, sdddb, sconddb,\
  sextrapackages, svisible, sprocessingpass, susable, sdqtag, soptsf, smulti, ssysconfig, smcTck,\
     rsstepid, rsname, rsapplicationname, rsapplicationversion, rsoptionfiles, rsdddb, rsconddb,\
     rsextrapackages, rsvisible, rsprocessingpass, rsusable , rdqtag, roptsf, rmulti, rsysconfig, rmcTck from \
    ( select ROWNUM r, s.stepid sstepid ,s.stepname sname, s.applicationname sapplicationname,\
    s.applicationversion sapplicationversion, s.optionfiles soptionfiles,\
    s.DDDB sdddb,s.CONDDB sconddb, s.extrapackages sextrapackages,s.Visible svisible ,\
    s.ProcessingPass sprocessingpass, s.Usable susable, s.dqtag sdqtag, s.optionsFormat soptsf,\
     s.isMulticore smulti, s.systemconfig ssysconfig, s.mcTCK smcTck, \
    s.rstepid rsstepid ,s.rstepname rsname, s.rapplicationname rsapplicationname,\
    s.rapplicationversion rsapplicationversion, s.roptionfiles rsoptionfiles,\
    s.rDDDB rsdddb,s.rCONDDB rsconddb, s.rextrapackages rsextrapackages,s.rVisible rsvisible , \
    s.rProcessingPass rsprocessingpass,s.rUsable rsusable, s.rdqtag rdqtag, s.roptionsFormat roptsf, \
    s.risMulticore rmulti, s.rsystemconfig rsysconfig, s.mcTCK rmcTck \
    from %s where s.stepid=s.stepid %s \
     ) where rownum <=%d ) where r >%d"
                        % (fileTypefilter, condition, maximum, start)
                    )
                else:
                    command = " select * from %s where s.stepid=s.stepid %s" % (fileTypefilter, condition)
            elif paging:
                command = (
                    "select sstepid, sname, sapplicationname, sapplicationversion, soptionfiles, \
                    sdddb, sconddb, sextrapackages, svisible, sprocessingpass, susable, \
                    sdqtag, soptsf, smulti, ssysconfig, smcTck, \
                     rsstepid, rsname, rsapplicationname, rsapplicationversion, rsoptionfiles, rsdddb, \
                     rsconddb, rsextrapackages, rsvisible, rsprocessingpass, rsusable, \
                     rdqtag, roptsf, rmulti, rsysconfig, rmcTck from \
  ( select ROWNUM r , sstepid, sname, sapplicationname, sapplicationversion, soptionfiles, sdddb, sconddb,\
  sextrapackages, svisible, sprocessingpass, susable, sdqtag, soptsf, smulti, ssysconfig, smcTck,\
     rsstepid, rsname, rsapplicationname, rsapplicationversion, rsoptionfiles, rsdddb, rsconddb,\
     rsextrapackages, rsvisible, rsprocessingpass, rsusable , rdqtag, roptsf, rmulti, rsysconfig, rmcTck from \
    ( select ROWNUM r, s.stepid sstepid ,s.stepname sname, s.applicationname sapplicationname,\
    s.applicationversion sapplicationversion, s.optionfiles soptionfiles,\
    s.DDDB sdddb,s.CONDDB sconddb, s.extrapackages sextrapackages,s.Visible svisible ,\
    s.ProcessingPass sprocessingpass, s.Usable susable, s.dqtag sdqtag, s.optionsFormat soptsf,\
     s.isMulticore smulti, s.systemconfig ssysconfig, s.mcTCK smcTck, \
    r.stepid rsstepid ,r.stepname rsname, r.applicationname rsapplicationname,\
    r.applicationversion rsapplicationversion, r.optionfiles rsoptionfiles,\
    r.DDDB rsdddb,r.CONDDB rsconddb, r.extrapackages rsextrapackages,r.Visible rsvisible ,\
    r.ProcessingPass rsprocessingpass,r.Usable rsusable, r.dqtag rdqtag, r.optionsFormat roptsf, \
    r.isMulticore rmulti, r.systemconfig rsysconfig, r.mcTCK rmcTck \
    from %s where s.stepid=rr.stepid(+) and r.stepid(+)=rr.runtimeprojectid %s \
     ) where rownum <=%d ) where r >%d"
                    % (tables, condition, maximum, start)
                )

            else:
                command = (
                    "select s.stepid,s.stepname, s.applicationname,s.applicationversion,s.optionfiles,s.DDDB,s.CONDDB,\
         s.extrapackages,s.Visible, s.ProcessingPass, s.Usable, s.dqtag, s.optionsformat, s.ismulticore, \
         s.systemconfig, s.mcTCK, r.stepid, r.stepname, r.applicationname,r.applicationversion,r.optionfiles,\
         r.DDDB,r.CONDDB, r.extrapackages,r.Visible, r.ProcessingPass, r.Usable, r.dqtag, r.optionsformat, \
         r.ismulticore, r.systemconfig, r.mcTCK from %s where s.stepid=rr.stepid(+) and \
         r.stepid(+)=rr.runtimeprojectid  %s "
                    % (tables, condition)
                )
            retVal = self.dbR_.query(command)
        else:
            command = (
                "select s.stepid, s.stepname, s.applicationname,s.applicationversion,s.optionfiles,s.DDDB,s.CONDDB, \
      s.extrapackages,s.Visible, s.ProcessingPass, s.Usable, s.dqtag, s.optionsformat, s.isMulticore, s.systemconfig, \
      s.mcTCK,r.stepid, r.stepname, r.applicationname,r.applicationversion,r.optionfiles,r.DDDB,r.CONDDB, \
      r.extrapackages,r.Visible, r.ProcessingPass, r.Usable, r.dqtag, r.optionsformat, r.ismulticore,\
      r.systemconfig, r.mcTCK \
      from %s where s.stepid=rr.stepid(+) and r.stepid(+)=rr.runtimeprojectid "
                % (tables)
            )
            retVal = self.dbR_.query(command)

        if not retVal["OK"]:
            return retVal

        parameters = [
            "StepId",
            "StepName",
            "ApplicationName",
            "ApplicationVersion",
            "OptionFiles",
            "DDDB",
            "CONDDB",
            "ExtraPackages",
            "Visible",
            "ProcessingPass",
            "Usable",
            "DQTag",
            "OptionsFormat",
            "isMulticore",
            "SystemConfig",
            "mcTCK",
            "RuntimeProjects",
        ]
        rParameters = [
            "StepId",
            "StepName",
            "ApplicationName",
            "ApplicationVersion",
            "OptionFiles",
            "DDDB",
            "CONDDB",
            "ExtraPackages",
            "Visible",
            "ProcessingPass",
            "Usable",
            "DQTag",
            "OptionsFormat",
            "isMulticore",
            "SystemConfig",
            "mcTCK",
        ]
        records = []
        for record in retVal["Value"]:
            step = list(record[0:16])
            runtimeProject = []
            runtimeProject = [rec for rec in list(record[16:]) if rec is not None]
            if runtimeProject:
                runtimeProject = [runtimeProject]
            step += [
                {"ParameterNames": rParameters, "Records": runtimeProject, "TotalRecords": len(runtimeProject) + 1}
            ]
            records += [step]

        if not paging:
            return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})

        if fileTypefilter:
            command = "select count(*) from %s where s.stepid>0 %s " % (fileTypefilter, condition)
        else:
            command = "select count(*) from steps s where s.stepid>0 %s " % (condition)

        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        totrec = retVal["Value"][0][0]
        return S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": totrec})

    #############################################################################
    def getRuntimeProjects(self, in_dict):
        """get runtime projects.

        :param dict in_dict: dictionary which contains the StepId
        :return: runtime projects if no StepId is given otherwise the runtime project
        """
        result = S_ERROR()
        condition = ""
        selection = "s.stepid,stepname, s.applicationname,s.applicationversion,s.optionfiles,s.DDDB,CONDDB,\
     s.extrapackages,s.Visible, s.ProcessingPass, s.Usable, s.DQTag, s.optionsformat, s.ismulticore, \
     s.systemconfig, s.mcTCK"
        tables = "steps s, runtimeprojects rp"
        stepId = in_dict.get("StepId", default)
        if stepId != default:
            condition += " rp.stepid=%d" % (stepId)
            command = " select %s from %s where s.stepid=rp.runtimeprojectid and %s" % (selection, tables, condition)
            retVal = self.dbR_.query(command)
            if retVal["OK"]:
                parameters = [
                    "StepId",
                    "StepName",
                    "ApplicationName",
                    "ApplicationVersion",
                    "OptionFiles",
                    "DDDB",
                    "CONDDB",
                    "ExtraPackages",
                    "Visible",
                    "ProcessingPass",
                    "Usable",
                    "DQTag",
                    "OptionsFormat",
                    "isMulticore",
                    "SystemConfig",
                    "mcTCK",
                ]
                records = []
                for record in retVal["Value"]:
                    records += [list(record)]
                result = S_OK({"ParameterNames": parameters, "Records": records, "TotalRecords": len(records)})
            else:
                result = retVal
        else:
            result = S_ERROR("You must provide a StepId!")
        return result

    #############################################################################
    def getStepInputFiles(self, stepId):
        """input file types of a given step.

        :param int stepId: given step id.
        :return: the step input files
        """
        command = (
            "select inputFiletypes.name,inputFiletypes.visible from steps, \
     table(steps.InputFileTypes) inputFiletypes where steps.stepid="
            + str(stepId)
        )
        return self.dbR_.query(command)

    #############################################################################
    def setStepInputFiles(self, stepid, fileTypes):
        """set input file types to a given step.

        :param int stepId: given step id.
        :param list fileTypes: file types
        """
        fileTypes = sorted(fileTypes, key=lambda k: k["FileType"])
        if not fileTypes:
            values = "null"
        else:
            values = "filetypesARRAY("
            for i in fileTypes:
                fileType = i.get("FileType", default)
                visible = i.get("Visible", default)
                if fileType != default and visible != default:
                    values += "ftype('%s','%s')," % (fileType, visible)
            values = values[:-1]
            values += ")"
        command = "update steps set inputfiletypes=%s where stepid=%s" % (values, str(stepid))
        return self.dbW_.query(command)

    #############################################################################
    def setStepOutputFiles(self, stepid, fileTypes):
        """set output file types to a given step.

        :param int stepid: given step id
        :param list fileTypes: list of file types
        """
        fileTypes = sorted(fileTypes, key=lambda k: k["FileType"])
        if not fileTypes:
            values = "null"
        else:
            values = "filetypesARRAY("
            for i in fileTypes:
                fileType = i.get("FileType", default)
                visible = i.get("Visible", default)
                if fileType != default and visible != default:
                    values += "ftype('%s','%s')," % (fileType, visible)
            values = values[:-1]
            values += ")"
        command = "update steps set Outputfiletypes=%s  where stepid=%s" % (values, str(stepid))
        return self.dbW_.query(command)

    #############################################################################
    def getStepOutputFiles(self, stepId):
        """For retrieving the step output file types.

        :param int stepid: step id
        :return: the output file types for a given step
        """
        command = (
            "select outputfiletypes.name,outputfiletypes.visible from steps, \
    table(steps.outputfiletypes) outputfiletypes where  steps.stepid="
            + str(stepId)
        )
        return self.dbR_.query(command)

    #############################################################################
    def getProductionOutputFileTypes(self, prod, stepid):
        """returns the production output file types.

        :param int prod:  production number
        :param int stepid: step id
        :return S_OK/S_ERROR: return a dictionary with file types and visibility flag.
        """
        condition = ""
        if stepid != default:
            condition = " and s.stepid=%s" % stepid

        command = (
            "select distinct ft.name, s.visible from productionoutputfiles s, filetypes ft where \
    s.filetypeid=ft.filetypeid and s.production=%s %s"
            % (prod, condition)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        if not retVal["Value"]:
            # this is for backward compatibility.
            # FIXME: make sure the productionoutputfiles is correctly propagated and after the method can be simpified
            command = (
                "select o.name,o.visible from steps s, table(s.outputfiletypes) o, stepscontainer st \
            where st.stepid=s.stepid and st.production=%d %s order by step"
                % (int(prod), condition)
            )
            retVal = self.dbR_.query(command)

        outputFiles = {}
        if retVal["OK"]:
            for filetype, visible in retVal["Value"]:
                outputFiles[filetype] = visible
        else:
            return retVal

        return S_OK(outputFiles)

    #############################################################################
    def getAvailableFileTypes(self):
        """
        For retrieving all file types.

        :return: the available file types
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getAvailableFileTypes", [])

    #############################################################################
    def insertFileTypes(self, ftype, desc, fileType):
        """inserts a given file type."""
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.insertFileTypes", int, [ftype, desc, fileType])

    #############################################################################
    def insertStep(self, in_dict):
        """
        inserts a given step for example:

        .. code-block:: python

          {'Step': {'ApplicationName': 'DaVinci',
                    'Usable': 'Yes',
                    'StepId': '',
                    'ApplicationVersion': 'v29r1',
                    'ExtraPackages': '',
                    'StepName': 'davinci prb2',
                    'ProcessingPass': 'WG-Coool',
                    'Visible': 'Y',
                    'isMulticore': 'N',
                    'OptionFiles': '',
                    'DDDB': '',
                    'CONDDB': ''},
           'OutputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.MDST'}],
           'InputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.DST'}],
           'RuntimeProjects': [{'StepId': 13878}]}

        :param dict in_dict: dictionary which contains step parameters
        """
        result = S_ERROR()
        values = ""
        command = "SELECT applications_index_seq.nextval from dual"
        sid = 0
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            result = retVal
        else:
            sid = retVal["Value"][0][0]

        selection = "insert into steps(stepid,stepname,applicationname,applicationversion,OptionFiles,dddb,conddb,\
    extrapackages,visible, processingpass, usable, DQTag, optionsformat,isMulticore, SystemConfig, mcTCK"
        inFileTypes = in_dict.get("InputFileTypes", default)
        if inFileTypes != default:
            inFileTypes = sorted(inFileTypes, key=lambda k: k["FileType"])
            values = ",filetypesARRAY("
            selection += ",InputFileTypes"
            for i in inFileTypes:
                values += "ftype('%s', '%s')," % (
                    (i.get("FileType", "").strip() if i.get("FileType", "") else i.get("FileType", "")),
                    (i.get("Visible", "").strip() if i.get("Visible", "") else i.get("Visible", "")),
                )
            values = values[:-1]
            values += ")"

        outFileTypes = in_dict.get("OutputFileTypes", default)
        if outFileTypes != default:
            outFileTypes = sorted(outFileTypes, key=lambda k: k["FileType"])
            values += " , filetypesARRAY("
            selection += ",OutputFileTypes"
            for i in outFileTypes:
                values += "ftype('%s', '%s')," % (
                    (i.get("FileType", "").strip() if i.get("FileType", "") else i.get("FileType", "")),
                    (i.get("Visible", "").strip() if i.get("Visible", "") else i.get("Visible", "")),
                )
            values = values[:-1]
            values += ")"

        step = in_dict.get("Step", default)
        if step != default:
            command = selection + ")values(%d" % (sid)
            command += ",'%s'" % (step.get("StepName", "NULL"))
            command += ",'%s'" % (step.get("ApplicationName", "NULL"))
            command += ",'%s'" % (step.get("ApplicationVersion", "NULL"))
            command += ",'%s'" % (step.get("OptionFiles", "NULL"))
            command += ",'%s'" % (step.get("DDDB", "NULL"))
            command += ",'%s'" % (step.get("CONDDB", "NULL"))
            command += ",'%s'" % (step.get("ExtraPackages", "NULL"))
            command += ",'%s'" % (step.get("Visible", "NULL"))
            command += ",'%s'" % (step.get("ProcessingPass", "NULL"))
            command += ",'%s'" % (step.get("Usable", "Not ready"))
            command += ",'%s'" % (step.get("DQTag", ""))
            command += ",'%s'" % (step.get("OptionsFormat", ""))
            command += ",'%s'" % (step.get("isMulticore", "N"))
            command += ",'%s'" % (step.get("SystemConfig", "NULL"))
            command += ",'%s'" % (step.get("mcTCK", "NULL"))
            command += values + ")"
            retVal = self.dbW_.query(command)
            if retVal["OK"]:
                r_project = in_dict.get("RuntimeProjects", step.get("RuntimeProjects", default))
                if r_project != default:
                    for i in r_project:
                        rid = i["StepId"]
                        retVal = self.insertRuntimeProject(sid, rid)
                        if not retVal["OK"]:
                            result = retVal
                        else:
                            result = S_OK(sid)
                else:
                    result = S_OK(sid)
            else:
                result = retVal
        else:
            result = S_ERROR("The Step is not provided!")
        return result

    #############################################################################
    def deleteStep(self, stepid):
        """deletes a step.

        :param int stepid: step id to be deleted
        """
        self.log.warn("Deleting step", stepid)

        retVal = self.dbW_.query("DELETE runtimeprojects WHERE stepid=%d" % (stepid))
        if not retVal["OK"]:
            return retVal
        # now we can delete the step
        return self.dbW_.query("DELETE steps WHERE stepid=%d" % (stepid))

    #############################################################################

    def deleteStepContainer(self, prod):
        """delete a production from the step container.

        :param int prod: production number
        """
        self.log.warn("Deleting step container for prod", prod)
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.deleteStepContainer", [prod], False)

    #############################################################################

    def deleteProductionsContainer(self, prod):
        """delete a production from the productions container.

        :param int prod: the production number
        """
        self.log.warn("Deleting production container for prod", prod)
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.deleteProductionsCont", [prod], False)

    #############################################################################
    def updateStep(self, in_dict):
        """update an existing step.
        input data {'ApplicationName': 'DaVinci', 'Usable': 'Yes', 'StepId': '13860',
        'ApplicationVersion': 'v29r1', 'ExtraPackages': '', 'StepName': 'davinci prb3', 'ProcessingPass':
        'WG-Coool-new', 'InputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.DST'}], 'Visible': 'Y',
        'DDDB': '', 'OptionFiles': '', 'CONDDB': '',
        'OutputFileTypes': [{'Visible': 'Y', 'FileType': 'CHARM.MDST'}],
        'RuntimeProjects':[{'StepId':13879}]}
        :param dict in_dict: step parameters which will be updated
        """
        result = S_ERROR()
        ok = True
        rProjects = in_dict.get("RuntimeProjects", default)
        if rProjects != default:
            if rProjects:
                for i in rProjects:
                    if "StepId" not in in_dict:
                        result = S_ERROR("The runtime project can not changed, because the StepId is missing!")
                        ok = False
                    else:
                        retVal = self.updateRuntimeProject(in_dict["StepId"], i["StepId"])
                        if not retVal["OK"]:
                            result = retVal
                            ok = False
                        else:
                            in_dict.pop("RuntimeProjects")
            else:
                retVal = self.removeRuntimeProject(in_dict["StepId"])
                if not retVal["OK"]:
                    result = retVal
                    ok = False
                else:
                    in_dict.pop("RuntimeProjects")

        if ok:
            stepid = in_dict.get("StepId", default)
            if stepid != default:
                in_dict.pop("StepId")
                condition = " where stepid=%s" % (str(stepid))
                command = "update steps set "
                for i in in_dict:
                    if isinstance(in_dict[i], six.string_types):
                        command += " %s='%s'," % (i, str(in_dict[i]))
                    else:
                        if in_dict[i]:
                            values = "filetypesARRAY("
                            ftypes = in_dict[i]
                            ftypes = sorted(ftypes, key=lambda k: k["FileType"])
                            for j in ftypes:
                                filetype = j.get("FileType", default)
                                if filetype != default:
                                    values += "ftype('%s','')," % filetype.strip()
                            values = values[:-1]
                            values += ")"
                            command += i + "=" + values + ","
                        else:
                            command += i + "=null,"
                command = command[:-1]
                command += condition
                result = self.dbW_.query(command)
            else:
                result = S_ERROR("Please provide a StepId!")

        return result

    #############################################################################
    def getAvailableConfigNames(self):
        """For retrieving the list of configuration names using the materialized
        view.

        :return: the available configuration names
        """
        command = (
            "select c.configname from configurations c, productionoutputfiles prod, productionscontainer cont\
                where cont.configurationid=c.configurationid\
                and prod.production=cont.production %s\
                group by c.configname order by c.configname"
            % self.__buildVisible(visible="Y", replicaFlag="Yes")
        )
        return self.dbR_.query(command)

    ##############################################################################
    def getAvailableConfigurations(self):
        """For retrieving all available configurations even the configurations
        which are not used.

        :return: the available configurations from the configurations table
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getAvailableConfigurations", [])

    #############################################################################
    def getConfigVersions(self, configname):
        """For retrieving configuration version.

        :param str configname: the configuration name for example: MC, LHCb, etc.
        :return: the configuration version for a given configname
        """
        result = S_ERROR()
        if configname != default:
            command = (
                "select c.configversion from configurations c, productionoutputfiles prod, productionscontainer cont\
                  where cont.configurationid=c.configurationid\
                  and c.configname='%s' and prod.production=cont.production %s\
                  group by c.configversion \
                  order by c.configversion"
                % (configname, self.__buildVisible(visible="Y", replicaFlag="Yes"))
            )
            result = self.dbR_.query(command)
        else:
            result = S_ERROR("You must provide a Configuration Name!")
        return result

    #############################################################################
    def getConditions(self, configName, configVersion, evt):
        """Retrieving the data taking or simulation conditions for a given event
        type.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param long evt: event type id
        :return: the conditions for a given configuration name, version and event type
        """

        condition = " and cont.production=prod.production %s " % self.__buildVisible(visible="Y", replicaFlag="Yes")
        tables = " configurations c, productionscontainer cont, productionoutputfiles prod "
        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        if evt != default:
            condition += " and prod.eventtypeid=%s" % (str(evt))

        command = (
            "select distinct simulationConditions.SIMID,data_taking_conditions.DAQPERIODID,\
    simulationConditions.SIMDESCRIPTION, simulationConditions.BEAMCOND, \
    simulationConditions.BEAMENERGY, simulationConditions.GENERATOR,\
    simulationConditions.MAGNETICFIELD,simulationConditions.DETECTORCOND, \
    simulationConditions.LUMINOSITY, simulationconditions.G4settings, \
    data_taking_conditions.DESCRIPTION,data_taking_conditions.BEAMCOND, \
    data_taking_conditions.BEAMENERGY,data_taking_conditions.MAGNETICFIELD, \
    data_taking_conditions.VELO,data_taking_conditions.IT, \
    data_taking_conditions.TT,data_taking_conditions.OT,\
    data_taking_conditions.RICH1,data_taking_conditions.RICH2, \
    data_taking_conditions.SPD_PRS, data_taking_conditions.ECAL, \
    data_taking_conditions.HCAL, data_taking_conditions.MUON, data_taking_conditions.L0, data_taking_conditions.HLT,\
     data_taking_conditions.VeloPosition from simulationConditions,data_taking_conditions, %s where \
      cont.simid=simulationConditions.simid(+) and \
      cont.DAQPERIODID=data_taking_conditions.DAQPERIODID(+) %s"
            % (tables, condition)
        )

        return self.dbR_.query(command)

    #############################################################################
    def getProcessingPass(
        self, configName, configVersion, conddescription, runnumber, production, eventType=default, path="/"
    ):
        """For retrieving the processing pass for given conditions.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking or simulation description
        :param long runnumber: run number
        :param int production: production number
        :param eventType: event type identifier
        :param str path: processing pass
        :return: the processing pass for a given dataset
        """
        erecords = []
        eparameters = []
        precords = []
        pparameters = []

        condition = " and cont.production=prod.production %s " % self.__buildVisible(visible="Y", replicaFlag="Yes")
        tables = ""
        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        if eventType != default:
            condition += " and prod.eventtypeid=%s" % (str(eventType))

        if conddescription != default:
            retVal = self.__getConditionString(conddescription, "cont")
            if not retVal["OK"]:
                return retVal
            else:
                condition += retVal["Value"]

        if production != default:
            condition += " and prod.production=" + str(production)

        tables = ""
        if runnumber != default:
            tables += " , prodrunview "
            condition += " and prodrunview.production=prod.production and prodrunview.runnumber=%s" % (str(runnumber))

        proc = path.split("/")[len(path.split("/")) - 1]
        if proc != "":
            command = (
                "select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                           FROM processing v   \
                                           START WITH id in (select distinct id from processing where name='%s') \
                                              CONNECT BY NOCYCLE PRIOR  id=parentid) v \
                     where v.path='%s'"
                % (path.split("/")[1], path)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                return retVal
            pro = ""
            for i in retVal["Value"]:
                pro += "%s," % (str(i[0]))
            pro = pro[:-1]

            if pro == "":
                return S_ERROR("Empty Directory")
            command = (
                "select distinct eventTypes.EventTypeId,\
       eventTypes.Description from eventtypes, productionoutputfiles prod,\
         productionscontainer cont, configurations c, processing %s where \
        eventTypes.EventTypeId=prod.eventtypeid and \
        cont.processingid=processing.id and \
        processing.id in (%s) %s"
                % (tables, pro, condition)
            )

            retVal = self.dbR_.query(command)
            if retVal["OK"]:
                eparameters = ["EventType", "Description"]
                for record in retVal["Value"]:
                    erecords += [list(record)]
            else:
                return retVal

            command = (
                "SELECT distinct name \
      FROM processing   where parentid in (%s) \
      START WITH id in (select distinct cont.processingid \
      from productionscontainer cont, productionoutputfiles prod, configurations c %s where \
      cont.production=prod.production  %s )  CONNECT BY NOCYCLE PRIOR  parentid=id \
      order by name desc"
                % (pro, tables, condition)
            )
        else:
            command = (
                "SELECT distinct name \
      FROM processing  where parentid is null START WITH id in \
      (select distinct cont.processingid \
      from productionscontainer cont, productionoutputfiles prod, configurations c %s where \
      cont.production=prod.production %s ) CONNECT BY NOCYCLE PRIOR  parentid=id \
      order by name desc"
                % (tables, condition)
            )
        retVal = self.dbR_.query(command)
        if retVal["OK"]:
            precords = []
            pparameters = ["Name"]
            for record in retVal["Value"]:
                precords += [[record[0]]]
        else:
            return retVal

        return S_OK(
            [
                {"ParameterNames": pparameters, "Records": precords, "TotalRecords": len(precords)},
                {"ParameterNames": eparameters, "Records": erecords, "TotalRecords": len(erecords)},
            ]
        )

    #############################################################################
    def __getConditionString(self, conddescription, table="productionscontainer"):
        """builds the condition for data taking/ simulation conditions.

        :param str conddescription: data taking or simulation condition
        :param str table: table(s) will be used in the JOIN
        :return: condition used in the SQL WHERE clauses.
        """
        condition = ""
        retVal = self._getDataTakingConditionId(conddescription)
        if retVal["OK"]:
            if retVal["Value"] != -1:
                condition += " and %s.DAQPERIODID=%s and %s.DAQPERIODID is not null " % (
                    table,
                    str(retVal["Value"]),
                    table,
                )
            else:
                retVal = self.__getSimulationConditionId(conddescription)
                if retVal["OK"]:
                    if retVal["Value"] != -1:
                        condition += " and %s.simid=%s and %s.simid is not null " % (table, str(retVal["Value"]), table)
                    else:
                        return S_ERROR("Condition does not exists!")
                else:
                    return retVal
        else:
            return retVal
        return S_OK(condition)

    #############################################################################
    def _getDataTakingConditionId(self, desc):
        """For retrieving the data taking id for a given data taking description.

        :param str desc: data taking description
        :return: the data taking conditions identifire
        """
        command = "select DAQPERIODID from data_taking_conditions where DESCRIPTION='" + str(desc) + "'"
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        if retVal["Value"]:
            return S_OK(retVal["Value"][0][0])
        return S_OK(-1)

    #############################################################################
    def __getSimulationConditionId(self, desc):
        """For retrieving the simulation condition id for a given simulation
        description.

        :param str desc: simulation condition description
        :return: the simulation condition identifier
        """
        command = "select simid from simulationconditions where simdescription='%s'" % (desc)
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        if retVal["Value"]:
            return S_OK(retVal["Value"][0][0])
        return S_OK(-1)

    #############################################################################
    def getProductions(
        self,
        configName=default,
        configVersion=default,
        conddescription=default,
        processing=default,
        evt=default,
        visible=default,
        fileType=default,
        replicaFlag=default,
    ):
        """For retrieving the productions.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking or simulation description
        :param str processing: processing pass
        :param long evt: event type identifier
        :param str visible: the file visibility flag
        :param str file type: file type
        :param str replicaFlag: replica flag
        :return: list of productions
        """

        tables = " productionoutputfiles prod, productionscontainer cont "
        condition = " and cont.production=prod.production %s " % self.__buildVisible(
            visible=visible, replicaFlag=replicaFlag
        )

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        retVal = self._buildConditions(default, conddescription, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildEventType(evt, condition, tables, useMainTables=False)

        condition, tables = self.__buildFileTypes(fileType, condition, tables, useMainTables=False)

        retVal = self.__buildProcessingPass(processing, condition, tables, useMainTables=False)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        command = "select prod.production from %s where 1=1  %s group by prod.production" % (tables, condition)

        return self.dbR_.query(command)

    #############################################################################
    def getFileTypes(
        self,
        configName,
        configVersion,
        conddescription=default,
        processing=default,
        evt=default,
        runnb=default,
        production=default,
        visible=default,
        replicaFlag=default,
    ):
        """For retrieving the file types

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking or simulation description
        :param str processing: processing pass
        :param long evt: event type identifier
        :param long runnb: run number
        :param int production: production number
        :param str visible: the file visibility flag
        :param str file type: file type
        :param str replicaFlag: replica flag
        :return: the file types
        """

        tables = " productionoutputfiles prod, productionscontainer cont, filetypes ftypes "
        condition = " and cont.production=prod.production %s " % self.__buildVisible(
            visible=visible, replicaFlag=replicaFlag
        )

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        retVal = self._buildConditions(default, conddescription, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildEventType(evt, condition, tables, useMainTables=False)

        condition, tables = self.__buildProduction(production, condition, tables, useMainTables=False)

        retVal = self._buildRunnumbers(runnb, None, None, condition, tables, useMainTables=False)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        proc = ""
        if processing != default:
            command = (
                "select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                           FROM processing v   \
                                           START WITH id in (select distinct id from processing where name='%s') \
                                              CONNECT BY NOCYCLE PRIOR  id=parentid) v \
                     where v.path='%s'"
                % (processing.split("/")[1], processing)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                return retVal
            pro = "("
            for i in retVal["Value"]:
                pro += "%s," % (str(i[0]))
            pro = pro[:-1]
            pro += ")"
            proc = " and cont.processingid in %s " % pro
        command = (
            "select ftypes.name from %s \
                 where prod.production=cont.production %s\
                   and prod.filetypeId=ftypes.filetypeid  %s group by ftypes.name"
            % (tables, condition, proc)
        )

        return self.dbR_.query(command)

    #############################################################################
    def getFilesWithMetadata(
        self,
        configName,
        configVersion,
        conddescription=default,
        processing=default,
        evt=default,
        production=default,
        filetype=default,
        quality=default,
        visible=default,
        replicaflag=default,
        startDate=None,
        endDate=None,
        runnumbers=None,
        startRunID=None,
        endRunID=None,
        tcks=default,
        jobStart=None,
        jobEnd=None,
        selection=None,
    ):
        """For retrieving files with meta data.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking or simulation description
        :param str processing: processing pass
        :param long evt: event type identifier
        :param int production: production number
        :param str filetype: file type
        :param str quality: data quality flag
        :param str visible: visibility flag
        :param str replicaflag: replica flag
        :param datetime startDate: job/run insert start time stamp
        :param datetime endDate: job/run end insert time stamp
        :param list runnumbers: run numbers
        :param long startRunID: start run
        :param long endRunID: end run
        :param str tcks: TCK number
        :param datetime jobStart: job starte date
        :param datetime jobEnd: job end date
        :return: a list of files with their metadata
        """

        if runnumbers is None:
            runnumbers = []

        if selection is None:
            selection = " distinct f.FileName, f.EventStat, f.FileSize, f.CreationDate, j.JobStart, j.JobEnd, \
    j.WorkerNode, ft.Name, j.runnumber, j.fillnumber, f.fullstat, d.dataqualityflag, \
    j.eventinputstat, j.totalluminosity, f.luminosity, f.instLuminosity, j.tck, f.guid, f.adler32, \
    f.eventTypeid, f.md5sum,f.visibilityflag, j.jobid, f.gotreplica, f.inserttimestamp "

        tables = " files f, dataquality d, jobs j, productionoutputfiles prod, productionscontainer cont, filetypes ft "
        condition = (
            " and cont.production=prod.production and \
    j.production=prod.production and j.stepid=prod.stepid  and \
    prod.eventtypeid=f.eventtypeid %s "
            % self.__buildVisible(visible=visible, replicaFlag=replicaflag)
        )

        condition = self.__buildStartenddate(startDate, endDate, condition)

        condition = self.__buildJobsStartJobEndDate(jobStart, jobEnd, condition)

        retVal = self._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        retVal = self.__buildTCKS(tcks, condition)
        if not retVal["OK"]:
            return retVal
        condition = retVal["Value"]

        condition, tables = self.__buildVisibilityflag(visible, condition, tables)

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        retVal = self._buildConditions(default, conddescription, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildProduction(production, condition, tables, useMainTables=False)

        condition = self.__buildReplicaflag(replicaflag, condition)

        retVal = self.__buildDataquality(quality, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        retVal = self.__buildProcessingPass(processing, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildEventType(evt, condition, tables, useMainTables=False)

        condition, tables = self.__buildFileTypes(filetype, condition, tables, useMainTables=False)

        command = (
            "select %s from %s  where \
    j.jobid=f.jobid  and \
    ft.filetypeid=f.filetypeid and \
    f.qualityid=d.qualityid %s"
            % (selection, tables, condition)
        )
        return self.dbR_.query(command)

    #############################################################################
    def getAvailableDataQuality(self):
        """For retrieving the data quality flags.

        :return: the available data quality flags
        """
        result = S_ERROR()
        command = " select dataqualityflag from dataquality"
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            result = retVal
        else:
            flags = retVal["Value"]
            values = []
            for i in flags:
                values += [i[0]]
            result = S_OK(values)
        return result

    #############################################################################
    def getAvailableProductions(self):
        """For retrieving the productions form the view.

        :return: the available productions
        """
        command = "select distinct production from productionoutputfiles where production > 0 and\
    gotreplica='Yes' and visible='Y'"
        return self.dbR_.query(command)

    #############################################################################
    def getAvailableRuns(self):
        """For retrieving the runs from the view.

        :return: aviable runs
        """
        command = " select distinct runnumber from prodrunview"
        res = self.dbR_.query(command)
        return res

    #############################################################################
    def getAvailableEventTypes(self):
        """For retrieving the event types.

        :return: all event types
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getAvailableEventTypes", [])

    #############################################################################
    def getProductionProcessingPass(self, prodid):
        """For retrieving the processing pass from a given production.

        :param long prodid: production number
        :return: processing pass
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getProductionProcessingPass", str, [prodid])

    #############################################################################
    def getRunProcessingPass(self, runnumber):
        """For retrieving the processing pass for a given run number.

        :param long runnumber: run number
        :return: the processing pass for a given run
        """
        return self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.getProductionProcessingPass", str, [-1 * runnumber]
        )

    #############################################################################
    def getProductionProcessingPassID(self, prodid):
        """For retrieving the processing pass id.

        :param long prodid: production number
        :return: the processing pass identifier of a production
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getProductionProcessingPassId", int, [prodid])

    #############################################################################
    def getMoreProductionInformations(self, prodid):
        """For retrieving the production statistics.

        :param long prodid: production number
        :return: the statistics of a production
        """

        command = (
            "select c.configname, c.configversion, s.ApplicationName, s.ApplicationVersion from \
    productionscontainer cont, configurations c, stepscontainer scont, steps s where cont.production=%s and\
    cont.configurationid=c.configurationid and cont.production=scont.production and scont.stepid=s.stepid \
    group by c.configname, c.configversion, s.ApplicationName, s.ApplicationVersion"
            % prodid
        )

        res = self.dbR_.query(command)
        if not res["OK"]:
            return res
        record = res["Value"]
        cname = record[0][0]
        cversion = record[0][1]
        pname = record[0][2]
        pversion = record[0][3]

        retVal = self.getProductionProcessingPass(prodid)
        if not retVal["OK"]:
            return retVal
        procdescription = retVal["Value"]

        simdesc = None
        daqdesc = None

        command = (
            "select distinct sim.simdescription, daq.description from simulationconditions sim, \
    data_taking_conditions daq,productionscontainer prod \
    where sim.simid(+)=prod.simid and daq.daqperiodid(+)=prod.daqperiodid and prod.production="
            + str(prodid)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        value = retVal["Value"]
        if value:
            simdesc = value[0][0]
            daqdesc = value[0][1]
        else:
            return S_ERROR("Simulation condition or data taking condition not exist!")
        if simdesc is not None:
            return S_OK(
                {
                    "ConfigName": cname,
                    "ConfigVersion": cversion,
                    "ProgramName": pname,
                    "ProgramVersion": pversion,
                    "Processing pass": procdescription,
                    "Simulation conditions": simdesc,
                }
            )
        else:
            return S_OK(
                {
                    "ConfigName": cname,
                    "ConfigVersion": cversion,
                    "ProgramName": pname,
                    "ProgramVersion": pversion,
                    "Processing pass": procdescription,
                    "Data taking conditions": daqdesc,
                }
            )

    #############################################################################
    def getJobInfo(self, lfn):
        """For retrieving the job parameters for a given LFN.

        :param str lfn: logical file name
        :return: Job information for a given file
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getJobInfo", [lfn])

    #############################################################################
    def bulkJobInfo(self, in_dict):
        """For retrieving jobs parameters for a list of LFNs, jobIds, or JobName.

        :param dict in_dict: dictionary which contains lfn, jobId or JobName elements
        :return: the job information for a list of files
        """

        data = []
        if "lfn" in in_dict:
            data = in_dict["lfn"]
            if not data:
                return S_ERROR("Please give at least one lfn")
            retVal = self.dbR_.executeStoredProcedure(
                packageName="BOOKKEEPINGORACLEDB.bulkJobInfo", parameters=[], output=True, array=data
            )
        elif "jobId" in in_dict:
            data = in_dict["jobId"]
            if not data:
                return S_ERROR("Please give at least one jobId")
            retVal = self.dbR_.executeStoredProcedure(
                packageName="BOOKKEEPINGORACLEDB.bulkJobInfoForJobId", parameters=[], output=True, array=data
            )

        elif "jobName" in in_dict:
            data = in_dict["jobName"]
            if not data:
                return S_ERROR("Please give at least one jobName")
            retVal = self.dbR_.executeStoredProcedure(
                packageName="BOOKKEEPINGORACLEDB.bulkJobInfoForJobName", parameters=[], output=True, array=data
            )
        else:
            return S_ERROR(
                "Wrong input parameters. You can use a dictionary with the following keys: lfn,jobId, jobName"
            )

        records = {}
        if retVal["OK"]:
            for i in retVal["Value"]:
                record = dict(
                    zip(
                        (
                            "DIRACJobId",
                            "DIRACVersion",
                            "EventInputStat",
                            "ExecTime",
                            "FirstEventNumber",
                            "Location",
                            "Name",
                            "NumberOfEvents",
                            "StatisticsRequested",
                            "WNCPUPOWER",
                            "CPUTIME",
                            "WNCACHE",
                            "WNMEMORY",
                            "WNMODEL",
                            "WORKERNODE",
                            "WNCPUHS06",
                            "JobId",
                            "TotalLumonosity",
                            "Production",
                            "ApplicationName",
                            "ApplicationVersion",
                            "WNMJFHS06",
                        ),
                        i[1:],
                    )
                )
                j = 0
                if i[0] not in records:
                    records[i[0]] = [record]
                else:
                    records[i[0]] += [record]

                j += 1

            failed = [i for i in data if i not in records]
            result = S_OK({"Successful": records, "Failed": failed})
        else:
            result = retVal

        return result

    #############################################################################
    def getJobInformation(self, params):
        """For retrieving only job information for a given production, lfn or
        DiracJobId.

        :param dict params: dictionary which contains LFN, Production, DiracJobId elements
        :return: job parameters
        """
        production = params.get("Production", default)
        lfn = params.get("LFN", default)
        condition = ""
        diracJobids = params.get("DiracJobId", default)

        tables = " jobs j, files f, configurations c"
        result = None
        if production != default:
            if isinstance(production, (six.string_types + six.integer_types)):
                condition += " and j.production=%d " % (int(production))
            elif isinstance(production, list):
                condition += " and j.production in ( " + ",".join([str(p) for p in production]) + ")"
            else:
                result = S_ERROR("The production type is invalid. It can be a list, integer or string!")
        elif lfn != default:
            if isinstance(lfn, six.string_types):
                condition += " and f.filename='%s' " % (lfn)
            elif isinstance(lfn, list):
                condition += " and (" + " or ".join(["f.filename='%s'" % x for x in lfn]) + ")"
            else:
                result = S_ERROR("You must provide an LFN or a list of LFNs!")
        elif diracJobids != default:
            if isinstance(diracJobids, (six.string_types + six.integer_types)):
                condition += " and j.DIRACJOBID=%s " % diracJobids
            elif isinstance(diracJobids, list):
                condition += " and j.DIRACJOBID in ( " + ",".join([str(djobid) for djobid in diracJobids]) + ")"
            else:
                result = S_ERROR("Please provide a correct DIRAC jobid!")

        if not result:
            command = (
                " select  distinct j.DIRACJOBID, j.DIRACVERSION, j.EVENTINPUTSTAT, j.EXECTIME,\
      j.FIRSTEVENTNUMBER,j.LOCATION,  j.NAME, j.NUMBEROFEVENTS, \
                 j.STATISTICSREQUESTED, j.WNCPUPOWER, j.CPUTIME, j.WNCACHE, j.WNMEMORY, j.WNMODEL, \
                 j.WORKERNODE, j.WNCPUHS06, j.jobid, j.totalluminosity, j.production, j.WNMJFHS06,\
                 c.ConfigName,c.ConfigVersion, j.JobEnd, j.JobStart, j.RunNumber, j.FillNumber, j.Tck, j.stepid \
                 from %s where f.jobid=j.jobid and c.configurationid=j.configurationid %s"
                % (tables, condition)
            )
            retVal = self.dbR_.query(command)
            if retVal["OK"]:
                records = []

                parameters = [
                    "DiracJobId",
                    "DiracVersion",
                    "EventInputStat",
                    "Exectime",
                    "FirstEventNumber",
                    "Location",
                    "JobName",
                    "NumberOfEvents",
                    "StatisticsRequested",
                    "WNCPUPower",
                    "CPUTime",
                    "WNCache",
                    "WNMemory",
                    "WNModel",
                    "WorkerNode",
                    "WNCPUHS06",
                    "JobId",
                    "TotalLuminosity",
                    "Production",
                    "WNMJFHS06",
                    "ConfigName",
                    "ConfigVersion",
                    "JobEnd",
                    "JobStart",
                    "RunNumber",
                    "FillNumber",
                    "Tck",
                    "StepId",
                ]
                for i in retVal["Value"]:
                    records += [dict(zip(parameters, i))]
                result = S_OK(records)
            else:
                result = retVal

        return result

    #############################################################################
    def getRunNumber(self, lfn):
        """For retrieving the run number for a given LFN.

        :param str lfn: logical file name
        :return: the run number of a given file
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getRunNumber", int, [lfn])

    #############################################################################
    def getRunNbAndTck(self, lfn):
        """For retrieving the run number and TCK for a given LFN.

        :param str lfn: logical file name
        :return: the run number and tck for a given file
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getRunNbAndTck", [lfn])

    #############################################################################
    def getProductionFiles(self, prod, ftype, gotreplica=default):
        """For retrieving the list of LFNs for a given production.

        :param int prod: production number
        :param str ftype: file type
        :param str gotreplica: replica flag
        :return: the files which are belongs to a given production
        """
        result = S_ERROR()
        value = {}
        condition = ""
        if gotreplica != default:
            condition += " and files.gotreplica='%s'" % (str(gotreplica))

        if ftype != default:
            condition += " and filetypes.name='%s'" % (ftype)

        command = (
            "select files.filename, files.gotreplica, files.filesize,files.guid, \
    filetypes.name, files.inserttimestamp, files.visibilityflag from jobs,files,filetypes where\
    jobs.jobid=files.jobid and files.filetypeid=filetypes.filetypeid and jobs.production=%d %s"
            % (prod, condition)
        )

        res = self.dbR_.query(command)
        if res["OK"]:
            dbResult = res["Value"]
            for record in dbResult:
                value[record[0]] = {
                    "GotReplica": record[1],
                    "FileSize": record[2],
                    "GUID": record[3],
                    "FileType": record[4],
                    "Visible": record[6],
                }
            result = S_OK(value)
        else:
            result = S_ERROR(res["Message"])
        return result

    #############################################################################
    def getProductionFilesBulk(self, prods, ftype, gotreplica=default):
        """For retrieving the list of LFNs for a given production.

        :param list prods: production numbers
        :param str ftype: file type
        :param str gotreplica: replica flag
        :return: dictionary of production number to the list of files
        """
        command = (
            "select "
            "    jobs.production, "
            "    files.filename, "
            "    files.gotreplica, "
            "    files.filesize, "
            "    files.guid, "
            "    filetypes.name, "
            "    files.visibilityflag "
            "from "
            "    jobs "
            "    INNER JOIN files on files.jobid = jobs.jobid "
            "    INNER JOIN filetypes on filetypes.filetypeid = files.filetypeid "
            "where "
            "    jobs.production in (%s)"
        )
        kwparams = {}
        if gotreplica != default:
            kwparams["gotreplica"] = str(gotreplica)
            command += " and files.gotreplica = :gotreplica"
        if ftype != default:
            kwparams["ftype"] = ftype
            command += " and filetypes.name = :ftype"

        value = {str(p): {} for p in prods}
        for prodChunk in breakListIntoChunks(prods, 100):
            res = self.dbR_.query(
                # Ensure each element is a valid int to avoid SQL injection attacks
                command % ",".join(str(int(p)) for p in prodChunk),
                kwparams=kwparams,
            )
            if not res["OK"]:
                return S_ERROR(res["Message"])
            for production, filename, gotreplica, filesize, guid, filetype, visibilityflag in res["Value"]:
                value[str(production)][filename] = {
                    "GotReplica": gotreplica,
                    "FileSize": filesize,
                    "GUID": guid,
                    "FileType": filetype,
                    "Visible": visibilityflag,
                }
        return S_OK(value)

    #############################################################################
    def getRunFiles(self, runid):
        """Retrieving list of LFNs for a given run.

        :param long runid: run number
        :return: a list of files with metadata for a given run
        """
        result = S_ERROR()
        value = {}
        res = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getRunFiles", [runid])
        if res["OK"]:
            dbResult = res["Value"]
            for record in dbResult:
                value[record[0]] = {
                    "GotReplica": record[1],
                    "FileSize": record[2],
                    "GUID": record[3],
                    "Luminosity": record[4],
                    "InstLuminosity": record[5],
                    "EventStat": record[6],
                    "FullStat": record[7],
                }
            result = S_OK(value)
        else:
            result = res
        return result

    #############################################################################
    def updateFileMetaData(self, filename, fileAttr):
        """updates the file metadata.

        :param str filename:
        :param dict fileAttr: file attributes
        """
        utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        command = "update files Set inserttimestamp=TO_TIMESTAMP('%s','YYYY-MM-DD HH24:MI:SS') ," % (str(utctime))
        command += ",".join(["%s=%s" % (str(attribute), str(fileAttr[attribute])) for attribute in fileAttr])
        command += " where fileName='%s'" % (filename)
        res = self.dbW_.query(command)
        return res

    #############################################################################
    def bulkupdateFileMetaData(self, lfnswithmeta):
        """For updating the metadata a list of files:

        :param dict lfnswithmetadata: dictionary which contains LFNs and file attributes.
        """

        utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sqls = []
        for filename in lfnswithmeta:
            command = "update files Set inserttimestamp=TO_TIMESTAMP('%s','YYYY-MM-DD HH24:MI:SS') ," % (str(utctime))
            command += ",".join(
                [
                    "%s=%s" % (str(attribute), str(lfnswithmeta[filename][attribute]))
                    for attribute in lfnswithmeta[filename]
                ]
            )
            command += " where fileName='%s'" % (filename)
            sqls += [command]

        retVal = self.dbR_.executeStoredProcedure(
            packageName="BOOKKEEPINGORACLEDB.bulkupdateFileMetaData", parameters=[], output=False, array=sqls
        )
        return retVal

    #############################################################################
    def renameFile(self, oldLFN, newLFN):
        """renames a file.

        :param str oldLFN: old logical file name
        :param str newLFN: new logical file name
        """
        utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        command = (
            " update files set inserttimestamp=TO_TIMESTAMP('%s','YYYY-MM-DD HH24:MI:SS'),\
     filename ='%s' where filename='%s'"
            % (str(utctime), newLFN, oldLFN)
        )
        res = self.dbW_.query(command)
        return res

    #############################################################################
    def getInputFiles(self, jobid):
        """For retrieving the input files for a given job.

        :param long jobid: bookkeeping job id
        :return: the input files for a given jobid
        """
        command = (
            " select files.filename from inputfiles,files where \
    files.fileid=inputfiles.fileid and inputfiles.jobid="
            + str(jobid)
        )
        res = self.dbR_.query(command)
        return res

    #############################################################################
    def getOutputFiles(self, jobid):
        """For retrieving the output files for a given job.

        :param long jobid: bookkeeping jobid
        :return: the outputfiles for a given jobid
        """
        command = " select files.filename from files where files.jobid =" + str(jobid)
        res = self.dbR_.query(command)
        return res

    #############################################################################
    def insertTag(self, name, tag):
        """inserts the CONDD,DDDB tags to the database.

        :param str name: tag name: CONDDB, DDDB, etc.
        :param str tag: CONDDB, DDDB tag
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.insertTag", [name, tag], False)

    #############################################################################
    def existsTag(self, name, value):  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """checks the tag existence in the database.

        :param str name: tag name: CONDDB, DDDB, etc.
        :param str value: CONDDB, DDDB, etc. tag
        """
        result = False
        command = "select count(*) from tags where name='%s' and tag='%s'" % (str(name), str(value))
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            result = retVal
        elif retVal["Value"][0][0] > 0:
            result = True
        return S_OK(result)

    #############################################################################
    def setFileDataQuality(self, lfns, flag):
        """sets the data quality for a list of lfns.

        :param list lfns: list of LFNs
        :param str flag: data quality flag
        """
        result = S_ERROR()
        values = {}
        retVal = self.__getDataQualityId(flag)
        if not retVal["OK"]:
            result = retVal
        else:
            qid = retVal["Value"]
            failed = []
            succ = []
            retVal = self.dbR_.executeStoredProcedure(
                packageName="BOOKKEEPINGORACLEDB.updateDataQualityFlag", parameters=[qid], output=False, array=lfns
            )
            if not retVal["OK"]:
                failed = lfns
                self.log.error(retVal["Message"])
            else:
                succ = lfns
            values["Successful"] = succ
            values["Failed"] = failed
            result = S_OK(values)
        return result

    #############################################################################
    def __getProcessingPassId(self, root, fullpath):
        """For retrieving processing pass id.

        :param str root: root path for example /Real Data
        :param str fullpath: full processing pass for exampe: /Real Data/Reco19/Stripping20
        :return: the processing pass id
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getProcessingPassId", int, [root, fullpath])

    #############################################################################
    def getProcessingPassId(self, fullpath):
        """For retrieving processing pass id.

        :param str fullpath: processing pass for example: /Real Data/Reco19
        :return: the processing pass identifier for a given path
        """
        return self.__getProcessingPassId(fullpath.split("/")[1:][0], fullpath)

    #############################################################################
    def __getDataQualityId(self, name):
        """For retrieving data quality id.

        :param str name: data quality for example OK, BAD, etc.
        :return: data quality id
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getDataQualityId", int, [name])

    #############################################################################
    def setRunAndProcessingPassDataQuality(self, runNB, procpass, flag):
        """set the data quality of a run which belongs to a given processing pass.

        :param int runNB: run number
        :param str procpass: processing pass
        :param str flag: data quality flag
        """
        retVal = self.__getProcessingPassId(procpass.split("/")[1:][0], procpass)
        if not retVal["OK"]:
            self.log.error("Could not get a processing pass ID", retVal["Message"])
            return retVal
        processingid = retVal["Value"]

        retVal = self.__getDataQualityId(flag)
        if not retVal["OK"]:
            self.log.error("Could not get a data quality ID", retVal["Message"])
            return retVal
        flag = retVal["Value"]

        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.insertRunquality", [runNB, flag, processingid], False
        )

    #############################################################################
    def setRunDataQuality(self, runNb, flag):
        """sets the data quality flag for a given run.

        :param long runNb: run number
        :param flag: data quality flag
        """
        result = S_ERROR()
        command = (
            "select distinct j.runnumber from  jobs j, productionscontainer prod where \
    j.production=prod.production and \
    j.production<0 and \
    j.runnumber=%s"
            % (str(runNb))
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            result = retVal
        else:

            if not retVal["Value"]:
                result = S_ERROR("This " + str(runNb) + " run is missing in the BKK DB!")
            else:
                retVal = self.__getDataQualityId(flag)

                if not retVal["OK"]:
                    result = retVal
                else:
                    qid = retVal["Value"]
                    utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    command = (
                        " update files set inserttimestamp=TO_TIMESTAMP('%s','YYYY-MM-DD HH24:MI:SS'), \
          qualityId=%d where fileid in ( select files.fileid from jobs, files where jobs.jobid=files.jobid and \
            jobs.runnumber=%d)"
                        % (str(utctime), qid, runNb)
                    )
                    retVal = self.dbW_.query(command)

                    if not retVal["OK"]:
                        result = retVal
                    else:
                        command = (
                            "select files.filename from jobs, files where jobs.jobid=files.jobid and \
              jobs.runnumber=%s"
                            % (runNb)
                        )

                        retVal = self.dbR_.query(command)

                        if not retVal["OK"]:
                            result = retVal
                        else:
                            succ = []
                            records = retVal["Value"]
                            for record in records:
                                succ += [record[0]]
                            values = {}
                            values["Successful"] = succ
                            values["Failed"] = []
                            result = S_OK(values)
        return result

    #############################################################################
    def setProductionDataQuality(self, prod, flag):
        """sets the data quality to a production.

        :param int prod: production number
        :param str flag: data quality flag
        """
        result = S_ERROR()
        command = "select distinct jobs.production  from jobs where jobs.production=%d" % (prod)
        retVal = self.dbR_.query(command)

        if not retVal["OK"]:
            result = retVal
        else:

            if not retVal["Value"]:
                result = S_ERROR("This " + str(prod) + " production is missing in the BKK DB!")
            else:
                retVal = self.__getDataQualityId(flag)

                if not retVal["OK"]:
                    result = retVal
                else:
                    qid = retVal["Value"]
                    utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    command = (
                        " update files set inserttimestamp=TO_TIMESTAMP('%s' + str(utctime),'YYYY-MM-DD HH24:MI:SS'), \
          qualityId=%d where fileid in ( select files.fileid from jobs, files where jobs.jobid=files.jobid and \
            jobs.production=%d)"
                        % (str(utctime), qid, prod)
                    )
                    retVal = self.dbW_.query(command)

                    if not retVal["OK"]:
                        result = retVal
                    else:
                        command = (
                            "select files.filename from jobs, files where jobs.jobid=files.jobid and \
              jobs.production=%d"
                            % (prod)
                        )
                        retVal = self.dbR_.query(command)

                        if not retVal["OK"]:
                            result = retVal
                        else:
                            succ = []
                            records = retVal["Value"]
                            for record in records:
                                succ += [record[0]]
                            values = {}
                            values["Successful"] = succ
                            values["Failed"] = []
                            result = S_OK(values)
        return result

    #############################################################################
    def getFileAncestorHelper(self, fileName, files, depth, checkreplica):
        """Recursively retrieve the ancestors for a given file.

        :param str fileName: actual file name
        :param list files: the ancestor files list
        :param int depth: the depth of the processing pass chain(how far to go)
        :param bool checkreplica: take into account the replica flag
        :return: the ancestor of a file
        """
        failed = []

        if depth:
            depth -= 1
            result = self.dbR_.executeStoredFunctions(
                "BOOKKEEPINGORACLEDB.getJobIdWithoutReplicaCheck", int, [fileName]
            )

            if not result["OK"]:
                self.log.error("Error getting jobID", result["Message"])
            jobID = int(result.get("Value", 0))
            if jobID:
                command = (
                    "select files.fileName,files.jobid, files.gotreplica, files.eventstat,\
         files.eventtypeid, files.luminosity, files.instLuminosity, filetypes.name \
        from inputfiles,files, filetypes where files.filetypeid=filetypes.filetypeid \
         and inputfiles.fileid=files.fileid and inputfiles.jobid=%d"
                    % (jobID)
                )
                res = self.dbR_.query(command)
                if not res["OK"]:
                    self.log.error("Error getting job input files", result["Message"])
                else:
                    dbResult = res["Value"]
                    for record in dbResult:
                        if not checkreplica or (record[2] != "No"):
                            files.append(
                                {
                                    "FileName": record[0],
                                    "GotReplica": record[2],
                                    "EventStat": record[3],
                                    "EventType": record[4],
                                    "Luminosity": record[5],
                                    "InstLuminosity": record[6],
                                    "FileType": record[7],
                                }
                            )
                        if depth:
                            failed += self.getFileAncestorHelper(record[0], files, depth, checkreplica)
            else:
                failed.append(fileName)
        return failed

    #############################################################################
    def getFileAncestors(self, lfn, depth=0, replica=True):
        """ " iterates on the list of lfns and prepare the ancestor list using a
        recursive helper function.

        :param list lfn:
        :param int depth: the depth of the processing pass chain(how far to go)
        :param bool replica: take into account the replica flag
        """
        depth = min(10, max(1, depth))

        logicalFileNames = {"Failed": []}
        ancestorList = {}
        filesWithMetadata = {}
        self.log.debug("original", "%s" % lfn)
        failed = []
        for fileName in lfn:
            files = []
            failed += self.getFileAncestorHelper(fileName, files, depth, replica)
            logicalFileNames["Failed"] = failed
            if files:
                ancestorList[fileName] = files
                tmpfiles = {}
                for i in files:
                    tmpattr = dict(i)
                    tmpfiles[tmpattr.pop("FileName")] = tmpattr
                filesWithMetadata[fileName] = tmpfiles
        logicalFileNames["Successful"] = ancestorList
        logicalFileNames["WithMetadata"] = filesWithMetadata
        return S_OK(logicalFileNames)

    #############################################################################
    def getFileDescendentsHelper(self, fileName, files, depth, production, checkreplica, productionFound=False):
        """Helper function for retrieving the file descendents.

        :param str fileName: actual file name
        :param list files: the descendents file list (producced files)
        :param int depth: the depth of the processing pass chain(how far to go)
        :param productin: production number
        :param bool checkreplica: take into account the replica flag
        :param bool productionFound: It breaks the check if the production found
          but we but we no longer are in it
        :return: the descendents of a file
        """
        failed = set()
        notprocessed = set()

        if depth:
            depth -= 1

            res = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getFileDesJobId", [fileName])
            if not res["OK"]:
                self.log.error("Error getting fileId", res["Message"])
                failed.add(fileName)
            elif not res["Value"]:
                notprocessed.add(fileName)
            else:
                for jobID in [item[0] for item in res["Value"]]:
                    getProd = bool(production)

                    res = self.dbW_.executeStoredProcedure(
                        "BOOKKEEPINGORACLEDB.getFileAndJobMetadata", [jobID, getProd]
                    )
                    if not res["OK"]:
                        self.log.error("Error getting job output files", res["Message"])
                        failed.add(fileName)
                    elif not res["Value"]:
                        notprocessed.add(fileName)
                    else:
                        for record in res["Value"]:
                            inRequestedProd = getProd and int(record[3]) == int(production)
                            if not productionFound or inRequestedProd:
                                # If we have already found the production but we no longer are in it, break the recursive loop
                                if (not checkreplica or (record[2] != "No")) and (not getProd or inRequestedProd):
                                    files[record[0]] = {
                                        "GotReplica": record[2],
                                        "EventStat": record[4],
                                        "EventType": record[5],
                                        "Luminosity": record[6],
                                        "InstLuminosity": record[7],
                                        "FileType": record[8],
                                    }

                                if depth:
                                    # Only call if we are not at the correct depth
                                    newFailed, _newNotprocessed = self.getFileDescendentsHelper(
                                        record[0],
                                        files,
                                        depth,
                                        production,
                                        checkreplica,
                                        productionFound=inRequestedProd,
                                    )
                                    failed.update(newFailed)

        return sorted(failed), sorted(notprocessed)

    #############################################################################
    def getFileDescendents(self, lfn, depth=0, production=0, checkreplica=True):
        """iterates over a list of lfns and collects their descendents.

        :param str fileName: actual file name
        :param list files: the descendents file list (producced files)
        :param int depth: the depth of the processing pass chain(how far to go)
        :param productin: production number
        :param bool checkreplica: take into account the replica flag
        :returns: all descendents
        """
        logicalFileNames = {"Failed": [], "NotProcessed": []}
        ancestorList = {}
        filesWithMetadata = {}

        depth = min(10, max(1, depth))

        for fileName in lfn:
            files = {}
            failed, notprocessed = self.getFileDescendentsHelper(fileName, files, depth, production, checkreplica)
            logicalFileNames["Failed"] += failed
            logicalFileNames["NotProcessed"] += notprocessed
            if files:
                ancestorList[fileName] = list(files)
                filesWithMetadata[fileName] = files
        logicalFileNames["Successful"] = ancestorList
        logicalFileNames["WithMetadata"] = filesWithMetadata
        return S_OK(logicalFileNames)

    #############################################################################
    def checkfile(self, fileName):  # file
        """checks the status of a file.

        :param str fileName: logical file name
        :return: fileId, jobId, filetypeid
        """
        result = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.checkfile", [fileName])
        if not result["OK"]:
            return result

        res = result["Value"]
        if res:
            return S_OK(res)
        self.log.warn("File not found! ", "%s" % fileName)
        return S_ERROR("File not found: %s" % fileName)

    #############################################################################
    def checkFileTypeAndVersion(self, filetype, version):  # fileTypeAndFileTypeVersion(self, type, version):
        """checks the the format and the version.

        :param str filetype: file type
        :param str version: file type version
        :return: file type id
        """
        return self.dbR_.executeStoredFunctions("BOOKKEEPINGORACLEDB.checkFileTypeAndVersion", int, [filetype, version])

    #############################################################################
    def checkEventType(self, eventTypeId):  # eventType(self, eventTypeId):
        """checks the event type.

        :param long eventTypeId: event type
        :return: event type
        """
        result = S_ERROR()

        retVal = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.checkEventType", [eventTypeId])
        if retVal["OK"]:
            value = retVal["Value"]
            if value:
                result = S_OK(value)
            else:
                self.log.info("Event type not found:", "%s" % eventTypeId)
                result = S_ERROR("Event type not found: %s" % eventTypeId)
        else:
            result = retVal
        return result

    #############################################################################
    def insertJob(self, job):
        """inserts a job to the database.

        :param dict job: job attributes
        :returns: jobId
        """
        self.log.debug("Insert job into database!")
        attrList = {
            "ConfigName": None,
            "ConfigVersion": None,
            "DiracJobId": None,
            "DiracVersion": None,
            "EventInputStat": None,
            "ExecTime": None,
            "FirstEventNumber": None,
            "JobEnd": None,
            "JobStart": None,
            "Location": None,
            "Name": None,
            "NumberOfEvents": None,
            "Production": None,
            "ProgramName": None,
            "ProgramVersion": None,
            "StatisticsRequested": None,
            "WNCPUPOWER": None,
            "CPUTIME": None,
            "WNCACHE": None,
            "WNMEMORY": None,
            "WNMODEL": None,
            "WorkerNode": None,
            "RunNumber": None,
            "FillNumber": None,
            "WNCPUHS06": 0,
            "TotalLuminosity": 0,
            "Tck": "None",
            "StepID": None,
            "WNMJFHS06": 0,
            "HLT2Tck": "None",
            "NumberOfProcessors": 1,
        }

        for param in job:
            if not attrList.__contains__(param):
                self.log.error("insert job error: ", " the job table not contain attribute %s" % param)
                return S_ERROR(" The job table not contain attribute %s" % param)

            if param == "JobStart" or param == "JobEnd":  # We have to convert data format
                dateAndTime = job[param].split(" ")
                date = dateAndTime[0].split("-")
                time = dateAndTime[1].split(":")
                if len(time) > 2:
                    timestamp = datetime.datetime(
                        int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]), 0
                    )
                else:
                    timestamp = datetime.datetime(
                        int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), 0, 0
                    )
                attrList[param] = timestamp
            else:
                attrList[param] = job[param]

        try:
            conv = int(attrList["Tck"])
            attrList["Tck"] = str(hex(conv))
        except ValueError:
            pass  # it is already defined

        result = self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.insertJobsRow",
            int,
            [
                attrList["ConfigName"],
                attrList["ConfigVersion"],
                attrList["DiracJobId"],
                attrList["DiracVersion"],
                attrList["EventInputStat"],
                attrList["ExecTime"],
                attrList["FirstEventNumber"],
                attrList["JobEnd"],
                attrList["JobStart"],
                attrList["Location"],
                attrList["Name"],
                attrList["NumberOfEvents"],
                attrList["Production"],
                attrList["ProgramName"],
                attrList["ProgramVersion"],
                attrList["StatisticsRequested"],
                attrList["WNCPUPOWER"],
                attrList["CPUTIME"],
                attrList["WNCACHE"],
                attrList["WNMEMORY"],
                attrList["WNMODEL"],
                attrList["WorkerNode"],
                attrList["RunNumber"],
                attrList["FillNumber"],
                attrList["WNCPUHS06"],
                attrList["TotalLuminosity"],
                attrList["Tck"],
                attrList["StepID"],
                attrList["WNMJFHS06"],
                attrList["HLT2Tck"],
                attrList["NumberOfProcessors"],
            ],
        )
        return result

    #############################################################################
    def insertInputFile(self, jobID, fileId):
        """inserts the input file of a job.

        :param long jobID: internal bookkeeping job id
        :param long fileId: internal file id
        """
        result = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.insertInputFilesRow", [fileId, jobID], False)
        return result

    #############################################################################
    def insertOutputFile(self, fileobject):
        """inserts an output file.

        :param dict fileobject: file attributes
        :returns: fileid
        """
        attrList = {
            "Adler32": None,
            "CreationDate": None,
            "EventStat": None,
            "EventTypeId": None,
            "FileName": None,
            "FileTypeId": None,
            "GotReplica": None,
            "Guid": None,
            "JobId": None,
            "MD5Sum": None,
            "FileSize": 0,
            "FullStat": None,
            "QualityId": "UNCHECKED",
            "Luminosity": 0,
            "InstLuminosity": 0,
            "VisibilityFlag": "Y",
        }

        for param in fileobject:
            if param not in attrList:
                self.log.error("insert file error: ", " the files table not contain attribute %s " % param)
                return S_ERROR(" The files table not contain attribute %s" % param)

            if param == "CreationDate":  # We have to convert data format
                dateAndTime = fileobject[param].split(" ")
                date = dateAndTime[0].split("-")
                time = dateAndTime[1].split(":")
                timestamp = datetime.datetime(
                    int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), 0, 0
                )
                attrList[param] = timestamp
            else:
                attrList[param] = fileobject[param]
        utctime = datetime.datetime.utcnow()

        return self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.insertFilesRow",
            int,
            [
                attrList["Adler32"],
                attrList["CreationDate"],
                attrList["EventStat"],
                attrList["EventTypeId"],
                attrList["FileName"],
                attrList["FileTypeId"],
                attrList["GotReplica"],
                attrList["Guid"],
                attrList["JobId"],
                attrList["MD5Sum"],
                attrList["FileSize"],
                attrList["FullStat"],
                utctime,
                attrList["QualityId"],
                attrList["Luminosity"],
                attrList["InstLuminosity"],
                attrList["VisibilityFlag"],
            ],
        )

    #############################################################################
    def updateReplicaRow(self, fileID, replica):  # , name, location):
        """adds the replica flag.

        :param long fileID: internal bookkeeping file id
        :param str replica: replica flag
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.updateReplicaRow", [fileID, replica], False)

    #############################################################################
    def deleteJob(self, jobID):
        """deletes a job.

        :param long jobID: internal bookkeeping job id
        """
        self.log.warn("Deleting job", jobID)
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.deleteJob", [jobID], False)

    #############################################################################
    def deleteInputFiles(self, jobID):
        """deletes the input files of a job.

        :param long jobid:internal bookkeeping job id
        """
        self.log.warn("Deleting input files of", jobID)
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.deleteInputFiles", [jobID], False)

    #############################################################################
    def deleteFile(self, fileID):
        """deletes a file.

        :param long fileid: internal bookkeeping file id
        """
        self.log.warn("Deleting file", fileID)
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.deletefile", [fileID], False)

    #############################################################################
    @staticmethod
    def deleteFiles(lfns):
        """For having the same interface as other catalogs. We do not delete file
        from the db.

        :param list lfns: list of lfns
        """
        return S_ERROR("Not Implemented !!" + lfns)

    #############################################################################
    def insertSimConditions(self, in_dict):
        """inserts a simulation conditions.

        :param dict in_dict: simulation condition attributes
        :return: simid
        """

        simdesc = in_dict.get("SimDescription", None)
        beamCond = in_dict.get("BeamCond", None)
        beamEnergy = in_dict.get("BeamEnergy", None)
        generator = in_dict.get("Generator", None)
        magneticField = in_dict.get("MagneticField", None)
        detectorCond = in_dict.get("DetectorCond", None)
        luminosity = in_dict.get("Luminosity", None)
        g4settings = in_dict.get("G4settings", None)
        visible = in_dict.get("Visible", "Y")
        return self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.insertSimConditions",
            int,
            [simdesc, beamCond, beamEnergy, generator, magneticField, detectorCond, luminosity, g4settings, visible],
        )

    #############################################################################
    def getSimConditions(self):
        """For retrieving the simulation conditions.

        :rerturn: the available simulation conditions
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getSimConditions", [])

    #############################################################################
    def insertDataTakingCond(self, conditions):
        """inserts a data taking condition:

        :param dict conditions: data taking conditions attributes.
        :returns: data quality id
        """
        datataking = {
            "Description": None,
            "BeamCond": None,
            "BeamEnergy": None,
            "MagneticField": None,
            "VELO": None,
            "IT": None,
            "TT": None,
            "OT": None,
            "RICH1": None,
            "RICH2": None,
            "SPD_PRS": None,
            "ECAL": None,
            "HCAL": None,
            "MUON": None,
            "L0": None,
            "HLT": None,
            "VeloPosition": None,
        }

        for param in conditions:
            if not datataking.__contains__(param):
                self.log.error("Can not insert data taking condition the files table not contains:", "%s" % param)
                return S_ERROR("Can not insert data taking condition the files table not contains: %s " % param)
            datataking[param] = conditions[param]

        res = self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.insertDataTakingCond",
            int,
            [
                datataking["Description"],
                datataking["BeamCond"],
                datataking["BeamEnergy"],
                datataking["MagneticField"],
                datataking["VELO"],
                datataking["IT"],
                datataking["TT"],
                datataking["OT"],
                datataking["RICH1"],
                datataking["RICH2"],
                datataking["SPD_PRS"],
                datataking["ECAL"],
                datataking["HCAL"],
                datataking["MUON"],
                datataking["L0"],
                datataking["HLT"],
                datataking["VeloPosition"],
            ],
        )
        return res

    def insertDataTakingCondDesc(self, dtDescription: str):
        """inserts a data taking condition just from the description string

        It reuses the existing oracle function until we decide what to do
        with this table.

        :param dtDescription: data taking conditions description
        :returns: data quality id
        """

        res = self.dbW_.executeStoredFunctions(
            "BOOKKEEPINGORACLEDB.insertDataTakingCond",
            int,
            [
                dtDescription,
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
                "None",
            ],
        )
        return res

    def deleteDataTakingCondition(self, dtcId):
        """it deletes a given data taking condition.

        :param int dtcId: Data taking condition ID
        """
        return self.dbW_.query("delete data_taking_conditions where DaqPeriodId=:dtcId", kwparams={"dtcId": dtcId})

    #############################################################################
    def removeReplica(self, fileNames):
        """removes the replica flag of a file.

        :param list fileNames: list LFNs
        :return: successfully deleted and failed to delete LFNs
        """
        result = S_ERROR()
        retVal = self.dbR_.executeStoredProcedure(
            packageName="BOOKKEEPINGORACLEDB.bulkcheckfiles", parameters=[], output=True, array=fileNames
        )
        failed = {}

        if not retVal["OK"]:
            result = retVal
        else:
            for i in retVal["Value"]:
                failed[i[0]] = "The file %s does not exist in the BKK database!!!" % (i[0])
                fileNames.remove(i[0])
            if fileNames:
                retVal = self.dbW_.executeStoredProcedure(
                    packageName="BOOKKEEPINGORACLEDB.bulkupdateReplicaRow",
                    parameters=["No"],
                    output=False,
                    array=fileNames,
                )
                if not retVal["OK"]:
                    result = retVal
                else:
                    failed["Failed"] = list(failed)
                    failed["Successful"] = fileNames
                    result = S_OK(failed)
            else:  # when no files are exists
                files = {"Failed": [i[0] for i in retVal["Value"]], "Successful": []}
                result = S_OK(files)
        return result

    #############################################################################
    def getFileMetadata(self, lfns):
        """returns the metadata of a list of files.

        :param list lfns: list of LFNs
        :return: successful lfns with associated meta data and failed lfns.
        """
        result = {}

        for lfnList in breakListIntoChunks(lfns, 5000):
            retVal = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getFileMetaData3", [], True, lfnList)
            if not retVal["OK"]:
                result = retVal
            else:
                for record in retVal["Value"]:
                    row = {
                        "ADLER32": record[1],
                        "CreationDate": record[2],
                        "EventStat": record[3],
                        "FullStat": record[10],
                        "EventType": record[4],
                        "FileType": record[5],
                        "GotReplica": record[6],
                        "GUID": record[7],
                        "MD5SUM": record[8],
                        "FileSize": record[9],
                        "DataqualityFlag": record[11],
                        "JobId": record[12],
                        "RunNumber": record[13],
                        "InsertTimeStamp": record[14],
                        "Luminosity": record[15],
                        "InstLuminosity": record[16],
                        "VisibilityFlag": record[17],
                    }
                    result[record[0]] = row

        retVal = {"Successful": result, "Failed": list(set(lfns) - set(result))}
        return S_OK(retVal)

    #############################################################################
    def getFileMetaDataForWeb(self, lfns):
        """For retrieving file metdata for web.

        :param list lfns: list of LFNs

        :returns lfn metadata
        """
        totalrecords = len(lfns)
        parametersNames = ["Name", "FileSize", "FileType", "CreationDate", "EventType", "EventStat", "GotReplica"]
        records = []
        for lfn in lfns:
            res = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getFileMetaData", [lfn])
            if not res["OK"]:
                records = [str(res["Message"])]
            else:
                values = res["Value"]
                for record in values:
                    row = [lfn, record[9], record[5], record[2], record[4], record[3], record[6]]
                    records += [row]
        return S_OK({"TotalRecords": totalrecords, "ParameterNames": parametersNames, "Records": records})

    #############################################################################
    def __getProductionStatisticsForUsers(self, prod):
        """For retrieving the statistics of a production.

        :param int prod: production number
        :return: number of files, evenet stat, filesize end luminosity
        """
        command = (
            "select count(*), SUM(files.EventStat), SUM(files.FILESIZE), sum(files.Luminosity), \
    sum(files.instLuminosity) from files ,jobs where jobs.jobid=files.jobid and jobs.production=%d"
            % (prod)
        )
        res = self.dbR_.query(command)
        return res

    #############################################################################
    def getProductionFilesForWeb(self, prod, ftypeDict, sortDict, startItem, maxitems):
        """For retrieving the production file used by WebApp.

        :param int prod: production number
        :param dict ftypeDict: dictionary which contains the file type.
        :param dict sortDict: the columns which will be sorted.
        :param int startItem: used for paging. The row number
        :param int maxitems: number of rows
        :return: production files and its meta data
        """
        command = ""
        parametersNames = [
            "Name",
            "FileSize",
            "FileType",
            "CreationDate",
            "EventType",
            "EventStat",
            "GotReplica",
            "InsertTimeStamp",
            "Luminosity",
            "InstLuminosity",
        ]
        records = []
        result = S_ERROR()

        totalrecords = 0
        nbOfEvents = 0
        filesSize = 0
        ftype = ftypeDict["type"]
        if sortDict:
            res = self.__getProductionStatisticsForUsers(prod)
            if not res["OK"]:
                self.log.error(res["Message"])
            else:
                totalrecords = res["Value"][0][0]
                nbOfEvents = res["Value"][0][1]
                filesSize = res["Value"][0][2]

        if ftype != "ALL":

            command = (
                "select rnum, filename, filesize, name , creationdate, eventtypeId, \
      eventstat,gotreplica, inserttimestamp , luminosity ,instLuminosity from \
                ( select rownum rnum, filename, filesize, name , creationdate, \
                eventtypeId, eventstat, gotreplica, inserttimestamp, luminosity,instLuminosity \
                from ( select files.filename, files.filesize, filetypes.name , files.creationdate, \
                files.eventtypeId, files.eventstat,files.gotreplica, \
                files.inserttimestamp, files.luminosity, files.instLuminosity \
                           from jobs,files, filetypes where \
                           jobs.jobid=files.jobid and \
                           jobs.production=%s and filetypes.filetypeid=files.filetypeid and filetypes.name='%s' \
                           Order by files.filename) where rownum <= %d )\
                            where rnum > %d"
                % (prod, ftype, maxitems, startItem)
            )
        else:

            command = (
                "select rnum, fname, fsize, name, fcreation, feventtypeid,\
       feventstat, fgotreplica, finst, flumi, finstlumy from \
      (select rownum rnum, fname, fsize, ftypeid, fcreation, feventtypeid, \
      feventstat, fgotreplica, finst, flumi, finstlumy\
      from ( select files.filename fname, files.filesize fsize, filetypeid \
      ftypeid, files.creationdate fcreation, files.eventtypeId feventtypeid, \
          files.eventstat feventstat, files.gotreplica fgotreplica, \
          files.inserttimestamp finst, files.luminosity flumi, files.instLuminosity finstlumy\
            from jobs,files where\
            jobs.jobid=files.jobid and\
            jobs.production=%d\
            Order by files.filename) where rownum <=%d)f , filetypes ft where rnum > %d \
            and ft.filetypeid=f.ftypeid"
                % (prod, maxitems, startItem)
            )

        res = self.dbR_.query(command)
        if res["OK"]:
            dbResult = res["Value"]
            for record in dbResult:
                row = [record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8]]
                records += [row]
            result = S_OK(
                {
                    "TotalRecords": totalrecords,
                    "ParameterNames": parametersNames,
                    "Records": records,
                    "Extras": {"GlobalStatistics": {"Number of Events": nbOfEvents, "Files Size": filesSize}},
                }
            )
        else:
            result = res
        return result

    #############################################################################
    def exists(self, lfns):
        """checks the files in the databse.

        :param list lfns: list of LFNs
        :return: True or False depending of the file existence
        """
        result = {}
        for lfn in lfns:
            res = self.dbR_.executeStoredFunctions("BOOKKEEPINGORACLEDB.fileExists", int, [lfn])
            if not res["OK"]:
                return res
            if res["Value"] == 0:
                result[lfn] = False
            else:
                result[lfn] = True
        return S_OK(result)

    #############################################################################
    def addReplica(self, fileNames):
        """adds the replica flag to a file.

        :param list fileNames: list of LFNs
        :return: dictionary which contains the failed and successful lfns
        """
        retVal = self.dbR_.executeStoredProcedure(
            packageName="BOOKKEEPINGORACLEDB.bulkcheckfiles", parameters=[], output=True, array=fileNames
        )
        if not retVal["OK"]:
            return retVal

        failed = {}
        for i in retVal["Value"]:
            failed[i[0]] = "The file %s does not exist in the BKK database!!!" % (i[0])
            fileNames.remove(i[0])

        if fileNames:
            retVal = self.dbW_.executeStoredProcedure(
                packageName="BOOKKEEPINGORACLEDB.bulkupdateReplicaRow",
                parameters=["Yes"],
                output=False,
                array=fileNames,
            )
            if not retVal["OK"]:
                return retVal
            else:
                failed["Failed"] = list(failed)
                failed["Successful"] = fileNames
                return S_OK(failed)
        else:  # when no files exist
            files = {"Failed": [i[0] for i in retVal["Value"]], "Successful": []}
            return S_OK(files)

    #############################################################################
    def getRunInformations(self, runnb):
        """For retrieving the run statistics.

        :param long runnb: run number
        :return: the run statistics
        """
        result = S_ERROR()
        command = (
            "select distinct j.fillnumber, conf.configname, conf.configversion, \
    daq.description, j.jobstart, j.jobend, j.tck, j.TOTALLUMINOSITY \
        from jobs j, configurations conf,data_taking_conditions \
        daq, productionscontainer prod where \
        j.configurationid=conf.configurationid and \
        j.production<0 and prod.daqperiodid=daq.daqperiodid and\
         j.production=prod.production and j.runnumber=%d"
            % (runnb)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        value = retVal["Value"]
        if not value:
            return S_ERROR("This run is missing in the BKK DB!")

        values = {"Configuration Name": value[0][1], "Configuration Version": value[0][2], "FillNumber": value[0][0]}
        values["DataTakingDescription"] = value[0][3]
        values["RunStart"] = value[0][4]
        values["RunEnd"] = value[0][5]
        values["Tck"] = value[0][6]
        values["TotalLuminosity"] = value[0][7]

        retVal = self.getRunProcessingPass(runnb)
        if not retVal["OK"]:
            result = retVal
        else:
            values["ProcessingPass"] = retVal["Value"]
            command = (
                " select count(*), SUM(files.EventStat), SUM(files.FILESIZE), sum(files.fullstat), \
      files.eventtypeid , sum(files.luminosity), sum(files.instLuminosity)  from files,jobs \
           where files.JobId=jobs.JobId and  \
           files.gotReplica='Yes' and \
           jobs.production<0 and \
           jobs.runnumber="
                + str(runnb)
                + " Group by files.eventtypeid"
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result = retVal
            else:
                value = retVal["Value"]
                if not value:
                    result = S_ERROR("Replica flag is not set!")
                else:
                    nbfile = []
                    nbevent = []
                    fsize = []
                    fstat = []
                    stream = []
                    luminosity = []
                    ilumi = []
                    for i in value:
                        nbfile += [i[0]]
                        nbevent += [i[1]]
                        fsize += [i[2]]
                        fstat += [i[3]]
                        stream += [i[4]]
                        luminosity += [i[5]]
                        ilumi += [i[6]]

                    values["Number of file"] = nbfile
                    values["Number of events"] = nbevent
                    values["File size"] = fsize
                    values["FullStat"] = fstat
                    values["Stream"] = stream
                    values["luminosity"] = luminosity
                    values["InstLuminosity"] = ilumi
                    result = S_OK(values)

        return result

    #############################################################################
    def getRunInformation(self, inputParams):
        """For retrieving only the requested information for a given run.

        :param dict inputParams:RunNumber, Fields (CONFIGNAME, CONFIGVERSION, JOBSTART, JOBEND,
        TCK, FILLNUMBER, PROCESSINGPASS, CONDITIONDESCRIPTION,CONDDB, DDDB), Statistics (NBOFFILES, EVENTSTAT,
        FILESIZE, FULLSTAT, LUMINOSITY, INSTLUMINOSITY, EVENTTYPEID)
        :return: run statistics
        """
        result = S_ERROR()
        runnb = inputParams.get("RunNumber", default)
        if runnb == default:
            result = S_ERROR("The RunNumber must be given!")
        else:
            if isinstance(runnb, (six.string_types + six.integer_types)):
                runnb = [runnb]
            runs = ""
            for i in runnb:
                runs += "%d," % (int(i))
            runs = runs[:-1]
            fields = inputParams.get(
                "Fields",
                [
                    "CONFIGNAME",
                    "CONFIGVERSION",
                    "JOBSTART",
                    "JOBEND",
                    "TCK",
                    "FILLNUMBER",
                    "PROCESSINGPASS",
                    "CONDITIONDESCRIPTION",
                    "CONDDB",
                    "DDDB",
                ],
            )
            statistics = inputParams.get("Statistics", [])
            configurationsFields = ["CONFIGNAME", "CONFIGVERSION"]
            jobsFields = ["JOBSTART", "JOBEND", "TCK", "FILLNUMBER", "PROCESSINGPASS"]
            conditionsFields = ["CONDITIONDESCRIPTION"]
            stepsFields = ["CONDDB", "DDDB"]
            selection = ""
            tables = "jobs j,"
            conditions = " j.runnumber in (%s) and j.production <0 " % (runs)

            for i in fields:
                if i.upper() in configurationsFields:
                    if tables.find("configurations") < 0:
                        tables += " configurations c,"
                        conditions += " and j.configurationid=c.configurationid "
                    selection += "c.%s," % (i)
                elif i.upper() in jobsFields:
                    if i.upper() == "PROCESSINGPASS":
                        selection += "BOOKKEEPINGORACLEDB.getProductionProcessingPass(-1 * j.runnumber),"
                    else:
                        selection += "j.%s," % (i)
                elif i.upper() in conditionsFields:
                    if tables.find("productionscontainer") < 0:
                        tables += " productionscontainer prod, data_taking_conditions daq,"
                        conditions += " and j.production=prod.production and prod.daqperiodid=daq.daqperiodid "
                    selection += "daq.description,"
                elif i.upper() in stepsFields:
                    if tables.find("stepscontainer") < 0:
                        tables += " stepscontainer st, steps s,"
                        conditions += " and j.production=st.production and st.stepid=s.stepid "
                    selection += " s.%s," % (i)

            selection = selection[:-1]
            tables = tables[:-1]

            command = "select j.runnumber, %s from %s where %s" % (selection, tables, conditions)
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result = retVal
            else:
                values = {}
                for i in retVal["Value"]:
                    rnb = i[0]
                    i = i[1:]
                    record = dict(zip(fields, i))
                    values[rnb] = record

                if statistics:
                    filesFields = [
                        "NBOFFILES",
                        "EVENTSTAT",
                        "FILESIZE",
                        "FULLSTAT",
                        "LUMINOSITY",
                        "INSTLUMINOSITY",
                        "EVENTTYPEID",
                    ]
                    tables = "jobs j, files f"
                    conditions = (
                        " j.jobid=f.jobid and j.runnumber in (%s) and \
          j.production <0 and f.gotreplica='Yes' \
          Group by j.runnumber,f.eventtypeid"
                        % (runs)
                    )
                    selection = "j.runnumber,"
                    for i in statistics:
                        if i.upper() == "NBOFFILES":
                            selection += "count(*),"
                        elif i.upper() == "EVENTTYPEID":
                            selection += "f.%s," % (i)
                        elif i.upper() in filesFields:
                            selection += "sum(f.%s)," % (i)
                    selection = selection[:-1]
                    command = "select %s  from %s where %s" % (selection, tables, conditions)
                    retVal = self.dbR_.query(command)
                    if not retVal["OK"]:
                        result = retVal
                    else:
                        for i in retVal["Value"]:
                            rnb = i[0]
                            if "Statistics" not in values[rnb]:
                                values[rnb]["Statistics"] = []
                            i = i[1:]
                            record = dict(zip(statistics, i))
                            values[rnb]["Statistics"] += [record]
                result = S_OK(values)
        return result

    #############################################################################
    def getProductionFilesStatus(self, productionid=None, lfns=None):
        """the status of the files produced by a production.

        :param long productionid: production number
        :param list lfns: list of LFNs
        :return: replica, noreplica, missing
        """

        if lfns is None:
            lfns = []
        result = {}
        missing = []
        replicas = []
        noreplicas = []
        if productionid is not None:
            command = (
                "select files.filename, files.gotreplica from files,jobs where \
                 files.jobid=jobs.jobid and \
                 jobs.production=%d"
                % (productionid)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                return retVal
            files = retVal["Value"]
            for lfn in files:
                if lfn[1] == "Yes":
                    replicas += [lfn[0]]
                else:
                    noreplicas += [lfn[0]]
            result["replica"] = replicas
            result["noreplica"] = noreplicas
        elif lfns:
            for lfn in lfns:
                command = " select files.filename, files.gotreplica from files where filename='%s'" % (lfn)
                retVal = self.dbR_.query(command)
                if not retVal["OK"]:
                    return retVal
                value = retVal["Value"]
                if not value:
                    missing += [lfn]
                else:
                    for i in value:
                        if i[1] == "Yes":
                            replicas += [i[0]]
                        else:
                            noreplicas += [i[0]]
            result["replica"] = replicas
            result["noreplica"] = noreplicas
            result["missing"] = missing

        return S_OK(result)

    #############################################################################
    def getFileCreationLog(self, lfn):
        """For retrieving the Log file.

        :param str lfn: logical file name
        :return: the logs of a file
        """

        result = S_ERROR("getLogfile error!")
        command = "select files.jobid from files where files.filename='%s'" % (lfn)
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            result = retVal
        elif not retVal["Value"]:
            result = S_ERROR("Job not in the DB")
        else:
            jobid = retVal["Value"][0][0]
            command = (
                "select filename from files where \
      (files.filetypeid=17 or files.filetypeid=9) and files.jobid=%d"
                % (jobid)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result = retVal
            elif not retVal["Value"]:
                result = S_ERROR("Log file is not exist!")
            else:
                result = S_OK(retVal["Value"][0][0])
        return result

    #############################################################################
    def insertEventTypes(self, evid, desc, primary):
        """inserts an event type.

        :param long evid: event type id
        :param str desc: event type description
        :param str primary: event type short description
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.insertEventTypes", [desc, evid, primary], False)

    #############################################################################
    def updateEventType(self, evid, desc, primary):
        """updates and existing event type."""
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.updateEventTypes", [desc, evid, primary], False)

    #############################################################################
    def getProductionSummary(
        self, cName, cVersion, conddesc=default, processing=default, production=default, ftype=default, evttype=default
    ):
        """For retrieving the statistics for a given data set.

        :param str cName: configuration name
        :param str: cVersion: configuration version
        :param str: conddesc: simulation or data taking description
        :param str processing: processing pass
        :paran int production: production number
        :param str ftype: file type
        :param long evttype: event type id
        :return: production statistics
        """

        tables = " productionoutputfiles prod, productionscontainer cont, simulationconditions sim,\
     data_taking_conditions daq, configurations c "
        condition = (
            " cont.production=prod.production and\
    c.configurationid=cont.configurationid  %s "
            % self.__buildVisible(visible="Y", replicaFlag="Yes")
        )

        condition, tables = self.__buildConfiguration(cName, cVersion, condition, tables)

        condition, tables = self.__buildProduction(production, condition, tables, useMainTables=False)

        condition, tables = self.__buildEventType(evttype, condition, tables, useMainTables=False)

        retVal = self.__buildProcessingPass(processing, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildFileTypes(ftype, condition, tables, useMainTables=False)

        retVal = self._buildConditions(default, conddesc, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        command = (
            " select c.configname, c.configversion, sim.simdescription, daq.description, \
 cont.processingid, prod.eventtypeid,e.description, prod.production, ftypes.name, sum(f.eventstat) \
from jobs j, files f, filetypes ftypes, eventtypes e, %s where j.jobid= f.jobid and \
f.gotreplica='Yes' and prod.stepid= j.stepid and e.eventtypeid=f.eventtypeid and prod.eventtypeid=f.eventtypeid and\
  prod.stepid= j.stepid and sim.simid(+)=cont.simid and prod.filetypeid=f.filetypeid and \
  prod.filetypeid=ftypes.filetypeid and daq.daqperiodid(+)=cont.daqperiodid  and \
  prod.production = cont.production and %s\
  group by c.configname, c.configversion, sim.simdescription, \
    daq.description, cont.processingid, prod.eventtypeid, e.description, \
    prod.production, ftypes.name"
            % (tables, condition)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        parameters = [
            "ConfigurationName",
            "ConfigurationVersion",
            "ConditionDescription",
            "Processing pass ",
            "EventType",
            "EventType description",
            "Production",
            "FileType",
            "Number of events",
        ]
        dbResult = retVal["Value"]
        records = []
        nbRecords = 0
        for record in dbResult:
            if record[2] is not None:
                conddesc = record[2]
            else:
                conddesc = record[3]
            row = [record[0], record[1], conddesc, record[4], record[5], record[6], record[7], record[8], record[9]]
            records += [row]
            nbRecords += 1
        result = S_OK({"TotalRecords": nbRecords, "ParameterNames": parameters, "Records": records, "Extras": {}})

        return result

    #############################################################################
    def getProductionSimulationCond(self, prod):
        """For retrieving the simulation or data taking description of a
        production.

        :param int prod: production number
        :return: simulation condition
        """
        simdesc = None
        daqdesc = None

        command = (
            "select distinct sim.simdescription, daq.description from \
    simulationconditions sim, data_taking_conditions daq,productionscontainer prod \
              where sim.simid(+)=prod.simid and daq.daqperiodid(+)=prod.daqperiodid and prod.production="
            + str(prod)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        else:
            value = retVal["Value"]
            if value:
                simdesc = value[0][0]
                daqdesc = value[0][1]
            else:
                return S_ERROR("Simulation condition or data taking condition not exist!")

        if simdesc is not None:
            return S_OK(simdesc)
        else:
            return S_OK(daqdesc)

    #############################################################################
    def getFileHistory(self, lfn):
        """For retrieving the ancestor for a given file.

        :param str lfn: logical file name
        :retun: files and associated meta data
        """

        command = (
            "select  files.fileid, files.filename,files.adler32,\
    files.creationdate,files.eventstat,files.eventtypeid,files.gotreplica, \
files.guid,files.jobid,files.md5sum, files.filesize,files.fullstat, dataquality.\
dataqualityflag, files.inserttimestamp, files.luminosity, files.instLuminosity from files, dataquality \
where files.fileid in ( select inputfiles.fileid from files,inputfiles where \
files.jobid= inputfiles.jobid and files.filename='%s')\
and files.qualityid= dataquality.qualityid"
            % lfn
        )

        return self.dbR_.query(command)

    #############################################################################
    #
    #          MONITORING
    #############################################################################
    def getProductionNbOfJobs(self, prodid):
        """Number of jobs for given production.

        :param int prodid: production number
        :return: the number of jobs
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getJobsNb", [prodid])

    #############################################################################
    def getProductionNbOfEvents(self, prodid):
        """Number of event for a given production.

        :param int prodid: production number
        :return: the number of events
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getNumberOfEvents", [prodid])

    #############################################################################
    def getProductionSizeOfFiles(self, prodid):
        """Size of the files for a given production.

        :param int prodid: production number
        :return: the size of files
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getSizeOfFiles", [prodid])

    #############################################################################
    def getProductionNbOfFiles(self, prodid):
        """For retrieving number of files for a given production.

        :param int prodid: production number
        :return: the number of files
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getNbOfFiles", [prodid])

    #############################################################################
    @deprecated("Unused?")
    def getProductionInformation(self, prodid):
        """For retrieving production statistics.

        :param int prodid: production number
        :return: the statistics of a production
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getProductionInformation", [prodid])

    #############################################################################
    def getSteps(self, prodid):
        """For retrieving the production step.

        :param int prodid: production number

        :return: the steps used by a production, with resolved DB tags
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getSteps", [prodid])

    #############################################################################
    def getNbOfJobsBySites(self, prodid):
        """the number of successfully finished jobs at different Grid sites for a
        given production.

        :param int prodid: production number
        :return: number of jobs
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getJobsbySites", [prodid])

    #############################################################################
    def getConfigsAndEvtType(self, prodid):
        """For retrieving the configuration name, version and event type.

        :param int prodid: production number
        :return: the configurations and event type of a production
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getConfigsAndEvtType", [prodid])

    #############################################################################
    def getAvailableTags(self):
        """For retrieving the database tags.

        :return: the tags
        """
        command = "select name, tag from tags order by inserttimestamp desc"
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        parameters = ["TagName", "TagValue"]
        dbResult = retVal["Value"]
        records = []
        nbRecords = 0
        for record in dbResult:
            row = [record[0], record[1]]
            records += [row]
            nbRecords += 1
        return S_OK({"TotalRecords": nbRecords, "ParameterNames": parameters, "Records": records, "Extras": {}})

    #############################################################################
    def getProductionProcessedEvents(self, prodid):
        """For retreiving all events in specific production.

        :param int prodid: production number
        :return: the processed event by a production
        """
        return self.dbR_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getProcessedEvents", int, [prodid])

    #############################################################################
    def getRunsForAGivenPeriod(self, in_dict):
        """For retrieving list of runs.

        :param dict in_dict: bkQuery bookkeeping query
        :return: the runs for a given conditions
        """
        condition = ""
        startDate = in_dict.get("StartDate", default)
        endDate = in_dict.get("EndDate", default)
        allowOutside = in_dict.get("AllowOutsideRuns", default)

        if allowOutside != default:
            if startDate == default and endDate == default:
                return S_ERROR("The Start and End date must be given!")
            else:
                condition += " and jobs.jobstart >= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (startDate)
                condition += " and jobs.jobstart <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (endDate)
        else:
            if startDate != default:
                condition += " and jobs.jobstart >= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (startDate)
            if endDate != default:
                condition += " and jobs.jobend <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (endDate)
            elif startDate != default and endDate == default:
                currentTimeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                condition += (
                    " and jobs.jobend <= TO_TIMESTAMP ('" + str(currentTimeStamp) + "','YYYY-MM-DD HH24:MI:SS')"
                )
                condition += " and jobs.jobend <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(currentTimeStamp))

        command = " select jobs.runnumber from jobs where jobs.production < 0" + condition
        retVal = self.dbR_.query(command)
        runIds = []
        if retVal["OK"]:
            records = retVal["Value"]
            for record in records:
                if record[0] is not None:
                    runIds += [record[0]]
        else:
            return retVal

        check = in_dict.get("CheckRunStatus", False)
        if check:
            processedRuns = []
            notProcessedRuns = []
            for i in runIds:
                command = (
                    "select files.filename from files,jobs where jobs.jobid=files.jobid\
         and files.gotreplica='Yes' and jobs.production<0 and jobs.runnumber=%d"
                    % (i)
                )
                retVal = self.dbR_.query(command)
                if retVal["OK"]:
                    files = retVal["Value"]
                    ok = True
                    for lfn in files:
                        name = lfn[0]
                        retVal = self.getFileDescendents([name], 1, 0, True)
                        successful = retVal["Value"]["Successful"]
                        if not successful:
                            ok = False
                    if ok:
                        processedRuns += [i]
                    else:
                        notProcessedRuns += [i]
            return S_OK({"Runs": runIds, "ProcessedRuns": processedRuns, "NotProcessedRuns": notProcessedRuns})
        else:
            return S_OK({"Runs": runIds})
        return S_ERROR()

    #############################################################################

    # FIXME: is this useful at all? Does prodrunview still exist?
    def getProductionsFromView(self, in_dict):
        """For retrieving productions.

        :param dict in_dict: bkQuery bookkeeping query
        :return: the productions using the bookkeeping view
        """
        run = in_dict.get("RunNumber", in_dict.get("Runnumber", default))
        proc = in_dict.get("ProcessingPass", in_dict.get("ProcPass", default))
        result = S_ERROR()
        if "Runnumber" in in_dict:
            self.log.verbose("The Runnumber has changed to RunNumber!")

        if run != default:
            if proc != default:
                retVal = self.__getProcessingPassId(proc.split("/")[1:][0], proc)
                if retVal["OK"]:
                    processingid = retVal["Value"]
                    command = (
                        "select distinct prod.production  from productionoutputfiles prod,\
           prodrunview prview, productionscontainer cont where \
      prod.production=prview.production and prview.runnumber=%d and \
      prod.production>0 and prod.production=cont.production and cont.processingid=%d"
                        % (run, processingid)
                    )
                    result = self.dbR_.query(command)
            else:
                result = S_ERROR("The processing pass is missing!")
        else:
            result = S_ERROR("The run number is missing!")

        return result

    #############################################################################
    def getRunFilesDataQuality(self, runs):
        """For retrieving list of files.

        :param list runs: list of run numbers
        :retun: the files with data quality
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getRunQuality", [], True, runs)

    #############################################################################
    def getRunAndProcessingPassDataQuality(self, runnb, processing):
        """For retrieving the data quality flag for run and processing pass.

        :param int runnb: run number
        :param str processing: processing pass
        :return: data quality
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getQFlagByRunAndProcId", str, [runnb, processing])

    #############################################################################
    def getRunWithProcessingPassAndDataQuality(self, procpass, flag=default):
        """For retrieving a list of runs for a given processing pass and data
        quality flag.

        :param str procpass: processing pass
        :param str flag: file data quality flag
        :return: runs
        """
        retVal = self.__getProcessingPassId(procpass.split("/")[1:][0], procpass)
        if retVal["OK"]:
            processingid = retVal["Value"]
            qualityid = None
            if flag != default:
                retVal = self.__getDataQualityId(flag)
                if retVal["OK"]:
                    qualityid = retVal["Value"]
                else:
                    return retVal
        retVal = self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.getRunByQflagAndProcId", [processingid, qualityid]
        )
        if not retVal["OK"]:
            return retVal
        else:
            result = [i[0] for i in retVal["Value"]]
        return S_OK(result)

    #############################################################################
    def setFilesInvisible(self, lfns):
        """sets a given list of lfn invisible.

        :param list lfns: list of LFNs
        """

        for i in lfns:
            retVal = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.setFileInvisible", [i], False)
            if not retVal["OK"]:
                return retVal
        return S_OK("The files are invisible!")

    #############################################################################
    def setFilesVisible(self, lfns):
        """sets a given list of lfn visible.

        :param list lfns: list of LFNs
        """
        for i in lfns:
            res = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.setFileVisible", [i], False)
            if not res["OK"]:
                return res
        return S_OK("The files are visible!")

    #############################################################################
    def getFiles(
        self,
        simdesc,
        datataking,
        procPass,
        ftype,
        evt,
        configName=default,
        configVersion=default,
        production=default,
        flag=default,
        startDate=None,
        endDate=None,
        nbofEvents=False,
        startRunID=None,
        endRunID=None,
        runnumbers=None,
        replicaFlag=default,
        visible=default,
        filesize=False,
        tcks=None,
        jobStart=None,
        jobEnd=None,
    ):
        """returns a list of lfns.

        :param str simdesc: simulation condition description
        :param str datataking: data taking condition description
        :pram str procPass: processing pass
        :param str ftype: file type
        :param long evt: event type
        :param str configName: configuration name
        :param str configVersion: configuration version
        :param int production: production number
        :param str flag: data quality flag
        :param datetime startDate: job/run insert start time stamp
        :param datetime endDate: job/run insert end time stamp
        :param bool nbofEvents: count number of events
        :param long startRunID: start run number
        :param long endRunID: end run number
        :param list runnumbers: list of run numbers
        :param str replicaFlag: file replica flag
        :param str visible: file visibility flag
        :param bool filesize: only sum the files size
        :param list tcks: list of run TCKs
        :param datetime jobStart: job starte date
        :param datetime jobEnd: job end date
        :returns: list of files
        """

        if runnumbers is None:
            runnumbers = []

        if tcks is None:
            tcks = []

        condition = ""
        tables = " files f,jobs j "

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        condition, tables = self.__buildProduction(production, condition, tables)

        retVal = self.__buildTCKS(tcks, condition)
        if not retVal["OK"]:
            return retVal
        condition = retVal["Value"]

        retVal = self.__buildProcessingPass(procPass, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildFileTypes(ftype, condition, tables)

        retVal = self._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildEventType(evt, condition, tables)

        condition = self.__buildStartenddate(startDate, endDate, condition)

        condition = self.__buildJobsStartJobEndDate(jobStart, jobEnd, condition)

        retVal = self.__buildDataquality(flag, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition = self.__buildReplicaflag(replicaFlag, condition)

        condition, tables = self.__buildVisibilityflag(visible, condition, tables)

        retVal = self._buildConditions(simdesc, datataking, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        # hint = ''
        # if (not startDate and not endDate) and tables.strip() == 'files f,jobs j  ,filetypes ft':
        #  hint = '/*+INDEX(j JOBS_PRODUCTIONID) INDEX(f FILES_JOB_EVENT_FILETYPE) INDEX(ft FILETYPES_ID_NAME)*/'

        if nbofEvents:
            command = (
                " select sum(f.eventstat) \
      from %s where f.jobid= j.jobid %s "
                % (tables, condition)
            )
        elif filesize:
            command = (
                " select sum(f.filesize) \
      from %s where f.jobid= j.jobid %s "
                % (tables, condition)
            )
        else:
            command = (
                " select distinct f.filename \
      from %s where f.jobid= j.jobid %s "
                % (tables, condition)
            )
        return self.dbR_.query(command)

    #############################################################################
    @staticmethod
    def __buildConfiguration(configName, configVersion, condition, tables):
        """it make the condition string for a given configName and configVersion.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str condition: condition string
        :param str tables: tables used by join
        :return: condition and tables
        """

        if configName not in [default, None, ""] and configVersion not in [default, None, ""]:
            if "productionscontainer" not in tables.lower():
                tables += " ,productionscontainer cont"
            if "configurations" not in tables.lower():
                tables += " ,configurations c "
            condition += " and c.configurationid=cont.configurationid  and c.configname='%s' " % (configName)
            condition += " and c.configversion='%s' " % (configVersion)

        return condition, tables

    def __buildVisible(self, condition=None, visible=default, replicaFlag=default):
        """It makes the condition for a given visibility flag and replica flag."""
        if condition is None:
            condition = ""
        if not visible.upper().startswith("A"):
            if visible.upper().startswith("Y"):
                condition += " and prod.visible='Y'"
            elif visible.upper().startswith("N"):
                condition += " and prod.visible='N'"
        if replicaFlag.upper() != default:
            condition += " and prod.gotreplica='%s'" % replicaFlag

        return condition

    #############################################################################
    @staticmethod
    def __buildProduction(production, condition, tables, useMainTables=True):
        """it adds the production which can be a list or string to the jobs table.

        :param list,int long the production number(s)
        :param str condition It contains the where conditions
        :param str tables it containes the tables.
        :param str visible the default value is 'ALL'. [Y,N]
        :param bool useView It is better not to use the view in some cases. This variable is used to
        disable the view usage.
        """

        table = "prod"
        if production not in [default, None]:
            if useMainTables:
                table = "j"
            else:
                if "productionoutputfiles" not in tables.lower():
                    tables += " ,productionoutputfiles prod"

            if isinstance(production, list) and production:
                condition += " and "
                cond = " ( "
                for i in production:
                    cond += " %s.production=%s or " % (table, str(i))
                cond = cond[:-3] + ")"
                condition += cond
            elif isinstance(production, (six.string_types + six.integer_types)):
                condition += " and %s.production=%s" % (table, str(production))

        return condition, tables

    #############################################################################
    @staticmethod
    def __buildTCKS(tcks, condition):
        """it adds the tck to the jobs table.

        :param list tcks: list of run TCKs
        :param str condition: condition string
        :return: condition and tables
        """

        if tcks not in [None, default]:
            if isinstance(tcks, list):
                if default in tcks:
                    tcks.remove(default)
                if tcks:
                    condition += " and ( " + " or ".join([" j.tck='%s'" % i for i in tcks]) + ")"
            elif isinstance(tcks, six.string_types):
                condition += " and j.tck='%s'" % (tcks)
            else:
                return S_ERROR("The TCK should be a list or a string")

        return S_OK(condition)

    #############################################################################
    def __buildProcessingPass(self, procPass, condition, tables, useMainTables=True):
        """It adds the processing pass condition to the query.

        :param str procPass it is a processing pass for example: /Real Data/Reco20
        :param str condition It contains the where conditions
        :param str tables it containes the tables.
        :param str visible the default value is 'ALL'. [Y,N]
        :param bool useView It is better not to use the view in some cases. This variable is used to
        disable the view usage.
        """
        if procPass not in [default, None]:
            if not re.search("^/", procPass):
                procPass = procPass.replace(procPass, "/%s" % procPass)
            command = (
                "select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                           FROM processing v   \
                                           START WITH id in (select distinct id from processing where name='%s') \
                                              CONNECT BY NOCYCLE PRIOR  id=parentid) v \
                     where v.path='%s'"
                % (procPass.split("/")[1], procPass)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                return retVal

            if len(retVal["Value"]) < 1:
                return S_ERROR("No file found! Processing pass is missing!")

            pro = "("
            for i in retVal["Value"]:
                pro += "%s," % (str(i[0]))
            pro = pro[:-1]
            pro += ")"
            condition += " and cont.processingid in %s" % (pro)

            if useMainTables:
                condition += " and cont.production=j.production "

            if "productionscontainer" not in tables.lower():
                tables += ",productionscontainer cont"
        return S_OK((condition, tables))

    #############################################################################
    @staticmethod
    def __buildFileTypes(ftype, condition, tables, useMainTables=True):
        """it adds the file type to the files list.

        :param list, str ftype it is used to construct the file type query filter
        using a given file type or a list of filetypes.
        :param str condition It contains the where conditions
        :param str tables it containes the tables.
        :param str visible the default value is 'ALL'. [Y,N]
        :param bool useView It is better not to use the view in some cases. This variable is used to
        disable the view usage.
        """

        if ftype not in [default, None]:
            if tables.lower().find("filetypes") < 0:
                tables += " ,filetypes ft"
            if isinstance(ftype, list) and ftype:
                condition += " and "
                cond = " ( "
                for i in ftype:
                    cond += " ft.name='%s' or " % (i)
                cond = cond[:-3] + ")"
                condition += cond
            elif isinstance(ftype, six.string_types):
                condition += " and ft.name='%s'" % (ftype)
            else:
                return S_ERROR("File type problem!")

            if useMainTables:
                condition += " and f.filetypeid=ft.filetypeid"
            else:
                condition += " and ft.filetypeid=prod.filetypeid"

        if isinstance(ftype, six.string_types) and ftype.upper() == "RAW" and "jobs" in tables:
            # we know the production of a run is less than 0.
            # this is needed to speed up the queries when the file type is raw
            # (we reject all recostructed + stripped jobs/files. ).
            condition += " and j.production<0"
        return condition, tables

    #############################################################################
    @staticmethod
    def _buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables, useMainTables=True):
        """it adds the run numbers or start end run to the jobs table.

        :param list runnumbers: list of runs
        :param long startRunID: start run number
        :param long endRunID: end run number
        :param str condition: condition string
        :param str tables: tables used by join
        :return: condition and tables
        """
        table = "prview"
        if useMainTables:
            table = "j"
        if runnumbers and runnumbers != default:
            if useMainTables:
                condition += " and prview.runnumber=j.runnumber "
            else:
                condition += " and prview.production=cont.production "
            if "prodrunview" not in tables.lower():
                tables += " ,prodrunview prview"
            if "productionscontainer" not in tables.lower():
                tables += " ,productionscontainer cont"
        cond = None
        if isinstance(runnumbers, six.integer_types):
            condition += " and %s.runnumber=%s" % (table, str(runnumbers))
        elif isinstance(runnumbers, six.string_types) and runnumbers.upper() != default:
            condition += " and %s.runnumber=%s" % (table, str(runnumbers))
        elif isinstance(runnumbers, list) and runnumbers:
            cond = " ( "
            for i in runnumbers:
                cond += " %s.runnumber=%s or " % (table, str(i))
            cond = cond[:-3] + ")"
            if startRunID is not None and endRunID is not None:
                condition += " and (%s.runnumber>=%s and %.runnumber<=%s or %s)" % (
                    table,
                    str(startRunID),
                    table,
                    str(endRunID),
                    cond,
                )
            elif startRunID is not None or endRunID is not None:
                condition += " and %s " % (cond)
            elif startRunID is None or endRunID is None:
                condition += " and %s " % (cond)
        else:
            if (isinstance(startRunID, six.string_types) and startRunID.upper() != default) or (
                isinstance(startRunID, six.integer_types) and startRunID is not None
            ):
                condition += " and %s.runnumber>=%s" % (table, str(startRunID))
            if (isinstance(endRunID, six.string_types) and endRunID.upper() is not default) or (
                isinstance(endRunID, six.integer_types) and endRunID is not None
            ):
                condition += " and %s.runnumber<=%s" % (table, str(endRunID))
        return S_OK((condition, tables))

    #############################################################################
    @staticmethod
    def __buildEventType(evt, condition, tables, useMainTables=True):
        """adds the event type to the files table.

    :param list, str evt it is used to construct the event type query filter using a \
    given event type or a list of event types.
    :param str condition It contains the where conditions
    :param str tables it containes the tables.
    :param str visible the default value is 'ALL'. [Y,N]
    :param bool useView It is better not to use the view in some cases. This variable is used to
    disable the view usage.
    """

        table = "prod"
        if evt not in [0, None, default]:
            if useMainTables:
                table = "f"
            else:
                if "productionoutputfiles" not in tables.lower():
                    tables += " ,productionoutputfiles prod"

            if isinstance(evt, (list, tuple)) and evt:
                condition += " and "
                cond = " ( "
                for i in evt:
                    cond += " %s.eventtypeid=%s or " % (table, (str(i)))
                cond = cond[:-3] + ")"
                condition += cond
            elif isinstance(evt, (six.string_types + six.integer_types)):
                condition += " and %s.eventtypeid=%s" % (table, str(evt))
            if useMainTables:
                if isinstance(evt, (list, tuple)) and evt:
                    condition += " and "
                    cond = " ( "
                    for i in evt:
                        cond += " %s.eventtypeid=%s or " % (table, (str(i)))
                    cond = cond[:-3] + ")"
                    condition += cond
                elif isinstance(evt, (six.string_types + six.integer_types)):
                    condition += " and %s.eventtypeid=%s" % (table, str(evt))
        return condition, tables

    #############################################################################
    @staticmethod
    def __buildStartenddate(startDate, endDate, condition):
        """it adds the start and end date to the files table.

        :param datetime startDate:  file insert start date
        :param datetime endDate: file insert end date
        :param str condition: condition string
        :return: condition and tables
        """
        if startDate not in [None, default, []]:
            condition += " and f.inserttimestamp >= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(startDate))

        if endDate not in [None, default, []]:
            condition += " and f.inserttimestamp <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(endDate))
        elif startDate not in [None, default, []] and endDate in [None, default, []]:
            currentTimeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            condition += " and f.inserttimestamp <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (
                str(currentTimeStamp)
            )
        return condition

    #############################################################################
    @staticmethod
    def __buildJobsStartJobEndDate(jobStartDate, jobEndDate, condition):
        """it adds the start and end date to the files table.

        :param datetime startDate:  file insert start date
        :param datetime jobStartDate:  file insert start date
        :param datetime jobEndDate: file insert end date
        :param str condition: condition string
        :return: condition and tables
        """
        if jobStartDate not in [None, default, []]:
            condition += " and j.jobstart >= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(jobStartDate))

        if jobEndDate not in [None, default, []]:
            condition += " and j.jobend <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(jobEndDate))
        elif jobStartDate not in [None, default, []] and jobEndDate in [None, default, []]:
            currentTimeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            condition += " and j.jobend <= TO_TIMESTAMP ('%s','YYYY-MM-DD HH24:MI:SS')" % (str(currentTimeStamp))
        return condition

    #############################################################################
    def __buildDataquality(self, flag, condition, tables):
        """it adds the data quality to the files table.

        :param str flag: data quality flag
        :param str condition: condition string
        :param str tables: tables used by join
        :return: condition and tables
        """
        if flag not in [default, None]:
            if isinstance(flag, (list, tuple)):
                conds = " ("
                for i in flag:
                    quality = None
                    command = "select QualityId from dataquality where dataqualityflag='%s'" % (str(i))
                    res = self.dbR_.query(command)
                    if not res["OK"]:
                        self.log.error("Data quality problem:", res["Message"])
                    elif not res["Value"]:
                        return S_ERROR("No file found! Dataquality is missing!")
                    else:
                        quality = res["Value"][0][0]
                    conds += " f.qualityid=" + str(quality) + " or"
                condition += " and" + conds[:-3] + ")"
            else:
                quality = None
                command = "select QualityId from dataquality where dataqualityflag='" + str(flag) + "'"
                res = self.dbR_.query(command)
                if not res["OK"]:
                    self.log.error("Data quality problem:", res["Message"])
                elif not res["Value"]:
                    return S_ERROR("No file found! Dataquality is missing!")
                else:
                    quality = res["Value"][0][0]

                condition += " and f.qualityid=" + str(quality)
        return S_OK((condition, tables))

    #############################################################################
    @staticmethod
    def __buildReplicaflag(replicaFlag, condition):
        """it adds the replica flag to the files table.

        :param str replicaFlag: file replica flag
        :param str condition: condition string
        :return: condition and tables
        """
        if replicaFlag in ["Yes", "No"]:
            condition += " and f.gotreplica='%s' " % replicaFlag
        return condition

    #############################################################################
    @staticmethod
    def __buildVisibilityflag(visible, condition, tables):
        """it adds the visibility flag to the files table.

        :param str visible: visibility flag
        :param str condition: condition string
        :param str tables: tables used by the join
        :return: condition and tables
        """
        if not visible.upper().startswith("A"):
            if visible.upper().startswith("Y"):
                condition += " and f.visibilityflag='Y'"
            elif visible.upper().startswith("N"):
                condition += " and f.visibilityflag='N'"
        if tables.upper().find("FILES") < 0:
            tables += " ,file f "
        if tables.upper().find("JOBS") < 0:
            tables += " ,jobs j "
        return condition, tables

    #############################################################################
    def _buildConditions(self, simdesc, datataking, condition, tables):
        """adds the data taking or simulation conditions to the query.

        :param str simdesc it is used to construct the simulation condition query filter
        :param str datataking it is used to construct the data taking condition query filter
        :param str condition It contains the where conditions
        :param str tables it containes the tables.
        """
        if tables is None:
            tables = ""
        if condition is None:
            condition = ""
        if simdesc != default or datataking != default:
            conddesc = simdesc if simdesc != default else datataking
            retVal = self.__getConditionString(conddesc, "cont")
            if not retVal["OK"]:
                return retVal
            condition += retVal["Value"]
            if tables.upper().find("PRODUCTIONSCONTAINER") < 0:
                tables += " ,productionscontainer cont "

        return S_OK((condition, tables))

    #############################################################################
    def getVisibleFilesWithMetadata(
        self,
        simdesc,
        datataking,
        procPass,
        ftype,
        evt,
        configName=default,
        configVersion=default,
        production=default,
        flag=default,
        startDate=None,
        endDate=None,
        nbofEvents=False,
        startRunID=None,
        endRunID=None,
        runnumbers=None,
        replicaFlag="Yes",
        tcks=None,
        jobStart=None,
        jobEnd=None,
    ):
        """For  retrieving only visible files.

        :param str simdesc: simulation desctription
        :param str datataking: data taking description
        :param str procPass: processing pass
        :param str ftype: file type
        :param str evt: event type
        :param str configName: configuration name
        :param str configVersion: configuration version
        :param int production: production number
        :param str flag: data quality
        :param datetime startDate: job start insert time stamp
        :param datetime endDate: job end insert time stamp
        :param bool nbofEvemts: count number of events
        :param long startRunID: start run number
        :param long endRunID: end run number
        :param str replicaFlag: file replica flag
        :param list tcks: run TCKs
        :param datetime jobStart: job starte date
        :param datetime jobEnd: job end date
        :return: the visible files
        """
        conddescription = datataking
        if simdesc != default:
            conddescription = simdesc

        selection = " distinct f.filename, f.eventstat, j.eventinputstat, \
     j.runnumber, j.fillnumber, f.filesize, j.totalluminosity, f.luminosity, f.instLuminosity, j.tck "

        return self.getFilesWithMetadata(
            configName,
            configVersion,
            conddescription,
            procPass,
            evt,
            production,
            ftype,
            flag,
            "Y",
            "Yes",
            startDate,
            endDate,
            runnumbers,
            startRunID,
            endRunID,
            tcks,
            jobStart,
            jobEnd,
            selection,
        )

    #############################################################################
    def getFilesSummary(
        self,
        configName,
        configVersion,
        conditionDescription=default,
        processingPass=default,
        eventType=default,
        production=default,
        fileType=default,
        dataQuality=default,
        startRun=default,
        endRun=default,
        visible=default,
        startDate=None,
        endDate=None,
        runNumbers=None,
        replicaFlag=default,
        tcks=default,
        jobStart=None,
        jobEnd=None,
    ):
        """File summary for a given data set.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: simulation or data taking condition
        :param str processingPass: processing pass
        :param long eventType: event type
        :param int production: production number
        :param str filetype: file type
        :param str dataQuality: data quality
        :param long startRun: satart run number
        :param long endRun: end run number
        :param str visible: visibility flag
        :param datetime startDate: job start insert time stamp
        :param datetime endDate: job end insert time stamp
        :param list runNumbers: list of run numbers
        :param str replicaFlag: file replica flag
        :param list tcks: list of run TCKs
        :param datetime jobStart: job starte date
        :param datetime jobEnd: job end date
        :retun: the number of event, files, etc for a given data set
        """

        if runNumbers is None:
            runNumbers = []

        tables = " files f, jobs j, productionscontainer cont, productionoutputfiles prod "
        condition = (
            " and cont.production=prod.production and \
    j.production=prod.production and j.stepid=prod.stepid and\
    prod.eventtypeid=f.eventtypeid %s "
            % self.__buildVisible(visible=visible, replicaFlag=replicaFlag)
        )

        condition = self.__buildStartenddate(startDate, endDate, condition)

        condition = self.__buildJobsStartJobEndDate(jobStart, jobEnd, condition)

        retVal = self._buildRunnumbers(runNumbers, startRun, endRun, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        retVal = self.__buildTCKS(tcks, condition)
        if not retVal["OK"]:
            return retVal
        condition = retVal["Value"]

        retVal = self._buildConditions(default, conditionDescription, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildVisibilityflag(visible, condition, tables)

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        condition, tables = self.__buildProduction(production, condition, tables, useMainTables=False)

        condition, tables = self.__buildEventType(eventType, condition, tables, useMainTables=False)

        if production != default:
            condition += " and j.production=" + str(production)

        condition, tables = self.__buildFileTypes(fileType, condition, tables, useMainTables=False)

        condition = self.__buildReplicaflag(replicaFlag, condition)

        retVal = self.__buildProcessingPass(processingPass, condition, tables, useMainTables=False)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        retVal = self.__buildDataquality(dataQuality, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        command = (
            "select count(distinct fileid),\
    SUM(f.EventStat), SUM(f.FILESIZE), \
    SUM(f.luminosity),SUM(f.instLuminosity) from  %s  where \
    j.jobid=f.jobid and \
    prod.production=cont.production and prod.filetypeid=f.filetypeid %s"
            % (tables, condition)
        )
        return self.dbR_.query(command)

    #############################################################################
    def getLimitedFiles(
        self,
        configName,
        configVersion,
        conddescription=default,
        processing=default,
        evt=default,
        production=default,
        filetype=default,
        quality=default,
        runnb=default,
        startitem=0,
        maxitems=10,
    ):
        """For retrieving a subset of files.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: simulation or data taking condition
        :param str processing: processing pass
        :param long evt: event type
        :param int production: production number
        :param str filetype: file type
        :param str quality: data quality
        :param long runnb: run number
        :param long startitem: staring row number
        :pram long maxitems: maximum returned rows
        :return: a list of limited number of files
        """

        tables = " files f, jobs j, productionoutputfiles prod, productionscontainer cont, filetypes ft, dataquality d "
        condition = (
            " and cont.production=prod.production and d.qualityid=f.qualityid and \
    j.production=prod.production and j.stepid=prod.stepid and \
    prod.eventtypeid=f.eventtypeid %s "
            % self.__buildVisible(visible="Y", replicaFlag="Yes")
        )

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        retVal = self._buildConditions(default, conddescription, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildProduction(production, condition, tables, useMainTables=False)

        condition = self.__buildReplicaflag("Yes", condition)

        retVal = self.__buildDataquality(quality, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        retVal = self.__buildProcessingPass(processing, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        condition, tables = self.__buildEventType(evt, condition, tables, useMainTables=False)

        condition, tables = self.__buildFileTypes(filetype, condition, tables, useMainTables=False)

        retVal = self._buildRunnumbers(runnb, None, None, condition, tables)
        if not retVal["OK"]:
            return retVal
        condition, tables = retVal["Value"]

        # TODO: Distinct is being used here to work around https://its.cern.ch/jira/browse/LHCBDIRAC-895
        command = (
            "select distinct fname, fstat, fsize, fcreation, jstat, jend, jnode, ftypen, evttypeid, \
    jrun, jfill, ffull, dflag,   jevent, jtotal, flum, finst, jtck from \
              (select rownum r, fname, fstat, fsize, fcreation, jstat, jend, jnode, ftypen,\
               evttypeid, jrun, jfill, ffull, dflag,   jevent, jtotal, flum, finst, jtck from \
                  (select ROWNUM r, f.FileName fname, f.EventStat fstat, f.FileSize fsize, \
                  f.CreationDate fcreation, j.JobStart jstat, j.JobEnd jend, j.WorkerNode jnode, \
                  ft.Name ftypen, f.eventtypeid evttypeid, j.runnumber jrun, j.fillnumber jfill,\
                   f.fullstat ffull, d.dataqualityflag dflag,j.eventinputstat jevent, j.totalluminosity jtotal,\
                           f.luminosity flum, f.instLuminosity finst, j.tck jtck, j.WNMJFHS06,j.HLT2TCK,\
                           j.NumberOfProcessors from %s where \
    j.jobid=f.jobid and \
    ft.filetypeid=prod.filetypeid and \
    f.filetypeid=prod.filetypeid and \
    f.gotreplica='Yes' and \
    f.visibilityflag='Y' %s) where\
     rownum <=%d ) where r >%d"
            % (tables, condition, int(maxitems), int(startitem))
        )
        return self.dbR_.query(command)

    #############################################################################
    def getDataTakingCondId(self, condition):
        """For retrieving the data quality id.

        :param dict condition: data taking attributes
        :return: the data taking conditions identifier
        """
        command = "select DaqPeriodId from data_taking_conditions where "
        for param in condition:
            if isinstance(condition[param], six.string_types) and not condition[param].strip():
                command += str(param) + " is NULL and "
            elif condition[param] is not None:
                command += str(param) + "='" + condition[param] + "' and "
            else:
                command += str(param) + " is NULL and "

        command = command[:-4]
        res = self.dbR_.query(command)
        if res["OK"]:
            if not res["Value"]:
                command = "select DaqPeriodId from data_taking_conditions where "
                for param in condition:
                    if param != "Description":
                        if isinstance(condition[param], six.string_types) and not condition[param].strip():
                            command += str(param) + " is NULL and "
                        elif condition[param] is not None:
                            command += str(param) + "='" + condition[param] + "' and "
                        else:
                            command += str(param) + " is NULL and "

                command = command[:-4]
                retVal = self.dbR_.query(command)
                if retVal["OK"]:
                    if retVal["Value"]:
                        return S_ERROR(
                            "Only the Description is different, \
            the other attributes are the same and they are exists in the DB!"
                        )
        return res

    #############################################################################
    def getDataTakingCondDesc(self, condition):
        """For retrieving the data taking conditions which fullfill for given
        condition.

        :param dict condition: data taking attributes
        :return: the data taking description which adequate a given conditions.
        """
        command = "select description from data_taking_conditions where "
        for param in condition:
            if isinstance(condition[param], six.string_types) and not condition[param].strip():
                command += str(param) + " is NULL and "
            elif condition[param] is not None:
                command += str(param) + "='" + condition[param] + "' and "
            else:
                command += str(param) + " is NULL and "

        command = command[:-4]
        res = self.dbR_.query(command)
        if res["OK"]:
            if not res["Value"]:
                command = "select DaqPeriodId from data_taking_conditions where "
                for param in condition:
                    if param != "Description":
                        if isinstance(condition[param], six.string_types) and not condition[param].strip():
                            command += str(param) + " is NULL and "
                        elif condition[param] is not None:
                            command += str(param) + "='" + condition[param] + "' and "
                        else:
                            command += str(param) + " is NULL and "

                command = command[:-4]
                retVal = self.dbR_.query(command)
                if retVal["OK"]:
                    if retVal["Value"]:
                        return S_ERROR(
                            "Only the Description is different,\
             the other attributes are the same and they are exists in the DB!"
                        )
        return res

    #############################################################################
    def getStepIdandNameForRUN(self, programName, programVersion, conddb, dddb):
        """For retrieving the steps which is used by given application, conddb,
        dddb.

        :param str programName: application name
        :param str programVersion: application version
        :param str conddb: CONDB database tag
        :param str dddb: DDDB database tag
        :return: the step used to process data
        """
        dataset = {
            "Step": {
                "StepName": "Real Data",
                "ApplicationName": programName,
                "ApplicationVersion": programVersion,
                "ProcessingPass": "Real Data",
                "Visible": "Y",
                "CONDDB": None,
                "DDDB": None,
            },
            "OutputFileTypes": [{"FileType": "RAW", "Visible": "Y"}],
        }
        condition = ""
        if conddb is None or conddb == "":
            condition += " and CondDB is NULL "
            dataset["Step"].pop("CONDDB")
        else:
            condition += " and CondDB='%s' " % (conddb)
            dataset["Step"]["CONDDB"] = conddb

        if dddb is None or dddb == "":
            condition += " and DDDB is NULL "
            dataset["Step"].pop("DDDB")
        else:
            condition += " and DDDB='%s'" % (dddb)
            dataset["Step"]["DDDB"] = dddb

        command = (
            "select stepid, stepname from steps where applicationname='%s' \
    and applicationversion='%s' %s "
            % (programName, programVersion, condition)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        if not retVal["Value"]:
            retVal = self.insertStep(dataset)
            if retVal["OK"]:
                return S_OK([retVal["Value"], "Real Data"])
            else:
                return retVal
        else:
            return S_OK([retVal["Value"][0][0], retVal["Value"][0][1]])

    #############################################################################
    def __getPassIds(self, name):
        """For retrieving processing pass ids.

        :param str name: processing pass name for example: Sim10
        :return: the processing pass ids for a given processing pass name
        """
        command = "select id from processing where name='%s'" % (name)
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        return S_OK([i[0] for i in retVal["Value"]])

    #############################################################################
    def __getprocessingid(self, processingpassid):
        """For retrieving processing pass for a given id.

        :param long processongpassid: processing pass id
        :return: processing pass
        """
        command = (
            'SELECT name "Name", CONNECT_BY_ISCYCLE "Cycle", \
   LEVEL, SYS_CONNECT_BY_PATH(name, \'/\') "Path", id "ID" \
   FROM processing \
   START WITH id='
            + str(processingpassid)
            + '\
   CONNECT BY NOCYCLE PRIOR  parentid=id AND LEVEL <= 5 \
   ORDER BY  Level desc, "Name", "Cycle", "Path"'
        )
        return self.dbR_.query(command)

    #############################################################################
    @staticmethod
    def __checkprocessingpass(opath, values):
        """checks the processing pass: compare the processing passes.

        :param list opath: processing pass names
        :param list values: processing pass names
        """
        if len(opath) != len(values):
            return False
        else:
            j = 0
            for i in values:
                if i[0] != opath[j]:
                    return False
                j += 1
            return True

    #############################################################################
    def __insertprocessing(self, values, parentid=None, ids=None):
        """inserts a processing pass.

        :param list values: processing pass names: Reco09, Stripping19
        :param long parentid: the parent processing pass
        :param list ids: keeps all processing pass ids
        """
        if ids is None:
            ids = []
        for i in values:
            command = ""
            if parentid is not None:
                command = "select id from processing where name='%s' and parentid=%s" % (i, parentid)
            else:
                command = "select id from processing where name='%s' and parentid is null" % (i)
            retVal = self.dbR_.query(command)
            if retVal["OK"]:
                if not retVal["Value"]:
                    if parentid is not None:
                        command = "select max(id)+1 from processing"
                        retVal = self.dbR_.query(command)
                        if retVal["OK"]:
                            processingpassid = retVal["Value"][0][0]
                            ids += [processingpassid]
                            command = "insert into processing(id,parentid,name)values(%d,%d,'%s')" % (
                                processingpassid,
                                parentid,
                                i,
                            )
                            retVal = self.dbW_.query(command)
                            if not retVal["OK"]:
                                self.log.error(retVal["Message"])
                            values.remove(i)
                            self.__insertprocessing(values, processingpassid, ids)
                    else:
                        command = "select max(id)+1 from processing"
                        retVal = self.dbR_.query(command)
                        if retVal["OK"]:
                            processingpassid = retVal["Value"][0][0]
                            if processingpassid is None:
                                processingpassid = 1
                            ids += [processingpassid]
                            command = "insert into processing(id,parentid,name)values(%d,null,'%s')" % (
                                processingpassid,
                                i,
                            )
                            retVal = self.dbW_.query(command)
                            if not retVal["OK"]:
                                self.log.error(retVal["Message"])
                            values.remove(i)
                            self.__insertprocessing(values, processingpassid, ids)
                else:

                    values.remove(i)
                    parentid = retVal["Value"][0][0]
                    ids += [parentid]
                    self.__insertprocessing(values, parentid, ids)

    #############################################################################
    def addProcessing(self, path):
        """adds a new processing pass.

        :param str path: processing pass for example: /Real Data/Reco19/Striping29
        """
        lastindex = len(path) - 1
        retVal = self.__getPassIds(path[lastindex])
        stepids = []
        if not retVal["OK"]:
            return retVal

        ids = retVal["Value"]
        if len(ids) == 0:
            newpath = list(path)
            self.__insertprocessing(newpath, None, stepids)
            return S_OK(stepids[-1:])
        else:
            for i in ids:
                procs = self.__getprocessingid(i)
                if len(procs) > 0:
                    if self.__checkprocessingpass(path, procs):
                        return S_OK()
            newpath = list(path)
            self.__insertprocessing(newpath, None, stepids)
            return S_OK(stepids[-1:])

    #############################################################################
    def insertproductionscontainer(self, prod, processingid, simid, daqperiodid, configName, configVersion):
        """inserts a production to the productions container.

        :param int prod: production number
        :param int processingid: processing pass id
        :param int simid: simulation condition id
        :param int daqperiodid: data taking condition id
        :param str configName: configuration name
        :param str configVersion: configuration version
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.insertproductionscontainer",
            [prod, processingid, simid, daqperiodid, configName, configVersion],
            False,
        )

    #############################################################################
    def addProductionSteps(self, steps, prod):
        """adds a step to a production. The steps which used by the production.

        :param list steps: list of dict of steps [{'StepId':123}, {'StepId':321}]
        :param int prod: production number
        """
        level = 1
        for step in steps:
            retVal = self.dbW_.executeStoredProcedure(
                "BOOKKEEPINGORACLEDB.insertStepsContainer", [prod, step["StepId"], level], False
            )
            if not retVal["OK"]:
                return retVal
            level += 1
        return S_OK()

    #############################################################################
    def checkProcessingPassAndSimCond(self, production):
        """checks the processing pass and simulation condition.

        :param int production: production number
        """
        return self.dbR_.query("select count(*) from productionscontainer where production=" + str(production))

    #############################################################################
    def addProduction(
        self,
        production,
        simcond=None,
        daq=None,
        steps=default,
        inputproc="",
        configName=None,
        configVersion=None,
        eventType=None,
    ):
        """adds a production to the productions container table.

        :param int production: production number
        :param str simcond: simulation condition description
        :param str daq: data taking description
        :param list steps: list of dictionaries of steps (min fields {'Visible': 'Y/N', 'StepID': '123'})
        :param str inputproc: input processing pass
        :param str configName: configuration name
        :param str configVersion: configuration version
        :param long eventType: eventTyoe
        """
        self.log.verbose("Adding production", production)
        path = []
        if inputproc != "":
            if inputproc[0] != "/":
                inputproc = "/" + inputproc
            path = inputproc.split("/")[1:]

        for step in steps:
            if step["Visible"] == "Y":
                res = self.getAvailableSteps({"StepId": step["StepId"]})
                if not res["OK"]:
                    self.log.error(res["Message"])
                    return res
                if res["Value"]["TotalRecords"] > 0:
                    procpas = res["Value"]["Records"][0][9]
                    path += [procpas]
                else:
                    self.log.error("Missing step", "(StepID: %s)" % step["StepId"])
                    return S_ERROR("Missing step")

        if not path:
            self.log.error("You have to define the input processing pass or you have to have a visible step!")
            return S_ERROR("You have to define the input processing pass or you have to have a visible step!")
        processingid = None
        retVal = self.addProcessing(path)
        if not retVal["OK"]:
            self.log.error("Failed adding processing", path)
            return retVal
        if not retVal["Value"]:
            return S_ERROR("The processing pass already exists! Write to lhcb-bookkeeping@cern.ch")
        processingid = retVal["Value"][0]
        retVal = self.addProductionSteps(steps, production)
        if not retVal["OK"]:
            return retVal

        sim = None
        did = None
        if daq is not None:
            retVal = self._getDataTakingConditionId(daq)
            if not retVal["OK"]:
                return retVal
            if retVal["Value"] > -1:
                did = retVal["Value"]
            else:
                return S_ERROR("Data taking condition is missing")
        if simcond is not None:
            retVal = self.__getSimulationConditionId(simcond)
            if not retVal["OK"]:
                return retVal
            if retVal["Value"] == -1:
                return S_ERROR("Simulation condition is missing")
            sim = retVal["Value"]
        retVal = self.insertproductionscontainer(production, processingid, sim, did, configName, configVersion)
        if not retVal["OK"]:
            return retVal

        return self.insertProductionOutputFiletypes(production, steps, eventType)

    #############################################################################
    def insertProductionOutputFiletypes(self, production, steps, eventType):
        """This method is used to register the output filetypes for a given
        production.

        :param int production: it is the production number
        :param list steps: it contains all the steps and output file types
        :param number/list eventtype: given event type which will be produced by the jobs
        :returns: S_OK/S_ERROR
        """
        # if we have some specific file type version, it can be added to this dictionary
        fileTypeMap = {"RAW": "MDF"}
        eventtypes = []
        if eventType:
            if isinstance(eventType, (six.string_types, six.integer_types)):
                eventtypes.append(int(eventType))
            elif isinstance(eventType, list):
                eventtypes = eventType
            else:
                return S_ERROR("%s event type is not valid!" % eventType)
        self.log.verbose("The following event types will be inserted:", "%s" % eventtypes)

        for step in steps:
            # the runs have more than one event type
            for eventtype in eventtypes:
                for ftype in step.get("OutputFileTypes", {}):
                    fversion = fileTypeMap.get(ftype.get("FileType"), "ROOT")
                    result = self.checkFileTypeAndVersion(ftype.get("FileType"), fversion)
                    if not result["OK"]:
                        return S_ERROR("The type:%s, version:%s is missing." % (ftype.get("FileType"), fversion))
                    else:
                        fileTypeid = int(result["Value"])
                    retVal = self.dbW_.executeStoredProcedure(
                        "BOOKKEEPINGORACLEDB.insertProdnOutputFtypes",
                        [production, step["StepId"], fileTypeid, ftype.get("Visible", "Y"), eventtype],
                        False,
                    )
                    if not retVal["OK"]:
                        return retVal

        return S_OK()

    #############################################################################
    def getEventTypes(self, configName=default, configVersion=default, prod=default):
        """For retrieving the event type for given conditions.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param int prod: production number
        :return: event types
        """

        tables = "  productionoutputfiles prod, productionscontainer cont, eventtypes e, configurations c "
        condition = (
            " cont.production=prod.production and \
    prod.eventtypeid=e.eventtypeid %s "
            % self.__buildVisible(visible="Y", replicaFlag="Yes")
        )

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        condition, tables = self.__buildProduction(prod, condition, tables, useMainTables=False)

        command = (
            " select e.eventtypeid, e.description \
    from  %s where %s group by e.eventtypeid, e.description"
            % (tables, condition)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        records = [list(record) for record in retVal["Value"]]
        return S_OK({"ParameterNames": ["EventType", "Description"], "Records": records, "TotalRecords": len(records)})

    #############################################################################
    def getProcessingPassSteps(self, procpass=default, cond=default, stepname=default):
        """For retrieving the step metadata for given condition.

        :param str procpass: processing pass
        :param str cond: data taking or simulation condition
        :param str stepname: name of the step
        :return: the steps with metadata
        """
        processing = {}
        condition = ""

        if procpass != default:
            condition += (
                " and prod.processingid in ( \
                    select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                        FROM processing v   \
                                        START WITH id in (select distinct id from processing where name='%s') \
                                        CONNECT BY NOCYCLE PRIOR  id=parentid) v where v.path='%s' \
                       )"
                % (procpass.split("/")[1], procpass)
            )

        if cond != default:
            retVal = self.__getConditionString(cond, "prod")
            if retVal["OK"]:
                condition += retVal["Value"]
            else:
                return retVal

        if stepname != default:
            condition += " and s.processingpass='%s' " % (stepname)

        command = (
            "select distinct s.stepid,s.stepname,s.applicationname,s.applicationversion, \
    s.optionfiles,s.dddb, s.conddb,s.extrapackages,s.visible, cont.step \
                from steps s, productionscontainer prod, stepscontainer cont \
               where \
              cont.stepid=s.stepid and \
              prod.production=cont.production %s order by cont.step"
            % (condition)
        )

        retVal = self.dbR_.query(command)
        records = []
        # parametersNames = [ 'StepId', 'StepName','ApplicationName', 'ApplicationVersion',
        # 'OptionFiles','DDDB','CONDDB','ExtraPackages','Visible']
        parametersNames = ["id", "name"]
        if retVal["OK"]:
            nb = 0
            for i in retVal["Value"]:
                # records = [[i[0],i[1],i[2],i[3],i[4],i[5],i[6], i[7], i[8]]]
                records = [
                    ["StepId", i[0]],
                    ["StepName", i[1]],
                    ["ApplicationName", i[2]],
                    ["ApplicationVersion", i[3]],
                    ["OptionFiles", i[4]],
                    ["DDDB", i[5]],
                    ["CONDDB", i[6]],
                    ["ExtraPackages", i[7]],
                    ["Visible", i[8]],
                ]
                step = "Step-%s" % (i[0])
                processing[step] = records
                nb += 1
        else:
            return retVal

        return S_OK({"Parameters": parametersNames, "Records": processing, "TotalRecords": nb})

    #############################################################################
    def getProductionProcessingPassSteps(self, prod):
        """For retrieving the processing pass of a given production.

        :param int prod: production number
        :return: the production processing pass
        """
        processing = {}
        retVal = self.getProductionProcessingPass(prod)
        if not retVal["OK"]:
            return retVal
        procpass = retVal["Value"]

        condition = ""

        if procpass != default:
            condition += (
                " and prod.processingid in ( \
                    select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                        FROM processing v   \
                                        START WITH id in (select distinct id from processing where name='%s') \
                                        CONNECT BY NOCYCLE PRIOR  id=parentid) v where v.path='%s' \
                       )"
                % (procpass.split("/")[1], procpass)
            )

        command = (
            "select distinct s.stepid,s.stepname,s.applicationname,s.applicationversion, \
    s.optionfiles,s.dddb, s.conddb,s.extrapackages,s.visible, cont.step \
                from steps s, productionscontainer prod, stepscontainer cont \
               where \
              cont.stepid=s.stepid and \
              prod.production=cont.production %s and prod.production=%dorder by cont.step"
            % (condition, prod)
        )

        retVal = self.dbR_.query(command)
        records = []
        # parametersNames = [ 'StepId', 'StepName','ApplicationName',
        # 'ApplicationVersion','OptionFiles','DDDB','CONDDB','ExtraPackages','Visible']
        parametersNames = ["id", "name"]
        if retVal["OK"]:
            nb = 0
            for i in retVal["Value"]:
                # records = [[i[0],i[1],i[2],i[3],i[4],i[5],i[6], i[7], i[8]]]
                records = [
                    ["StepId", i[0]],
                    ["ProcessingPass", procpass],
                    ["ApplicationName", i[2]],
                    ["ApplicationVersion", i[3]],
                    ["OptionFiles", i[4]],
                    ["DDDB", i[5]],
                    ["CONDDB", i[6]],
                    ["ExtraPackages", i[7]],
                    ["Visible", i[8]],
                ]
                step = i[1]
                processing[step] = records
                nb += 1
        else:
            return retVal

        return S_OK({"Parameters": parametersNames, "Records": processing, "TotalRecords": nb})

    #############################################################################
    def getRuns(self, cName, cVersion):
        """For retrieving list of runs.

        :param str cName: configuration name
        :param str cVersion: configuration version
        :return: runs
        """
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getRuns", [cName, cVersion])

    #############################################################################
    def getRunAndProcessingPass(self, runnb):
        """For retrieving the processing pass of a given run.

        :param long runnb: run number
        :return: the processing pass of a run
        """
        command = "select distinct runnumber, processingpass from table (BOOKKEEPINGORACLEDB.getRunProcPass(%d))" % (
            runnb
        )
        return self.dbR_.query(command)
        # return self.dbR_.executeStoredProcedure('BOOKKEEPINGORACLEDB.getRunProcPass', [runnb])

    #############################################################################
    def getNbOfRawFiles(self, runid, eventtype, replicaFlag="Yes", visible="Y", isFinished=default):
        """For retrieving the number of raw files for a given condition.

        :param long runid: run number
        :param long eventtype: event type
        :param str replicaFlag: file replica flag
        :param str visible: file visibility flag
        :param str isFinished: the run status
        :retun: the number of raw files
        """
        condition = ""
        tables = "jobs j, files f"
        if eventtype != default:
            condition = " and f.eventtypeid=%d" % (eventtype)

        if visible != default:
            condition += " and f.visibilityFlag='%s'" % (visible)

        if replicaFlag != default:
            condition += " and f.gotreplica='%s'" % (replicaFlag)

        if isFinished != default:
            tables += " ,runstatus r"
            condition += " and j.runnumber=r.runnumber and r.finished='%s' " % isFinished

        command = (
            " select count(*) from %s  where \
    j.jobid=f.jobid and j.production<0 and j.runnumber=%d %s "
            % (tables, runid, condition)
        )
        return self.dbR_.query(command)

    #############################################################################
    def getFileTypeVersion(self, lfns):
        """For retrieving the file type version.

        :param list lfns: list of lfns
        :return: the format of an lfn
        """
        retVal = self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.bulkgetTypeVesrsion", [], True, lfns)
        if not retVal["OK"]:
            return retVal
        values = {}
        for i in retVal["Value"]:
            values[i[0]] = i[1]
        return S_OK(values)

    #############################################################################
    def insertRuntimeProject(self, projectid, runtimeprojectid):
        """inserts a runtime project.

        :param long projectid: run time project stepid
        :param long runtimeprojectid: reference to other step
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.insertRuntimeProject", [projectid, runtimeprojectid], False
        )

    #############################################################################
    def updateRuntimeProject(self, projectid, runtimeprojectid):
        """changes the runtime project.

        :param long projectid: run time project stepid
        :param long runtimeprojectid: new run time project stepid (new reference to a stepid)
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.updateRuntimeProject", [projectid, runtimeprojectid], False
        )

    def removeRuntimeProject(self, stepid):
        """removes the runtime project.

        :param long stepid: step id
        """
        return self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.removeRuntimeProject", [stepid], False)

    #############################################################################
    def getTCKs(
        self,
        configName,
        configVersion,
        conddescription=default,
        processing=default,
        evt=default,
        production=default,
        filetype=default,
        quality=default,
        runnb=default,
    ):
        """TCKs for a given data set.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking condition
        :param str processing: processing pass
        :param long evt: event type
        :param int production: production number
        :param str filetype: file type
        :param str quality: data quality
        :param long runnb: run number
        :return: the TCKs for a given dataset
        """

        return self.getFilesWithMetadata(
            configName=configName,
            configVersion=configVersion,
            conddescription=conddescription,
            processing=processing,
            evt=evt,
            production=production,
            filetype=filetype,
            quality=quality,
            visible="Y",
            replicaflag="Yes",
            runnumbers=runnb,
            selection=" distinct j.tck ",
        )

    #############################################################################
    def __prepareStepMetadata(
        self,
        configName,
        configVersion,
        cond=default,
        procpass=default,
        evt=default,
        production=default,
        filetype=default,
        runnb=default,
        visible=default,
        replica=default,
        selection="",
    ):
        """it generates the sql command depending on the selection.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str procpass: processing pass
        :param long evt: event type
        :param int production: production number
        :param str filetype: file type
        :param long runnb: run number
        :param str selection: select state
        :return: sql command
        """
        condition = ""
        tables = (
            "steps s, productionscontainer cont, stepscontainer scont, productionoutputfiles prod, configurations c"
        )
        if configName != default:
            condition += " and c.configname='%s' " % (configName)

        if configVersion != default:
            condition += " and c.configversion='%s' " % (configVersion)

        if procpass != default:
            condition += (
                " and cont.processingid in ( \
                    select v.id from (SELECT distinct SYS_CONNECT_BY_PATH(name, '/') Path, id ID \
                                        FROM processing v   \
                                        START WITH id in (select distinct id from processing where name='%s') \
                                        CONNECT BY NOCYCLE PRIOR  id=parentid) v where v.path='%s' \
                       )"
                % (procpass.split("/")[1], procpass)
            )

        if cond != default:
            retVal = self.__getConditionString(cond, "cont")
            if retVal["OK"]:
                condition += retVal["Value"]
            else:
                return retVal

        if evt != default:
            condition += "  and prod.eventtypeid=%s " % (str(evt))

        if production != default:
            condition += " and prod.production=" + str(production)

        if runnb != default:
            tables += " ,prodrunview rview"
            condition += " and rview.production=prod.production and rview.runnumber=%d and prod.production<0" % (runnb)

        if filetype != default:
            tables += ", filetypes ftypes"
            condition += " and ftypes.name='%s' and prod.filetypeid=ftypes.filetypeid " % (filetype)

        if visible != default:
            condition += " and prod.visible='%s'" % visible

        if replica != default:
            condition += " and prod.gotreplica='%s'" % replica

        command = (
            "select %s  from  %s \
               where \
              scont.stepid=s.stepid and \
              cont.production=prod.production and \
              c.configurationid=cont.configurationid and\
              prod.production=scont.production %s order by scont.step"
            % (selection, tables, condition)
        )
        return command

    #############################################################################
    def getStepsMetadata(
        self,
        configName,
        configVersion,
        cond=default,
        procpass=default,
        evt=default,
        production=default,
        filetype=default,
        runnb=default,
    ):
        """Step metadata, which describes how the data set is created.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str procpass: processing pass
        :param long evt: event type
        :param int production: production number
        :param str filetype: file type
        :param long runnb: run number
        :return: the steps with metadata
        """

        command = None
        processing = {}
        productions = None
        result = None
        if "MC" in configName.upper():
            command = self.__prepareStepMetadata(
                configName,
                configVersion,
                cond,
                procpass,
                evt,
                production,
                filetype,
                runnb,
                "Y",
                "Yes",
                selection="prod.production",
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result = retVal
            else:
                productions = set([i[0] for i in retVal["Value"]])
                self.log.debug("Productions:", "%s" % str(productions))
                parametersNames = ["id", "name"]
                for prod in productions:
                    retVal = self.getSteps(prod)
                    if not retVal:
                        result = retVal
                    else:
                        nb = 0
                        steps = retVal["Value"]
                        for (
                            stepName,
                            appName,
                            appVersion,
                            optionFiles,
                            dddb,
                            conddb,
                            extrapackages,
                            stepid,
                            visible,
                        ) in steps:
                            records = [
                                ["StepId", stepid],
                                ["StepName", stepName],
                                ["ApplicationName", appName],
                                ["ApplicationVersion", appVersion],
                                ["OptionFiles", optionFiles],
                                ["DDDB", dddb],
                                ["CONDDB", conddb],
                                ["ExtraPackages", extrapackages],
                                ["Visible", visible],
                            ]
                            step = "Step-%d" % stepid
                            processing[step] = records
                            nb += 1
                        result = S_OK({"Parameters": parametersNames, "Records": processing, "TotalRecords": nb})
        else:
            # #Now we are getting the metadata for a given run
            command = self.__prepareStepMetadata(
                configName,
                configVersion,
                cond,
                procpass,
                evt,
                production,
                filetype,
                runnb,
                "Y",
                "Yes",
                selection="distinct s.stepid,s.stepname,s.applicationname,\
                                           s.applicationversion,s.optionfiles,s.dddb,\
                                           s.conddb,s.extrapackages,s.visible, scont.step",
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result = retVal
            else:
                nb = 0
                parametersNames = ["id", "name"]
                steps = retVal["Value"]
                for (
                    stepid,
                    stepName,
                    appName,
                    appVersion,
                    optionFiles,
                    dddb,
                    conddb,
                    extrapackages,
                    visible,
                    _,
                ) in steps:
                    records = [
                        ["StepId", stepid],
                        ["StepName", stepName],
                        ["ApplicationName", appName],
                        ["ApplicationVersion", appVersion],
                        ["OptionFiles", optionFiles],
                        ["DDDB", dddb],
                        ["CONDDB", conddb],
                        ["ExtraPackages", extrapackages],
                        ["Visible", visible],
                    ]
                    step = "Step-%d" % stepid
                    nb += 1
                    processing[step] = records

                result = S_OK({"Parameters": parametersNames, "Records": processing, "TotalRecords": nb})

        return result

    #############################################################################
    def getDirectoryMetadata(self, lfn):
        """For retrieving the directory metadata.

        :param list lfn: list of lfns: for example: ['/lhcb/MC/2016/LOG/00057824/0010/']
        :return: a directory meradata
        """

        self.log.verbose("Getting directory metadata:", "%s" % lfn)
        lfns = [i + "%" for i in lfn]
        retVal = self.dbR_.executeStoredProcedure(
            packageName="BOOKKEEPINGORACLEDB.getDirectoryMetadata_new", parameters=[], output=True, array=lfns
        )
        if not retVal["OK"]:
            return retVal

        records = {}
        failed = []
        for i in retVal["Value"]:
            fileName = i[0][:-1]
            if fileName in records:
                records[fileName] += [
                    dict(
                        zip(
                            (
                                "Production",
                                "ConfigName",
                                "ConfigVersion",
                                "EventType",
                                "FileType",
                                "ProcessingPass",
                                "ConditionDescription",
                                "VisibilityFlag",
                            ),
                            i[1:],
                        )
                    )
                ]
            else:
                records[fileName] = [
                    dict(
                        zip(
                            (
                                "Production",
                                "ConfigName",
                                "ConfigVersion",
                                "EventType",
                                "FileType",
                                "ProcessingPass",
                                "ConditionDescription",
                                "VisibilityFlag",
                            ),
                            i[1:],
                        )
                    )
                ]
        failed = [i[:-1] for i in lfns if i[:-1] not in records]
        return S_OK({"Successful": records, "Failed": failed})

    #############################################################################
    def getFilesForGUID(self, guid):
        """For retrieving the file for a given guid.

        :param str guid: file GUID
        :return: the file for a given GUID
        """
        return self.dbW_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getFilesForGUID", str, [guid])

    #############################################################################
    def getRunsGroupedByDataTaking(self):
        """For retrieving all runs grouped by data taking description.

        :return: the runs data taking description and production
        """
        command = " select d.description, r.runnumber, r.production from \
    prodrunview r, productionoutputfiles p, data_taking_conditions d, productionscontainer cont where \
    d.daqperiodid=cont.daqperiodid and p.production=r.production and cont.production=p.production\
     group by d.description,  r.runnumber, r.production order by r.runnumber"
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        values = {}
        for i in retVal["Value"]:
            rnb = i[1]
            desc = i[0]
            prod = i[2]
            if desc in values:
                if rnb in values[desc]:
                    if prod > 0:
                        values[desc][rnb] += [prod]
                else:
                    if prod > 0:
                        values[desc].update({rnb: [prod]})
                    else:
                        values[desc].update({rnb: []})
            else:
                if prod > 0:
                    values[desc] = {rnb: [prod]}
                else:
                    values[desc] = {rnb: []}
        return S_OK(values)

    #############################################################################
    def getListOfFills(self, configName=default, configVersion=default, conddescription=default):
        """It returns a list of fills for a given condition.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: data taking condition
        :return: run numbers
        """
        condition = ""
        if configName != default:
            condition += " and c.configname='%s' " % (configName)

        if configVersion != default:
            condition += " and c.configversion='%s' " % (configVersion)

        if conddescription != default:
            retVal = self.__getConditionString(conddescription, "prod")
            if retVal["OK"]:
                condition += retVal["Value"]
            else:
                return retVal

        command = (
            "select distinct j.FillNumber from jobs j, productionscontainer prod,\
     configurations c where \
    j.configurationid=c.configurationid %s and \
    prod.production=j.production and j.production<0"
            % (condition)
        )
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        return S_OK([i[0] for i in retVal["Value"]])

    #############################################################################
    def getRunsForFill(self, fillid):
        """It returns a list of runs for a given FILL.

        :param long fillid: fill number
        :return: runs
        """

        command = "select distinct j.runnumber from jobs j where j.production<0 and j.fillnumber=%d" % (fillid)
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        return S_OK([i[0] for i in retVal["Value"]])

    #############################################################################
    def getListOfRuns(
        self,
        configName=default,
        configVersion=default,
        conddescription=default,
        processing=default,
        evt=default,
        quality=default,
    ):
        """For retriecing run numbers.

        :param str configName: configuration name
        :param str configVersion: configuration version
        :param str conddescription: simulation or data taking condition
        :param str processing: processing pass
        :param long evt: event type
        :param str quality: data quality
        :return: runs
        """

        return self.getFilesWithMetadata(
            configName=configName,
            configVersion=configVersion,
            conddescription=conddescription,
            processing=processing,
            evt=evt,
            quality=quality,
            visible="Y",
            replicaflag="Yes",
            selection=" distinct j.runnumber ",
        )

    #############################################################################
    def getSimulationConditions(self, in_dict):
        """For retrieving the simulation conditions for a given BKQuery.

        :param dict in_dict: bookkeeping query
        :return: simulation conditions
        """
        condition = ""
        tables = " simulationconditions sim"
        paging = False
        start = in_dict.get("StartItem", default)
        maximum = in_dict.get("MaxItem", default)

        simid = in_dict.get("SimId", default)
        if simid != default:
            condition += " and sim.simid=%d " % int(simid)

        simdesc = in_dict.get("SimDescription", default)
        if simdesc != default:
            condition += " and sim.simdescription like '%" + simdesc + "%'"

        visible = in_dict.get("Visible", default)
        if visible != default:
            condition += " and sim.visible='%s'" % visible

        if start != default and maximum != default:
            paging = True

        sort = in_dict.get("Sort", default)
        if sort != default:
            condition += "Order by "
            order = sort.get("Order", "Asc")
            if order.upper() not in ["ASC", "DESC"]:
                return S_ERROR("wrong sorting order!")
            items = sort.get("Items", default)
            if isinstance(items, list):
                order = ""
                for item in items:
                    order += "sim.%s," % (item)
                condition += " %s" % order[:-1]
            elif isinstance(items, six.string_types):
                condition += " sim.%s %s" % (items, order)
            else:
                result = S_ERROR("SortItems is not properly defined!")
        else:
            condition += " order by sim.inserttimestamps desc"

        if paging:
            command = (
                " select sim_simid, sim_simdescription, sim_beamcond, sim_beamenergy, sim_generator,\
      sim_magneticfield, sim_detectorcond, sim_luminosity, sim_g4settings, sim_visible from \
      ( select ROWNUM r , sim_simid, sim_simdescription, sim_beamcond, sim_beamenergy, sim_generator, \
      sim_magneticfield, sim_detectorcond, sim_luminosity, sim_g4settings, sim_visible from \
      ( select ROWNUM r, sim.simid sim_simid, sim.simdescription sim_simdescription, sim.beamcond\
      sim_beamcond, sim.beamenergy sim_beamenergy, sim.generator sim_generator, \
      sim.magneticfield sim_magneticfield, sim.detectorcond sim_detectorcond, sim.luminosity\
      sim_luminosity, sim.g4settings sim_g4settings, sim.visible sim_visible \
      from %s where sim.simid=sim.simid %s ) where rownum <=%d ) where r >%d"
                % (tables, condition, maximum, start)
            )
            retVal = self.dbR_.query(command)
        else:
            command = (
                "select sim.simid sim_simid, sim.simdescription sim_simdescription, sim.beamcond sim_beamcond,\
      sim.beamenergy sim_beamenergy, sim.generator sim_generator, \
      sim.magneticfield sim_magneticfield, sim.detectorcond sim_detectorcond, sim.luminosity sim_luminosity,\
      sim.g4settings sim_g4settings, sim.visible sim_visible from %s where sim.simid=sim.simid %s"
                % (tables, condition)
            )
            retVal = self.dbR_.query(command)

        if not retVal["OK"]:
            return retVal
        command = "select count(*) from simulationconditions"

        parameterNames = [
            "SimId",
            "SimDescription",
            "BeamCond",
            "BeamEnergy",
            "Generator",
            "MagneticField",
            "DetectorCond",
            "Luminosity",
            "G4settings",
            "Visible",
        ]
        records = [list(record) for record in retVal["Value"]]
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        totalRecords = retVal["Value"][0][0]
        return S_OK({"ParameterNames": parameterNames, "Records": records, "TotalRecords": totalRecords})

    #############################################################################
    def updateSimulationConditions(self, in_dict):
        """it updates a given simulation condition.

        :param dict in_dict: dictionary which contains the simulation conditions attributes.
        """
        simid = in_dict.get("SimId", default)
        if simid != default:
            condition = ""
            for cond in in_dict:
                if cond != "SimId":
                    condition += "%s='%s'," % (cond, in_dict[cond])
            condition = condition[:-1]
            command = "update simulationconditions set %s where simid=%d" % (condition, int(simid))
            return self.dbW_.query(command)
        else:
            return S_ERROR("SimId is missing!")

    #############################################################################
    def deleteSimulationConditions(self, simid):
        """it deletes a given simulation condition.

        :param long simid: simulation condition id
        """
        return self.dbW_.query("delete simulationconditions where simid=%d" % simid)

    #############################################################################
    def getProductionSummaryFromView(self, in_dict):
        """Data set summary.

        :param dict in_dict: bookkeeping query dictionary
        """
        evt = in_dict.get("EventType", default)
        prod = in_dict.get("Production", default)
        configName = in_dict.get("ConfigName", default)
        configVersion = in_dict.get("ConfigVersion", default)

        tables = " productionoutputfiles prod, productionscontainer cont, simulationconditions sim,\
     data_taking_conditions daq, configurations c "
        condition = (
            " cont.production=prod.production and\
    c.configurationid=cont.configurationid  %s "
            % self.__buildVisible(visible="Y", replicaFlag="Yes")
        )

        condition, tables = self.__buildConfiguration(configName, configVersion, condition, tables)

        condition, tables = self.__buildProduction(prod, condition, tables, useMainTables=False)

        condition, tables = self.__buildEventType(evt, condition, tables, useMainTables=False)

        command = (
            "select prod.production, prod.eventtypeid, c.configname, c.configversion, \
                      BOOKKEEPINGORACLEDB.getProductionProcessingPass(prod.production),\
                      sim.simdescription, daq.description\
                 from %s \
                 where sim.simid(+)=cont.simid and \
                daq.daqperiodid(+)=cont.daqperiodid and %s"
            % (tables, condition)
        )
        parameterNames = [
            "Production",
            "EventType",
            "ConfigName",
            "ConfigVersion",
            "ProcessingPass",
            "ConditionDescription",
        ]
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal
        rows = []
        for record in retVal["Value"]:
            i = dict(zip(parameterNames[:-1], record[:-2]))
            i["ConditionDescription"] = (
                record[len(parameterNames)]
                if record[len(parameterNames)] is not None
                else record[len(parameterNames) - 1]
            )
            rows += [i]
        return S_OK(rows)

    #############################################################################
    def getJobInputOutputFiles(self, diracjobids):
        """For retrieving the input and output files for jobs by a given list of
        DIRAC jobid.

        :param list diracjobids: list of DIRAC jobid
        :return: Successful: DIRAC job which has input/output
          Failed: DIRAC job which does not exists in the db.
        """
        result = {"Failed": {}, "Successful": {}}
        for diracJobid in diracjobids:
            command = (
                "select j.jobid, f.filename from inputfiles i, files f, jobs j where f.fileid=i.fileid and \
      i.jobid=j.jobid and j.diracjobid=%d order by j.jobid, f.filename"
                % int(diracJobid)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result["Failed"][diracJobid] = retVal["Message"]
            result["Successful"][diracJobid] = {}
            result["Successful"][diracJobid]["InputFiles"] = []
            for i in retVal["Value"]:
                result["Successful"][diracJobid]["InputFiles"] += [i[1]]

            command = (
                "select j.jobid, f.filename  from jobs j, files f where j.jobid=f.jobid and \
      diracjobid=%d order by j.jobid, f.filename"
                % int(diracJobid)
            )
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                result["Failed"][diracJobid] = retVal["Message"]
            result["Successful"][diracJobid]["OutputFiles"] = []
            for i in retVal["Value"]:
                result["Successful"][diracJobid]["OutputFiles"] += [i[1]]
        return S_OK(result)

    #############################################################################
    def insertRunStatus(self, runnumber, jobId, isFinished="N"):
        """inserts the run status of a give run.

        :param long runnumber: run number
        :param long jobId: internal bookkeeping job id
        :param str isFinished: the run is not finished by default
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.insertRunStatus", [runnumber, jobId, isFinished], False
        )

    #############################################################################
    def setRunStatusFinished(self, runnumber, isFinished):
        """Set the run status.

        :param long runnumber: run number
        :param str isFinished: 'Y' if it is finished otherwise 'N'
        """
        result = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.setRunFinished", [runnumber, isFinished], False)
        if not result["OK"]:
            return result
        else:
            return S_OK("%s is finished" % (str(runnumber)))

    #############################################################################
    def getRunStatus(self, runnumbers):
        """For retrieving the run status.

        :param list runnumbers: list of runs.
        :return: dictionary which contains the failed runs with the result and sucessful run
        """
        status = {}
        params = ["Finished"]
        status["Successful"] = {}
        status["Failed"] = []
        for i in runnumbers:
            command = "select Finished from runstatus where runnumber=%d" % i
            retVal = self.dbR_.query(command)
            if not retVal["OK"]:
                self.log.error(i, retVal["Message"])
                status["Failed"] += [i]
            else:
                if len(retVal["Value"]) > 0:
                    status["Successful"][i] = dict(zip(params, retVal["Value"][0]))
                else:
                    status["Failed"] += [i]
        return S_OK(status)

    #############################################################################
    def fixRunLuminosity(self, runnumbers):
        """Fix run luminosity for run filea and also all descendants.

        :param list runnumbers: list of run numbers
        :return: Successful runs and Failed runs
        """
        status = {"Failed": [], "Successful": []}
        for run in runnumbers:
            result = self.dbW_.executeStoredProcedure("BOOKKEEPINGORACLEDB.updateLuminosity", [run], False)
            if result["OK"]:
                status["Successful"] += [run]
            else:
                status["Failed"] += [run]
        return S_OK(status)

    #############################################################################
    def getProductionProducedEvents(self, prodid):
        """the produced event by a production taking into account the step.

        :param long prodid: production number
        :return: produced events
        """
        return self.dbR_.executeStoredFunctions("BOOKKEEPINGORACLEDB.getProducedEvents", int, [prodid])

    #############################################################################
    def bulkinsertEventType(self, eventtypes):
        """It inserts a list of event types to the db.

        :param list eventtypes it inserts a list of event types. For example: the list elements are the following:

          .. code-block:: python

            {'EVTTYPEID': '12265021',
             'DESCRIPTION': 'Bu_D0pipipi,Kpi-withf2=DecProdCut_pCut1600MeV',
             'PRIMARY': '[B+ -> (D~0 -> K+ pi-) pi+ pi- pi+]cc'}

        :returns: S_ERROR S_OK({'Failed':[],'Successful':[]})
        """
        failed = []
        for evt in eventtypes:
            evtId = evt.get("EVTTYPEID")
            evtDesc = evt.get("DESCRIPTION")
            evtPrimary = evt.get("PRIMARY")
            retVal = self.insertEventTypes(evtId, evtDesc, evtPrimary)
            if not retVal["OK"]:
                failed.append({evtId: {"Error": retVal["Message"], "EvtentType": evt}})

        successful = list(set(evt["EVTTYPEID"] for evt in eventtypes) - set(list(i)[0] for i in failed))
        return S_OK({"Failed": failed, "Successful": successful})

    #############################################################################
    def bulkupdateEventType(self, eventtypes):
        """It updates a list of event types which are exist in the db.

        :param list eventtypes it is a list of event types. For example: the list elements are the following:

          .. code-block:: python

            {'EVTTYPEID': '12265021',
             'DESCRIPTION': 'Bu_D0pipipi,Kpi-withf2=DecProdCut_pCut1600MeV',
             'PRIMARY': '[B+ -> (D~0 -> K+ pi-) pi+ pi- pi+]cc'}

        :returns: S_ERROR S_OK({'Failed':[],'Successful':[]})
        """
        failed = []
        for evt in eventtypes:
            evtId = evt.get("EVTTYPEID")
            evtDesc = evt.get("DESCRIPTION")
            evtPrimary = evt.get("PRIMARY")
            retVal = self.updateEventType(evtId, evtDesc, evtPrimary)
            if not retVal["OK"]:
                failed.append({evtId: {"Error": retVal["Message"], "EvtentType": evt}})

        successful = list(set(evt["EVTTYPEID"] for evt in eventtypes) - set(list(i)[0] for i in failed))
        return S_OK({"Failed": failed, "Successful": successful})

    def getRunConfigurationsAndDataTakingCondition(self, runnumber):
        """For retrieving the run configuration name and version and the data
        taking condition.

        :param: int runnumber
        :return: S_OK()/S_ERROR ConfigName, ConfigVersion and DataTakingDescription
        """
        command = (
            "select c.configname, c.configversion from jobs j, configurations c \
                  where j.configurationid=c.configurationid and \
                        j.production<0 and j.runnumber=%d"
            % runnumber
        )

        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        if not retVal["Value"]:
            return S_ERROR("Run does not exists in the db")

        result = {"ConfigName": retVal["Value"][0][0], "ConfigVersion": retVal["Value"][0][1]}

        command = (
            "select d.description from jobs j, productionscontainer prod, data_taking_conditions d\
                WHERE j.production=prod.production and \
                      j.production<0 and \
                      prod.daqperiodid=d.daqperiodid and \
                      j.runnumber=%d"
            % runnumber
        )

        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        if not retVal["Value"]:
            return S_ERROR("Data taking description does not exists")
        result["ConditionDescription"] = retVal["Value"][0][0]

        return S_OK(result)

    def deleteCertificationData(self):
        """It destroy the data used by the integration test."""
        return self.dbR_.executeStoredProcedure("BKUTILITIES.destroyDatasets", [], False)

    def updateProductionOutputfiles(self):
        """It is used to trigger an update of the productionoutputfiles table."""
        return self.dbR_.executeStoredProcedure("BKUTILITIES.updateProdOutputFiles", [], False)

    #############################################################################
    def getAvailableTagsFromSteps(self):
        """Availabe database tags.

        :returns: S_OK/S_ERROR a list of db tags
        """

        command = "select distinct DDDB,CONDDB,DQTAG from steps where Usable='Yes'"
        retVal = self.dbR_.query(command)
        if not retVal["OK"]:
            return retVal

        records = []
        for record in retVal["Value"]:
            if record[0] is not None:
                records.append(["DDDB", record[0]])
            if record[1] is not None:
                records.append(["CONDDB", record[1]])
            if record[2] is not None:
                records.append(["DQTAG", record[2]])

        return S_OK({"ParameterNames": ["TagName", "TagValue"], "Records": records})

    #############################################################################
    def bulkgetIDsFromFilesTable(self, lfns):
        """This method used to retreive the JobId, FileId and FiletypeId for a
        given list of lfns.

        :param list lfns: list of lfns
        :returns: S_OK/S_ERROR {"FileId:1","JobId":22, "FileTypeId":3}
        """
        retVal = self.dbR_.executeStoredProcedure(
            packageName="BOOKKEEPINGORACLEDB.bulkgetIdsFromFiles", parameters=[], output=True, array=lfns
        )
        if not retVal["OK"]:
            return retVal

        fileParams = ["JobId", "FileId", "FileTypeId"]
        result = {}
        for record in retVal["Value"]:
            result[record[0]] = dict(zip(fileParams, record[1:]))

        failed = list(set(lfns) - set(result))
        return S_OK({"Successful": result, "Failed": failed})
