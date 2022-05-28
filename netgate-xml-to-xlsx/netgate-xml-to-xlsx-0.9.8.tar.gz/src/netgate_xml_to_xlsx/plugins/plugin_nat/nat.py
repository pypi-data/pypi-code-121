"""NAT plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

RULE_NAMES = (
    "descr,disabled,interface,protocol,ipprotocol,source,"
    "sourceport,source_hash_key,destination,dstport,target,"
    "targetip,targetip_subnet,local-port,associated-rule-id,poolopts,"
    "updated,created"
)

NODE_NAMES = "direction,mode," + RULE_NAMES
WIDTHS = "20,20,20,60,20,20,40,20,30,30,20,40,20,20,20,60,30,60,60"


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "NAT",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)
        self.local_data = {}

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        nat_node = xml_findone(parsed_xml, "nat")
        if not len(nat_node):
            return

        rule_names = RULE_NAMES.split(",")

        # No mode in inbound.
        self.local_data = dict(direction="inbound", mode="")

        # Cycle through top-level rules, which are inbound.
        rule_nodes = xml_findall(nat_node, "rule")

        for node in rule_nodes:
            self.report_unknown_node_elements(node, rule_names)
            row = []

            for node_name in self.node_names:
                if node_name in ("direction", "mode"):
                    row.append(self.local_data[node_name])
                    continue

                value = self.adjust_node(xml_findone(node, node_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        # Cycle through the outbound children's rules.

        outbound_node = xml_findone(nat_node, "outbound")
        self.local_data["direction"] = "outbound"
        self.local_data["mode"] = self.adjust_node(xml_findone(outbound_node, "mode"))
        row = []

        rule_nodes = xml_findall(outbound_node, "rule")
        for node in rule_nodes:
            self.report_unknown_node_elements(node, rule_names)
            row = []

            for node_name in self.node_names:
                if node_name in ("direction", "mode"):
                    row.append(self.local_data[node_name])
                    continue

                value = self.adjust_node(xml_findone(node, node_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
