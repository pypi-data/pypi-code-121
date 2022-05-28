"""Base plugin class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
from abc import ABC, abstractmethod
from typing import Generator, cast

import lxml  # nosec

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from .support.elements import nice_address_sort, unescape, xml_findall, xml_findone


def split_commas(data: str | list, make_int: bool = False) -> list[int | str]:
    """
    Create list from comma-delimited string (or list).

    If make_int is True, ensure final list contents are integers.

    Args:
        data:
            String or list of data to process.

        make_int:
            True if final list must contain only integers.

    Returns:
        list

    """
    if not data:
        # Don't mess with empty strings.
        return []

    if isinstance(data, str):
        data = data.split(",")

    if make_int:
        return [int(x) for x in data]
    # Yes, we know it is a list[str]...
    # Without cast mypy thinks we're returning list[Any].
    return cast(list[int | str], data)


def _destination_source(node: Node) -> str:
    """Format destination and source addresses/ports."""
    any_address: bool = False
    address: str = ""
    port: str = ""

    for child in node.getchildren():
        match child.tag:
            case "any":
                any_address = True
            case "address" | "network":
                address = unescape(child.text)
            case "port":
                port = unescape(child.text)
            case _:
                raise NodeError(f"Unknown tag {child.tag} in node {node.tag}.")

    result = []
    if any_address:
        if port:
            result.append(f"any:{port}")
        else:
            result.append("any")
    else:
        if address and port:
            result.append(f"{address}:{port}")
        else:
            # Ignore port without address as I don't think that is allowed.
            result.append(address)
    return "\n".join(result)


def _created_updated(node: Node) -> str:
    """Format created/updated user and date/time."""
    result = []
    for child in node.getchildren():
        match child.tag:
            case "username":
                result.append(child.text)
            case "time":
                date_time = datetime.datetime.fromtimestamp(int(child.text)).strftime(
                    "%Y-%m-%d %H-%M-%S"
                )
                result.append(date_time)
            case _:

                raise NodeError(f"Unknown tag {child.tag} in node {node.tag}.")

    return "\n".join(result)


class SheetData:
    """All information required to display a worksheet."""

    def __init__(
        self,
        *,
        sheet_name: str,
        header_row: list[str],
        data_rows: list[list],
        column_widths: list[int],
    ) -> None:
        """Gather all necessary information."""
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.data_rows = data_rows
        self.column_widths = column_widths


class BasePlugin(ABC):
    """Base of all plugins."""

    def __init__(
        self,
        display_name: str,
        node_names: str,
        column_widths: str | list[int],
        el_paths_to_sanitize: list[str] | None = None,
    ) -> None:
        """
        Initialize base plugin.

        node_names:
            Comma-delimited list of nodes to obtain.
            Also used for the sheet's header row.

        column_widths:
            Comma-delimited list of sheet column widths.

        el_paths_to_sanitize:
            List of comma-delimited elements to santitize
        """
        self.display_name: str = display_name
        self.node_names: list[str] = cast(list[str], split_commas(node_names))
        self.column_widths: list[int] = cast(
            list[int], split_commas(column_widths, make_int=True)
        )
        self.el_paths_to_sanitize = el_paths_to_sanitize

    def sanitize(self, parsed_xml: Node | None) -> None:
        """
        Sanitize defined paths.

        Args:
            parsed_xml: Parsed XML Node.

        """
        if parsed_xml is None or self.el_paths_to_sanitize is None:
            # Nothing to do
            return
        assert parsed_xml is not None
        assert self.el_paths_to_sanitize is not None
        for el_path in self.el_paths_to_sanitize:
            els = xml_findall(parsed_xml, el_path)
            for el in els:
                if el.text is not None:
                    el.text = "SANITIZED"

    def adjust_node(self, node: Node) -> str | Node:
        """
        Adjust a node based children and tag name.

        Args:
            node: XML node to check

        Returns:
            Processed node data or original node if no processing done.

        """
        if node is None:
            return ""

        children = node.getchildren()
        if not children:
            # Terminal node. Defaults to returning text.
            match node.tag:
                case "address":
                    if node.text is None:
                        return ""
                    return nice_address_sort(node.text)

                case "data_ciphers" | "local_network" | "local_networkv6" | "remote_network" | "remote_networkv6":  # NOQA
                    if node.text is None:
                        return ""
                    values = [x.strip() for x in node.text.split(",")]
                    values.sort()
                    return "\n".join(values)

                case "descr":
                    if node.text is None:
                        return ""
                    value = unescape(node.text)
                    value = value.replace("<br />", "\n")
                    lines = [x.strip() for x in value.split("\n")]
                    return "\n".join(lines)

                # May be specific only to our environment. Details divided by ||
                case "detail":
                    if node.text is None:
                        return ""
                    value = unescape(node.text)
                    value = value.replace("||", "\n")
                    lines = [x.strip() for x in value.split("\n")]
                    return "\n".join(lines)

                case "disable" | "disabled" | "enable" | "blockpriv" | "blockbogons":  # NOQA
                    if node.text:
                        raise NodeError(
                            f"Node {node.tag} has unexpected text: {node.text}."
                        )

                    return "YES"

                case _:
                    return node.text or ""

        # Process
        match node.tag:
            case "destination" | "source":
                return _destination_source(node)

            case "created" | "updated":
                return _created_updated(node)

        # Not processed.
        return node

    def adjust_nodes(self, nodes: list[Node]) -> str:
        """
        Adjust multiple nodes into cell.

        All nodes have the same tag.
        # TODO: Always process for 'nodes' as we'll compress the information
        # for single instances.
        """
        if nodes is None:
            return ""

        num_nodes = len(nodes)
        if num_nodes == 0:
            return ""

        cell = []
        for node in nodes:
            cell.append(self.adjust_node(node))
            cell.append("")

        #  Remove the trailing space.
        if len(cell) > 1 and cell[-1] == "":
            cell = cell[:-1]
            self.sanity_check_node_row(node.getparent(), cell)

        return "\n".join(cell)

    def sanity_check_node_row(self, node: Node, row: list) -> None:
        """
        Ensure no row items are an XML node.

        Args:
            node: Node being processed so we can grab the tag.
            row: List items ready to write to spreadsheet

        Raises:
            NodeError

        """
        errors = []
        bad_items = [x for x in row if isinstance(x, lxml.etree._Element)]
        if not bad_items:
            return

        for item in bad_items:
            errors.append(f"Unprocessed {self.node_ancesters(node)}:{item.tag}")
            print("\n".join(errors))

    def extract_node_elements(self, node: Node) -> dict[str, str]:
        """Create dictionary of node children's tag:value."""
        data = {}
        for child in node.getchildren():
            data[child.tag] = self.adjust_node(child)
        return data

    def node_ancesters(self, node: Node) -> str:
        """Walk up through node parents."""
        path = []
        path.append(node.tag)
        while (node := node.getparent()) is not None:
            path.append(node.tag)
        path.reverse()
        return "/".join(path)

    def load_cell(self, node, node_names) -> str:
        """Load node elements into a single cell."""
        if node is None:
            return ""

        cell = []
        self.report_unknown_node_elements(node, node_names)
        for node_name in node_names:
            cell.append(
                f"{node_name}: {self.adjust_node(xml_findone(node, node_name))}"
            )
        return "\n".join(cell)

    def report_unknown_node_elements(
        self, node: Node, node_names: list[str] | None = None
    ) -> None:
        """
        Report if any unknown node elements are present.

        Report if any of the node's children's tags are not found in the nodenames list.

        """
        if node is None:
            return

        unknowns = []
        if node_names is None:
            node_names = self.node_names
        fn_set = set(node_names)

        for child in node.getchildren():
            if child.tag not in fn_set:
                unknowns.append(child.tag)

        if unknowns:
            path = self.node_ancesters(node)
            unknowns.sort()
            print(f"""Node {path} has unknown child node(s): {", ".join(unknowns)}""")

    def wip(self, node: Node) -> str:
        """Output a WIP warning."""
        print(f"WIP: {self.display_name}/{node.tag}.")
        return "WIP"

    @abstractmethod
    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Run plugin.

        Args:
            pfsense:
                Root of the parsed XML file.

        Returns:
            List of rows to write to spreadsheet.

        """
        raise NotImplementedError
