# ----------------------------------------------------------------------------
# Description    : Plug & play/device discovery logic
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import sys
import inspect
import pprint
import socket
import select
import time
import json
import ifaddr
import ipaddress
import uuid
import os
from typing import Tuple, Any, Union, Iterable, Dict


# -- definitions -------------------------------------------------------------

# The UDP port used for plug & play communication.
PNP_PORT = 20801


# -- class -------------------------------------------------------------------

class PlugAndPlay:
    """
    Class that provides device discovery and IP address (re)configuration
    functionality, for instance to convert customer-controlled device names or
    serial numbers to IP addresses we can connect to via the usual interfaces.
    """

    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Creates a plug & play interface object. Use close() when you're done
        with the object, or a ``with`` clause::

            with PlugAndPlay() as p:
                # do stuff with p here
                pass

        Parameters
        ----------

        Raises
        ------
        OSError
            If creating the network socket fails.
        """
        super().__init__()

        # Iterate over all network adapters in the system, and create a
        # broadcast socket for all of them.
        self._socks = []
        self._ips = []
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            # Iterate over each IP address associated with the adapter.
            for ip in adapter.ips:

                try:
                    # Ignore IPv6 addresses, since Qblox PNP is IPv4-only.
                    if ip.is_IPv4:

                        # Create the UDP socket.
                        sock = socket.socket(
                            socket.AF_INET,
                            socket.SOCK_DGRAM,
                            socket.IPPROTO_UDP
                        )

                        # Enable the broadcast flag, so we receive UDP
                        # broadcast packets.
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                        # Bind to the IP address of this interface and to the plug
                        # and play port.
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        sock.bind((ip.ip, PNP_PORT))

                        # Store results.
                        self._socks.append(sock)
                        self._ips.append("{}/{}".format(ip.ip, ip.network_prefix))
                except OSError:
                    # This will catch exception thrown by disabled network
                    # adapters (on Windows).
                    pass

        # Generate a sufficiently random number to use as initial sequence
        # number.
        self._seq = uuid.uuid4().int

    # ------------------------------------------------------------------------
    def close(self):
        """
        Closes the underlying socket. The object must not be used anymore
        after this call.

        Parameters
        ----------

        Returns
        -------
        """
        while self._socks:
            self._socks.pop().close()
            self._ips.pop()

    # ------------------------------------------------------------------------
    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # ------------------------------------------------------------------------
    def _send(self, cmd: str, serial_or_name: str = "") -> str:
        """
        Broadcasts a command over the network to all available interfaces.

        Parameters
        ----------
        cmd: str
            The command to send (second line onwards, i.e. excluding header).
        serial_or_name: str
            If specified, only the device with the given serial number or
            customer-given name should respond to the command. If not
            specified or an empty string, all devices will respond.

        Returns
        -------
        str
            The exact sequence number string that was used for the command.

        Raises
        -------
        OSError
            If enumerating interfaces or packet transmission fails.
        """

        # Create a unique sequence number.
        self._seq += 1
        seq = str(self._seq)

        # Format the message content and sequence number as bytestrings.
        msg = "QBLOXPNPCMD:{}:{}\n{}".format(seq, serial_or_name, cmd)

        # Broadcast the message on all sockets.
        for sock in self._socks:

            # Disable socket timeout, so we block if the OS is for some
            # reason not immediately ready to send the UDP packet.
            sock.settimeout(None)

            # Send to everything.
            sock.sendto(msg.encode("utf-8"), ("255.255.255.255", PNP_PORT))

        # Return the sequence number that we used.
        return seq

    # ------------------------------------------------------------------------
    def _recv(
        self,
        seqs: Iterable[str],
        single: bool = False,
        timeout: float = 1.0
    ) -> Dict[str, Dict[str, Tuple[str, int]]]:
        """
        Waits for the reception of one or more responses to one or more
        commands.

        Parameters
        ----------
        seqs: Iterable[str]
            The sequence number(s) of the commands that were sent, as returned
            by _send().
        single: bool
            When set, only one response is expected for each command. This
            allows the function to terminate once a response has been received
            for all commands. If not set or unspecified, this method will
            always wait for the complete timeout duration, since it cannot
            know how many responses will arrive and when.
        timeout: float
            Timeout in seconds to wait for responses.

        Returns
        -------
        Dict[str, Dict[str, Tuple[str, int]]]
            All responses received. The outer dict maps from command sequence
            number to the set of responses received for that command. The
            inner dict maps from device serial number to a tuple of the
            response received from that device and the index of the socket it
            was received on.

        Raises
        -------
        OSError
            If enumerating interfaces or packet reception fails.
        """

        # Turn the iterable of sequence numbers into a set. If first is set,
        # we'll remove sequence numbers from the set when we receive the first
        # response for that sequence number. We stop when we run out of
        # sequence numbers or the timeout expires. Note that packets received
        # with unknown sequence numbers are ignored, and that if first is set,
        # a sequence number is ignored after the first response is processed.
        seqs = set(seqs)

        # Create an empty response structure to fill.
        responses = {seq: {} for seq in seqs}

        # Determine when the timeout expires.
        stop = time.time() + timeout

        # While we have sequence numbers that we're sensitive to...
        while seqs:

            # Determine how many seconds remain until the timeout expires.
            remain = stop - time.time()

            # Break if the timeout has already expired.
            if remain < 0:
                break

            # Listen for packets until the timeout expires. Note that since
            # we're listening for any broadcast packet, we could be receiving
            # packets from pretty much any protocol here. That's why we impose
            # a size limit, and why we silently ignore packets that don't look
            # like valid responses. We could also receive PNP responses to
            # commands that another host sent, hence the UUID-based sequence
            # number check.
            ready, *_ = select.select(self._socks, [], [], remain)
            if not ready:
                break
            for sock in ready:
                sock.settimeout(None)
                response, address = sock.recvfrom(1024)
                index = self._socks.index(sock)

                # PNP packets are unicode-safe, so we can decode into a regular
                # string for convenience.
                try:
                    response = response.decode("utf-8")
                except UnicodeError:
                    continue

                # Split header (first line) from payload (second line onwards).
                response = response.split("\n", maxsplit=1)
                if len(response) < 2:
                    continue
                recv_hdr, recv_result = response

                # Split header into its components.
                recv_hdr = recv_hdr.split(":")
                if len(recv_hdr) != 3:
                    continue
                recv_magic, recv_seq, recv_serial = recv_hdr

                # The first part of the header must match the magic number for
                # PNP responses.
                if recv_magic != "QBLOXPNPREP":
                    continue

                # The sequence number must be in our set.
                if recv_seq not in seqs:
                    continue

                # Looks like our packet is valid, so record it.
                responses[recv_seq][recv_serial] = (recv_result, index)

                # If we're only expecting one packet per sequence number,
                # remove the sequence number from the sensitivity set.
                if single:
                    seqs.remove(recv_seq)

        # Timeout expired or we received everything we were expecting to
        # receive.
        return responses

    # ------------------------------------------------------------------------
    def _broadcast(
        self,
        cmd: str,
        count: int = 3,
        timeout: float = 1.0
    ) -> Dict[str, Tuple[str, int]]:
        """
        Combines a broadcast transmission with waiting for the corresponding
        responses.

        Parameters
        ----------
        cmd: str
            The command to send.
        count: int
            Number of "retries": the command is sent out this number of times
            to reduce the odds of packet loss hindering device discovery.
        timeout: float
            Timeout in seconds to wait for responses.

        Returns
        -------
        Dict[str, Tuple[str, int]]
            The response received and socket index it was received on for each
            serial number. Note that if multiple *different* responses are
            received for a single serial number, the resulting response in this
            set is arbitrary. It is thus important that serial numbers are
            actually unique in practice.

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        # Send the commands, gathering their sequence numbers.
        seqs = [self._send(cmd) for _ in range(count)]

        # Gather the responses.
        responses = self._recv(seqs, False, timeout)

        # Combine the responses from the various sequence numbers.
        combined = {}
        for response in responses.values():
            combined.update(response)

        return combined

    # ------------------------------------------------------------------------
    def _query(
        self,
        serial_or_name: str,
        cmd: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> Tuple[str, int]:
        """
        Combines a "unicast" transmission (to a single serial number or
        customer-given name) with waiting for the corresponding response.

        Parameters
        ----------
        serial_or_name: str
            The serial number or customer-given name of the device we want to
            address.
        cmd: str
            The command to send.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------
        Tuple[str, int]
            The payload of the received response, and the index of the socket
            it was received on.

        Raises
        -------
        OSError
            If transmission or reception fails.
        TimeoutError
            If there was no response from the device.
        """

        # For each retry...
        for _ in range(retries):

            # Send the command.
            seq = self._send(cmd, serial_or_name)

            # Wait for and retrieve a single response.
            responses = self._recv([seq], True, timeout)[seq]

            # Return the response for the serial number we're interested in,
            # if any.
            if responses:
                return next(iter(responses.values()))

        # Ran out of retries.
        raise TimeoutError(
            "No response from device with serial or name {}".format(serial_or_name)
        )

    # ------------------------------------------------------------------------
    def list_devices(self, timeout: float = 1.0) -> Dict[str, dict]:
        """
        Lists all observable devices on the network.

        Parameters
        ----------
        timeout: float
            Timeout in seconds to wait for responses.

        Returns
        -------
        Dict[str, dict]
            Mapping from serial number to device description record as
            returned by the device. If a device returned an invalid structure,
            its dict will be {}.

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        # Broadcast an echo request to see which serial numbers are visible.
        serials = set(self._broadcast("ECHO", timeout=timeout))

        # Send a describe command to each visible device in parallel.
        seqs = [self._send("DESCRIBE", serial) for serial in serials]
        responses = self._recv(seqs, True)

        # Combine the responses from the various sequence numbers; we can
        # distinguish by means of serial number.
        devices = {}
        for response in responses.values():
            devices.update(response)

        # Parse the JSON structure for each device.
        for serial in devices:
            response, socket = devices[serial]
            try:
                devices[serial] = json.loads(response)
            except json.JSONDecodeError:
                devices[serial] = {}
            devices[serial]["connected_via"] = self._ips[socket]

        return devices

    # ------------------------------------------------------------------------
    def print_devices(self, timeout: float = 1.0) -> None:
        """
        Like list_devices(), but prints a user-friendly device list instead of
        returning a data structure.

        Parameters
        ----------
        timeout: float
            Timeout in seconds to wait for responses.

        Returns
        -------

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        devices = self.list_devices(timeout)
        if not devices:
            print("No devices found")
            return
        print("Devices:")
        for serial, data in sorted(
            devices.items(),
            key=lambda x: x[1].get("identity", {}).get("ip", None)
        ):

            remote_ip = data.get("identity", {}).get("ip", None)
            local_ip_and_prefix = data.get("connected_via", None)
            if remote_ip is None:
                ip_info = "<unknown IP>"
            elif local_ip_and_prefix is None:
                ip_info = remote_ip
            else:
                local_net = ipaddress.IPv4Network(local_ip_and_prefix, strict=False)
                remote_net = ipaddress.IPv4Network("{}/32".format(remote_ip), strict=False)
                if local_net.overlaps(remote_net):
                    ip_info = remote_ip
                else:
                    ip_info = "{} via {} (reconfiguration needed!)".format(
                        remote_ip, local_ip_and_prefix
                    )

            print(' - {}: {} {} with name "{}" and serial number {}'.format(
                ip_info,
                data.get("description", {}).get("model", "<unknown model>"),
                ".".join(
                    map(
                        str,
                        data.get("description", {})
                        .get("sw", {})
                        .get("version", ["?"] * 3),
                    )
                ),
                data.get("description", {}).get("name", "<unknown name>"),
                serial)
            )

    # ------------------------------------------------------------------------
    def identify(
        self,
        serial_or_name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> None:
        """
        Visually identifies the device with the given serial number or
        customer-given name by having it blink its LEDs for a while.

        Parameters
        ----------
        serial_or_name: str
            Serial number of the device that is to be identified.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------

        Raises
        -------
        TypeError
            If serial_or_name is invalid.
        ValueError
            If serial_or_name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        """

        serial_or_name = str(serial_or_name)
        if not serial_or_name:
            raise ValueError("Serial number or name must not be blank")
        response, _ = self._query(serial_or_name, "IDENTIFY", retries, timeout)
        if response != "OK":
            raise RuntimeError("Unexpected response: {}".format(response))

    # ------------------------------------------------------------------------
    def identify_all(self, count: int = 3) -> None:
        """
        Instructs all devices visible on the network to blink their LEDs.

        Parameters
        ----------
        count: int
            Number of times to repeat the command packet, to reduce the odds
            of packet loss being a problem.

        Returns
        -------

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        for _ in range(count):
            self._send("IDENTIFY")

    # ------------------------------------------------------------------------
    def describe(
        self,
        serial_or_name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> dict:
        """
        Returns the device description structure corresponding to the device
        with the given serial number or customer-given name.

        Parameters
        ----------
        serial_or_name: str
            Serial number or customer-given name of the device that is to be
            queried.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------
        dict
            The device description structure.

        Raises
        -------
        TypeError
            If serial_or_name is invalid.
        ValueError
            If serial_or_name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        """

        response, socket = self._query(
            serial_or_name,
            "DESCRIBE",
            retries,
            timeout
        )

        try:
            response = json.loads(response)
            response["connected_via"] = self._ips[socket]
            return response
        except json.JSONDecodeError:
            raise RuntimeError("Unexpected response: {}".format(response))

    # ------------------------------------------------------------------------
    def get_serial(
        self,
        name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> str:
        """
        Returns the serial number of the device with the given customer-given
        name.

        Parameters
        ----------
        name: str
            Customer-given name of the device that is to be queried.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------
        str
            The serial number of the device.

        Raises
        -------
        TypeError
            If name is invalid.
        ValueError
            If name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        KeyError
            If the device response did not contain the requested information.
        """

        return self.describe(name, retries, timeout)["description"]["ser"]

    # ------------------------------------------------------------------------
    def get_name(
        self,
        serial: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> str:
        """
        Returns the customer-given name of the device with the given serial
        number.

        Parameters
        ----------
        serial: str
            Serial number of the device that is to be queried.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------
        str
            The customer-given name of the device.

        Raises
        -------
        TypeError
            If serial is invalid.
        ValueError
            If serial is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        KeyError
            If the device response did not contain the requested information.
        """

        return self.describe(serial, retries, timeout)["description"]["name"]

    # ------------------------------------------------------------------------
    def set_name(
        self,
        serial_or_name: str,
        new_name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> None:
        """
        Renames the device with the given serial number or name.

        Parameters
        ----------
        serial_or_name: str
            Serial number or customer-given name of the device that is to be
            reconfigured.
        new_name: str
            The new customer-given name for the device. May not contain
            newlines, double quotes, or backslashes.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------

        Raises
        -------
        TypeError
            If serial_or_name or new_name are invalid.
        ValueError
            If serial_or_name or new_name are invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        """

        serial_or_name = str(serial_or_name)
        if not serial_or_name:
            raise ValueError("Serial number or name must not be blank")
        new_name = str(new_name)
        if not new_name:
            raise ValueError("New name must not be blank")
        if "\n" in new_name:
            raise ValueError("Device name may not include newlines")
        if "\\" in new_name:
            raise ValueError("Device name may not include backslashes")
        if '"' in new_name:
            raise ValueError("Device name may not include double quotes")
        response, _ = self._query(
            serial_or_name,
            "SET_NAME {}".format(new_name),
            retries,
            timeout
        )
        if response != "OK":
            raise RuntimeError("Unexpected response: {}".format(response))

    # ------------------------------------------------------------------------
    def get_ip(
        self,
        serial_or_name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> str:
        """
        Returns the IP address of the device with the given serial number or
        customer-given name.

        Parameters
        ----------
        serial_or_name: str
            Serial number or customer-given name of the device that is to be
            queried.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------
        str
            The IP address of the device.

        Raises
        -------
        TypeError
            If serial_or_name is invalid.
        ValueError
            If serial_or_name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        KeyError
            If the device response did not contain the requested information.
        """

        return self.describe(serial_or_name, retries, timeout)["identity"]["ip"]

    # ------------------------------------------------------------------------
    def set_ip(
        self,
        serial_or_name: str,
        ip_address: str,
        retries: int = 3,
        timeout: float = 1.0,
    ) -> None:
        """
        Adjusts the IP address configuration of the device with the given
        serial number or customer-given name. The device will reboot as a
        result of this.

        Parameters
        ----------
        serial_or_name: str
            Serial number or customer-given name of the device that is to be
            reconfigured.
        ip_address: str
            The new IP address configuration for the device. This may be an
            IPv4 address including prefix length (`x.x.x.x/x`), an IPv6
            address including prefix length (e.g. `x:x::x:x/x`), a combination
            thereof separated via a semicolon, or the string `dhcp` to have
            the device obtain an IPv4 address via DHCP.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------

        Raises
        -------
        TypeError
            If serial_or_name is invalid.
        ValueError
            If serial_or_name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        """

        serial_or_name = str(serial_or_name)
        if not serial_or_name:
            raise ValueError("Serial number or name must not be blank")
        response, _ = self._query(
            serial_or_name,
            "SET_IP {}".format(ip_address),
            retries,
            timeout
        )
        if response != "OK":
            raise RuntimeError("Unexpected response: {}".format(response))

    # ------------------------------------------------------------------------
    def set_all_dhcp(self, count: int = 3) -> None:
        """
        Instructs all devices on the network to reboot and obtain an IP
        address via DHCP.

        Parameters
        ----------
        count: int
            Number of times to repeat the command packet, to reduce the odds
            of packet loss being a problem.

        Returns
        -------

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        for _ in range(count):
            self._send("SET_IP dhcp")

    # ------------------------------------------------------------------------
    def reboot(
        self,
        serial_or_name: str,
        retries: int = 3,
        timeout: float = 1.0
    ) -> None:
        """
        Reboots the device with the given serial number or customer-given
        name.

        Parameters
        ----------
        serial_or_name: str
            Serial number of the device that is to be rebooted.
        retries: int
            Number of times to retry sending the command, if no response is
            received.
        timeout: float
            Timeout in seconds to wait for a response, per retry.

        Returns
        -------

        Raises
        -------
        TypeError
            If serial_or_name is invalid.
        ValueError
            If serial_or_name is invalid.
        OSError
            If transmission or reception fails.
        TimeoutError
            If no respone is received from the device.
        RuntimeError
            If an unexpected response is received from the device.
        """

        serial_or_name = str(serial_or_name)
        if not serial_or_name:
            raise ValueError("Serial number or name must not be blank")
        response, _ = self._query(serial_or_name, "REBOOT", retries, timeout)
        if response != "OK":
            raise RuntimeError("Unexpected response: {}".format(response))

    # ------------------------------------------------------------------------
    def reboot_all(self, count: int = 3) -> None:
        """
        Instructs all devices on the network to reboot.

        Parameters
        ----------
        count: int
            Number of times to repeat the command packet, to reduce the odds
            of packet loss being a problem.

        Returns
        -------

        Raises
        -------
        OSError
            If transmission or reception fails.
        """

        for _ in range(count):
            self._send("REBOOT")

    # ------------------------------------------------------------------------
    def recover_device(self) -> None:
        """
        Attempts to recover a device with a severely broken IP configuration,
        by instructing ALL devices on the network to revert back to
        192.168.0.2/24. ONLY RUN THIS COMMAND WHEN YOU ARE ONLY CONNECTED TO
        A SINGLE DEVICE, OR YOU WILL GET IP ADDRESS CONFLICTS.

        Parameters
        ----------

        Returns
        -------

        Raises
        -------
        OSError
            If recovery packet transmission fails.
        """

        for _ in range(10):
            self._send("SET_IP 192.168.0.2/24")
            time.sleep(0.1)

    # ------------------------------------------------------------------------
    @staticmethod
    def cmd_line(*args: Iterable[str]) -> Any:
        """
        Runs the plug & play command-line tool with the given arguments.

        Parameters
        ----------
        *args: Iterable[str]
            The command-line arguments.

        Returns
        -------
        Any
            If the given command logically returns something, it will be
            returned as a Python value in addition to being printed as a
            string. Otherwise, None will be returned.

        Raises
        ------
        RuntimeError
            If the command-line tool returns a nonzero exit status.
        """

        # This version is intended to be called from within a script or
        # notebook, so catch sys.exit() calls, and enable tracebacks.
        code = 0
        try:
            _main(*args)
        except SystemExit as e:
            code = e.code
        if code != 0:
            raise RuntimeError("exit with status {}".format(code))


# -- command-line tool -------------------------------------------------------
def _main(args: Union[None, Iterable[str]]=None) -> Any:
    """
    Runs the Qblox plug & play tool.

    Parameters
    ----------
    args: Union[None, Iterable[str]]
        When None, this will run the plug & play tool as if called from the
        command line. Arguments are taken from ``sys.argv``, and
        ``sys.exit()`` is called when complete. When this is an iterable of
        strings, these strings are interpreted as ``sys.argv[1:]``, and
        exceptions will never be caught.

    Returns
    -------
    Any
        If run from a script and the command logically returns something, it
        will be returned as a Python value in addition to being printed as a
        string. If run from the command line, this always calls sys.exit().
    """

    with PlugAndPlay() as p:

        # Definitions.
        VERSION = "0.0.1"
        HELP_TEXT = (
            "Qblox plug & play version {}\n"
            "\n"
            "This program allows you to scan your LAN for instruments from Qblox.\n"
            "A list of available commands follows. Run `{} <command> help` for\n"
            "more information about a command.\n"
        ).format(VERSION, os.path.basename(sys.argv[0]))
        HELP_LIKE = ("help", "-h", "--help", "/?")

        # Define commands available on the command line. The code after this
        # is pretty much just boilerplate to
        cmds = {
            "list": p.print_devices,
            "describe": p.describe,
            "identify": p.identify,
            "reboot": p.reboot,
            "get": {
                "name": p.get_name,
                "ip": p.get_ip,
                "serial": p.get_serial,
                "json": p.describe,
            },
            "set": {
                "name": p.set_name,
                "ip": p.set_ip,
            },
            "all": {
                "describe": p.list_devices,
                "identify": p.identify_all,
                "reboot": p.reboot_all,
                "dhcp": p.set_all_dhcp,
            },
            "recover-device": p.recover_device,
        }

        def print_cmds_and_exit(arg_stack, cmds):
            """
            Prints the list of (sub)commands in the given cmds structure,
            assumed to be (sub)commands of the commands listed in arg_stack.
            """
            if arg_stack:
                print(
                    "Available subcommands of {}:".format(" ".join(arg_stack)),
                    file=sys.stderr,
                )
            else:
                print("Available commands:", file=sys.stderr)

            def recurse(cmds, prefix=" -"):
                for name, action in cmds.items():
                    if isinstance(action, dict):
                        recurse(action, "{} {}".format(prefix, name))
                    else:
                        print("{} {}".format(prefix, name), file=sys.stderr)

            recurse(cmds)
            sys.exit(2)

        def print_help_and_exit(arg_stack, fn):
            """
            Prints the call signature and docstring of the given function,
            going by the command-line command name given by arg_stack.
            """
            params = arg_stack
            for param in inspect.signature(fn).parameters.values():
                if param.default is inspect.Parameter.empty:
                    params.append("<{}>".format(param.name))
                else:
                    params.append("[{}={}]".format(param.name, param.default))
            print(
                "Syntax: {} {}\n\n{}".format(sys.argv[0],
                                             " ".join(arg_stack),
                                             inspect.cleandoc(fn.__doc__)),
                file=sys.stderr,
            )
            sys.exit(2)

        # Print help if no arguments are given or a help-like argument is
        # given.
        if args is None:
            args = sys.argv[1:]
            from_script = False
        else:
            from_script = True
        if not args or args[0] in HELP_LIKE:
            print(HELP_TEXT, file=sys.stderr)
            print_cmds_and_exit([], cmds)

        # Determine which command is being run.
        arg_stack = []
        while isinstance(cmds, dict):
            if not args:
                print_cmds_and_exit(arg_stack, cmds)
            arg, *args = args
            subcmds = cmds.get(arg, None)
            if subcmds is None:
                print("Error: unknown command '{}'\n".format(arg), file=sys.stderr)
                print_cmds_and_exit(arg_stack, cmds)
            cmds = subcmds
            arg_stack.append(arg)
        fn = cmds

        # Print help for a specific command if requested.
        if len(args) > 0 and args[0] in HELP_LIKE:
            print_help_and_exit(arg_stack, fn)

        # Convert the remaining command-line arguments to the types expected
        # by the command function.
        fn_args = []
        signature = inspect.signature(fn)
        for param in signature.parameters.values():
            if not args:
                if param.default is inspect.Parameter.empty:
                    print_help_and_exit(arg_stack, fn)
                break
            arg, *args = args
            try:
                if param.annotation is str:
                    fn_args.append(arg)
                elif param.annotation is int:
                    fn_args.append(int(arg))
                elif param.annotation is float:
                    fn_args.append(float(arg))
                else:
                    raise TypeError(
                        "unsupported annotation {}".format(param.annotation)
                    )
            except (ValueError, TypeError):
                print(
                    "Error: invalid value for '{}'\n".format(param.name),
                    file=sys.stderr,
                )
                print_help_and_exit(arg_stack, fn)
        if args:
            print("Error: too many arguments\n", file=sys.stderr)
            print_help_and_exit(arg_stack, fn)

        # Actually run the command.
        try:
            result = fn(*fn_args)
        except Exception as e:

            # Unsuccessful run.
            if from_script:
                raise
            else:
                print("{}: {}".format(type(e).__name__, e), file=sys.stderr)
                sys.exit(1)

        # If the command is supposed to return something, pretty-print it.
        if signature.return_annotation is not None:
            pprint.pprint(result)

        # Successful run.
        if from_script:
            return result
        else:
            sys.exit(0)


# - main ---------------------------------------------------------------------
if __name__ == "__main__":
    _main()
