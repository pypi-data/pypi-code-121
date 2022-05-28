"""System plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import nice_address_sort, unescape, xml_findall, xml_findone

NODE_NAMES = (
    "aliasesresolveinterval,already_run_config_upgrade,authserver,bogons,crypto_hardware,"
    "dhcpbackup,disablebeep,disablechecksumoffloading,disablechecksumoffloading,disablelargereceiveoffloading,"  # NOQA
    "disablenatreflection,disablesegmentationoffloading,dns1host,dns2host,dnsserver,"
    "do_not_send_uniqueid,domain,firmware,gitsync,hn_altq_enable,"
    "hostname,ipv6dontcreatelocaldns,language,lastchange,logsbackup,"
    "maximumfrags,maximumstates,maximumtableentries,nextgid,nextuid,"
    "optimization,pkg_repo_conf_path,powerd_ac_mode,powerd_battery_mode,powerd_normal_mode,"
    "primaryconsole,reflectiontimeout,revision,rrdbackup,scrubrnid,serialspeed,"
    "ssh,sshguard_blocktime,sshguard_detection_time,sshguard_threshold,sshguard_whitelist,"
    "timeservers,timezone,use_mfs_tmp_size,use_mfs_var_size,version,"
    "webgui"
)
WIDTHS = "80,100"


class Plugin(BasePlugin):
    """Gather data for the System sheet."""

    def __init__(
        self,
        display_name: str = "System",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_nodes(self, nodes: list[Node]) -> str:
        """Custom node adjustments."""
        if nodes is None or len(nodes) == 0:
            return ""

        result = []
        for node in nodes:
            match node.tag:
                case "authserver":
                    node_names = (
                        "name,type,host,radius_protocol,radius_nasip_attribute,"
                        "radius_secret,radius_timeout,radius_auth_port,refid".split(",")
                    )
                    for node_name in node_names:
                        # Only the nodes that appear.
                        # Prep for other types of authentication.
                        value = self.adjust_node(xml_findone(node, node_name))
                        if value:
                            result.append(f"{node_name}: {value}")

                case "firmware":
                    node_names = "disablecheck".split(",")
                    result.append(self.load_cell(node, node_names))

                case "bogons":
                    result.append(self.adjust_node(xml_findone(node, "interval")))

                case "dnsserver":
                    result.append(unescape(node.text))

                case "gitsync":
                    node_names = "repositoryurl,branch".split(",")
                    result.append(self.load_cell(node, node_names))

                case "ssh":
                    result.append(self.adjust_node(xml_findone(node, "enabled")))

                case "timeservers":
                    time_servers = node.text or ""
                    result.append(nice_address_sort(time_servers))

                case "version":
                    if version := int(float(node.text)) < 21:
                        print(
                            f"Warning: File uses version {version}.x. "
                            "Script is only tested on XML format versions 21+."
                        )
                    result.append(node.text)

                case "webgui":
                    node_names = (
                        "althostnames,auth_refresh_time,authmode,"
                        "dashboardavailablewidgetspanel,dashboardcolumns,"
                        "interfacessort,loginautocomplete,logincss,loginshowhost,"
                        "max_procs,noantilockout,port,protocol,ssl-certref,"
                        "statusmonitoringsettingspanel,systemlogsfilterpanel,"
                        "systemlogsmanagelogpanel,webguicss,webguifixedmenu,"
                        "webguihostnamemenu"
                    ).split(",")

                    for node_name in node_names:
                        # Only the nodes that appear.
                        # Prep for other types of authentication.
                        value = self.adjust_node(xml_findone(node, node_name))
                        if value:
                            result.append(f"{node_name}: {value}")
        result.sort()

        if len(result):
            # Remove possible trailing space.
            if result[-1] == "":
                result = result[:-1]
            return "\n".join(result)

        return super().adjust_nodes(nodes)

    def adjust_node(self, node: Node) -> str:
        """Custom node adjustment."""
        if node is None:
            return ""

        # TODO: Multi-line case statement that black doesn't undo.
        match node.tag:
            case "loginshowhost" | "noantilockout" | "interfacessort" | "dashboardavailablewidgetspanel":  # NOQA
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

            case "systemlogsfilterpanel" | "systemlogsmanagelogpanel" | "statusmonitoringsettingspanel":  # NOQA
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        System-level information.

        Only showing interesting information (at least to me at the moment).
        TODO: Needs custom report_unknown_node_elements.

        """
        rows = []

        top_level = {}
        # Version and change information is at top level.
        for key in "version,lastchange".split(","):
            top_level[key] = self.adjust_node(xml_findone(parsed_xml, key))

        system_node = xml_findone(parsed_xml, "system")
        if system_node is None:
            return

        for key in self.node_names:
            if key in top_level:
                rows.append([key, top_level[key]])
                continue

            row = [key, self.adjust_nodes(xml_findall(system_node, key))]
            self.sanity_check_node_row(system_node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row="name,value".split(","),
            data_rows=rows,
            column_widths=self.column_widths,
        )
