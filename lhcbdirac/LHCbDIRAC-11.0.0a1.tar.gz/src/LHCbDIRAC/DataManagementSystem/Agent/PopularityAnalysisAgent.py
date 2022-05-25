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
"""
:mod: PopularityAnalysisAgent

.. module: PopularityAnalysisAgent

:synopsis: The PopularityAnalysis Agent generates the popularity CSV file, sends it for analysis to the
           Yandex data popularity service, and sends the result by email
"""
# imports
import os
import json
import csv
import datetime

from requests import post

# # from DIRAC
from DIRAC import S_OK
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.Mail import Mail

from LHCbDIRAC.DataManagementSystem.Client.ScanPopularity import scanPopularity

AGENT_NAME = "DataManagement/PopularityAnalysisAgent"


class FakeException(Exception):
    """Fake exception to drive the error handling."""

    pass


class PopularityAnalysisAgent(AgentModule):
    """
    .. class:: PopularityAnalysisAgent
    """

    def __init__(self, *args, **kwargs):
        """c'tor."""

        super(PopularityAnalysisAgent, self).__init__(*args, **kwargs)

        # Default number of days to analyze
        self.analysisPeriod = 910

        # Top directory to analyze
        self.topDirectory = "/lhcb"

        # address of the DataPopularity server
        self.dataPopularityURL = "http://localhost:5000"

        # Mail address to use as report sender
        self.mailSender = None

        # Mail address to send the report to
        self.mailRecipients = ["lhcb-datamanagement@cern.ch"]

        # Enable sending the email
        self.mailEnabled = True

        # target space saved (in TB)
        self.savedSpaceTarget = 100

        # Min number of replicas
        self.minReplicas = 1

        # Max number of replicas
        self.maxReplicas = 7

        # Placeholder to keep the start date
        self.startDate = None

    def initialize(self):
        """agent initialisation."""

        self.workDirectory = self.am_getOption("WorkDirectory")  # pylint: disable=attribute-defined-outside-init

        self.log.info("Working directory: %s" % self.workDirectory)
        if not os.path.isdir(self.workDirectory):
            os.makedirs(self.workDirectory)

        self.analysisPeriod = self.am_getOption("AnalysisPeriod", self.analysisPeriod)
        self.log.info("Analysis period: %s" % self.analysisPeriod)

        self.topDirectory = self.am_getOption("TopDirectory", self.topDirectory)
        self.log.info("Top directory: %s" % self.topDirectory)

        self.mailSender = self.am_getOption("MailSender", self.mailSender)
        self.log.info("Mail sender: %s" % self.mailSender)

        self.mailRecipients = self.am_getOption("MailRecipients", self.mailRecipients)
        self.log.info("Mail recipients: %s" % self.mailRecipients)

        self.mailEnabled = self.am_getOption("MailEnabled", self.mailEnabled)
        self.log.info("Mail enabled: %s" % self.mailEnabled)

        self.dataPopularityURL = self.am_getOption("DataPopularityURL", self.dataPopularityURL)
        self.log.info("Data Popularity URL: %s" % self.dataPopularityURL)

        self.savedSpaceTarget = self.am_getOption("SavedSpaceTarget", self.savedSpaceTarget)
        self.log.info("Data Popularity URL: %s" % self.savedSpaceTarget)

        self.minReplicas = self.am_getOption("MinReplicas", self.minReplicas)
        self.log.info("Min Replicas: %s" % self.minReplicas)

        self.maxReplicas = self.am_getOption("MaxReplicas", self.maxReplicas)
        self.log.info("Max Replicas: %s" % self.maxReplicas)

        return S_OK()

    def execute(self):
        """Main loop of Popularity agent.

        We first trigger the generation of the csv file which contains all the
        popularity and datasets data.

        We then send it to the Yandex data popularity service, and receive a csv file back.

        We merge the two files into an html human readable file.

        We send the html and the Yandex report by email
        """

        self.startDate = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M")

        popularityFile = os.path.join(self.workDirectory, "popularity_%s.csv" % self.startDate)
        csvReportFile = os.path.join(self.workDirectory, "popularityAnalysis_%s.csv" % self.startDate)

        scanPopularity(self.analysisPeriod, True, topDirectory=self.topDirectory, csvFile=popularityFile)

        params = json.dumps(
            {"n_tb": self.savedSpaceTarget, "min_replicas": self.minReplicas, "max_replicas": self.maxReplicas}
        )
        errorMail = None
        try:
            postResult = post(self.dataPopularityURL, files={"file": open(popularityFile)}, data={"params": params})
            if postResult.status_code != 200:
                errorMail = {"status_code": postResult.status_code, "reason": postResult.reason}
                raise FakeException()
            with open(csvReportFile, "w") as report:
                report.write(postResult.content)

            htmlReportFile = self._generateHtmlReport(popularityFile, csvReportFile)

        except FakeException as e:
            pass
        except Exception as e:  # pylint: disable=broad-except
            self.log.exception("Exception generating the reports", lException=e)
            errorMail = {"status_code": 0, "reason": "Exception generating the reports %s" % repr(e)}
        finally:
            if self.mailEnabled:
                if not errorMail:
                    self._sendReport([csvReportFile, htmlReportFile])
                else:
                    self._sendErrorMail(errorMail)

        return S_OK()

    def _generateHtmlReport(self, popularityFile, inputCsvFile):
        """Generate a report, html formated.

        args:
            popularityFile (str): path to the popularity csv file
            inputCsvFile (str): report of the analysis

        returns:
            path to the html report file
        """

        htmlReportFile = os.path.join(self.workDirectory, "popularityAnalysis_%s.html" % self.startDate)

        html_string = """
              <!DOCTYPE html>
               <html>
               <head>
               <meta charset='UTF-8'>
                 <style>
                   table{
                      color:#333;
                      font-family:Helvetica,Arial,sans-serif;
                      min-width:700px;
                      border-collapse:collapse;
                      border-spacing:0
                   }
                   td,th{
                      border:1px solid ;
                      height:30px;
                      transition:all .3s;
                      padding: 15px;
                      padding-top: 0px;
                      padding-bottom: 0px
                   }
                   th{
                      background:#DFDFDF;
                      font-weight:700
                   }
                   td{
                      background:#FAFAFA;
                      text-align:center
                   }
                   tr:nth-child(even) td{background:#F1F1F1}tr:nth-child(odd)
                   td{background:#FEFEFE}tr td:hover{background:#666;color:#FFF}
                 </style>
               </head>
               <body>
                 <table>
                   <tr>
                     <th>Name</th>
                     <th>Size</th>
                     <th>Current Replicas</th>
                     <th>Recommended number of disk replicas</th>
                     <th>Archived</th>
                   </tr>
    """

        archivedDataset = set()

        with open(popularityFile, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                if row["Nb ArchReps"] >= 1:
                    archivedDataset.add(row["Name"])

        with open(inputCsvFile, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")

            for row in reader:
                row.pop("")
                dsName = row.pop("Name")
                dsSize = row.pop("LFNSize")
                dsReplicas = row.pop("Nb_Replicas")
                dsDecrease = row.pop("DecreaseReplicas")

                line_str = (
                    "<tr>"
                    + "<td>"
                    + "<a title='"
                    + "&#10;".join([":".join(t) for t in row.items()])
                    + "'>"
                    + dsName
                    + "</a></td>"
                    + "<td>"
                    + str(dsSize)
                    + "</td>"
                    + "<td>"
                    + str(dsReplicas)
                    + "</td>"
                    + "<td>"
                    + str(dsDecrease)
                    + "</td>"
                    + "<td>"
                    + str(dsName in archivedDataset)
                    + "</td>"
                    + "</tr>\n"
                )

                html_string += line_str

        html_string += "</table></body></html>"

        with open(htmlReportFile, "w") as ht:
            ht.write(html_string)

        return htmlReportFile

    # pylint: disable=protected-access
    def _sendReport(self, listOfFiles):
        """Send the reports by email.

        args:
            listOfFiles (list): list of files to be sent
        """

        mail = Mail()
        mail._subject = "Popularity report %s" % self.startDate
        mail._message = " Popularity report %s" % self.startDate
        mail._attachments = listOfFiles
        mail._mailAddress = self.mailRecipients
        if self.mailSender:
            mail._fromAddress = self.mailSender
        mail._send()

    # pylint: disable=protected-access
    def _sendErrorMail(self, errorMail):
        """Send the reports by email.

        args:
            errorMail : Error to report
        """

        mail = Mail()
        mail._subject = "Error popularity report %s" % self.startDate
        mail._message = "Error Popularity report %s: %s" % (self.startDate, errorMail)
        mail._mailAddress = self.mailRecipients
        if self.mailSender:
            mail._fromAddress = self.mailSender
        mail._send()
