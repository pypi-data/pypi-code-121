from sqlalchemy import create_engine
from .utils import get_env_vars
from .umnetdb import UMnetdb
import logging
import ipaddress

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

class UMnetinfo(UMnetdb):
    '''
    This class wraps helpful netinfo db queries in python.
    '''
    def __init__(self, host='kannada.web.itd.umich.edu', port=1521):

        eqdb_creds = get_env_vars(['NETINFO_USERNAME','NETINFO_PASSWORD'])
        self._url = f"oracle://{eqdb_creds['NETINFO_USERNAME']}:{eqdb_creds['NETINFO_PASSWORD']}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID=KANNADA)))"
        self._e = create_engine(self._url)
        

    def get_network_by_name(self, netname, active_only=False):
        '''
        Looks up a network by netname.
        '''
        select = [
                "p.itemname as netname",
                "i.itemname as ipv4_subnet",
                "six_i.itemname as ipv6_subnet",
                "NVL(n.vlanid,n.local_vlanid) as vlan_id",
                "s.statusdes as status",
                ]
        table = "UMNET_ONLINE.ITEM p"
        joins = [
                "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
                "join UMNET_ONLINE.STATUS_CODE s on p.statuscd = s.statuscd",
                "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
                "left outer join UMNET_ONLINE.IP_SUBNET ip on i.itemidnum = ip.itemidnum",
                "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
                "left outer join UMNET_ONLINE.IP6NET six on r.itemidnum = six.itemidnum",
                "left outer join UMNET_ONLINE.ITEM six_i on six.itemidnum = six_i.itemidnum",
                ]
        where = [
                f"p.itemname = '{netname}'",
            ]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        # there are also IPv4 subnets that are "pending removal" or "pending activation"
        # tied to the network in the RELATED_ITEM table, we need to find those too.
        # doing it as a separate query to maintain existing results row structure
        select = [
                "p.itemname as netname",
                "r_i.itemname as ipv4_subnet",
                "'' as ipv6_subnet",
                "NVL(n.vlanid,n.local_vlanid) as vlan_id",
                "r.itemreltypcd as status",
                ]     
        joins = [
                "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
                "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
                "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
                "left outer join UMNET_ONLINE.ITEM r_i on r.itemidnum = r_i.itemidnum",
        ]
        where = [
            f"p.itemname = '{netname}'",
            "r_i.itemcatcd = 'IP'",
        ]
        # if we're doing active only, we only want "pending removal"
        if active_only:
            where.append("r.itemreltypcd = 'IP-PRNET'")

        sql = self._build_select(select, table, joins=joins, where=where)
        more_results = self._execute(sql)

        if more_results:
            results.extend(more_results)


        return results

    def get_network_by_ip(self, ip, active_only=False):
        '''
        Looks up a network based on an IPv4 or IPv6 address. Returns the netname,
        vlan id, as well as *all active subnets* (IPv4 and IPv6) tied to the netname.
        '''

        ip = ipaddress.ip_address(ip)

        # to make our lives simpler we're breaking this up into two steps.
        # first let's find the network entry in the 'item' table
        if ip.version == 4:
            select = ["NVL(p.itemidnum, r.relitemidnum) as id"]
            table = 'UMNET_ONLINE.IP_SUBNET ip'
            joins = [
                "join UMNET_ONLINE.ITEM i on ip.itemidnum = i.itemidnum",
                "left outer join UMNET_ONLINE.RELATED_ITEM r on r.itemidnum = ip.itemidnum",
                "left outer join UMNET_ONLINE.ITEM p on i.parentitemidnum = p.itemidnum",
                ]
            where = [
                    f"{int(ip)} >= ip.ADDRESS32BIT",
                    f"{int(ip)} <= ip.ENDADDRESS32BIT",
                    "NVL(p.itemidnum, r.relitemidnum) is not null",
                    ]

        # IPv6 table is related to the 'item' table via the RELATED_ITEM table
        elif ip.version == 6:
            select = ["p.itemidnum"]
            table = 'UMNET_ONLINE.IP6NET ip'
            joins = [
                'join UMNET_ONLINE.RELATED_iTEM r on r.itemidnum = ip.itemidnum',
                'join UMNET_ONLINE.ITEM p on p.itemidnum = r.relitemidnum',
                    ]
            # and the start/end addresses are stored as hex strings
            addr_str = ip.exploded.replace(":","")
            where = [
                    f"'{addr_str}' >= ip.ADDRESS128BIT",
                    f"'{addr_str}' <= ip.ENDADDRESS128BIT",
                    ]

        sql = self._build_select(select, table, joins=joins, where=where)
        network = self._execute(sql)

        if not(network):
            return False
        net_id = network[0][0]

        # Now let's use the network itemidnum to find all associated subnets
        # with that network, as well as the netname and VLAN ID
        select = [
                "p.itemname as netname",
                "i.itemname as ipv4_subnet",
                "six_i.itemname as ipv6_subnet",
                "NVL(n.vlanid,n.local_vlanid) AS vlan_id",
                "i.itemcatcd as ITEMCAT",
                "p.itemcatcd as PCAT",
                "r.itemreltypcd as RELCAT",
                ]
        table = "UMNET_ONLINE.ITEM p"
        joins = [
                "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
                "join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
                "join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
                "join UMNET_ONLINE.IP6NET six on r.itemidnum = six.itemidnum",
                "join UMNET_ONLINE.ITEM six_i on six.itemidnum = six_i.itemidnum",
                ]
        where = [
                f"p.itemidnum = {net_id}",
            ]


        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        # there are also IPv4 subnets that are "pending removal" or "pending activation"
        # tied to the network in the RELATED_ITEM table, we need to find those too.
        # doing it as a separate query to maintain existing results row structure
        select = [
                "p.itemname as netname",
                "r_i.itemname as ipv4_subnet",
                "'' as ipv6_subnet",
                "NVL(n.vlanid,n.local_vlanid) AS vlan_id",
                "r.itemreltypcd as RELTYPCD",
        ]
        joins = [
                "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
                "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
                "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
                "left outer join UMNET_ONLINE.ITEM r_i on r.itemidnum = r_i.itemidnum",
        ]
        where = [
            f"p.itemidnum = {net_id}",
            "r_i.itemcatcd = 'IP'",
        ]
        # if we're doing active only, we only want "pending removal"
        if active_only:
            where.append("r.itemreltypcd = 'IP-PRNET'")

        sql = self._build_select(select, table, joins=joins, where=where)
        more_results = self._execute(sql)

        if more_results:
            results.extend(more_results)

        return results

    
    def get_vrfs(self, vrf_name=None, rd=None):
        '''
        Pulls data from the vrf table on netinfo. If you supply a name and/or rd, it filters only
        for that vrf. Otherwise it returns all VRFs
        '''

        select = [
            "shortname",
            "route_distinguisher",
            "default_vrf",
            "inside_vrf",
        ]
        table = "UMNET_ONLINE.VRF"

        where = []
        if vrf_name:
            where.append(f"shortname = '{vrf_name}'")
        if rd:
            where.append(f"route_distinguisher = '{rd}'")

        sql = self._build_select(select, table, where=where)
        results = self._execute(sql)

        return results

    def get_special_acl(self, netname:str):
        '''
        Looks for a special ACL assignment by netname
        '''
        select = ["acl.itemname"]
        table = "UMNET_ONLINE.ITEM net"
        joins = [
            "join UMNET_ONLINE.FILTER_NETWORK fn on fn.net_itemidnum = net.itemidnum",
            "join UMNET_ONLINE.ITEM acl on fn.filter_itemidnum = acl.itemidnum",
            ]
        where = [f"net.itemname='{netname}'"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results
    
    def get_asns(self, name_filter:str=""):
        '''
        Pulls all the ASNs from the AUTONOMOUS_SYSTEM
        table, optionally filtering by asname
        '''
        select = ["ASNAME", "ASN"]
        table = "UMNET_ONLINE.AUTONOMOUS_SYSTEM"

        where = []
        if name_filter:
            where = [f"ASNAME like '%{name_filter}%'"]

        sql = self._build_select(select, table, where=where)
        results = self._execute(sql)

        return results
