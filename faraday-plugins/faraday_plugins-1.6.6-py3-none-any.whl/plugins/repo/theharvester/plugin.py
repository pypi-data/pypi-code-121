"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from faraday_plugins.plugins.plugin import PluginBase
import re



__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"


class TheharvesterParser:
    """
    The objective of this class is to parse an xml file generated by the theharvester tool.

    TODO: Handle errors.
    TODO: Test theharvester output version. Handle what happens if the parser doesn't support it.
    TODO: Test cases.

    @param theharvester_filepath A proper simple report generated by theharvester
    """

    def __init__(self, output):

        self.items = []
        _hosts, _vhosts = [], []

        mregex = re.search(
            r"\[\+\] Hosts found in search engines:[-=\s]+([\w\W]*)\[\+\]", output)
        if mregex is None:
            mregex = re.search(
                "\\[\\+\\] Hosts found in search engines:[-=\\s]+([\\w\\W]*)\n", output)
        mregex2 = re.search("\\[\\+\\] Virtual hosts:[-=\\s]+([\\w\\W]*)\n", output)

        if mregex is None and mregex2 is None:
            return

        if mregex:
            _hosts = mregex.group(1).strip().split("\n")
        if mregex2:
            _vhosts = mregex2.group(1).strip().split("\n")

        for line in _hosts:

            info = line.split(":")

            if len(info) > 1:
                item = {'host': info[1].strip(), 'ip': info[0].strip()}

                self.items.append(item)

        for line in _vhosts:

            info = line.split()
            if len(info) > 1:
                item = {'host': info[1].strip(), 'ip': info[0].strip()}

                self.items.append(item)


class TheharvesterPlugin(PluginBase):
    """
    Example plugin to parse theharvester output.
    """

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.id = "Theharvester"
        self.name = "Theharvester XML Output Plugin"
        self.plugin_version = "0.0.1"
        self.version = "2.2a"
        self.options = None
        self._current_output = None
        self._current_path = None
        self._command_regex = re.compile(
            r'^(sudo theHarvester\.py|theHarvester\.py|python theHarvester\.py|\.\/theHarvester\.py)\s+.*?')
        self._completition = {
            "": "Examples:./theharvester.py -d microsoft.com -l 500 -b google",
            "-d": "Domain to search or company name",
            "-b": "Data source (google,bing,bingapi,pgp,linkedin,google-profiles,exalead,all)",
            "-s": "Start in result number X (default 0)",
            "-v": "Verify host name via dns resolution and search for vhosts(basic)",
            "-l": "Limit the number of results to work with(bing goes from 50 to 50 results,",
            "-f": "Save the results into an XML file",
            "-n": "Perform a DNS reverse query on all ranges discovered",
            "-c": "Perform a DNS brute force for the domain name",
            "-t": "Perform a DNS TLD expansion discovery",
            "-e": "Use this DNS server",
            "-h": "use SHODAN database to query discovered hosts. google 100 to 100, and pgp doesn't use this option)",
        }


    def parseOutputString(self, output):
        """
        This method will discard the output the shell sends, it will read it from
        the xml where it expects it to be present.
        """
        parser = TheharvesterParser(output)
        for item in parser.items:
            host = []
            if item['host'] != item['ip']:
                host = [item['host']]
            h_id = self.createAndAddHost(item['ip'], hostnames=host)
        del parser



def createPlugin(ignore_info=False, hostname_resolution=True):
    return TheharvesterPlugin(ignore_info=ignore_info, hostname_resolution=hostname_resolution)
