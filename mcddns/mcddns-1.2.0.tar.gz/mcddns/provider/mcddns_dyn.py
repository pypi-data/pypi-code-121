import argparse
import re

import mcddns.provider as provider


class CheckIP(provider.AddressProvider):
    def fetch(self, options: argparse.Namespace) -> str:
        html = self.fetch_url("http://checkip.dyndns.com/", timeout=options.timeout)
        pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        matches = re.search(pattern, str(html), re.ASCII)
        return matches[0] if matches else ""
