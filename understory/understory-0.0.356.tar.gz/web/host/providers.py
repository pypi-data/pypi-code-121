"""
Supported machine hosts and domain registrars.

Supported hosts: DigitalOcean, Linode, Hetzner
Supported registrars: Dynadot, Name.com

"""

import time

import lxml.etree
import requests


class TokenError(Exception):
    """Bad auth token."""


class DomainExistsError(Exception):
    """Domain already exists."""


class Provider:
    """A service provider."""

    def __init__(self, token=None):
        """Store the access token."""
        self.token = token


class Host(Provider):
    """A machine host."""


class Registrar(Provider):
    """A domain registrar."""


class DigitalOcean(Host):
    """
    [DigitalOcean][0] client.

    [0]: https://digitalocean.com

    """

    endpoint = "https://api.digitalocean.com/v2"

    def __init__(self, token):
        """Set up authenticated session."""
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"
        super().__init__(token)

    def get_keys(self):
        """Return all SSH keys."""
        return self._request("get", "account/keys")

    def add_key(self, name, key_data):
        """Add an SSH key."""
        return self._request(
            "post", "account/keys", json={"name": name, "public_key": key_data}
        )["ssh_key"]

    @property
    def machines(self):
        """Return all machines."""
        machines = []
        for machine in self._request("get", "droplets")["droplets"]:
            machine.pop("region")
            machines.append(machine)
        return machines

    def create_machine(
        self,
        name,
        region="sfo2",
        size="s-1vcpu-1gb",
        image="debian-11-x64",
        ssh_keys=None,
    ):
        """Create a machine."""
        machine_id = self._request(
            "post",
            "droplets",
            json={
                "name": name,
                "region": region,
                "size": size,
                "image": image,
                "ssh_keys": ssh_keys,
            },
        )["droplet"]["id"]
        while (
            self._request("get", f"droplets/{machine_id}/actions")["actions"][0][
                "status"
            ]
            == "in-progress"
        ):
            time.sleep(1)
        return self.get_machine(machine_id)["droplet"]

    def get_machine(self, machine_id):
        """Get a machine."""
        return self._request("get", f"droplets/{machine_id}")

    def delete_machine(self, machine_id):
        """Delete a machine."""
        return self._request("delete", f"droplets/{machine_id}")

    def _request(self, method, path, **kwargs):
        return getattr(self.session, method)(f"{self.endpoint}/{path}", **kwargs).json()


class Linode(Host):
    """
    [Linode][0] client.

    [0]: https://linode.com

    """


class Hetzner(Host):
    """
    [Hetzner][0] client.

    [0]: https://hetzner.com

    """


class Dynadot(Registrar):
    """
    [Dynadot][0] client.

    [0]: https://dynadot.com

    """

    endpoint = "https://api.dynadot.com/api3.xml"

    @property
    def domains(self):
        """List currently registered domains."""
        response = self._request("list_domain")
        domains = []
        for domain in response.cssselect("Domain"):
            name = domain.cssselect("Name")[0].text
            expiration = domain.cssselect("Expiration")[0].text
            domains.append((name, expiration))
        return sorted(domains)

    def create_record(self, domain, record, subdomain=""):
        """Set DNS record for given domain."""
        # TODO set low ttl
        command = "set_dns2"
        record_type = "a"
        if subdomain:
            return self._request(
                command,
                domain=domain,
                main_record_type0=record_type,
                main_record0=record,
                subdomain0=subdomain,
                sub_record_type0=record_type,
                sub_record0=record,
            )
        return self._request(
            command, domain=domain, main_record_type0=record_type, main_record0=record
        )

    def search(self, *domains):
        """Search for available of domains."""
        domain_params = {
            "domain{}".format(n): domain for n, domain in enumerate(domains)
        }
        response = self._request(show_price="1", **domain_params)
        results = {}
        for result in response:
            # if len(result[0]) == 5:
            # data = {"price": result[0][4].text}
            # results[result[0][1].text] = data
            available = False if result[0].find("Available").text == "no" else True
            price = result[0].find("Price")
            if price is None:
                price = 0
            else:
                if " in USD" in price.text:
                    price = float(price.text.partition(" ")[0])
                else:
                    price = "?"
            results[result[0].find("DomainName").text] = (available, price)
        return results

    def register(self, domain, duration=1):
        """Register domain."""
        return self._request("register", domain=domain, duration=duration)

    def account_info(self):
        """Return account information."""
        return self._request("account_info")[1][0]

    def _request(self, command, **payload):
        """Send an API request."""
        payload.update(command=command, key=self.token)
        response = requests.get(self.endpoint, params=payload)
        message = lxml.etree.fromstring(response.text)
        try:
            if message.cssselect("ResponseCode")[0].text == "-1":
                print(response.text)
                raise TokenError()
        except IndexError:
            pass
        return message


class NameCom(Registrar):
    """
    [Name.com][0] client.

    [0]: https://name.com

    """

    endpoint = "https://api.name.com"

    def __init__(self, username=None, token=None):
        """Store the username."""
        self.username = username
        super().__init__(token)

    def list_domains(self):
        """List currently registered domains."""
        return [
            (domain["domainName"], domain["expireDate"])
            for domain in self._request("get", "domains")["domains"]
        ]

    def create_record(self, domain, record, subdomain=""):
        """
        Set DNS record for given domain.

        https://www.name.com/api-docs/DNS#CreateRecord

        """
        return self._request(
            "post",
            f"domains/{domain}/records",
            host=subdomain,
            type="A",
            answer=record,
            ttl="300",
        )

    def _request(self, method, command, **payload):
        """Send an API request."""
        post_body = {}
        if payload:
            post_body = {"json": payload}
        response = getattr(requests, method)(
            f"{self.endpoint}/v4/{command}",
            auth=(self.username, self.token),
            headers={"Content-Type": "application/json"},
            **post_body,
        )
        return response.json()
