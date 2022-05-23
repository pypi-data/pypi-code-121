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
"""Just couple utilities."""
import os
import sqlite3

import DIRAC
from DIRAC import gConfig, gLogger
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getUserOption, getUsersInGroup
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
from DIRAC.ConfigurationSystem.Client import PathFinder


def _getMemberMails(group):
    """get members mails."""
    members = getUsersInGroup(group)
    if members:
        emails = []
        for user in members:
            email = getUserOption(user, "Email")
            if email:
                emails.append(email)
        return emails


def _aggregate(reqId, reqType, reqWG, reqName, SimCondition, ProPath, groups, informPeoples):
    cacheFile = os.path.join(DIRAC.rootPath, "work/ProductionManagement/cache.db")

    with sqlite3.connect(cacheFile) as conn:

        try:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS ProductionManagementCache(
                    reqId VARCHAR(64) NOT NULL,
                    reqType VARCHAR(64) NOT NULL,
                    reqWG VARCHAR(64) DEFAULT "",
                    reqName VARCHAR(64) NOT NULL,
                    SimCondition VARCHAR(64) DEFAULT "",
                    ProPath VARCHAR(64) DEFAULT "",
                    thegroup VARCHAR(64) DEFAULT "",
                    reqInform VARCHAR(64) DEFAULT ""
                   );"""
            )

        except sqlite3.OperationalError:
            gLogger.error("Email cache database is locked")

        for group in groups:
            conn.execute(
                "INSERT INTO ProductionManagementCache (reqId, reqType, reqWG, reqName,\
             SimCondition, ProPath, thegroup, reqInform)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (reqId, reqType, reqWG, reqName, SimCondition, ProPath, group, informPeoples),
            )

            conn.commit()


def informPeople(rec, oldstate, state, author, inform):
    """inform utility."""

    if not state or state == "New":
        return  # was no state change or resurrect

    reqId = rec["RequestID"]
    csS = PathFinder.getServiceSection("ProductionManagement", "ProductionRequest")
    if not csS:
        gLogger.error("No ProductionRequest section in configuration")
        return

    fromAddress = gConfig.getValue("%s/fromAddress" % csS, "")
    if not fromAddress:
        gLogger.error("No fromAddress is defined in CS path %s/fromAddress" % csS)
        return
    sendNotifications = gConfig.getValue("%s/sendNotifications" % csS, "Yes")
    if sendNotifications != "Yes":
        gLogger.info("No notifications will be sent")
        return

    footer = "\n\nNOTE: This is an automated notification."
    footer += " Please do not reply.\n"

    footer += "DIRAC Web portal: https://lhcb-portal-dirac.cern.ch/DIRAC/s:%s/g:" % PathFinder.getDIRACSetup()

    ppath = "/?view=tabs&url_state=1|*LHCbDIRAC.ProductionRequestManager.classes.ProductionRequestManager:,\n\n"

    ppath += "The request details:\n"
    ppath += "  Type: %s" % str(rec["RequestType"])
    ppath += "  Name: %s\n" % str(rec["RequestName"])
    ppath += "  Conditions: %s\n" % str(rec["SimCondition"])
    ppath += "  Processing pass: %s\n" % str(rec["ProPath"])

    gLogger.info(".... %s ...." % ppath)

    authorMail = getUserOption(author, "Email")
    if authorMail:
        if state not in ["BK Check", "Submitted"]:
            if state == "BK OK":
                subj = "DIRAC: please resign your Production Request %s" % reqId
                body = "\n".join(
                    [
                        "Customized Simulation Conditions in your request was registered. ",
                        "Since the Bookkeeping expert could make changes in your request, ",
                        "you are asked to confirm it.",
                    ]
                )
            else:
                subj = "DIRAC: the state of Production Request %s is changed to '%s'; %s;%s" % (
                    reqId,
                    state,
                    rec.get("RequestWG", ""),
                    rec.get("RequestName", ""),
                )
                body = "\n".join(["The state of your request is changed. ", "This mail is for information only."])
            notification = NotificationClient()
            res = notification.sendMail(authorMail, subj, body + footer + "lhcb_user" + ppath, fromAddress, True)
            if not res["OK"]:
                gLogger.error("_inform_people: can't send email: %s" % res["Message"])

    if inform:
        subj = "DIRAC: the state of %s Production Request %s is changed to '%s'; %s;%s" % (
            rec["RequestType"],
            reqId,
            state,
            rec.get("RequestWG", ""),
            rec.get("RequestName", ""),
        )
        body = "\n".join(["You have received this mail because you are " "in the subscription list for this request"])
        for x in inform.replace(" ", ",").split(","):
            if x:
                if x.find("@") > 0:
                    eMail = x
                else:
                    eMail = getUserOption(x, "Email")
                if eMail:
                    notification = NotificationClient()
                    res = notification.sendMail(eMail, subj, body + footer + "lhcb_user" + ppath, fromAddress, True)
                    if not res["OK"]:
                        gLogger.error("_inform_people: can't send email: %s" % res["Message"])

    if state == "Accepted":
        subj = "DIRAC: the Production Request %s is accepted; %s;%s" % (
            reqId,
            rec.get("RequestWG", ""),
            rec.get("RequestName", ""),
        )
        body = "\n".join(
            ["The Production Request is signed and ready to process. ", "You are informed as member of %s group"]
        )
        groups = ["lhcb_prmgr"]

        for group in groups:
            for man in _getMemberMails(group):
                notification = NotificationClient()
                res = notification.sendMail(man, subj, body % group + footer + group + ppath, fromAddress, True)
                if not res["OK"]:
                    gLogger.error("_inform_people: can't send email: %s" % res["Message"])

    elif state == "PPG OK" and oldstate == "Accepted":
        subj = "DIRAC: returned Production Request %s; %s;%s" % (
            reqId,
            rec.get("RequestWG", ""),
            rec.get("RequestName", ""),
        )
        body = "\n".join(
            [
                "Production Request is returned by Production Manager. ",
                "As member of %s group, you are asked to correct and sign ",
                "or to reject it.",
                "",
                "In case some other member of the group has already ",
                "done that, please ignore this mail.",
            ]
        )
        groups = ["lhcb_tech"]

        for group in groups:
            for man in _getMemberMails(group):
                notification = NotificationClient()
                res = notification.sendMail(man, subj, body % group + footer + group + ppath, fromAddress, True)
                if not res["OK"]:
                    gLogger.error("_inform_people: can't send email: %s" % res["Message"])

    elif state == "BK Check":

        groups = ["lhcb_bk"]

        _aggregate(
            reqId,
            rec.get("RequestType", ""),
            rec.get("RequestWG", ""),
            rec.get("RequestName", ""),
            rec["SimCondition"],
            rec["ProPath"],
            groups,
            rec.get("reqInform", inform),
        )

    elif state == "Submitted":

        groups = ["lhcb_ppg", "lhcb_tech"]
        _aggregate(
            reqId,
            rec.get("RequestType", ""),
            rec.get("RequestWG", ""),
            rec.get("RequestName", ""),
            rec["SimCondition"],
            rec["ProPath"],
            groups,
            rec.get("reqInform", inform),
        )

    else:
        return
