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
"""DIRAC ProductionRequestDB class is a front-end to the repository database
containing Production Requests and other related tables."""
# Defined states:
# 'New'
# 'BK OK'
# 'Rejected'
# 'BK Check'
# 'Submitted'
# 'PPG OK'
# 'On-hold'
# 'Tech OK'
# 'Accepted'
# 'Active'
# 'Completed'
# 'Done'
# 'Cancelled'

import json
import time
import threading

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Base.DB import DB

from LHCbDIRAC.ProductionManagementSystem.Utilities.Utils import informPeople


class ProductionRequestDB(DB):
    """DB class for ProductionManagement/ProductionRequestDB."""

    def __init__(self):
        """Constructor."""
        DB.__init__(self, "ProductionRequestDB", "ProductionManagement/ProductionRequestDB")
        self.dateColumns = ["StartingDate", "FinalizationDate"]
        self.dateFormat = "%Y-%m-%d"
        self.lock = threading.Lock()

    # Production Requests table
    requestFields = [
        "RequestID",
        "ParentID",
        "MasterID",
        "RequestAuthor",
        "RequestName",
        "RequestType",
        "RequestState",
        "RequestPriority",
        "RequestPDG",
        "RequestWG",
        "SimCondition",
        "SimCondID",
        "SimCondDetail",
        "ProPath",
        "ProID",
        "ProDetail",
        "EventType",
        "NumberOfEvents",
        "Description",
        "Comments",
        "Inform",
        "RealNumberOfEvents",
        "IsModel",
        "Extra",
        "RetentionRate",
        "FastSimulationType",
        "StartingDate",
        "FinalizationDate",
        "HasSubrequest",
        "bk",
        "bkSrTotal",
        "bkTotal",  # runtime
        "rqTotal",
        "crTime",
        "upTime",
    ]  # runtime

    historyFields = ["RequestID", "RequestState", "RequestUser", "TimeStamp"]

    # !!! current _escapeValues is buggy !!! None and not using connection...
    # _insert use it, so I can't...
    def _fixedEscapeValues(self, inValues, escape=None):
        """This method used to insert null value to the db, if the inserted value
        is None.

        :param list inValues: list of values
        :param int escape: the index of the value, which will be not escaped.
        """
        result = self._escapeValues(inValues)
        if not result["OK"]:
            return result
        outValues = result["Value"]
        for i, x in enumerate(outValues):
            if x == "None" or str(x) == "" or x == '"None"':
                if escape and i == escape:
                    continue
                outValues[i] = "NULL"
        return S_OK(outValues)

    @staticmethod
    def __prefixComments(update, old, user):
        """Add Log style prefix to the record like change."""
        if not update:
            return update
        if not old:
            old = ""
        if not update.startswith(old) and not update.endswith(old):
            return update
        prefix = "Comment by %s on %s: " % (user, time.strftime("%b %d, %Y"))
        if update.startswith(old):
            if old.rstrip():
                old = old.rstrip() + "\n\n"
            return old + prefix + update[len(old) :].lstrip()
        return prefix + update.lstrip()

    def __getRequestInfo(self, iD, connection):
        """Retrive info fields from specified ID Used to get ParentID information.

        id must be checked before
        NOTE: it does self.lock.release() in case of errors
        """
        inFields = ["RequestState", "ParentID", "MasterID", "RequestAuthor", "Inform", "IsModel"]
        result = self._query(
            "SELECT %s " % ",".join(inFields) + "FROM ProductionRequests " + "WHERE RequestID=%s;" % iD, connection
        )
        if not result["OK"]:
            self.lock.release()
            return result
        if len(result["Value"]) == 0:
            self.lock.release()
            return S_ERROR("Request does not exist")
        return S_OK(dict(zip(inFields, result["Value"][0])))

    def __getStateAndAuthor(self, iD, connection):
        """Return state, Author and inform list of Master for id (or id's own if no parents)
        id must be checked before
        NOTE: it does self.lock.release() in case of errors
        """
        result = self.__getRequestInfo(iD, connection)
        if not result["OK"]:
            return result
        pinfo = result["Value"]
        if not pinfo["MasterID"]:
            return S_OK([pinfo["RequestState"], pinfo["RequestAuthor"], pinfo["Inform"], pinfo["IsModel"]])
        result = self.__getRequestInfo(pinfo["MasterID"], connection)
        if not result["OK"]:
            return result
        pinfo = result["Value"]
        return S_OK([pinfo["RequestState"], pinfo["RequestAuthor"], pinfo["Inform"], pinfo["IsModel"]])

    def __checkMaster(self, master, iD, connection):
        """Return State of Master for id (or id's own if no parents) id and master
        must be checked before.

        It check that master can
        be reached with ParentID links.
        NOTE: it does self.lock.release() in case of errors
        """
        while True:
            result = self.__getRequestInfo(iD, connection)
            if not result["OK"]:
                return result
            pinfo = result["Value"]
            if iD == master:
                return S_OK(pinfo["RequestState"])
            if pinfo["MasterID"] != master:
                self.lock.release()
                return S_ERROR("Wrong MasterID for this ParentID")
            if not pinfo["ParentID"] or pinfo["ParentID"] == iD:
                self.lock.release()
                return S_ERROR("Parent tree is broken. Please contact expert")
            iD = pinfo["ParentID"]

    def createProductionRequest(self, requestDict, creds):
        """Create new Production Request
        TODO: Complete check of content
        """

        rec = dict.fromkeys(self.requestFields[1:-9], None)

        for x in requestDict:
            if x in rec and str(requestDict[x]) != "":
                rec[x] = requestDict[x]  # set only known not empty fields
        if rec["NumberOfEvents"]:  # Set RealNumberOfEvents if specified
            try:
                num = int(rec["NumberOfEvents"])
                if num > 0:
                    rec["RealNumberOfEvents"] = num
            except ValueError:
                pass
            except TypeError:
                gLogger.warn("RealNumberOfEvents not defined")
        if not rec["MasterID"]:
            rec["RequestPDG"] = ""
            if not rec["RequestState"]:
                rec["RequestState"] = "New"
        else:
            rec["RequestPDG"] = None
            rec["RequestState"] = None

        if rec["RequestState"]:
            if not rec["RequestState"] in ["New", "BK Check", "Submitted"]:
                return S_ERROR("The request can't be created in '%s' state" % rec["requestState"])
            if rec["RequestState"] != "New":
                # !!! full information check must be here, but currently in the JS...
                # so we only check EventType consistency
                if not rec["EventType"]:
                    return S_ERROR("Please specify Event type/number or add subrequest(s)")
        if "Comments" in rec:
            rec["Comments"] = self.__prefixComments(rec["Comments"], "", creds["User"])
        rec["IsModel"] = 0

        recl = [rec[x] for x in self.requestFields[1:-9]]
        result = self._fixedEscapeValues(recl)
        if not result["OK"]:
            return result
        recls = result["Value"]
        if recl[-1] == "NULL":  # This is FastSimulationType, which can be None
            recls[-1] = '"None"'

        for dateValues in self.dateColumns:
            recls.append(
                "STR_TO_DATE('%s','%s')"
                % (requestDict.get(dateValues, time.strftime(self.dateFormat)), self.dateFormat)
            )

        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        if rec["MasterID"]:  # have to check ParentID and MasterID consistency
            try:
                masterID = int(rec["MasterID"])
            except ValueError:
                self.lock.release()
                return S_ERROR("MasterID is not a number")
            if not rec["ParentID"]:
                self.lock.release()
                return S_ERROR("MasterID can not be without ParentID")
            try:
                parentID = int(rec["ParentID"])
            except ValueError:
                self.lock.release()
                return S_ERROR("ParentID is not a number")
            result = self.__checkMaster(masterID, parentID, connection)
            if not result["OK"]:
                return result
            result = self.__getStateAndAuthor(masterID, connection)
            if not result["OK"]:
                return result
            requestState, requestAuthor, _requestInform, isModel = result["Value"]
            if requestState != "New":
                self.lock.release()
                return S_ERROR("Requests can't be modified after submission")
            if requestAuthor != creds["User"] and not (isModel and creds["Group"] == "lhcb_tech"):
                self.lock.release()
                return S_ERROR("Only request author can add subrequests")
        elif rec["ParentID"]:
            try:
                parentID = int(rec["ParentID"])
            except ValueError:
                self.lock.release()
                return S_ERROR("ParentID is not a number")
            result = self.__getStateAndAuthor(parentID, connection)
            if not result["OK"]:
                return result
        result = self.__checkIOTypes(requestDict)
        if not result["OK"]:
            self.lock.release()
            return result

        req = "INSERT INTO ProductionRequests ( " + ",".join(self.requestFields[1:-7])
        req += " ) VALUES ( %s );" % ",".join(recls)
        result = self._update(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        req = "SELECT LAST_INSERT_ID();"
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        requestID = int(result["Value"][0][0])

        # Update history for masters. Errors are not reported back to the user.
        if rec["RequestState"]:
            result = self._update(
                "INSERT INTO RequestHistory ("
                + ",".join(self.historyFields[:-1])
                + ") VALUES ( %s,'%s','%s')" % (requestID, str(rec["RequestState"]), str(rec["RequestAuthor"])),
                connection,
            )
            if not result["OK"]:
                gLogger.error(result["Message"])
        self.lock.release()
        if rec["RequestState"] in ["BK Check", "Submitted"]:
            rec["RequestID"] = requestID
            informPeople(rec, "", rec["RequestState"], creds["User"], rec["Inform"])
        return S_OK(requestID)

    def __checkIOTypes(self, requestDict):
        """Check the input type of each step matches the output of a previous
        step."""
        prodDetail = requestDict.get("ProDetail")
        if prodDetail is not None:
            try:
                proDetail = json.loads(prodDetail)
            except Exception:
                return S_ERROR("Content of ProDetail field cannot be loaded")
            for i in range(20):
                outputKey = "p" + str(i) + "OFT"
                inputKey = "p" + str(i + 1) + "IFT"
                if outputKey in proDetail and inputKey in proDetail:
                    inputFileTypes = set(proDetail[inputKey].replace("(N)", "").replace("(Y)", "").split(","))
                    outputFileTypes = set(proDetail[outputKey].replace("(N)", "").replace("(Y)", "").split(","))
                    if not inputFileTypes.issubset(outputFileTypes):
                        return S_ERROR("Input for step " + str(i + 1) + " does not match the output of step " + str(i))
        return S_OK()

    @staticmethod
    def __addMonitoring(req, order):
        """Append monitoring columns.

        Somehow tricky SQL. Most probable need optimizations, but ok for
        now.
        """
        rQuery = "SELECT t.*,MIN(rh.TimeStamp) AS crTime,"
        rQuery += "           MAX(rh.TimeStamp) AS upTime "
        rQuery += "FROM "
        rQuery += "(SELECT t.*,CAST(COALESCE(SUM(sr.RealNumberOfEvents),0)+"
        rQuery += "                COALESCE(t.RealNumberOfEvents,0) AS SIGNED)"
        rQuery += "           AS rqTotal "
        rQuery += " FROM "
        rQuery += " (SELECT t.*,CAST(COALESCE(SUM(t.bkSrTotal),0)+"
        rQuery += "                  COALESCE(t.bk,0) AS SIGNED) AS bkTotal FROM "
        rQuery += "  (SELECT t.*,CAST(LEAST(COALESCE(SUM(pp.BkEvents),0),"
        rQuery += "                   COALESCE(SUM(sr.RealNumberOfEvents),0)) AS SIGNED)"
        rQuery += "              AS bkSrTotal FROM "
        rQuery += "   (SELECT t.*, CAST(SUM(pp.BkEvents) AS SIGNED)"
        rQuery += "                AS bk FROM (%s) as t " % req
        rQuery += "    LEFT JOIN ProductionProgress as pp ON (pp.RequestID=t.RequestID "
        rQuery += "    AND pp.Used=1) GROUP BY t.RequestID) as t "
        rQuery += "   LEFT JOIN ProductionRequests AS sr ON t.RequestID=sr.MasterID "
        rQuery += "   LEFT JOIN ProductionProgress AS pp ON (sr.RequestID=pp.RequestID "
        rQuery += "   AND pp.Used=1) GROUP BY t.RequestID) AS t"
        rQuery += "  GROUP BY t.RequestID) AS t"
        rQuery += " LEFT JOIN ProductionRequests as sr ON sr.MasterID=t.RequestID "
        rQuery += " GROUP BY t.RequestID) as t"
        rQuery += " LEFT JOIN RequestHistory as rh ON rh.RequestID=t.RequestID "
        rQuery += " GROUP BY t.RequestID"

        return rQuery + order

    def getProductionRequest(
        self, requestIDList, subrequestsFor=0, sortBy="", sortOrder="ASC", offset=0, limit=0, filterIn=None
    ):
        """Get the Production Request(s) details.

        If requestIDList is not empty, only productions from the list are
        returned. Otherwise master requests are returned (without
        subrequests) or all subrequests of 'subrequestsFor' (when
        specified). Parameters with explicit types are assumed checked by
        service.
        """
        if filterIn is None:
            filterIn = {}
        try:  # test parameters
            for x in requestIDList:
                y = int(x)
        except ValueError:
            return S_ERROR("Bad parameters (all request IDs must be numbers)")
        idFilter = False
        try:  # test filters
            sfilter = []
            for x in filterIn:
                if x not in self.requestFields[:-7]:
                    return S_ERROR("bad field in filterIn")
                val = str(filterIn[x])
                if val:
                    val = "( " + ",".join(['"' + y + '"' for y in val.split(",")]) + ") "
                    if x == "RequestID":
                        # Collect also masters masters
                        req = "SELECT RequestID,MasterID FROM ProductionRequests "
                        req += "WHERE RequestID IN %s" % val
                        result = self._query(req)
                        if not result["OK"]:
                            return result
                        val = []
                        for y in result["Value"]:
                            if str(y[1]) != "None":
                                val.append(str(y[1]))
                            else:
                                val.append(str(y[0]))
                        if not val:
                            return S_OK({"Rows": [], "Total": 0})
                        val = "( " + ",".join(val) + ") "
                        idFilter = True
                    sfilter.append(" t.%s IN %s " % (x, val))
            sfilter = " AND ".join(sfilter)
        except Exception as e:
            return S_ERROR("Bad filter content " + str(e))

        if sortBy:
            if sortBy not in self.requestFields[:-7]:
                return S_ERROR("sortBy field does not exist")
            if sortOrder != "ASC":
                sortOrder = "DESC"

        fields = ",".join(["t." + x for x in self.requestFields[:-7]])
        req = "SELECT %s ,COUNT(sr.RequestID) AS HasSubrequest " % fields
        req += "FROM ProductionRequests as t "
        req += "LEFT JOIN ProductionRequests AS sr ON t.RequestID=sr.ParentID "
        req += "WHERE "

        if requestIDList:
            idlist = ",".join([str(x) for x in requestIDList])
            where = "t.RequestID IN (%s)" % idlist
        else:
            if subrequestsFor:
                where = "t.ParentID=%s" % subrequestsFor
            else:
                where = sfilter
                if not idFilter:
                    if where:
                        where += " AND t.ParentID IS NULL"
                    else:
                        where = "t.ParentID IS NULL"
        req += where
        req += " GROUP BY t.RequestID"
        order = ""
        if sortBy:
            # order have to be applyed twice: before LIMIT and at the end
            order = " ORDER BY %s %s" % (sortBy, sortOrder)
            req += order
        if limit and not subrequestsFor:
            req += " LIMIT %s,%s" % (offset, limit)
        result = self._query(self.__addMonitoring(req, order))
        if not result["OK"]:
            return result

        rows = [dict(zip(self.requestFields, row)) for row in result["Value"]]
        total = len(rows)
        if limit:
            result = self._query("SELECT COUNT(*) FROM ProductionRequests AS t WHERE %s" % where)
            if not result["OK"]:
                return result
            total = result["Value"][0][0]
        return S_OK({"Rows": rows, "Total": total})

    def __checkUpdate(self, update, old, creds, connection):
        """Check that update is possible.

        Return dict with values for _inform_people (with
        state=='' in  case notification is not required)
        NOTE: unlock in case of errors
        """
        requestID = old["RequestID"]
        result = self.__getStateAndAuthor(requestID, connection)
        if not result["OK"]:
            return result
        requestState, requestAuthor, requestInform, isModel = result["Value"]
        rec = old.copy()
        rec.update(update)
        inform = {
            "rec": rec,
            "state": "",
            "author": str(requestAuthor),
            "oldstate": requestState,
            "inform": requestInform,
        }

        hasSubreq = False
        if not old["MasterID"]:
            result = self._query(
                "SELECT RequestID " + "FROM ProductionRequests " + "WHERE MasterID=%s" % requestID, connection
            )
            if not result["OK"]:
                self.lock.release()
                return result
            if result["Value"]:
                hasSubreq = True

        if creds["Group"] in ["diracAdmin", "lhcb_admin"]:
            return S_OK(inform)

        # Tech expert can (un)mark any master request as model. But only explicitly.
        if creds["Group"] == "lhcb_tech" and not old["MasterID"]:
            if len(update) == 1 and "IsModel" in update:
                if str(update["IsModel"]) == "1":
                    update["IsModel"] = 1
                else:
                    update["IsModel"] = 0
                return S_OK(inform)
        else:
            if "IsModel" in update:
                del update["IsModel"]

        if requestState in ["Done", "Cancelled"] and (creds["Group"] not in ["diracAdmin", "lhcb_admin"]):
            self.lock.release()
            return S_ERROR("Done or cancelled requests can't be modified")

        # Check that a person can update in general (that also means he can
        # change at least comments)
        if requestState in ["New", "BK OK", "Rejected"]:
            if requestAuthor != creds["User"] and not (isModel and creds["Group"] == "lhcb_tech"):
                self.lock.release()
                return S_ERROR("Only author is allowed to modify unsubmitted request")
        elif requestState == "BK Check":
            if creds["Group"] != "lhcb_bk":
                self.lock.release()
                return S_ERROR("Only BK expert can manage new Simulation Conditions")
        elif requestState == "Submitted":
            if creds["Group"] != "lhcb_ppg" and creds["Group"] != "lhcb_tech":
                self.lock.release()
                return S_ERROR("Only PPG members or Tech. experts are allowed to sign submitted request")
        elif requestState == "PPG OK":
            if creds["Group"] != "lhcb_tech":
                self.lock.release()
                return S_ERROR("Only Tech. experts are allowed to sign this request")
        elif requestState == "On-hold":
            if creds["Group"] != "lhcb_tech":
                self.lock.release()
                return S_ERROR("Only Tech. experts are allowed to sign this request")
        elif requestState == "Tech OK":
            if creds["Group"] != "lhcb_ppg":
                self.lock.release()
                return S_ERROR("Only PPG members are allowed to sign this request")
        elif requestState == "Accepted":
            if creds["Group"] != "lhcb_prmgr":
                self.lock.release()
                return S_ERROR("Only Tech. experts are allowed to manage accepted request")
        elif requestState in ["Active", "Completed"]:
            if not creds["Group"] in ["lhcb_prmgr", "lhcb_prod"]:
                self.lock.release()
                return S_ERROR("Only experts are allowed to manage active request")
        elif requestState in ["Done", "Cancelled"]:
            if creds["Group"] not in ["diracAdmin", "lhcb_admin"]:
                self.lock.release()
                return S_ERROR("Only admin can violate the system logic")
        else:
            self.lock.release()
            return S_ERROR("The request is in unknown state '%s'" % requestState)

        if old["MasterID"]:  # for subrequests it's simple
            if requestState == "New":
                for x in update:
                    if x not in ["EventType", "NumberOfEvents", "RealNumberOfEvents", "Comments"]:
                        self.lock.release()
                        return S_ERROR("%s is not allowed in subrequests" % x)
                    if x != "Comments" and not update[x]:
                        self.lock.release()
                        return S_ERROR("You must specify event type and number")
            else:
                if len(update) != 1 or "Comments" not in update:
                    self.lock.release()
                    return S_ERROR("Only comments can be changed for subrequest in progress")
            return S_OK(inform)
        # for masters it is more complicated...
        if requestState == "New":
            if "RequestState" not in update:
                return S_OK(inform)
            if update["RequestState"] in ["BK Check", "Submitted"]:
                # !!! full information check must be here, but currently in the JS...
                # so we only check EventType consistency
                eventType = old["EventType"]
                if "EventType" in update:
                    eventType = update["EventType"]
                # gLogger.error(str(update))
                if eventType and hasSubreq:
                    self.lock.release()
                    return S_ERROR("The request has subrequests, so it must not specify Event type")
                if not eventType and not hasSubreq:
                    self.lock.release()
                    return S_ERROR("Please specify Event type/number or add subrequest(s)")
            else:
                self.lock.release()
                _msgTuple = (requestState, update["RequestState"])
                return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        elif requestState == "Rejected":
            if len(update) != 1 or update.get("RequestState", "") != "New":
                self.lock.release()
                return S_ERROR("Rejected requests must be resurrected before modifications")
        elif requestState == "BK Check":
            for x in update:
                if x not in [
                    "RequestState",
                    "SimCondition",
                    "SimCondID",
                    "SimCondDetail",
                    "Comments",
                    "Inform",
                    "Extra",
                ]:
                    self.lock.release()
                    return S_ERROR("%s can't be modified during BK check" % x)
            if "RequestState" not in update:
                return S_OK(inform)
            if not update["RequestState"] in ["BK OK", "Rejected"]:
                self.lock.release()
                _msgTuple = (requestState, update["RequestState"])
                return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
            if update["RequestState"] == "BK OK" and not update.get("SimCondID", old["SimCondID"]):
                self.lock.release()
                return S_ERROR("Registered simulation conditions required to sign for BK OK")
        elif requestState == "BK OK":
            for x in update:
                if x not in ["RequestState", "Comments", "Inform", "Extra"]:
                    self.lock.release()
                    return S_ERROR("%s can't be modified after BK check" % x)
            if "RequestState" not in update:
                return S_OK(inform)
            if not update["RequestState"] in ["Submitted", "Rejected"]:
                self.lock.release()
                _msgTuple = (requestState, update["RequestState"])
                return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        elif requestState == "Submitted":
            if creds["Group"] == "lhcb_ppg":
                for x in update:
                    if x not in (
                        "RequestState",
                        "RequestWG",
                        "Comments",
                        "Inform",
                        "RequestPriority",
                        "Extra",
                        "StartingDate",
                        "FinalizationDate",
                        "RetentionRate",
                    ):
                        self.lock.release()
                        return S_ERROR("%s can't be modified during PPG signing" % x)
                if "RequestState" not in update:
                    return S_OK(inform)
                if update["RequestState"] == "Accepted":
                    update["RequestState"] = "PPG OK"
                if not update["RequestState"] in ["PPG OK", "Rejected"]:
                    self.lock.release()
                    _msgTuple = (requestState, update["RequestState"])
                    return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
            if creds["Group"] == "lhcb_tech":
                for x in update:
                    if x not in ["RequestState", "Comments", "Inform", "ProPath", "ProID", "ProDetail", "Extra"]:
                        self.lock.release()
                        return S_ERROR("%s can't be modified during Tech signing" % x)
                if "RequestState" not in update:
                    return S_OK(inform)
                if update["RequestState"] == "Accepted":
                    update["RequestState"] = "Tech OK"
                if not update["RequestState"] in ["Tech OK", "Rejected"]:
                    self.lock.release()
                    _msgTuple = (requestState, update["RequestState"])
                    return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        # AZ: removed from logic
        #        if update['RequestState'] == 'Tech OK' and not update.get('ProID',old['ProID']):
        #          self.lock.release()
        #          return S_ERROR("Registered processing pass is required to sign for Tech OK")
        elif requestState in ["PPG OK", "On-hold"]:
            for x in update:
                if x not in ["RequestState", "Comments", "Inform", "ProPath", "ProID", "ProDetail", "Extra"]:
                    self.lock.release()
                    return S_ERROR("%s can't be modified during Tech signing" % x)
            if "RequestState" not in update:
                return S_OK(inform)
            if update["RequestState"] == "Tech OK":
                update["RequestState"] = "Accepted"
            if not update["RequestState"] in ["Accepted", "Rejected", "On-hold"]:
                self.lock.release()
                _msgTuple = (requestState, update["RequestState"])
                return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        # AZ: removed from logic
        #      if update['RequestState'] == 'Accepted' and not update.get('ProID',old['ProID']):
        #        self.lock.release()
        #        return S_ERROR("Registered processing pass is required to sign for Tech OK")
        elif requestState == "Tech OK":
            for x in update:
                if x not in ["RequestState", "RequestWG", "Comments", "Inform", "RequestPriority", "Extra"]:
                    self.lock.release()
                    return S_ERROR("%s can't be modified during PPG signing" % x)
            if "RequestState" not in update:
                return S_OK(inform)
            if update["RequestState"] == "PPG OK":
                update["RequestState"] = "Accepted"
            if not update["RequestState"] in ["Accepted", "Rejected"]:
                self.lock.release()
                _msgTuple = (requestState, update["RequestState"])
                return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        elif requestState in ["Accepted", "Active", "Completed"]:
            for x in update:
                if x not in ["RequestState", "Comments", "Inform", "ProPath", "ProID", "ProDetail", "Extra"]:
                    self.lock.release()
                    return S_ERROR("%s can't be modified during the progress" % x)
            if "RequestState" not in update:
                return S_OK(inform)
            if requestState == "Accepted":
                if not update["RequestState"] in ["Active", "Cancelled", "PPG OK"]:
                    self.lock.release()
                    _msgTuple = (requestState, update["RequestState"])
                    return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
            elif requestState == "Active":
                if (update["RequestState"] not in ["Done", "Cancelled", "Completed", "Accepted"]) or (
                    update["RequestState"] != "Accepted" and creds["Group"] != "lhcb_prmgr"
                ):
                    self.lock.release()
                    _msgTuple = (requestState, update["RequestState"])
                    return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
            else:
                if not update["RequestState"] in ["Active", "Done", "Cancelled"]:
                    self.lock.release()
                    _msgTuple = (requestState, update["RequestState"])
                    return S_ERROR("The request is '%s' now, moving to '%s' is not possible" % _msgTuple)
        inform["state"] = update["RequestState"]
        inform["rec"].update(update)
        return S_OK(inform)

    def updateProductionRequest(self, requestID, requestDict, creds):
        """Update existing production request In states other than New only state
        and comments are changable.

        TODO: RequestPDG change in ??? state
              Protect fields in subrequests
        """
        fdict = dict.fromkeys(self.requestFields[4:-7], None)
        rec = {}
        for x in requestDict:
            if x in fdict:
                if requestDict[x]:
                    rec[x] = requestDict[x]  # set only known fields
                else:
                    rec[x] = None  # to be more deterministic...

        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        fields = ",".join(["t." + x for x in self.requestFields[:-7]])
        req = "SELECT %s " % fields
        req += "FROM ProductionRequests as t "
        req += "WHERE t.RequestID=%s" % requestID
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        if not result["Value"]:
            self.lock.release()
            return S_ERROR("The request is no longer exist")

        old = dict(zip(self.requestFields[:-7], result["Value"][0]))

        update = {}  # Decide what to update (and if that is required)
        for x in rec:
            if x in ("ProDetail", "SimCondDetail", "Extra"):
                if rec[x] == old[x]:
                    continue
                try:
                    recx = json.loads(rec[x])
                    oldx = json.loads(old[x])
                    if recx == oldx:
                        continue
                except TypeError:
                    # This happens if, for example, oldx is None (meaning there was not prodetail, while now there is).
                    # Which means that now we can update
                    pass
            elif str(rec[x]) == str(old[x]):
                continue

            if x == "RetentionRate" and float(rec[x]) == old[x]:
                continue
            if x == "ProDetail":
                result = self.__checkIOTypes(requestDict)
                if not result["OK"]:
                    self.lock.release()
                    return result
            update[x] = rec[x]

        if len(update) == 0:
            self.lock.release()
            return S_OK(requestID)  # nothing to update

        if "NumberOfEvents" in update:  # Update RealNumberOfEvents if specified
            num = 0
            try:
                num = int(rec["NumberOfEvents"])
                if num < 0:
                    num = 0
            except ValueError:
                pass
            except TypeError:
                gLogger.warn("NumberOfEvents not defined for %s" % requestID)
            update["RealNumberOfEvents"] = str(num)

        if "Comments" in update:
            update["Comments"] = self.__prefixComments(update["Comments"], old["Comments"], creds["User"])

        result = self.__checkUpdate(update, old, creds, connection)
        if not result["OK"]:
            return result
        inform = result["Value"]

        # we have to escape values... tricky way
        # in addition we can not escape the datetime.date values. so if they are being updated,
        # they will be added to this list later
        recl_fields = [column for column in update if column not in self.dateColumns]
        recl = [update[x] for x in recl_fields]
        result = self._fixedEscapeValues(recl)
        if not result["OK"]:
            self.lock.release()
            return result
        updateValues = result["Value"]
        for dateValue in self.dateColumns:
            # we are going to check if we have column which type is date
            # the order is very important that's why we use recl_fields
            if dateValue in self.dateColumns and requestDict.get(dateValue):
                recl_fields.append(dateValue)
                updateValues.append("STR_TO_DATE('%s','%s')" % (requestDict.get(dateValue), self.dateFormat))
        updates = ",".join([x + "=" + y for x, y in zip(recl_fields, updateValues)])

        req = "UPDATE ProductionRequests "
        req += "SET %s " % updates
        req += "WHERE RequestID=%s" % requestID
        result = self._update(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result

        if "RequestState" in update:
            result = self._update(
                "INSERT INTO RequestHistory ("
                + ",".join(self.historyFields[:-1])
                + ") VALUES ( %s,'%s','%s')" % (requestID, str(update["RequestState"]), str(creds["User"])),
                connection,
            )
            if not result["OK"]:
                gLogger.error(result["Message"])

        result = S_OK()
        gLogger.info(str(update))

        if result["OK"]:
            self.lock.release()

        informPeople(**inform)
        return S_OK(requestID)

    def __getSubrequestsList(self, iD, master, connection):
        """Return list of all subrequests for this request
        NOTE: it does self.lock.release() in case of errors
        """
        result = self._query(
            "SELECT RequestID " + "FROM ProductionRequests " + "WHERE ParentID=%s and MasterID=%s" % (iD, master),
            connection,
        )
        if not result["OK"]:
            self.lock.release()
            return result
        sr = []
        for x in result["Value"]:
            sr.append(x[0])
            result = self.__getSubrequestsList(x[0], master, connection)
            if not result["OK"]:
                self.lock.release()
                return result
            sr += result["Value"]
        return S_OK(sr)

    def deleteProductionRequest(self, requestID, creds):
        """Delete existing production.

        Subrequests are deleted. Substructure is moved up in the tree.
        Available is New and Rejected states only
        """
        try:
            requestID = int(requestID)
        except ValueError:
            return S_ERROR("RequestID is not a number")
        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        result = self.__getStateAndAuthor(requestID, connection)
        if not result["OK"]:
            return result
        requestState, requestAuthor, _requestInform, isModel = result["Value"]
        if creds["Group"] not in ["diracAdmin", "lhcb_admin"]:
            if requestAuthor != creds["User"] and not (isModel and creds["Group"] == "lhcb_tech"):
                self.lock.release()
                gLogger.error("%s can't remove %s request" % (creds["User"], requestAuthor))
                return S_ERROR("Only author can remove a request")
            if requestState != "New" and requestState != "Rejected":
                self.lock.release()
                return S_ERROR("Can not remove request in processing")
        result = self.__getRequestInfo(requestID, connection)
        if not result["OK"]:
            return result
        pinfo = result["Value"]
        parentID = pinfo["ParentID"]
        masterID = pinfo["MasterID"]

        upperID = parentID
        if not upperID:
            upperID = "NULL"

        # delete subrequests
        req = ""
        if not masterID:  # this request is a master
            # delete history
            result = self._update("DELETE FROM RequestHistory " + "WHERE RequestID=%s" % requestID)
            if not result["OK"]:
                self.lock.release()
                return result
            # delete tracking
            result = self._update(
                "DELETE FROM ProductionProgress "
                + "WHERE RequestID IN "
                + "(SELECT RequestID FROM ProductionRequests "
                + "WHERE RequestID=%s OR MasterID=%s" % (requestID, requestID)
                + ")",
                connection,
            )
            if not result["OK"]:
                self.lock.release()
                return result
            req = "DELETE FROM ProductionRequests "
            req += "WHERE MasterID=%s" % requestID
        else:  # this request is subrequest
            result = self.__getSubrequestsList(requestID, masterID, connection)
            if not result["OK"]:
                return result
            rlist = result["Value"]
            # delete tracking
            result = self._update(
                "DELETE FROM ProductionProgress "
                + "WHERE RequestID IN (%s)" % ",".join([str(x) for x in rlist] + [str(requestID)])
            )
            if not result["OK"]:
                self.lock.release()
                return result
            if len(rlist):
                req = "DELETE FROM ProductionRequests "
                req += "WHERE RequestID in (%s)" % ",".join([str(x) for x in rlist])
        if req:
            result = self._update(req, connection)
            if not result["OK"]:
                self.lock.release()
                return result

        # move substructure
        req = "UPDATE ProductionRequests SET ParentID=%s " % upperID
        req += "WHERE ParentID=%s" % requestID
        result = self._update(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result

        # finally delete us
        req = "DELETE FROM ProductionRequests "
        req += "WHERE RequestID=%s" % requestID
        result = self._update(req, connection)

        self.lock.release()

        if not result["OK"]:
            return result
        return S_OK(requestID)

    def __getRequest(self, requestID, connection):
        """retrive complete request record.

        NOTE: unlock in case of errors
        """
        fields = ",".join(["t." + x for x in self.requestFields[:-7]])
        req = "SELECT %s " % fields
        req += "FROM ProductionRequests as t "
        req += "WHERE t.RequestID=%s" % requestID
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        if not result["Value"]:
            self.lock.release()
            return S_ERROR("The request is no longer exist")
        rec = dict(zip(self.requestFields[:-7], result["Value"][0]))
        return S_OK(rec)

    @staticmethod
    def __clearProcessingPass(rec):
        """clear processing pass section."""
        rec["ProID"] = None
        nd = {}
        rec["ProDetail"] = json.dumps(nd)

    def __duplicateDeep(self, requestID, masterID, parentID, creds, connection, clearpp):
        """recurcive duplication function.

        NOTE: unlock in case of errors
        """

        result = self.__getRequest(requestID, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        rec = result["Value"]
        if clearpp:
            self.__clearProcessingPass(rec)
        rec["IsModel"] = 0

        if masterID and not rec["MasterID"]:
            return S_OK("")  # substructured request

        if rec["ParentID"]:
            rec["ParentID"] = parentID
        if rec["MasterID"]:
            rec["MasterID"] = masterID
        if rec["RequestAuthor"]:
            rec["RequestAuthor"] = creds["User"]
        if rec["RequestState"]:
            rec["RequestState"] = "New"

        # Clear RealNumberOfEvents if required
        try:
            num = 0
            num = int(rec["NumberOfEvents"])
            if num < 0:
                num = 0
        except ValueError:
            pass
        except TypeError:
            gLogger.warn("NumberOfEvents is not defined for %s" % requestID)
        rec["RealNumberOfEvents"] = str(num)

        recl = [rec[x] for x in self.requestFields[1:-7]]
        escapeIndex = self.requestFields[1:-7].index("FastSimulationType")
        result = self._fixedEscapeValues(recl, escapeIndex)
        if not result["OK"]:
            self.lock.release()
            return result
        recls = result["Value"]

        req = "INSERT INTO ProductionRequests ( " + ",".join(self.requestFields[1:-7])
        req += " ) VALUES ( %s );" % ",".join(recls)
        result = self._update(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        req = "SELECT LAST_INSERT_ID();"
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        newRequestID = int(result["Value"][0][0])

        # Update history for masters. Errors are not reported back to the user.
        if rec["RequestState"]:
            result = self._update(
                "INSERT INTO RequestHistory ("
                + ",".join(self.historyFields[:-1])
                + ") VALUES ( %s,'%s','%s')" % (newRequestID, str(rec["RequestState"]), str(rec["RequestAuthor"])),
                connection,
            )
            if not result["OK"]:
                gLogger.error(result["Message"])

        # now for subrequests
        if not masterID:
            masterID = newRequestID
        parentID = newRequestID

        req = "SELECT RequestID "
        req += "FROM ProductionRequests as t "
        req += "WHERE t.ParentID=%s" % requestID
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        for chID in [row[0] for row in result["Value"]]:
            result = self.__duplicateDeep(chID, masterID, parentID, creds, connection, False)
            if not result["OK"]:
                return result

        return S_OK(int(newRequestID))

    def duplicateProductionRequest(self, requestID, creds, clearpp):
        """Duplicate production request with all it's subrequests (but without
        substructure).

        If that is subrequest, master must be in New state and user must be
        the author. If clearpp is set, all details in the Processing pass
        (of the master) are cleaned.
        """
        try:
            requestID = int(requestID)
        except ValueError:
            return S_ERROR("RequestID is not a number")
        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        result = self.__getRequestInfo(requestID, connection)
        if not result["OK"]:
            return result
        pinfo = result["Value"]
        parentID = pinfo["ParentID"]
        masterID = pinfo["MasterID"]

        if masterID:
            clearpp = False
            result = self.__getStateAndAuthor(requestID, connection)
            if not result["OK"]:
                return result
            requestState, requestAuthor, _requestInform, isModel = result["Value"]
            if requestState != "New" or (
                requestAuthor != creds["User"] and not (isModel and creds["Group"] == "lhcb_tech")
            ):
                self.lock.release()
                return S_ERROR("Can not duplicate subrequest of request in progress")

        result = self.__duplicateDeep(requestID, masterID, parentID, creds, connection, clearpp)
        if result["OK"]:
            self.lock.release()
        return result

    @staticmethod
    def __checkAuthorizeSplit(requestState, creds):
        """Check that current user is allowed to split in specified state."""
        if creds["Group"] in ["diracAdmin", "lhcb_admin"]:
            return S_OK()
        if (requestState in ["Submitted", "PPG OK", "On-hold"]) and creds["Group"] == "lhcb_tech":
            return S_OK()
        if requestState in ["Accepted", "Active", "Completed"] and creds["Group"] == "lhcb_prmgr":
            return S_OK()
        return S_ERROR("You are not allowed to split the request")

    def __moveChildDeep(self, requestID, masterID, setParent, connection):
        """Update parent for this request if setParent is True and update master
        for this and all subrequests."""
        if setParent:
            updates = "ParentID=%s,MasterID=%s" % (str(masterID), str(masterID))
        req = "UPDATE ProductionRequests "
        req += "SET %s " % updates
        req += "WHERE RequestID=%s" % requestID
        result = self._update(req, connection)
        if not result["OK"]:
            return result
        req = "SELECT RequestID,MasterID "
        req += "FROM ProductionRequests as t "
        req += "WHERE t.ParentID=%s" % requestID
        result = self._query(req, connection)
        if not result["OK"]:
            return result
        for ch in result["Value"]:
            if ch[1]:
                ret = self.__moveChildDeep(ch[0], masterID, False, connection)
                if not ret["OK"]:
                    gLogger.error("_moveChildDeep: can not move to %s: %s" % (str(masterID), ret["Message"]))
                # !!! Failing that will leave both requests inconsistant !!!
                # But since we have only one subrequest level now, it will never happened
        return S_OK()

    def splitProductionRequest(self, requestID, splitlist, creds):
        """Fully duplicate master production request with its history and
        reassociate first level subrequests from splitlist (with there subrequest
        structure).

        Substructures can not be moved. Only experts in appropriate request
        state can request the split.
        """
        try:
            requestID = int(requestID)
        except ValueError:
            return S_ERROR("RequestID is not a number")
        if not splitlist:
            return S_ERROR("Split list is empty")
        isplitlist = []
        try:
            isplitlist = [int(x) for x in splitlist]
        except ValueError:
            return S_ERROR("RequestID in split list is not a number")

        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        result = self.__getRequest(requestID, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        rec = result["Value"]

        # Check that operation is valid
        if rec["MasterID"]:
            self.lock.release()
            return S_ERROR("Can not duplicate subrequest of request in progress")
        result = self.__checkAuthorizeSplit(rec["RequestState"], creds)
        if not result["OK"]:
            self.lock.release()
            return result
        req = "SELECT RequestID,MasterID "
        req += "FROM ProductionRequests as t "
        req += "WHERE t.ParentID=%s" % requestID
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        fisplitlist = []
        keeplist = []
        for ch in result["Value"]:
            if ch[0] in isplitlist and ch[1] == requestID:
                fisplitlist.append(int(ch[0]))
            elif ch[1]:
                keeplist.append(int(ch[0]))
        if len(isplitlist) != len(fisplitlist):
            self.lock.release()
            return S_ERROR("Requested for spliting subrequests are no longer exist")
        if not keeplist:
            self.lock.release()
            return S_ERROR("You have to keep at least one subrequest")

        # Now copy the master
        recl = [rec[x] for x in self.requestFields[1:-7]]
        result = self._fixedEscapeValues(recl, 24)
        if not result["OK"]:
            self.lock.release()
            return result
        recls = result["Value"]
        req = "INSERT INTO ProductionRequests ( " + ",".join(self.requestFields[1:-7])
        req += " ) VALUES ( %s );" % ",".join(recls)
        result = self._update(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        req = "SELECT LAST_INSERT_ID();"
        result = self._query(req, connection)
        if not result["OK"]:
            self.lock.release()
            return result
        newRequestID = int(result["Value"][0][0])

        # Move subrequests (!! Errors are not fatal !!)
        rsplitlist = []
        for x in fisplitlist:
            if self.__moveChildDeep(x, newRequestID, True, connection)["OK"]:
                rsplitlist.append(x)
        # If nothing could be moved, remove the master
        if not rsplitlist:
            req = "DELETE FROM ProductionRequests "
            req += "WHERE RequestID=%s" % str(newRequestID)
            result = self._update(req, connection)
            self.lock.release()
            return S_ERROR("Could not move subrequests")

        # Copy the history (failures are not fatal since
        # it is hard to revert the previous changes...)
        req = "SELECT " + ",".join(self.historyFields) + " FROM RequestHistory WHERE RequestID=%s " % requestID
        req += "ORDER BY TimeStamp"
        result = self._query(req, connection)
        if not result["OK"]:
            gLogger.error(
                "SplitProductionRequest: can not get history for %s: %s" % (str(requestID), result["Message"])
            )
        else:
            for x in result["Value"]:
                x = list(x)
                x[0] = newRequestID
                ret = self._update(
                    "INSERT INTO RequestHistory ("
                    + ",".join(self.historyFields)
                    + ") VALUES ( %s,'%s','%s','%s')" % tuple([str(y) for y in x]),
                    connection,
                )
            if not ret["OK"]:
                gLogger.error("SplitProductionRequest: add history fail: %s", ["Message"])

        self.lock.release()
        return S_OK(newRequestID)

    progressFields = ["ProductionID", "RequestID", "Used", "BkEvents"]

    def getProductionProgress(self, requestID):
        """return the list of associated productions requestID must be Long and
        already checked."""
        req = "SELECT * FROM ProductionProgress WHERE RequestID=%s" % requestID
        result = self._query(req)
        if not result["OK"]:
            return result

        rows = [dict(zip(self.progressFields, row)) for row in result["Value"]]
        total = len(rows)
        return S_OK({"Rows": rows, "Total": total})

    def addProductionToRequest(self, pdict):
        """Associate production to request.

        Existence of request is checked first.
        TODO: check requestState
        """
        try:
            for x in self.progressFields:
                pdict[x] = int(pdict[x])
        except ValueError:
            return S_ERROR("Bad parameters")

        self.lock.acquire()  # transaction begin ?? may be after connection ??
        result = self._getConnection()
        if not result["OK"]:
            self.lock.release()
            return S_ERROR("Failed to get connection to MySQL: " + result["Message"])
        connection = result["Value"]

        result = self.__getStateAndAuthor(pdict["RequestID"], connection)
        if not result["OK"]:
            self.lock.release()
            return result
        # requestState, requestAuthor, requestInform = result['Value']

        req = "INSERT INTO ProductionProgress ( "
        req += ",".join(self.progressFields)
        req += " ) VALUES ( "
        req += ",".join([str(pdict[x]) for x in self.progressFields])
        req += " )"
        result = self._update(req, connection)
        self.lock.release()
        if not result["OK"]:
            return result
        return S_OK(pdict["ProductionID"])

    def removeProductionFromRequest(self, productionID):
        """Deassociate production."""
        req = "DELETE FROM ProductionProgress "
        req += "WHERE ProductionID=%s" % str(productionID)
        result = self._update(req)
        if not result["OK"]:
            return result
        return S_OK(productionID)

    def useProductionForRequest(self, productionID, used):
        """Deassociate production."""
        used = int(used)
        req = "UPDATE ProductionProgress "
        req += "SET Used=%s " % str(used)
        req += "WHERE ProductionID=%s" % str(productionID)
        result = self._update(req)
        if not result["OK"]:
            return result
        return S_OK(productionID)

    def getRequestHistory(self, requestID):
        """return the list of state changes for the requests requestID must be Long
        and already checked."""
        req = "SELECT " + ",".join(self.historyFields)
        req += " FROM RequestHistory WHERE RequestID=%s " % requestID
        req += "ORDER BY TimeStamp"
        result = self._query(req)
        if not result["OK"]:
            return result

        rows = [dict(zip(self.historyFields, row)) for row in result["Value"]]
        total = len(rows)
        return S_OK({"Rows": rows, "Total": total})

    def getTrackedProductions(self):
        """return a list of all productions associated with requests in 'Active' or
        'Completed' state."""
        req1 = "SELECT RequestID FROM ProductionRequests WHERE RequestState in ('Active','Completed')"
        req2 = "SELECT RequestID FROM ProductionRequests WHERE RequestState in ('Active','Completed')"
        req2 += " OR MasterID in (%s)" % req1
        req = "SELECT ProductionID FROM ProductionProgress WHERE RequestID "
        req += "in (%s)" % req2

        result = self._query(req)
        if not result["OK"]:
            return result
        values = [row[0] for row in result["Value"]]
        return S_OK(values)

    def updateTrackedProductions(self, update):
        """update tracked productions."""
        # check parameters
        try:
            for x in update:
                x["ProductionID"] = int(x["ProductionID"])
                x["BkEvents"] = int(x["BkEvents"])
        except ValueError:
            return S_ERROR("Bad parameters")
        except TypeError:
            return S_ERROR("Parameters not defined")

        for x in update:
            result = self._update(
                "UPDATE ProductionProgress "
                + "SET BkEvents=%s " % x["BkEvents"]
                + "WHERE ProductionID=%s" % x["ProductionID"]
            )
            if not result["OK"]:
                gLogger.info("Problem in updating progress. Not fatal: %s" % result["Message"])
        return S_OK("")

    def __trackedInputSQL(self, fields):
        req = "SELECT %s " % fields
        req += "FROM ProductionRequests as t WHERE"
        req += ' t.RequestState in ("Active","Completed")'
        req += " AND NumberOfEvents<0 "
        return self._query(req)

    def getTrackedInput(self):
        """return a list of all requests with dynamic input in 'Active' or
        'Completed' states."""

        fields = ",".join(["t." + x for x in self.requestFields[:-7]])
        result = self.__trackedInputSQL(fields)
        if not result["OK"]:
            return result
        rec = []
        for x in result["Value"]:
            res = dict(zip(self.requestFields[:-7], x))
            if res["SimCondDetail"]:
                res.update(json.loads(res["SimCondDetail"]))
            else:
                continue
            del res["SimCondDetail"]
            try:
                num = int(res["RealNumberOfEvents"])
            except ValueError:
                num = 0
            except TypeError:
                num = 0
            if num > 0:
                continue
            rec.append(res)
        return S_OK(rec)

    def updateTrackedInput(self, update):
        """update real number of input events."""
        # check parameters
        try:
            for x in update:
                x["RequestID"] = int(x["RequestID"])
                x["RealNumberOfEvents"] = int(x["RealNumberOfEvents"])
        except ValueError:
            return S_ERROR("Bad parameters")
        except TypeError:
            return S_ERROR("Parameters not defined")
        result = self.__trackedInputSQL("RequestID")
        if not result["OK"]:
            return result
        allowed = dict.fromkeys([x[0] for x in result["Value"]], None)
        skiped = []
        for x in update:
            if not x["RequestID"] in allowed:
                skiped.append(x["RequestID"])
                continue
            req = "UPDATE ProductionRequests "
            req += "SET RealNumberOfEvents=%s " % str(x["RealNumberOfEvents"])
            req += "WHERE RequestID=%s" % str(x["RequestID"])
            result = self._update(req)
            if not result["OK"]:
                skiped.append(x["RequestID"])
        if skiped:
            return S_ERROR("updateTrackedInput has skiped requests %s" % ",".join(skiped))
        return S_OK("")

    def getProductionList(self, requestID):
        """return a list of all productions associated with the request or any its
        subrequest."""
        req1 = "SELECT RequestID FROM ProductionRequests WHERE MasterID=%s" % requestID
        req = "SELECT ProductionID FROM ProductionProgress WHERE RequestID "
        req += "in (%s) OR RequestID=%s" % (req1, requestID)

        result = self._query(req)
        if not result["OK"]:
            return result

        gLogger.info(result["Value"])

        values = [row[0] for row in result["Value"]]
        return S_OK(values)

    def getAllSubRequestSummary(self, status="", rType=""):
        """return a dictionary containing a summary for each subrequest."""
        req = "SELECT RequestID,ParentID,RequestType,RequestState,NumberOfEvents FROM ProductionRequests"
        if status and rType:
            req = "%s WHERE RequestState = '%s' AND RequestType = '%s'" % (req, status, rType)
        elif status:
            req = "%s WHERE RequestState = '%s'" % (req, status)
        elif rType:
            req = "%s WHERE RequestType = '%s'" % (req, rType)
        res = self._query(req)
        if not res["OK"]:
            return res
        sRequestInfo = {}
        for sRequestID, parentID, tReq, status, reqEvents in res["Value"]:
            if not parentID:
                parent = 0
            sRequestInfo[sRequestID] = {"Master": parent, "RequestType": tReq, "Status": status, "ReqEvents": reqEvents}
        return S_OK(sRequestInfo)

    def getAllProductionProgress(self):
        """return a dictionary containing for each requestID the active productions
        and the number of events."""
        req = "SELECT RequestID, ProductionID, Used, BkEvents FROM ProductionProgress;"
        res = self._query(req)
        if not res["OK"]:
            return res
        sRequestInfo = {}
        for sRequestID, prodID, used, events in res["Value"]:
            if sRequestID not in sRequestInfo:
                sRequestInfo[sRequestID] = {}
            sRequestInfo[sRequestID][prodID] = {"Used": used, "Events": events}
        return S_OK(sRequestInfo)

    def getFilterOptions(self):
        """Return the dictionary with possible values for filter."""
        opts = {}
        for key, value in [
            ("State", "RequestState"),
            ("Type", "RequestType"),
            ("Author", "RequestAuthor"),
            ("EType", "EventType"),
            ("WG", "RequestWG"),
        ]:

            req = "SELECT DISTINCT %s FROM ProductionRequests " % value
            req += "WHERE %s IS NOT NULL " % value
            req += "ORDER BY %s" % value
            res = self._query(req)
            if not res["OK"]:
                return res
            opts[key] = [row[0] for row in res["Value"]]
        return S_OK(opts)
