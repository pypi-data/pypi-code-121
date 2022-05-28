"""
Diag plugin.

Our current XML samples have various levels of empty diag information.
Generate it, but you'll have columns with empty rows.

"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "name,ipv6nat"
WIDTHS = "20,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "DIAG",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []
        diag_node = xml_findone(parsed_xml, "diag")
        if diag_node is None:
            return

        self.report_unknown_node_elements(diag_node, "ipv6nat".split(","))
        for node in diag_node.getchildren():
            self.report_unknown_node_elements(node, "ipaddr".split(","))
            row = []

            for node_name in self.node_names:
                if node_name == "name":
                    row.append(node.tag)
                    continue
                row.append(self.adjust_node(xml_findone(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)

        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
