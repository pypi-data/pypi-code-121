"""
Napalm driver for ArubaOS 505 Wi-Fi Device using SSH.
Read https://napalm.readthedocs.io for more information.
"""

from napalm.base import NetworkDriver
from sshFRIEND.ssh_connector import ssh_connector, send_cmd

SECONDS = 1
MINUTE_SECONDS = 60
HOUR_SECONDS = 3600
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS


def show_version_sanitizer(data):
    """ Collects the vendor, model, os version and uptime from the 'show version'
    :returns a tuple with two values (vendor, model, os version, uptime)
    """

    # Initialize the vars to zero
    (years, weeks, days, hours, minutes, seconds) = (0, 0, 0, 0, 0, 0)

    vendor = "Hewlett Packard"
    model = ""
    os_version = ""
    uptime = ""

    if data:
        data_l = data.strip().splitlines()
        for l in data_l:
            if "MODEL" in l:
                temp_data = l.replace("(", "").replace(")", "")
                temp_model, temp_version = temp_data.split(",")
                if "MODEL:" in temp_model:
                    t = str(temp_model).split()[-1]
                    if t:
                        model = t
                if "Version" in temp_version:
                    v = str(temp_version).split()[-1]
                    if v:
                        os_version = v
            if "AP uptime is" in l:
                tmp_uptime = l.replace("AP uptime is", "").split()
                uptimes_records = [int(i) for i in tmp_uptime if i.isnumeric()]
                if uptimes_records:
                    weeks, days, hours, minutes, seconds = uptimes_records
                    uptime = sum([
                        (years * YEAR_SECONDS),
                        (weeks * WEEK_SECONDS),
                        (days * DAY_SECONDS),
                        (hours * HOUR_SECONDS),
                        (minutes * MINUTE_SECONDS),
                        (seconds * SECONDS), ])
    return vendor, model, os_version, uptime


def show_summary_sanitizer(data):
    """ Collects the fqdn and the serial number from the 'show summary'
        :returns a tuple with two values (hostname, fqdn, serial_number)
        """
    fqdn = ""
    serial_number = ""
    hostname_ = ""

    if data:
        data_l = data.strip().splitlines()
        for l in data_l:
            if "Name" in l and not hostname_:
                hostname_ = f"{l.split(':')[1].lower()}"
            if "DNSDomain" in l and hostname_:
                fqdn = f"{hostname_}.{l.split(':')[1]}"
            if "Serial Number" in l:
                serial_number = l.split(':')[1]
    return hostname_, fqdn, serial_number


class ArubaOS505(NetworkDriver):
    """Napalm driver for ArubaOS 505 Wi-Fi Device."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Initializer."""

        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.channel = None
        self.session_info = None
        self.isAlive = False
        if not optional_args:
            optional_args = {}

        if not self.channel:
            self.channel = ssh_connector(hostname=self.hostname, username=self.username, password=self.password)

    def open(self):
        """
        Implementation of NAPALM method 'open' to open a connection to the device.
        """
        try:
            self.session_info = self.channel
            self.isAlive = True
            print(f"connected to ---  {self.hostname}\n\n")
        except ConnectionError as error:
            # Raised if device not available
            # raise ConnectionException(str(error))
            print(f"Failed to connect to {self.hostname}\n\n")

    def close(self):
        """
        Implementation of NAPALM method 'close'. Closes the connection to the device and does
        the necessary cleanup.
        """
        self.isAlive = False
        self.channel.close()
        self.session_info.close()

    def is_alive(self):
        """
        Implementation of NAPALM method 'is_alive'. This is used to determine if there is a
        pre-existing connection that must be closed.
        :return: Returns a flag with the state of the connection.
        """
        return {"is_alive": self.isAlive}

    def get_config(self, retrieve="all", full=False, sanitized=False):
        """
        :return: The object returned is a dictionary with a key for each configuration store:
            - running(string) - Representation of the  running configuration
        """

        configs = {
            "running": "",
            "startup": "No Startup",
            "candidate": "No Candidate"
        }

        if retrieve.lower() in ('running', 'all'):
            command = "show running-config"
            try:
                if self.channel:
                    ...
            except Exception as e:
                print(f"Failed to interact with: {self.hostname} \n")
                print(e)
            else:
                self.isAlive = True
                output = send_cmd(command, self.channel)
                configs['running'] = output

                data = str(configs['running']).split("\n")
                non_empty_lines = [line for line in data if line.strip() != ""]

                string_without_empty_lines = ""
                for line in non_empty_lines:
                    string_without_empty_lines += line + "\n"
                configs['running'] = string_without_empty_lines
                # self.channel.close()
                self.close()
        if retrieve.lower() in ('startup', 'all'):
            ...

        return configs

    def get_facts(self):
        """Return a set of facts from the devices."""
        if not self.channel:
            self.channel = ssh_connector(hostname=self.hostname, username=self.username, password=self.password)
            self.session_info = self.channel
            self.isAlive = True

        configs = {}
        show_summary = "show summary"
        show_version = "show version"

        try:
            if self.channel: ...
        except:
            print(f"Failed to interact with: {self.hostname} \n")
        else:
            summary_output = send_cmd(show_summary, self.channel)
            self.channel2 = ssh_connector(hostname=self.hostname, username=self.username, password=self.password)
            self.isAlive = True
            show_version_output = send_cmd(show_version, self.channel2)

            # processing 'show summary' output
            configs['running_'] = summary_output
            data = str(configs['running_']).split("\n")
            non_empty_lines = [line for line in data if line.strip() != ""]
            string_without_empty_lines = ""
            for line in non_empty_lines:
                string_without_empty_lines += line + "\n"
            hostname_, fqdn_, serial_number_ = show_summary_sanitizer(string_without_empty_lines)

            # processing 'show version' output
            configs['show_version'] = show_version_output
            show_version_data = str(configs['show_version']).split("\n")
            show_version_non_empty_lines = [line for line in show_version_data if line.strip() != ""]
            show_version_string_without_empty_lines = ""
            for line in show_version_non_empty_lines:
                show_version_string_without_empty_lines += line + "\n"

            vendor, model, os_version, uptime = show_version_sanitizer(
                show_version_string_without_empty_lines)

            if self.channel:
                self.channel.close()
            self.channel2.close()
            self.close()
            return {
                "hostname": str(hostname_),
                "fqdn": fqdn_,
                "vendor": str(vendor),
                "model": str(model),
                "serial_number": str(serial_number_),
                "os_version": str(os_version),
                "uptime": uptime,
            }


    def get_lldp_neighbors__(self):
        """IOS implementation of get_lldp_neighbors."""
        lldp = {}
        neighbors_detail = self.get_lldp_neighbors_detail()
        for intf_name, entries in neighbors_detail.items():
            lldp[intf_name] = []
            for lldp_entry in entries:
                hostname = lldp_entry["remote_system_name"]
                # Match IOS behaviour of taking remote chassis ID
                # When lacking a system name (in show lldp neighbors)
                if hostname == "N/A":
                    hostname = lldp_entry["remote_chassis_id"]
                lldp_dict = {"port": lldp_entry["remote_port"], "hostname": hostname}
                lldp[intf_name].append(lldp_dict)

        return lldp


    def get_lldp_neighbors(self):
        """IOS implementation of get_lldp_neighbors."""
        lldp = {'Ethernet2': [{'hostname': 'junos-unittest1','port': '520',}]}

        return lldp


    # def get_environment(self):
    #     environment = {}
    #     environment.setdefault("cpu", {})
    #     environment["cpu"][0] = {}
    #
    #     environment.setdefault("memory", {})
    #     environment["memory"]["used_ram"] = "dummy data"
    #
    #     # Initialize 'power' and 'fan' to default values (not implemented)
    #     environment.setdefault("power", {})
    #     environment["power"]["invalid"] = {
    #         "status": True,
    #         "output": -1.0,
    #         "capacity": -1.0,
    #     }
    #     environment.setdefault("fans", {})
    #     environment["fans"]["invalid"] = {"status": True}
    #
    #     return environment
