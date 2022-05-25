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
"""LHCbDIRAC.ResourceStatusSystem.Agent.NagiosTopologyAgent.

NagiosTopologyAgent.__bases__: DIRAC.Core.Base.AgentModule.AgentModule

xml_append
"""
import os
import time
import xml.dom.minidom
import json
import socket

from six.moves.urllib.request import urlopen
from DIRAC import S_OK, rootPath, gLogger, gConfig
from DIRAC.ConfigurationSystem.Client.Helpers.Resources import getSites
from DIRAC.ConfigurationSystem.Client.Helpers.Path import cfgPath
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from DIRAC.Resources.Storage.StorageElement import StorageElement

AGENT_NAME = "ResourceStatus/NagiosTopologyAgent"


MAPPING_CE_TYPE = {
    "lcg": "CE",
    "cream": "CREAM-CE",
    "arc": "ARC-CE",
    "htcondorce": "HTCONDOR-CE",
    "vac": "VAC",
    "cloud": "CLOUD",
    "boinc": "BOINC",
    "vcycle": "VCYCLE",
    "dirac": "DIRAC",
}


class NagiosTopologyAgent(AgentModule):
    """This agent loops over the Dirac CS and extracts the necessary information
    to create a "topology map" which is used by the IT provided Nagios system to
    test Grid sites. The topology information defines the services to be tested.

    NagiosTopologyAgent, writes the xml topology consumed by Nagios to run
    the tests.
    """

    def __init__(self, *args, **kwargs):

        AgentModule.__init__(self, *args, **kwargs)

        self.xmlPath = "webRoot/www/topology/"
        self.urljson = "http://wlcg-cric.cern.ch/api/core/rcsite/query/?json"

        self.dryRun = False

    def initialize(self):
        """Initialize the agent."""

        self.xmlPath = rootPath + "/" + self.am_getOption("webRoot", self.xmlPath)

        try:
            os.makedirs(self.xmlPath)
        except OSError:
            pass  # The dir exists already, or cannot be created: do nothing

        return S_OK()

    def execute(self):
        """Generates xml and json topology files"""

        res = getSites()
        if not res["OK"]:
            return res
        sites = res["Value"]

        # First, create the JSON topology, which contains also what the XML topology needs
        res = self.createJSONTopology(sites)
        if not res["OK"]:
            self.log.error("Failed to create JSON topology", res["Message"])
            return res
        self.log.info("Created JSON topology")

        res = self.createXMLTopology(sites)
        if not res["OK"]:
            self.log.error("Failed to create XML topology", res["Message"])
            return res
        self.log.info("Created XML topology")

        return S_OK()

    def createJSONTopology(self, sites):
        """Function that creates a topology.json file, based on specification from WLCG group"""

        fullSitesDict = dict()
        for site in sites:
            grid = site.split(".")[0]
            res = gConfig.getOptionsDict("Resources/Sites/%s/%s" % (grid, site))
            if not res["OK"]:
                self.log.error("Failure getting options dict for site", "%s: %s" % (site, res["Message"]))
                continue
            siteInfoCS = res["Value"]
            wlcgName = siteInfoCS.get("Name")

            siteInfo = dict()
            siteInfo["WLCG_site"] = wlcgName
            # Tier level 4 is what they want for opportunistic resource
            siteInfo["Tier"] = siteInfoCS.get("MoUTierLevel", "4")
            siteInfo["Type"] = "GRID" if grid == "LCG" else site.split(".")[0]

            # Services is for CEs and SEs
            siteInfoServices = dict()

            # CEs
            res = gConfig.getSections(cfgPath("Resources", "Sites", grid, site, "CEs"), [])
            if not res["OK"]:
                self.log.error("Failure getting CEs section for site", "%s: %s" % (site, res["Message"]))
                continue
            if not res["Value"]:
                self.log.warn("Site without CEs", "(%s)" % site)
            else:
                cesList = res["Value"]
                for ce in cesList:
                    res = gConfig.getOptionsDict(cfgPath("Resources", "Sites", grid, site, "CEs", ce))
                    if not res["OK"]:
                        self.log.error("Failure getting info on ce", "%s: %s" % (ce, res["Message"]))
                        continue

                    ceDetailsInCS = res["Value"]
                    ceDetails = dict()
                    ceDetails["type"] = "compute"
                    ceDetails["access_points"] = dict()
                    ceDetails["access_points"][ce] = dict()
                    ceDetails["access_points"][ce]["endpoint_url"] = ce
                    ceDetails["access_points"][ce]["type"] = MAPPING_CE_TYPE.get(
                        ceDetailsInCS["CEType"].lower(), "UNDEFINED"
                    )
                    ceDetails["access_points"][ce]["monitored"] = "yes" if wlcgName else "no"
                    ceDetails["access_points"][ce]["quality_level"] = "production"
                    # queues
                    res = gConfig.getSections(cfgPath("Resources", "Sites", grid, site, "CEs", ce, "Queues"), [])
                    if not res["OK"]:
                        self.log.error("Failure getting info on ce/queues", "%s: %s" % (ce, res["Message"]))
                        continue
                    if not res["Value"]:
                        self.log.warn("CE without queues", "(%s)" % ce)
                    else:
                        for queue in res["Value"]:
                            ceDetails["compute_shares"] = dict()
                            ceDetails["compute_shares"][queue] = dict()
                            ceDetails["compute_shares"][queue]["type"] = "queue"
                            ceDetails["compute_shares"][queue]["name"] = queue

                    siteInfoServices[ce] = ceDetails

            # SEs
            ses = gConfig.getValue(cfgPath("Resources", "Sites", grid, site, "SE"), [])
            if not ses:
                pass
            for se in ses:
                diracSE = StorageElement(se)  # this 'se' is .e.g. 'CERN-DST-EOS'
                seDetailsForDIRACSE = dict()
                seStorageSharesForDIRACSE = dict()
                for diracSEoption in diracSE.protocolOptions:

                    # Building the storage_endpoints section
                    seDetails = dict()
                    ep = os.path.join(
                        diracSEoption["Protocol"]
                        + "://"
                        + diracSEoption["Host"].strip("/")
                        + ":"
                        + diracSEoption["Port"],
                        diracSEoption["Path"].strip("/"),
                    )
                    seDetails["endpoint_url"] = ep
                    seDetails["interface_type"] = diracSEoption["Protocol"]
                    seDetails["monitored"] = "yes" if wlcgName else "no"
                    seDetails["quality_level"] = "production"

                    dseep = "_".join([se, diracSEoption["Protocol"]])  # just a unique name e.g. 'CERN-DST-EOS_root'
                    seDetailsForDIRACSE[dseep] = seDetails

                    if diracSEoption.get("SpaceToken"):
                        # Building the storage_shares section
                        seDetails = dict()
                        seDetails["Name"] = diracSEoption["SpaceToken"]
                        seDetails["path"] = diracSEoption["WSUrl"]
                        if diracSEoption["Protocol"].lower() == "srm":
                            seDetails["assigned_endpoints"] = ep

                        dsess = "_".join(
                            [se, diracSEoption["SpaceToken"]]
                        )  # just a unique name e.g. 'CNAF-DST_LHCb-Disk'
                        seStorageSharesForDIRACSE[dsess] = seDetails

                siteInfoServices[se] = dict()
                siteInfoServices[se]["storage_endpoints"] = seDetailsForDIRACSE
                if seStorageSharesForDIRACSE:
                    siteInfoServices[se]["storage_shares"] = seStorageSharesForDIRACSE

                siteInfoServices[se]["type"] = "storage"
                siteInfoServices[se]["quality_level"] = "production"
                siteInfoServices[se]["monitored"] = "yes" if wlcgName else "no"

            siteInfo["Services"] = siteInfoServices
            fullSitesDict[site] = siteInfo

        with open(self.xmlPath + "topology.json", "w") as tj:
            json.dump(fullSitesDict, tj)
            self.log.verbose("JSON topology saved", self.xmlPath + "topology.json")

        return S_OK()

    def createXMLTopology(self, sites):
        """Creates a lhcb_topology_Generated.xml file to be used for Nagios tests

        :params list sites: list of sites (from DIRAC CS)
        """

        # instantiate xml doc
        xml_impl = xml.dom.minidom.getDOMImplementation()
        xml_doc = xml_impl.createDocument(None, "root", None)
        xml_root = xml_doc.documentElement

        # xml header info
        writeHeaderInfo(xml_doc, xml_root)

        # loop over sites
        response = urlopen(self.urljson)
        wlcg = json.loads(response.read())

        organized_list_of_sites = []
        for site in sites:
            grid, real_site_name, country = site.split(".")
            same_site = [s for s in sites if ("." + real_site_name + "." + country) in s]
            organized_list_of_sites = organized_list_of_sites + [same_site]

        for site in organized_list_of_sites:
            site_parameters = getSiteParameters(site, wlcg)

            if site_parameters:

                xml_site = xml_append(
                    xml_doc,
                    xml_root,
                    "atp_site",
                    infrast=site_parameters["Infrastructure"],
                    longitude=site_parameters["Coordinates"].split(":")[0],
                    latitude=site_parameters["Coordinates"].split(":")[1],
                    name=site_parameters["WlcgName"],
                )
                has_grid_elem = False

                dirac_name = site_parameters["DiracName"]
                site_tier = site_parameters["Tier"]
                site_subtier = site_parameters["Sub-Tier"]

                for grid in site_parameters["Grid"]:
                    site = site_parameters["Grid"][grid]["SiteName"]
                    ces = site_parameters["Grid"][grid]["CEs"]
                    # CE info
                    if ces:
                        res = writeCEInfo(xml_doc, grid, xml_site, site, ces)
                        # Update has_grid_elem
                        has_grid_elem = res or has_grid_elem

                # SE info
                if site_parameters["SE"] and (site_tier in ["0", "1", "2"] or site_subtier in ["T2-D"]):
                    # res = self.writeSEInfo( xml_doc, xml_site, dirac_name )
                    res = writeSEInfo(xml_doc, xml_site, dirac_name, site_tier, site_subtier)
                    # Update has_grid_elem
                    has_grid_elem = res or has_grid_elem

                if has_grid_elem:
                    xml_append(xml_doc, xml_site, "group", name="Tier " + site_tier, type="LHCb_Tier")
                    xml_append(xml_doc, xml_site, "group", name=dirac_name, type="LHCb_Site")
                    xml_append(xml_doc, xml_site, "group", name=dirac_name, type="All Sites")
                    xml_append(
                        xml_doc,
                        xml_site,
                        "group",
                        name=dirac_name,
                        type="WLCG_%s" % (site_parameters["FederationAccountingName"]),
                    )
                    xml_append(
                        xml_doc, xml_site, "group", name=dirac_name, type="WLCG_%s" % (site_parameters["Country"])
                    )
                    try:
                        if site_subtier == "T2-D":
                            xml_append(xml_doc, xml_site, "group", name=dirac_name, type="Tier 0/1/2D")
                            xml_append(xml_doc, xml_site, "group", name=dirac_name, type="Tier 2D")
                            xml_append(
                                xml_doc, xml_site, "group", name=dirac_name, type="Tier 2"
                            )  # Mod for T2-D also have T2 tag

                        elif int(site_tier) == 2:
                            xml_append(xml_doc, xml_site, "group", name=dirac_name, type="Tier 2")

                        # site_tier can be only 1 or 0, (see site_tier def above to
                        # convince yourself.)
                        else:
                            # If site_type is None, then we go to the exception.
                            xml_append(xml_doc, xml_site, "group", name=dirac_name, type="Tier 0/1/2D")
                            xml_append(xml_doc, xml_site, "group", name=dirac_name, type="Tier 0/1")

                    except ValueError:  # Site tier is None, do nothing
                        pass

                else:
                    _msg = "Site %s, (WLCG Name: %s) has no CE, SE or LFC, thus will not be put into the xml"
                    _msg = _msg % (site, site_parameters["WlcgName"])
                    self.log.warn(_msg)
                    xml_root.removeChild(xml_site)

        self.dryRun = self.am_getOption("DryRun", self.dryRun)
        if self.dryRun:
            self.log.info("Dry Run: XML file will not be created, just printed")
            print(xml_doc.toxml())

        else:
            # produce the xml
            with open(self.xmlPath + "lhcb_topology_Generated.xml", "w") as xmlf:
                xmlf.write(xml_doc.toxml())

            self.log.info("XML file created Successfully")

        return S_OK()


# Private methods #######################################################


def isHostIPV6(host):
    """Test if the given host is ipv6 capable.

    0:ipv6 capable. 1:ipv4 only. -1:Not a valid host (no DNS record?)
    """
    try:  # First try IPV6
        socket.getaddrinfo(host, None, socket.AF_INET6)
        return 0
    except socket.gaierror:  # No IPv6 address
        try:  # Next try IPv4
            socket.getaddrinfo(host, None, socket.AF_INET)
            return 1
        except socket.gaierror:  # The host does not exist (no IPv6 or IPv4 address)
            return -1


def getSiteParameters(sites, wlcg):
    """Function that returns the sites parameters.

    :param list sites:
      List of sites or single site with same site name (e.g ['LCG.CERN.cern'] or
      [LCG.Manchester.uk, VAC.Manchester.uk])

    :param dict wlcg:
      It's a dictionary with the WLCG parameters from all sites grabbed from
      http://wlcg-cric.cern.ch/api/core/rcsite/query/?json

    Keys:
    'WlcgName', 'Coordinates', 'Description', 'Mail', 'DiracName', 'Tier', 'Sub-Tier',
    'SE', 'Country':, 'Federation', 'FederationAccountingName', 'Infrastructure',
    'Institute Name', 'Grid'

    If the site is not listed in WLCG or have no MoU Tier Level the function will return False
    """

    grid_dict = {}
    grid, real_site_name, country = sites[0].split(".")
    res = gConfig.getOptionsDict("Resources/Sites/%s/%s" % (grid, sites[0]))
    if not res["OK"]:
        gLogger.error("Could not get options", "for site %s: %s" % (sites[0], res["Message"]))
        return False
    site_opts = res["Value"]
    site_name = site_opts.get("Name")  # This is Grid name (the one in GocDB)
    site_tier = site_opts.get("MoUTierLevel")
    if site_tier and site_name:
        wlcg_params = wlcg.get(site_name)
        if not wlcg_params:
            return False
        if len(sites) > 1:
            for i in sites:
                grid = i.split(".")[0]
                res = gConfig.getSections("Resources/Sites/%s/%s/CEs" % (grid, i))
                grid_dict.update({grid: {"SiteName": i, "CEs": res["Value"] if res["OK"] else None}})
        else:
            res = gConfig.getSections("Resources/Sites/%s/%s/CEs" % (grid, sites[0]))
            grid_dict.update({grid: {"SiteName": sites[0], "CEs": res["Value"] if res["OK"] else None}})

        site_subtier = site_opts.get("SubTier", None)
        ses = site_opts.get("SE", None)

        site_params = {
            "WlcgName": site_opts.get("Name"),
            "Coordinates": site_opts.get("Coordinates"),
            "Description": site_opts.get("Description"),
            "Mail": site_opts.get("Mail"),
            "DiracName": ("LCG." + real_site_name + "." + country),
            "Tier": site_tier,
            "Sub-Tier": site_subtier,
            "SE": ses,
            "Country": wlcg_params.get("country"),
            "Federation": wlcg_params.get("federations")[0],
            "FederationAccountingName": wlcg_params.get("federation_accounting_name", site_name),
            "Infrastructure": wlcg_params.get("infrastructure", "EGI"),
            "Institute Name": wlcg_params.get("institute"),
            "Grid": grid_dict,
        }

        return site_params
    else:
        return False


def writeHeaderInfo(xml_doc, xml_root):
    """Writes XML document header."""

    xml_append(xml_doc, xml_root, "title", "LHCb Topology Information for ATP")
    xml_append(
        xml_doc,
        xml_root,
        "description",
        "List of LHCb site names for monitoring and mapping to the SAM/WLCG site names",
    )
    xml_append(
        xml_doc,
        xml_root,
        "feed_responsible",
        dn="/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=roiser/CN=564059/CN=Stefan Roiser",
        name="Stefan Roiser",
    )
    xml_append(xml_doc, xml_root, "last_update", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    xml_append(xml_doc, xml_root, "vo", "lhcb")


def writeCEInfo(xml_doc, grid, xml_site, site, ces):
    """Writes CE information in the XML Document."""

    has_grid_elem = "False"

    for site_ce_name in ces:

        has_grid_elem = True

        # FIXME: use proper helpers
        site_ce_opts = gConfig.getOptionsDict("Resources/Sites/%s/%s/CEs/%s" % (grid, site, site_ce_name))
        if not site_ce_opts["OK"]:
            gLogger.error(site_ce_opts["Message"])
            continue
        site_ce_opts = site_ce_opts["Value"]

        site_ce_type = site_ce_opts.get("CEType")

        xml_ce = xml_append(
            xml_doc,
            xml_site,
            "service",
            hostname=site_ce_name,
            flavour=MAPPING_CE_TYPE.get(site_ce_type.lower(), "UNDEFINED"),
        )

        #   I'll leave this code commented in case it needs to be used in the future,
        #   this function consumes a hell lot of time to return a value that is not
        #   mandatory at the momment
        # ce_batch = ldapCEState(site_ce_name, site_ce_opts['VO'])
        # ce_batch = ce_batch['Value'][0]['GlueCEInfoJobManager'] if (ce_batch['OK'] and ce_batch['Value']) else None

        # ipv6 status of the CE
        i6Status = isHostIPV6(site_ce_name)
        i6Comment = ""
        if i6Status == -1:
            i6Comment = "Maybe DIRAC Service, not a valid machine"
        xml_append(xml_doc, xml_ce, "queues", ipv6_status=str(i6Status), ipv6_comment=i6Comment)

        ce_queues = gConfig.getSections("Resources/Sites/%s/%s/CEs/%s/Queues/" % (grid, site, site_ce_name))
        if not ce_queues["OK"]:
            continue

        ce_queues = ce_queues["Value"]
        for queue in ce_queues:
            queue_information = gConfig.getOptionsDict(
                "Resources/Sites/%s/%s/CEs/%s/Queues/%s" % (grid, site, site_ce_name, queue)
            )
            if queue_information["OK"]:
                queue_information = queue_information["Value"]
                # if queue_information.get('maxCPUTime') > max_CPU:
                #   etf_default = 'True'
                #   max_CPU = queue_information.get('maxCPUTime')

            xml_append(
                xml_doc,
                xml_ce,
                "queues",
                ce_resource=queue,
                # - the following items are already predicter for latter changes if necessary
                # batch_system=ce_batch,
                # queue=queue_information.get('VO'),
                # etf_default=etf_default # => this needs to be fixed, when necessary
                # maxWaitingJobs=queue_information.get('MaxWaitingJobs'),
                # maxCPUTime=queue_information.get('maxCPUTime')
            )
    return has_grid_elem


def writeSEInfo(xml_doc, xml_site, site, site_tier, site_subtier):
    """Writes SE information in the XML Document."""

    def write_SE_XML(site_se_opts):
        """Sub-function just to populate the XML with the SE values."""
        site_se_name = site_se_opts.get("Host")
        site_se_flavour = site_se_opts.get("Protocol")
        site_se_path = site_se_opts.get("Path", "UNDEFINED")
        site_se_endpoint = site_se_opts.get("URLBase")
        mappingSEFlavour = {"srm": "SRMv2", "root": "XROOTD", "http": "HTTPS"}

        xml_se = xml_append(
            xml_doc,
            xml_site,
            "service",
            endpoint=site_se_endpoint,
            flavour=mappingSEFlavour.get(site_se_flavour, "UNDEFINED"),
            hostname=site_se_name,
            path=site_se_path,
        )

        # ipv6 status of the SE
        i6Status = isHostIPV6(site_se_name)
        i6Comment = ""
        if i6Status == -1:
            i6Comment = "Maybe DIRAC Service, not a valid machine"
        xml_append(xml_doc, xml_se, "queues", ipv6_status=str(i6Status), ipv6_comment=i6Comment)

    has_grid_elem = True

    real_site_name = site.split(".")[1]
    dmsHelper = DMSHelpers()

    if int(site_tier) in (0, 1):
        dst = dmsHelper.getSEInGroupAtSite("Tier1-DST", real_site_name)
        raw = dmsHelper.getSEInGroupAtSite("Tier1-RAW", real_site_name)
        if not raw["OK"]:
            gLogger.error(raw["Message"])
            return False
        raw = raw["Value"]
        se_RAW = StorageElement(raw)
        se_plugins_RAW = se_RAW.getPlugins()

    if site_subtier == "T2-D":
        dst = dmsHelper.getSEInGroupAtSite("Tier2D-DST", real_site_name)

    if not dst["OK"]:
        gLogger.error(dst["Message"])
        return False

    dst = dst["Value"]
    se_DST = StorageElement(dst)
    se_plugins_DST = se_DST.getPlugins()
    if not se_plugins_DST["OK"]:
        gLogger.error(se_plugins_DST["Message"])
        return False

    for protocol in se_plugins_DST["Value"]:
        site_se_opts_DST = se_DST.getStorageParameters(protocol)
        if not site_se_opts_DST["OK"]:
            gLogger.error(site_se_opts_DST["Message"])
            return False
        site_se_opts_DST = site_se_opts_DST["Value"]
        write_SE_XML(site_se_opts_DST)

        if int(site_tier) in (0, 1):
            if protocol in se_plugins_RAW["Value"]:
                site_se_opts_RAW = se_RAW.getStorageParameters(protocol)
                if not site_se_opts_RAW["OK"]:
                    gLogger.error(site_se_opts_RAW["Message"])
                    return has_grid_elem
                site_se_opts_RAW = site_se_opts_RAW["Value"]
                # This tests if the DST and RAW StorageElements have the same endpoint.
                # If so it only uses the one already added.
                if site_se_opts_RAW["Host"] != site_se_opts_DST["Host"]:
                    write_SE_XML(site_se_opts_RAW)

    return has_grid_elem


def xml_append(doc, base, elem, cdata=None, **attrs):
    """Given a Document, we append to it an element."""

    new_elem = doc.createElement(elem)
    for attr in attrs:
        new_elem.setAttribute(attr, attrs[attr])
    if cdata:
        new_elem.appendChild(doc.createTextNode(cdata))

    return base.appendChild(new_elem)
