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
"""NotifyAgent This agent reads a cache file ( cache.db ) which contains the
aggregated information of what happened to each production request. After
reading the cache file ( by default every 30 minutes ) it sends an email for
every site and then clears it.

Please note that this agent is a hybrid agent that sends aggregated emails for both
LHCbDIRAC.ProductionManagementSystem.Utilities.Utils.informPeople and
LHCbDIRAC.ProductionManagementSystem.Agent.ProductionStatusAgent._mailProdManager
"""
import os
import sqlite3
import DIRAC
from DIRAC import gConfig, S_OK
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin
from DIRAC.ConfigurationSystem.Client import PathFinder
from LHCbDIRAC.ProductionManagementSystem.Utilities.Utils import _getMemberMails

AGENT_NAME = "ProductionManagement/NotifyAgent"


class NotifyAgent(AgentModule):
    def __init__(self, *args, **kwargs):

        super(NotifyAgent, self).__init__(*args, **kwargs)

        self.diracAdmin = None
        self.csS = None
        self.fromAddress = None
        self.cacheFile = os.path.join(DIRAC.rootPath, "work/ProductionManagement/cache.db")

    def initialize(self):
        """NotifyAgent initialization."""

        try:
            with sqlite3.connect(self.cacheFile) as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS ProductionManagementCache(
                      reqId VARCHAR(64) NOT NULL DEFAULT "",
                      reqType VARCHAR(64) NOT NULL DEFAULT "",
                      reqWG VARCHAR(64) NOT NULL DEFAULT "",
                      reqName VARCHAR(64) NOT NULL DEFAULT "",
                      SimCondition VARCHAR(64) NOT NULL DEFAULT "",
                      ProPath VARCHAR(64) NOT NULL DEFAULT "",
                      thegroup VARCHAR(64) NOT NULL DEFAULT "",
                      reqInform VARCHAR(64) NOT NULL DEFAULT ""
                     );"""
                )
        except sqlite3.OperationalError:
            self.log.error("Email cache database is locked")

        self.diracAdmin = DiracAdmin()

        self.csS = PathFinder.getServiceSection("ProductionManagement", "ProductionRequest")

        self.fromAddress = gConfig.getValue("%s/fromAddress" % self.csS, "")
        if not self.fromAddress:
            self.log.info("No fromAddress is defined, a default value will be used instead")
            self.fromAddress = "vladimir.romanovsky@cern.ch"

        return S_OK()

    def execute(self):

        if not os.path.isfile(self.cacheFile):
            self.log.error(self.cacheFile + " does not exist.")
            return S_OK()

        with sqlite3.connect(self.cacheFile) as conn:
            if not self.csS:
                self.log.error("No ProductionRequest section in configuration")
                return S_OK()
            self._executeForProductionManagementSystem(conn)
            self._executeForProductionStatusAgent(conn)

        return S_OK()

    def _executeForProductionManagementSystem(self, conn):
        """This is for the ProductionManagementSystem's Utilities"""
        aggregated_body = """\
          <!DOCTYPE html>
          <html>
          <head>
          <meta charset='UTF-8'>
            <style>
              table{color:#333;font-family:Helvetica,Arial,sans-serif;min-width:850px;border-collapse:collapse;border-spacing:0}
              td,th{border:1px solid transparent;height:30px;transition:all .3s}th{background:#DFDFDF;font-weight:700}
              td{background:#FAFAFA;text-align:center}tr:nth-child(even) td{background:#F1F1F1}tr:nth-child(odd)
              td{background:#FEFEFE}tr td:hover{background:#666;color:#FFF}tr td.link:hover{background:inherit;}
              p{width: 850px;}
            </style>
          </head>
          <body>
          """

        result = conn.execute(
            "SELECT DISTINCT thegroup, reqName, reqWG, reqInform, reqType from ProductionManagementCache;"
        )
        for thegroup, reqName, reqWG, reqInform, reqType in result:
            link = (
                "https://lhcb-portal-dirac.cern.ch/DIRAC/s:"
                + PathFinder.getDIRACSetup()
                + "/g:"
                + thegroup
                + "/?view=tabs&url_state=1|*LHCbDIRAC.ProductionRequestManager.classes.ProductionRequestManager:"
            )

            aggregated_body = ""
            html_elements = ""

            # Skip if group is empty
            if not thegroup:
                continue
            # Only ask people to act on MC requests
            if reqType != "Simulation":
                continue

            if thegroup == "lhcb_bk":
                header = (
                    "New Productions are requested and they have customized Simulation Conditions. "
                    "As member of <span style='color:green'>" + thegroup + "</span> group, you are asked either to "
                    "register new Simulation conditions or to reject the requests. In case some other member of the "
                    "group has already done that, please ignore this mail.\n"
                )

            elif thegroup == "lhcb_ppg":
                header = (
                    "New Productions are requested. As member of <span style='color:green'>" + thegroup + "</span> "
                    "group, you are asked either to sign or to reject it. In case some other member of the group has "
                    "already done that, please ignore this mail.\n"
                )
            else:
                header = (
                    "As member of <span style='color:green'>"
                    + thegroup
                    + "</span> group, your are asked to review the below requests.\n"
                )

            cursor = conn.execute(
                "SELECT reqId, reqType, reqWG, reqName, SimCondition, ProPath from ProductionManagementCache "
                "WHERE thegroup = ? and reqName=? and reqWG=? and reqType=? ",
                (thegroup, reqName, reqWG, reqType),
            )

            for row_reqId, row_reqType, row_reqWG, row_reqName, row_SimCondition, row_ProPath in cursor:
                html_elements += (
                    "<tr>"
                    + "<td>"
                    + row_reqId
                    + "</td>"
                    + "<td>"
                    + row_reqName
                    + "</td>"
                    + "<td>"
                    + row_reqType
                    + "</td>"
                    + "<td>"
                    + row_reqWG
                    + "</td>"
                    + "<td>"
                    + row_SimCondition
                    if row_SimCondition
                    else "" + "</td>" + "<td>" + row_ProPath
                    if row_ProPath
                    else ""
                    + "</td>"
                    + "<td class='link'><a href='"
                    + link
                    + "' target='_blank'> Link </a></td>"
                    + "</tr>"
                )

            # If there are no requests to display, don't bother sending emails
            if not html_elements:
                continue

            aggregated_body += """\
        <p>{header}</p>
        <table>
          <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Working Group</th>
              <th>Conditions</th>
              <th>Processing pass</th>
              <th>Link</th>
          </tr>
          {html_elements}
        </table>
      </body>
      </html>
      """.format(
                header=header, html_elements=html_elements
            )

            if reqInform:
                for emailaddress in reqInform.split(","):
                    res = self.diracAdmin.sendMail(
                        emailaddress,
                        "Notifications for production requests - Group %s; %s; %s" % (thegroup, reqWG, reqName),
                        aggregated_body,
                        self.fromAddress,
                        html=True,
                    )

            for people in _getMemberMails(thegroup):
                res = self.diracAdmin.sendMail(
                    people,
                    "Notifications for production requests - Group %s; %s; %s" % (thegroup, reqWG, reqName),
                    aggregated_body,
                    self.fromAddress,
                    html=True,
                )

                if res["OK"]:
                    conn.execute("DELETE FROM ProductionManagementCache;")
                else:
                    self.log.error("_inform_people: can't send email: %s" % res["Message"])

    def _executeForProductionStatusAgent(self, conn):
        """This is for the ProductionStatusAgent"""

        aggregated_body = """\
          <!DOCTYPE html>
          <html>
          <head>
          <meta charset='UTF-8'>
            <style>
              table{color:#333;font-family:Helvetica,Arial,sans-serif;min-width:700px;border-collapse:collapse;border-spacing:0}
              td,th{border:1px solid transparent;height:30px;transition:all .3s}th{background:#DFDFDF;font-weight:700}
              td{background:#FAFAFA;text-align:center}.setup{font-size:150%;color:grey}.Active{color:green}
              .Archived,.Cleaned,.Cleaning{color:gray}.Completed{color:purple}.Idle{color:#90ee90}.Stopped{color:orange}
              .Testing,.TransformationCleaned{color:gray}tr:nth-child(even) td{background:#F1F1F1}
              tr:nth-child(odd) td{background:#FEFEFE}tr td:hover{background:#666;color:#FFF}
            </style>
          </head>
          <body>
          """

        cursor = conn.execute("SELECT production, from_status, to_status, time from ProductionStatusAgentCache;")

        # Check if the results are non-empty
        if cursor.rowcount == 0:
            return S_OK()

        html_elements = ""
        for production, from_status, to_status, time in cursor:
            html_elements += (
                "<tr>"
                + "<td>"
                + production
                + "</td>"
                + "<td class='"
                + from_status
                + "'>"
                + from_status
                + "</td>"
                + "<td class='"
                + to_status
                + "'>"
                + to_status
                + "</td>"
                + "<td>"
                + time
                + "</td>"
                + "</tr>"
            )
        if html_elements:
            aggregated_body += """\
      <p class="setup">Transformations updated</p>
      <table>
        <tr>
            <th>Production</th>
            <th>From</th>
            <th>To</th>
            <th>Time</th>
        </tr>
        {html_elements}
      </table>
        """.format(
                html_elements=html_elements
            )

        cursor = conn.execute("SELECT prod_requests, time from ProductionStatusAgentReqCache;")

        # Check if the results are non-empty
        if cursor.rowcount == 0:
            return S_OK()

        html_elements = ""
        for prod_requests, time in cursor:
            html_elements += "<tr>" + "<td>" + prod_requests + "</td>" + "<td>" + time + "</td>" + "</tr>"

        if html_elements:
            aggregated_body += """\
        <br />
        <p class="setup">Production Requests updated to Done status</p>
        <table>
          <tr>
              <th>Production Requests</th>
              <th>Time</th>
          </tr>
          {html_elements}
        </table>
      </body>
      </html>
      """.format(
                html_elements=html_elements
            )

        aggregated_body += """\
      </body>
      </html>
      """

        res = self.diracAdmin.sendMail(
            "vladimir.romanovsky@cern.ch",
            "Transformation Status Updates",
            aggregated_body,
            "vladimir.romanovsky@cern.ch",
            html=True,
        )

        if not res["OK"]:
            self.log.error("Can't send email: %s" % res["Message"])
            return S_OK()

        conn.execute("DELETE FROM ProductionStatusAgentCache;")
        conn.commit()
        conn.execute("VACUUM;")

        conn.execute("DELETE FROM ProductionStatusAgentReqCache;")
        conn.commit()
        conn.execute("VACUUM;")
