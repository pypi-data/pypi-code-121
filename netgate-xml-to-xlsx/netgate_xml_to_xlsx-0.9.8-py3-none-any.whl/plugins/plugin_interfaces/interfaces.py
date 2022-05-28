"""Interfaces plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "enable,name,if,descr,alias-address,"
    "alias-subnet,spoofmac,enable,ipaddr,subnet,"
    "gateway,ipaddrv6,subnetv6,blockpriv,blockbogons,"
    "media,track6-interface,track6-prefix-id,dhcp6-duid,dhcp6-ia-pd-len,"
    "dhcp6cvpt,mediaopt,adv_dhcp6_prefix_selected_interface"
)
WIDTHS = "20,40,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,60"


class Plugin(BasePlugin):
    """Gather data for the Interfaces."""

    def __init__(
        self,
        display_name: str = "Interfaces",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Custom node adjustment."""
        if node is None:
            return ""

        match node.tag:
            case "media":
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"
        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document all interfaces."""
        rows = []

        # Don't sort interfaces. Want them in the order they are encountered.
        interfaces_node = xml_findone(parsed_xml, "interfaces")
        if interfaces_node is None:
            return

        children = interfaces_node.getchildren()
        if not len(children):
            return

        for node in children:
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                if node_name == "name":
                    row.append(node.tag)
                    continue
                value = self.adjust_node(xml_findone(node, node_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
