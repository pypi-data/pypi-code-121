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
"""LHCbDIRAC.ResourceStatusSystem.Agent.ShiftDBAgent.

ShiftDBAgent.__bases__:
  DIRAC.Core.Base.AgentModule.AgentModule
"""
# FIXME: should add a "DryRun" option to run in certification setup
from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError
import json
import suds.client

from DIRAC import gConfig, S_OK, S_ERROR
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin

AGENT_NAME = "ResourceStatus/ShiftDBAgent"


class ShiftDBAgent(AgentModule):
    """This agent queries the LHCb ShiftDB and gets the emails of each piquet
    Then, populates the eGroup associated
    The e-groups admin should be : lhcb-grid-experiment-egroup-admins
    """

    def __init__(self, *args, **kwargs):

        AgentModule.__init__(self, *args, **kwargs)

        # Members initialization

        # ShiftDB url where to find shifter emails
        self.lbshiftdburl = "https://lbshiftdb.cern.ch/list_email"
        # soap wsdl to access eGroups
        self.wsdl = "https://foundservices.cern.ch/ws/egroups/v1/EgroupsWebService/EgroupsWebService.wsdl"

        self.roles = {}
        self.roleShifters = {}
        self.newShifters = {}

        self.diracAdmin = None

    def initialize(self, *args, **kwargs):
        """Initialize."""

        self.lbshiftdburl = self.am_getOption("lbshiftdburl", self.lbshiftdburl)
        self.wsdl = self.am_getOption("wsdl", self.wsdl)

        self.user = self.am_getOption("user")
        self.passwd = self.am_getOption("password")

        if not (self.user and self.passwd):
            self.log.error("User and/or password for %s not provided" % self.wsdl)
            return S_ERROR("Creds not provided")

        self.diracAdmin = DiracAdmin()

        return S_OK()

    def execute(self):
        """Execution."""

        self.roles = {}
        self.roleShifters = {}
        self.newShifters = {}

        self.log.info("Getting roles from CS")
        roles = self.__getRolesFromCS()
        if not roles["OK"]:
            self.log.error(roles["Message"])
            return roles
        self.log.info("found %s " % ", ".join(roles["Value"]))

        self.log.info("Getting role emails")

        for role, eGroup in roles["Value"].items():

            self.roles[role] = eGroup

            email = self.__getRoleEmail(role)
            if not email["OK"]:
                self.log.error(email["Message"])
                # We do not return, we keep execution to clean old shifters
                email["Value"] = None

            email = email["Value"]
            self.roleShifters[eGroup] = (email, role)

            self.log.info("%s -> %s" % (role, email))

        self.log.info("Setting role emails")
        for eGroup, roleTuple in self.roleShifters.items():

            email, role = roleTuple

            setEmail = self.__setRoleEmail(eGroup, email, role)
            if not setEmail["OK"]:
                self.log.error(setEmail["Message"])

        for newShifterRole, shifterEgroup in self.newShifters.items():

            self.log.info("Notifying role %s" % newShifterRole)
            res = self.__notifyNewShifter(newShifterRole, shifterEgroup)
            if not res["OK"]:
                self.log.error(res["Message"])

        return S_OK()

    def __getRolesFromCS(self):
        """Gets from the CS the roles we want to add to an eGroup.
        Role1 : { eGroup: egroup-blah } in the CS

        returns S_OK( { role1: egroup1, .. } )
        """

        _section = self.am_getModuleParam("section")
        roles = gConfig.getSections("%s/roles" % _section)

        if not roles["OK"]:
            return roles

        eGroups = {}

        for role in roles["Value"]:
            eGroup = gConfig.getValue("%s/roles/%s/eGroup" % (_section, role))
            if eGroup:
                eGroups[role] = eGroup
                self.log.debug("Found %s : %s " % (role, eGroup))

        return S_OK(eGroups)

    def __getRoleEmail(self, role):
        """Get role email from shiftDB."""

        try:
            web = urlopen(self.lbshiftdburl, timeout=60)
        except URLError as e:
            return S_ERROR("Cannot open URL: %s, erorr %s" % (self.lbshiftdburl, e))

        emailperson = []

        for line in web.readlines():
            for item in json.loads(line):
                if role in item["role"]:
                    # There are three shifts per day, so we take into account what time is it
                    # before sending the email.
                    emailperson = item["email"]
                    self.log.info(emailperson)
                    return S_OK(emailperson)

        return S_ERROR("Email not found")

    def __setRoleEmail(self, eGroup, email, role):
        """Set email in eGroup."""

        client = suds.client.Client(self.wsdl, username=self.user, password=self.passwd)

        try:
            wgroup = client.service.FindEgroupByName(eGroup)
        except suds.WebFault as wError:
            return S_ERROR(wError)

        members = []
        lastShifterEmail = []
        lastShifterList = {}

        if hasattr(wgroup, "warnings"):
            if wgroup.warnings != []:
                self.log.warn(wgroup.warnings)
        #  return S_ERROR(wgroup.warnings)
        if hasattr(wgroup, "error"):
            if wgroup.error != []:
                self.log.error(wgroup.error)
        if hasattr(wgroup, "result") and hasattr(wgroup.result, "Members"):
            for members in wgroup.result.Members:
                lastShifterEmail.append(members.Email)
                lastShifterList[members.Email] = members

        if email is None:
            self.log.warn("None email. Keeping previous one till an update is found.")
            return S_OK()

        #    if lastShifterEmail.strip().lower() == email.strip().lower():
        #      self.log.info( "%s has not changed as shifter, no changes needed" % email )
        #      return S_OK()

        for lastShifter in lastShifterEmail:
            if email.count(lastShifter) == 0:
                self.log.info("%s is not anymore shifter, deleting ..." % lastShifter)
                try:
                    # The last boolean flag is to overwrite
                    client.service.RemoveEgroupMembers(eGroup, lastShifterList[lastShifter])
                except suds.WebFault as wError:
                    return S_ERROR(wError)

        # Adding a member means it will be the only one in the eGroup, as it is overwritten
        if email != []:
            res = self.__addMember(email, client, eGroup)
            self.log.info(email)
            if not res["OK"]:
                self.log.error(res["Message"])
                return res
            self.log.info("%s added successfully to the eGroup for role %s" % (email, role))

        self.newShifters[role] = eGroup

        return S_OK()

    def __addMember(self, email, client, wgroup):
        """Adds a new member to the group."""

        # Clear e-Group before inserting anything
        # self.__deleteMembers( client, wgroup )

        self.log.info("Adding member %s to eGroup %s" % (email, wgroup))

        members = []
        newmember = client.factory.create("ns0:MemberType")
        newmember.Type = "External"
        newmember.Email = email

        members.append(newmember)

        try:
            # The last boolean flag is to overwrite
            self.log.info(members)
            client.service.AddEgroupMembers(wgroup, True, members)
        except suds.WebFault as wError:
            return S_ERROR(wError)
        return S_OK()

    def __notifyNewShifter(self, role, eGroup):
        """Sends an email to the shifter ( if any ) at the beginning of the shift
        period."""

        if role == "Production":
            body = __productionBody__
        else:
            self.log.info("No email body defined for %s role" % role)
            return S_OK()

        prodRole = self.roles["Production"]
        geocRole = self.roles["Grid Expert"]
        body = body % (self.roleShifters[prodRole][0], self.roleShifters[geocRole][0])

        # Hardcoded Concezio's email to avoid dirac@mail.cern.ch be rejected by smtp server
        res = self.diracAdmin.sendMail(
            "%s@cern.ch" % eGroup, "Shifter information", body, fromAddress="concezio.bozzi@cern.ch"
        )
        return res


__productionBody__ = """Dear GEOC,

this is an (automatic) mail to welcome you on the grid operations shifts.
In order to facilitate your shift activities we wanted to provide you some pointers,
where you could find more information about shifts, the activities and your duties during this period.

http://lhcb-shifters.web.cern.ch/


LHCbDIRAC portal
https://lhcb-portal-dirac.cern.ch/DIRAC


The logbook for LHCb operations, where all activities concerning offline operation are being logged.
https://lblogbook.cern.ch/Operations/
"""
