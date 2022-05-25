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
:mod: UserStorageQuotaAgent

.. module: UserStorageQuotaAgent

:synopsis: UserStorageQuotaAgent obtains the usage by each user from the StorageUsageDB
  and compares with a quota present in the CS.
"""
from DIRAC import gConfig, S_OK
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB import StorageUsageDB
from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient

AGENT_NAME = "DataManagement/UserStorageQuotaAgent"


class UserStorageQuotaAgent(AgentModule):
    """.. class:: UserStorageQuotaAgent.

    :param int deafultQuota: default quota in MB
    :param NotificationClient notificationClient: NotificationClient instance
    :param LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB.StorageUsageDB storageUsageDB:
           StorageUsageDB or RPC client pointing to StorageUsageDB
    """

    defaultQuota = 1000
    notificationClient = None
    storageUsageDB = None

    def __init__(self, *args, **kwargs):
        """c'tor."""
        AgentModule.__init__(self, *args, **kwargs)

        self.notificationClient = NotificationClient()
        try:
            self.storageUsageDB = StorageUsageDB()
        except SystemExit:
            self.storageUsageDB = StorageUsageClient()

        self.defaultQuota = gConfig.getValue("/Registry/DefaultStorageQuota", self.defaultQuota)  # Default is 1TB

    def initialize(self):
        """agent initialisation.

        :param self: self reference
        """
        # This sets the Default Proxy to used as that defined under
        # /Operations/Shifter/DataManager
        # the shifterProxy option in the Configuration can be used to change this default.
        self.am_setOption("shifterProxy", "DataManager")

        self.log.info("initialize: Default quota found to be %d GB" % self.defaultQuota)
        return S_OK()

    def execute(self):
        """execution of one cycle.

        :param self: self reference
        """
        res = self.storageUsageDB.getUserStorageUsage()
        usageDict = res["Value"]

        byteToGB = 1000 * 1000 * 1000.0

        managerMsg = ""
        errorMsg = ""
        self.log.info("Determining quota usage for %s users." % len(usageDict))
        for userName in sorted(usageDict):
            usageGB = usageDict[userName] / byteToGB
            res = gConfig.getOptionsDict("/Registry/Users/%s" % userName)
            if not res["OK"]:
                msg = "Username not found in the CS: %s using %.2f GB" % (userName, usageGB)
                errorMsg += msg + "\n"
                self.log.error(msg)
                continue
            elif "Email" not in res["Value"]:
                msg = "CS does not contain email information for user %s" % userName
                errorMsg += msg + "\n"
                self.log.error(msg)
                continue
            elif "Quota" not in res["Value"]:
                userQuota = float(self.defaultQuota)
            else:
                userQuota = float(res["Value"]["Quota"])
            userMail = res["Value"]["Email"]
            # Different behaviour for 90% exceeded, 110% exceeded and 150% exceeded
            msg = None
            if (1.5 * userQuota) < usageGB:
                msg = "%s is at %d%s of quota %d GB (%.1f GB)." % (
                    userName,
                    (usageGB * 100) / userQuota,
                    "%",
                    userQuota,
                    usageGB,
                )
                self.log.info(msg)
                self.sendBlockedMail(userName, userMail, userQuota, usageGB)
                self.log.info("!!!!!!!!!!!!!!!!!!!!!!!!REMEMBER TO MODIFY THE ACLs and STATUS HERE!!!!!!!!!!!!!!!!!")
            elif (1.0 * userQuota) < usageGB:
                msg = "%s is at %d%s of quota %d GB (%.1f GB)." % (
                    userName,
                    (usageGB * 100) / userQuota,
                    "%",
                    userQuota,
                    usageGB,
                )
                self.log.info(msg)
                self.sendSecondWarningMail(userName, userMail, userQuota, usageGB)
            elif (0.9 * userQuota) < usageGB:
                msg = "%s is at %d%s of quota %d GB (%.1f GB)." % (
                    userName,
                    (usageGB * 100) / userQuota,
                    "%",
                    userQuota,
                    usageGB,
                )
                self.log.info(msg)
                self.sendFirstWarningMail(userName, userMail, userQuota, usageGB)
            if msg:
                managerMsg += msg + "\n"
        if managerMsg or errorMsg:
            if managerMsg:
                managerMsg = (
                    "Mails have been sent to the following list of users "
                    + "being close to or above quota:\n\n"
                    + managerMsg
                )
            if errorMsg:
                managerMsg += "\nThe following errors have been found by the UserStorageQuotaAgent:\n" + errorMsg
            fromAddress = "LHCb Data Manager <lhcb-datamanagement@cern.ch>"
            toAddress = "lhcb-datamanagement@cern.ch"
            self.notificationClient.sendMail(toAddress, "User quota warnings", managerMsg, fromAddress)
        return S_OK()

    def sendFirstWarningMail(self, userName, userMail, quota, usage):
        """first warning email.

        :param self: self reference
        :param str userName: DIRAC user name
        :param str userMail: email address
        :param int quota: default quota
        :param float usage: space currently used
        """
        msgbody = """
This mail has been generated automatically.

You have received this mail because you are approaching your Grid storage usage quota of %s GB.

You are currently using %.1f GB.

Please reduce you usage by removing some files. If you have reduced your usage in the last 24 hours
please ignore this message.

Explanations can be found at https://twiki.cern.ch/twiki/bin/view/LHCb/GridStorageQuota
""" % (
            int(quota),
            usage,
        )
        fromAddress = "LHCb Data Manager <lhcb-datamanagement@cern.ch>"
        subject = "Grid storage use near quota (%s)" % userName
        toAddress = userMail
        self.notificationClient.sendMail(toAddress, subject, msgbody, fromAddress)

    def sendSecondWarningMail(self, userName, userMail, quota, usage):
        """second warning email.

        :param self: self reference
        :param str userName: DIRAC user name
        :param str userMail: email address
        :param int quota: default quota
        :param float usage: space currently used
        """
        msgbody = """
This mail has been generated automatically.

You have received this mail because your Grid storage usage has exceeded your quota of %sGB.

You are currently using %.1f GB.

Please reduce you usage by removing some files. If you have reduced your usage in the last 24 hours
please ignore this message.

Explanations can be found at https://twiki.cern.ch/twiki/bin/view/LHCb/GridStorageQuota
""" % (
            int(quota),
            usage,
        )
        fromAddress = "LHCb Data Manager <lhcb-datamanagement@cern.ch>"
        subject = "Grid storage use over quota (%s)" % userName
        toAddress = userMail
        self.notificationClient.sendMail(toAddress, subject, msgbody, fromAddress)

    def sendBlockedMail(self, userName, userMail, quota, usage):
        """send blocked email.

        :param self: self reference
        :param str userName: DIRAC user name
        :param str userMail: email adress
        :param int quota: default quota
        :param float usage: space used
        """
        msgbody = """
This mail has been generated automatically.

You have received this mail because your Grid storage usage has exceeded your quota of %s GB.

You are currently using %.1f GB.

Your account could soon been given a lower priority and your jobs will run at a lower pace if you
don't create space.
If you have reduced your usage in the last 24 hours please ignore this message.
Explanations can be found at https://twiki.cern.ch/twiki/bin/view/LHCb/GridStorageQuota
""" % (
            int(quota),
            usage,
        )

        fromAddress = "LHCb Data Manager <lhcb-datamanagement@cern.ch>"
        subject = "Grid storage use blocked (%s)" % userName
        toAddress = userMail
        self.notificationClient.sendMail(toAddress, subject, msgbody, fromAddress)
