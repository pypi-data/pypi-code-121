"""DHCPD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "name,enable,range,ddnsclientupdates,ddnsdomain,"
    "ddnsdomainkey,ddnsdomainkeyalgorithm,ddnsdomainkeyname,ddnsdomainprimary,ddnsdomainsecondary,"  # NOQA
    "defaultleasetime,denyunknown,dhcpleaseinlocaltime,dnsserver,domain,"
    "domainsearchlist,failover_peerip,filename,filename32,filename32arm,"
    "filename64,filename64arm,gateway,ignorebootp,ldap,"
    "mac_allow,mac_deny,maxleasetime,netmask,nextserver,"
    "ntpserver,numberoptions,rootpath,staticmap,tftp"
)

WIDTHS = (
    "20,20,40,40,20,"
    "40,40,40,40,40,"
    "40,40,40,40,40,"
    "40,40,40,40,20,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "40,20,40,60,40"
)


class Plugin(BasePlugin):
    """Gather dhcpd information."""

    def __init__(
        self,
        display_name: str = "DHCPD",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "mac_allow" | "mac_deny":
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

            case "range":
                node_names = "from,to".split(",")
                return self.load_cell(node, node_names)

            case "staticmap":
                node_names = (
                    "descr,cid,ddnsdomain,ddnsdomainkey,ddnsdomainkeyalgorithm,"
                    "ddnsdomainkeyname,ddnsdomainprimary,ddnsdomainsecondary,"
                    "defaultleasetime,domain,domainsearchlist,"
                    "filename,filename32,filename32arm,filename64,filename64arm,"
                    "gateway,hostname,ipaddr,ldap,mac,"
                    "maxleasetime,nextserver,numberoptions,rootpath,tftp"
                )
                return self.load_cell(node, node_names.split(","))

        return super().adjust_node(node)

    def adjust_nodes(self, nodes: list[Node]) -> list[str]:
        """Local nodes adjustment."""

        if nodes is None or len(nodes) == 0:
            return ""

        match nodes[0].tag:
            case "staticmap":
                cell = []
                for node in nodes:
                    cell.append(self.adjust_node(node))
                    cell.append("")

                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]
                return "\n".join(cell)
        return super().adjust_nodes(nodes)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []
        dhcpd_node = xml_findone(parsed_xml, "dhcpd")
        if dhcpd_node is None:
            return

        self.report_unknown_node_elements(dhcpd_node, "lan,opt1,opt2,opt3".split(","))
        for node in dhcpd_node.getchildren():
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                if node_name == "name":
                    row.append(node.tag)
                    continue

                row.append(self.adjust_nodes(xml_findall(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)
        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
