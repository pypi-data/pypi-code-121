"""Switches plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "device,vlanmode,swports"
WIDTHS = "60,20,60"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Switches",
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
            case "swports":
                node_names = "port,state".split(",")
                swports = xml_findall(node, "swport")
                cell = []
                for swport in swports:
                    self.report_unknown_node_elements(swport, node_names)
                    for node_name in node_names:
                        cell.append(
                            f"{node_name}: {self.adjust_node(xml_findone(swport, node_name))}"
                        )
                    cell.append("")

                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]
                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        cron_nodes = xml_findall(parsed_xml, "switches,switch")
        if cron_nodes is None:
            return

        for node in cron_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
