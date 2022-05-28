"""OpenVPN Server plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

# No named top-level nodes.
# Using top-level tags.
NODE_NAMES = "name,details"
WIDTHS = "60,100"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "OpenVPN Server",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """
        Local adjustments.

        Note the missing steps which are not in our sample XML.
        """

        if node is None:
            return ""

        match node.tag:
            case "step1":
                node_names = "type".split(",")
                return self.load_cell(node, node_names)

            case "step6":
                node_names = (
                    "authcertca,certca,city,country,email,"
                    "keylength,lifetime,organization,state,uselist"
                ).split(",")
                return self.load_cell(node, node_names)

            case "step9":
                node_names = (
                    "authcertca,certca,authcertname,certname,city,country,email,"
                    "keylength,lifetime,organization,state,uselist"
                ).split(",")
                return self.load_cell(node, node_names)

            case "step10":
                node_names = (
                    "descr,crypto,concurrentcon,dhkey,digest,"
                    "dns1,dns2,dns3,dynip,engine,"
                    "gentlskey,interface,localnet,localport,nbttype,"
                    "protocol,tlsauth,topology,tunnelnet"
                ).split(",")
                return self.load_cell(node, node_names)

            case "step11":
                node_names = "ovpnrule,ovpnallow".split(",")
                return self.load_cell(node, node_names)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        node = xml_findone(parsed_xml, "ovpnserver")
        if node is None:
            return

        for child in node.getchildren():
            row = []
            row.append(child.tag)  # name
            row.append(self.adjust_node(child))

            self.sanity_check_node_row(child, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
