"""HAProxy plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from textwrap import indent
from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData, split_commas
from ..support.elements import xml_findall, xml_findone


class Plugin(BasePlugin):
    """
    Gather HAProxy data.

    Generates multiple sheets of data:
      * overview
      * backends
      * pools
    """

    def __init__(
        self,
        display_name: str = "HAProxy",
        node_names: str = "",
        column_widths: str = "",
    ) -> None:
        """Ignore node_names and column_widths as we create them individually."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
            ["pfsense,installedpackages,haproxy,advanced"],
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document haproxy configuration."""
        haproxy_node = xml_findone(parsed_xml, "installedpackages,haproxy")
        if haproxy_node is None:
            return

        for overview in self._overview(haproxy_node):
            yield overview

        ha_backends_nodes = xml_findall(haproxy_node, "ha_backends,item")
        for backend in self._backends(ha_backends_nodes):
            yield backend

        pools_nodes = xml_findall(haproxy_node, "ha_pools,item")
        for pool in self._pools(pools_nodes):
            yield pool

    def adjust_node(self, node: Node) -> str:
        """Local node adjustment."""
        if node is None:
            return ""

        # Custom nodes before standard
        match node.tag:
            case "a_extaddr":
                cells = []
                addr_nodes = xml_findall(node, "item")
                for a_node in addr_nodes:
                    cell = []
                    address = self.adjust_node(xml_findone(a_node, "extaddr"))
                    port = self.adjust_node(xml_findone(a_node, "extaddr_port"))
                    cell.append(f"{address}:{port}")
                    cell.append(
                        f"""ssl: {self.adjust_node(xml_findone(a_node, "extaddr_ssl"))}"""
                    )
                    cell.append(self.adjust_node(xml_findone(a_node, "_index")))
                    cells.append("\n".join(cell))

                return "\n".join(cells)

            case "dcertadv":
                # ssl-min-ver TLS ciphers x:x
                result = []
                value = node.text
                if not value:
                    return ""
                els = value.split(" ")
                if len(els) != 4:
                    raise NodeError(f"Unexpected tag value for {node.tag}: dcertadv")
                result.append(f"{els[0]}: {els[1]}")
                result.append("ciphers:")
                result.append(indent("\n".join(els[3].split(":")), " " * 4))
                return "\n".join(result)

            case "ha_servers":
                server_nodes = xml_findall(node, "item")
                rows = []
                for server_node in server_nodes:
                    row = []
                    row.append(
                        f"""name: {self.adjust_node(xml_findone(server_node, "name"))}"""
                    )
                    address = self.adjust_node(xml_findone(server_node, "address"))
                    port = self.adjust_node(xml_findone(server_node, "port"))
                    row.append(f"domain/port: {address}:{port}")
                    for node_name in "ssl,checkssl,id,_index".split(","):
                        value = self.adjust_node(xml_findone(server_node, node_name))
                        row.append(f"{node_name}: {value}")
                    row.append("")
                    rows.append("\n".join(row))

                return "\n".join(rows)

        return super().adjust_node(node)

    def _overview(self, node: Node) -> Generator[SheetData, None, None]:
        """
        Top-level haproxy elements.

        Display two columns (node, value).

        """
        node_names: list[str] = (
            "enable,configversion,nbproc,nbthread,maxconn,carpdev,"
            "logfacility,loglevel,log-send-hostname,remotesyslog,"
            "localstats_refreshtime,localstats_sticktable_refreshtime"
            ",dns_resolvers,resolver_retries,resolver_timeoutretry,resolver_holdvalid,"
            "hard_stop_after,ssldefaultdhparam,"
            "email_mailers,email_level,email_myhostname,email_from,email_to,"
            "config,files,advanced"
        ).split(",")
        header_row: list[str] = "name,value".split(",")
        column_widths: list[int] = split_commas("50,80")

        all_node_names = node_names[:]
        all_node_names.extend("ha_backends,ha_pools".split(","))
        self.report_unknown_node_elements(node, all_node_names)
        row = []

        for node_name in node_names:
            value = self.adjust_node(xml_findone(node, node_name))

            row.append(value)

        self.sanity_check_node_row(node, row)
        rows = list(zip(node_names, row))

        yield SheetData(
            sheet_name="HAProxy",
            header_row=header_row,
            data_rows=rows,
            column_widths=column_widths,
        )

    def _backends(self, nodes: list[Node]) -> Generator[SheetData, None, None]:
        """HAProxy backends have one or more items."""
        node_names: list[str] = split_commas(
            "name,status,type,primary_frontend,backend_serverpool,"  # 5
            "dontlognull,log-detailed,socket-stats,a_extaddr,ha_certificates,"  # 10
            "clientcert_ca,clientcert_crl,a_actionitems,a_errorfiles,dcertadv,"  # 15
            "ssloffloadcert,forwardfor,advanced,ha_acls,httpclose"  # 19
        )
        column_widths: list[int] = split_commas(
            "25,20,20,25,25,"  # 5
            "20,20,20,30,20,"  # 10
            "20,20,20,20,50,"  # 15
            "20,40,20,20,20"  # 19
        )

        rows = []

        for node in nodes:
            self.report_unknown_node_elements(node, node_names)
            row = []

            for node_name in node_names:
                value = self.adjust_node(xml_findone(node, node_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name="HAProxy Backends",
            header_row=node_names,
            data_rows=rows,
            column_widths=column_widths,
        )

    def _pools(self, nodes: list[Node]) -> Generator[SheetData, None, None]:
        """Report HAProxy pools."""
        rows = []

        node_names: list[str] = split_commas(
            "name,id,ha_servers,check_type,checkinter,log-health-checks,httpcheck_method,"
            "balance,balance_urilen,balance_uridepth,balance_uriwhole,"
            "a_acl,a_actionitems,errorfiles,advanced,advanced_backend,"
            "transparent_clientip,transparent_interface,"
            "monitor_uri,monitor_httpversion,monitor_username,monitor_domain,"
            "monitor_agentport,agent_check,agent_port,agent_port,"
            "connection_timeout,server_timeout,retries,"
            "stats_enabled,stats_username,stats_password,stats_uri,stats_scope,stats_realm,"
            "stats_admin,stats_node,stats_desc,stats_refresh,"
            "persist_stick_expire,persist_stick_tablesize,persist_stick_length,"
            "persist_stick_cookiename,persist_sticky_type,persist_cookie_enabled,"
            "persist_cookie_name,persist_cookie_mode,persist_cookie_cachable,"
            "persist_cookie_postonly,persist_cookie_httponly,persist_cookie_secure,"
            "haproxy_cookie_maxidle,haproxy_cookie_maxlife,haproxy_cookie_domains,"
            "haproxy_cookie_dynamic_cookie_key,strict_transport_security,"
            "cookie_attribute_secure,email_level,email_to,agent_inter"
        )

        column_widths: list[int] = split_commas(
            "20,20,80,20,20,30,25,20,20,25,"
            "25,20,20,20,20,25,25,30,20,25,"
            "25,25,20,25,20,20,20,25,20,20,"
            "25,30,25,30,25,40,25,25,30,25,"
            "30,30,30,30,30,30,30,30,30,30,"
            "30,30,30,30,30,30,30,20,20,30"
        )

        rows = []

        for node in nodes:
            self.report_unknown_node_elements(node, node_names)
            row = []

            for node_name in node_names:
                value = self.adjust_node(xml_findone(node, node_name))
                row.append(value)
            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name="HAProxy Pools",
            header_row=node_names,
            data_rows=rows,
            column_widths=column_widths,
        )
