"""Syslog plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "enable,logall,filterdescriptions,ipproto,nentries,"
    "remoteserver,remoteserver2,remoteserver3,reverse,sourceip,"
    "format,rotatecount,nologdefaultblock,nologbogons,nologprivatenets,"
    "logcompressiontype"
)

WIDTHS = "30,20,20,20,20,60,60,60,20,20,20,20,40,40,40,40"


class Plugin(BasePlugin):
    """Gather syslog information."""

    def __init__(
        self,
        display_name: str = "Syslog",
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
            case "logall" | "nologdefaultblock" | "nologbogons" | "nologprivatenets":
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather syslog information."""
        rows = []

        node = xml_findone(parsed_xml, "syslog")
        if node is None:
            return

        self.report_unknown_node_elements(node)
        row = []

        for node_name in self.node_names:
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
