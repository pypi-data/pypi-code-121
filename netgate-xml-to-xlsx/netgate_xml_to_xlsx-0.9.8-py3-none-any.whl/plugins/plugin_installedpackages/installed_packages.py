"""Installed Packages plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findall, xml_findone

NODE_NAMES = (
    "name,internal_name,version,descr,plugins,"
    "noembedded,logging,website,pkginfolink,filter_rule_function,"
    "configurationfile,include_file,text,tabs,"
    # package-specific information
    "ha_backends,ha_pools,config"
)
WIDTHS = "40,40,20,80,40,20,80,80,80,80,80,80,80,60,60,60,60"


def name_sort(node: Node) -> str:
    """Extract element name for sorting."""
    if node is None:
        return ""
    value = unescape(xml_findone(node, "name").text).casefold()
    return value


class Plugin(BasePlugin):
    """Gather data for the Installed Packages."""

    def __init__(
        self,
        display_name: str = "Installed Packages",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node customizations."""
        if node is None:
            return ""

        match node.tag:
            case "active":
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

            case "logging":
                node_names = "facilityname,logfilename,logsocket".split(",")
                return self.load_cell(node, node_names)

            case "plugins":
                # Get 'item'.
                children = node.getchildren()
                plugins = []
                for child in children:
                    assert child.tag == "item"
                    plugins.append(self.adjust_node(xml_findone(child, "type")))
                plugins.sort()
                return "\n".join(plugins)

            case "tabs":
                node_names = "name,active,tabgroup,url,text".split(",")
                tab_nodes = xml_findall(node, "tab")
                cells = []
                for tab_node in tab_nodes:
                    self.report_unknown_node_elements(tab_node, node_names)
                    cell = []
                    for node_name in node_names:
                        cell.append(
                            f"{node_name}: {self.adjust_node(xml_findone(tab_node, node_name))}"
                        )
                    cell.append("")
                    cells.append("\n".join(cell))
                if len(cells) > 0 and cells[-1] == "":
                    cells = cells[:-1]
                return "\n".join(cells)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document installed packages. Sort by name."""
        rows = []

        package_nodes = xml_findall(parsed_xml, "installedpackages,package")

        package_nodes.sort(
            key=name_sort,
            # key=lambda x: x.name.casefold(),
            reverse=False,
        )

        for node in package_nodes:
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
