"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from re import findall
from urllib.parse import urlsplit

from lxml import etree

from faraday_plugins.plugins.plugin import PluginXMLFormat
from faraday_plugins.plugins.repo.acunetix.DTO import Acunetix, Scan

__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"


class AcunetixXmlParser:
    """
    The objective of this class is to parse an xml file generated by
    the acunetix tool.

    TODO: Handle errors.
    TODO: Test acunetix output version. Handle what happens if
    the parser doesn't support it.
    TODO: Test cases.

    @param acunetix_xml_filepath A proper xml generated by acunetix
    """

    def __init__(self, xml_output):

        tree = self.parse_xml(xml_output)
        self.acunetix = Acunetix(tree)

    @staticmethod
    def parse_xml(xml_output):
        """
        Open and parse an xml file.

        TODO: Write custom parser to just read the nodes that we need instead
        of reading the whole file.

        @return xml_tree An xml tree instance. None if error.
        """

        try:
            parser = etree.XMLParser(recover=True)
            tree = etree.fromstring(xml_output, parser=parser)
        except SyntaxError as err:
            print(f"SyntaxError: {err}. {xml_output}")
            return None

        return tree


class AcunetixPlugin(PluginXMLFormat):
    """
    Example plugin to parse acunetix output.
    """

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.identifier_tag = "ScanGroup"
        self.id = "Acunetix"
        self.name = "Acunetix XML Output Plugin"
        self.plugin_version = "0.0.1"
        self.version = "9"
        self.framework_version = "1.0.0"
        self.options = None
        self._current_output = None
        self.target = None

    def parseOutputString(self, output):
        """
        This method will discard the output the shell sends, it will read it
        from the xml where it expects it to be present.

        NOTE: if 'debug' is true then it is being run from a test case and the
        output being sent is valid.
        """
        parser = AcunetixXmlParser(output)

        for site in parser.acunetix.scan:
            url_data = self.get_domain(site)
            if not url_data:
                continue
            if url_data.hostname:
                self.old_structure(url_data, site)
            else:
                self.new_structure(site)

    def new_structure(self, site):
        for item in site.reportitems.reportitem:
            if not item.technicaldetails.request:
                self.logger.warning("No request data")
                continue
            request_host = findall('Host: (.*)', item.technicaldetails.request)
            if request_host:
                host = request_host[0]
                url = f'http://{host}'
                url_data = urlsplit(url)
                site_ip = self.resolve_hostname(host)
                h_id = self.createAndAddHost(site_ip, site.os, hostnames=[host])
                s_id = self.createAndAddServiceToHost(
                    h_id,
                    "http",
                    "tcp",
                    ports=['443'],
                    version=site.banner,
                    status='open')
                self.create_vul(item, h_id, s_id, url_data)
            else:
                self.logger.warning("No host in request")

    def old_structure(self, url_data, site: Scan):
        site_ip = self.resolve_hostname(url_data.hostname)
        if url_data.hostname:
            hostnames = [url_data.hostname]
        else:
            hostnames = None
        port = url_data.port or (443 if url_data.scheme == "https" else 80)

        h_id = self.createAndAddHost(site_ip, site.os, hostnames=hostnames)
        s_id = self.createAndAddServiceToHost(
            h_id,
            "http",
            "tcp",
            ports=[port],
            version=site.banner,
            status='open')
        for item in site.reportitems.reportitem:
            self.create_vul(item, h_id, s_id, url_data)

    def create_vul(self, item, h_id, s_id, url_data):
        description = item.description
        if item.affects:
            description += f'\nPath: {item.affects}'
        if item.parameter:
            description += f'\nParameter: {item.parameter}'
        try:
            cve = [item.cvelist.cve.text if item.cvelist.cve else ""]
        except Exception:
            cve = [""]
        self.createAndAddVulnWebToService(
            h_id,
            s_id,
            item.name,
            description,
            website=url_data.hostname,
            severity=item.severity,
            resolution=item.recommendation,
            path=item.affects,
            params=item.parameter,
            request=item.technicaldetails.request,
            response=item.technicaldetails.response,
            ref=[i.url for i in item.references.reference],
            cve=cve)

    @staticmethod
    def get_domain(scan: Scan):
        url = scan.start_url
        if not url.startswith('http'):
            url = f'http://{url}'
        url_data = urlsplit(url)
        if not url_data.scheme:
            url_data = urlsplit(scan.crawler.start_url_attr)
        return url_data


def createPlugin(ignore_info=False, hostname_resolution=True):
    return AcunetixPlugin(ignore_info=ignore_info, hostname_resolution=hostname_resolution)
