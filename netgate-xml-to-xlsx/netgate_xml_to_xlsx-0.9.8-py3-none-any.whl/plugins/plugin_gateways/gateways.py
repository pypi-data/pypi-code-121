"""Gateways plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "name,interface,gateway,defaultgw4,defaultgw6,weight,ipprotocol,monitor_disable,"
    "action_disable,descr"
)
WIDTHS = "40,20,20,20,30," "10,20,20,20,80"


class Plugin(BasePlugin):
    """Gather data for the Gateways."""

    def __init__(
        self,
        display_name: str = "Gateways",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)
        self.default_gateways = {"defaultgw4": None, "defaultgw6": None}
        self.gateway_name = None

    def adjust_node(self, node: Node) -> str:
        """Custom node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "name":
                # Remember gateway name so we can use later for defaults.
                # name must come before defaultgwX in the nodename list.
                self.gateway_name = node.text

            case "action_disable" | "monitor_disable":
                # Existence indicates yes.
                return "YES"

        return super().adjust_node(node)

    def is_default_gw(self, ipvx: str) -> str:
        """
        Return YES if ipvx is for a default gateway, else "".

        Args:
            ipvx: ipv4 or ipv6

        Return:
            YES or "".

        """
        default = self.default_gateways[ipvx]
        if self.gateway_name and default == self.gateway_name:
            return "YES"
        return ""

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather data for Gateways."""
        rows = []

        gateways_node = xml_findone(parsed_xml, "gateways")
        if gateways_node is None:
            return

        # Load default IPV4 and IPV6 gateways.
        self.default_gateways["defaultgw4"] = self.adjust_node(
            xml_findone(gateways_node, "defaultgw4")
        )
        self.default_gateways["defaultgw6"] = self.adjust_node(
            xml_findone(gateways_node, "defaultgw6")
        )

        gateway_item_nodes = xml_findall(gateways_node, "gateway_item")
        for node in gateway_item_nodes:
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                value = self.adjust_node(xml_findone(node, node_name))

                if node_name in ("defaultgw4", "defaultgw6"):
                    value = self.is_default_gw(node_name)

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
