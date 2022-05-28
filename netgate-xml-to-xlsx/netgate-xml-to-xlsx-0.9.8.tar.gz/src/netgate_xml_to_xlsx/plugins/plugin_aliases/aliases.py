"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall

NODE_NAMES = "name,type,address,url,aliasurl,updatefreq,descr,detail"
WIDTHS = "40,40,40,80,80,20,80,80"


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "Aliases",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Aliases sheet."""
        rows = []

        alias_nodes = xml_findall(parsed_xml, "aliases,alias")
        if not alias_nodes:
            return

        alias_nodes.sort(key=lambda x: x.text.casefold())

        for node in alias_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                values = [self.adjust_node(x) for x in xml_findall(node, node_name)]
                values.sort()

                row.append("\n".join(values))

            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
