"""IPSEC plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findall, xml_findone

TOP_NODE_NAMES = "async_crypto,logging,uniqueids,vtimaps"
TOP_WIDTHS = "30,30,30,30"

CLIENT_NODENAMES = ""
CLIENT_WIDTHS = ""

PHASE1_NODENAMES = (
    "descr,authentication_method,caref,certref,closeaction,"
    "dpd_delay,dpd_maxfail,encryption,ikeid,iketype,"
    "interface,lifetime,mobike,myid_data,myid_type,"
    "nat_traversal,peerid_data,peerid_type,pre-shared-key,private-key,"
    "protocol,remote-gateway,mode,rekey_time,reauth_time,"
    "rand_time,pkcs11certref,pkcs11pin"
)
PHASE1_WIDTHS = (
    "40,30,10,10,20,"  # 5
    "20,20,60,10,10,"  # 10
    "30,10,10,20,20,"  # 15
    "20,20,20,20,20,"  # 20
    "20,40,10,20,20,"  # 25
    "20,40,40"
)

PHASE2_NODENAMES = (
    "descr,encryption-algorithm-option,hash-algorithm-option,ikeid,lifetime,"
    "localid,mode,pfsgroup,pinghost,protocol,"
    "rekey_time,rand_time,remoteid,reqid,uniqid"
)

PHASE2_WIDTHS = "40,40,30,20,20,20,20,20,20,20,20,40,40,20,30"


class Plugin(BasePlugin):
    """Gather data Unbound."""

    def __init__(
        self,
        display_name: str = "IPSEC",
        node_names: str = TOP_NODE_NAMES,
        column_widths: str = TOP_WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def should_process(self, node: Node) -> bool:
        """
        Should we process the element?

        Element needs to have at least the top number of node name children + 1.
        Netgate will store several empty items.
        This seems like a quick and reasonable check.
        """
        assert node.tag in ("ipsec", "client")
        children = node.getchildren()
        if len(children) < len(self.node_names) + 1:
            return False
        return True

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "encryption":
                cell = []
                node_names = (
                    "encryption-algorithm,hash-algorithm,dhgroup,prf-algorithm".split(
                        ","
                    )
                )
                item_nodes = xml_findall(node, "item")

                if item_nodes is None:
                    return ""

                for item_node in item_nodes:
                    cell.append(self.load_cell(item_node, node_names))
                    cell.append("")

                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]
                return "\n".join(cell)

            case "encryption-algorithm":
                node_names = "name,keylen".split(",")
                return self.load_cell(node, node_names)

            case "encryption-algorithm-option":
                node_names = "name,keylen".split(",")
                return self.load_cell(node, node_names)

            case "localid":
                node_names = "type,address,netbits".split(",")
                return self.load_cell(node, node_names)

            case "logging":
                cell = []
                children = node.getchildren()
                for child in children:
                    cell.append(f"{child.tag}: {unescape(child.text)}")
                cell.sort()
                return "\n".join(cell)

            case "remoteid":
                node_names = "type,address,netbits".split(",")
                return self.load_cell(node, node_names)

            case "vtimaps":
                cell = []
                node_names = "reqid,index,ifnum".split(",")
                item_nodes = xml_findall(node, "item")
                for item_node in item_nodes:
                    cell.append(self.load_cell(item_node, node_names))
                    cell.append("")

                if len(cell) and cell[-1] == "":
                    cell = cell[:-1]

                return "\n".join(cell)

        return super().adjust_node(node)

    def gather_top(self, node: Node) -> list[str]:
        """Gather single row of top-level ipsec data."""
        rows = []

        if node is None or not self.should_process(node):
            return rows

        # Check for top-level elements plus the different phases and client.
        l_nodenames = self.node_names[:]
        l_nodenames.extend("phase1,phase2,client".split(","))
        self.report_unknown_node_elements(node, l_nodenames)
        row = []

        for node_name in self.node_names:
            value = self.adjust_node(xml_findone(node, node_name))

            row.append(value)

        self.sanity_check_node_row(node, row)

        if len(row):
            rows.append(row)

        return rows

    def gather_client(self, node_in: Node) -> list[str]:
        """Not implemented, but check if there's data."""
        client_node = xml_findone(node_in, "client")
        if client_node is None:
            return
        if self.should_process(client_node):
            print(f"WARNING: {self.node_ancesters(client_node)} is unimplemented.")

        return []

    def gather_phase1s(self, node_in: Node) -> list[str]:
        """IPSEC Phase 1 information."""
        rows = []

        phase1_nodes = xml_findall(node_in, "phase1")

        for node in phase1_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))
            self.sanity_check_node_row(node, row)
            rows.append(row)

        rows.sort()
        return rows

    def gather_phase2s(self, node_in: Node) -> list[str]:
        """IPSEC Phase 2 information."""
        rows = []

        phase2_nodes = xml_findall(node_in, "phase2")

        for node in phase2_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_nodes(xml_findall(node, node_name)))
            self.sanity_check_node_row(node, row)
            rows.append(row)

        rows.sort()
        return rows

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document unbound elements.  One row."""
        node = xml_findone(parsed_xml, "ipsec")
        if node is None:
            return

        keep_processing = False
        rows = self.gather_top(node)
        if rows is not None and len(rows) > 0:
            keep_processing = True
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        if not keep_processing:
            return

        self.display_name = "IPSEC Client"
        self.node_names = CLIENT_NODENAMES.split(",")
        self.column_widths = CLIENT_WIDTHS.split(",")
        rows = self.gather_client(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        self.display_name = "IPSEC Phase 1"
        self.node_names = PHASE1_NODENAMES.split(",")
        self.column_widths = PHASE1_WIDTHS.split(",")
        rows = self.gather_phase1s(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        self.display_name = "IPSEC Phase 2"
        self.node_names = PHASE2_NODENAMES.split(",")
        self.column_widths = PHASE2_WIDTHS.split(",")
        rows = self.gather_phase2s(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
