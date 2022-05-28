"""DHCPDv6 plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "enable,name,range,ramode,rapriority"
WIDTHS = "20,20,20,20,20"


class Plugin(BasePlugin):
    """Gather dhcpdv6 information."""

    def __init__(
        self,
        display_name: str = "DHCPD v6",
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
            case "range":
                node_names = "from,to".split(",")
                self.report_unknown_node_elements(node, node_names)
                cell = []
                for node_name in node_names:
                    cell.append(
                        f"{node_name}: {self.adjust_node(xml_findone(node, node_name))}"
                    )
                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []
        dhcpd_node = xml_findone(parsed_xml, "dhcpdv6")
        if dhcpd_node is None:
            return

        for node in dhcpd_node.getchildren():
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                if node_name == "name":
                    row.append(node.getparent().tag)
                    continue
                row.append(self.adjust_node(xml_findone(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
