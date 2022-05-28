"""System Users plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_node_exists

NODE_NAMES = (
    "disabled,name,groupname,scope,expires,"
    "descr,ipsecpk,uid,cert,bcrypt-hash,"
    "authorizedkeys,ipsecpsk,priv,dashboardcolumns,webguicss"
)
WIDTHS = "12,40,40,20,20,60,20,10,20,20,20,20,40,40,60"


class Plugin(BasePlugin):
    """Gather data for the System Users sheet."""

    def __init__(
        self,
        display_name: str = "System Users",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Sheet with system.user information.

        Not all nodes displayed as # column on dashboard and webguicss are uninteresting
        (at least to me at the moment).
        """
        rows = []

        system_user_nodes = xml_findall(parsed_xml, "system,user")
        if not system_user_nodes:
            return

        system_user_nodes.sort(key=lambda x: x.text.casefold())

        for node in system_user_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                values = [self.adjust_node(x) for x in xml_findall(node, node_name)]
                values.sort()

                row.append("\n".join(values))

            # The existence of the disabled element indicates user is disabled.
            row[1] = "Yes" if xml_node_exists(node, "disabled") else "Yes"
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
