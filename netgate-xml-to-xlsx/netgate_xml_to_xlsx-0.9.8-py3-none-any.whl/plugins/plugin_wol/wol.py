"""WOL plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = ""
WIDTHS = ""


class Plugin(BasePlugin):
    """Gather wol information."""

    def __init__(
        self,
        display_name: str = "wol",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Gather wol information.

        Not yet implemented. Issue warning if it has data.
        """
        node = xml_findone(parsed_xml, "wol")
        if node is None:
            return

        self.report_unknown_node_elements(node)

        children = node.getchildren()
        if len(children) > 0:
            self.wip(node)

        yield None
