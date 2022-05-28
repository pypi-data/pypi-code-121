import argparse

import mcddns.provider as provider


class CheckIP(provider.AddressProvider):
    def fetch(self, options: argparse.Namespace) -> str:
        return self.fetch_url(
            "https://domains.google.com/checkip", timeout=options.timeout
        )
