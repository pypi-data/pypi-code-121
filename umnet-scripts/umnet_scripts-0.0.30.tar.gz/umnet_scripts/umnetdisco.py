from sqlalchemy import create_engine
import re
from .utils import get_env_vars, is_ip_address, is_mac_address, expand_interface
import logging
from .umnetdb import UMnetdb

logger = logging.getLogger(__name__)

class Umnetdisco(UMnetdb):
    '''
    This class wraps helpful netdisco db queries in python.
    The API is lame.
    '''
    def __init__(self, host='172.0.0.1', port=5432):

        creds = get_env_vars(['NETDISCO_DB_USER','NETDISCO_DB_PASSWORD'])

        self._url = f"postgresql://{creds['NETDISCO_DB_USER']}:{creds['NETDISCO_DB_PASSWORD']}@{host}:{port}/netdisco"
        self._e = create_engine(self._url)
        
        logger.debug(f"Created DB engine {self._url}")


    def host_arp(self, host, start_time=None, end_time=None, limit=1, active_only=False):
        '''
        Does an ARP query against the netdisco db for a single host. 
        :host: A string representing a MAC address or an IPv4 address
        '''

        # what table are we querying?
        table = 'node_ip nip'
        joins = ['join node n on nip.mac = n.mac']

        # define select statements
        select = ['nip.mac', 'nip.ip', 'n.switch', 'n.port', 'nip.time_first', 'nip.time_last']

        # First determine if this host is a MAC address or an IP
        where = []
        if is_mac_address(host):
            where.append(f"nip.mac ='{host}'")
        elif is_ip_address(host, version=4):
            where.append(f"nip.ip ='{host}'")
        else:
            raise ValueError(f"{host} is not a valid IP or mac address")

        # filter for specific start/end times if specified
        if start_time and end_time:
            where.append(f"n.time_last between timestamp '{start_time}' and timestamp '{end_time}'")
        elif start_time:
            where.append(f"n.time_last > timestamp '{start_time}'")

        # filter for active if defined
        if active_only:
            where.append(f"nip.active = true")

        # order by last seen
        sql = self._build_select(select, table, joins=joins, where=where, order_by="time_last", limit=limit)
        result = self._execute(sql)

        return result

    def arp_count(self, prefix=None, start_time=None, end_time=None, active_only=False):
        '''
        Queries the host data in netdisco based on prefix and start/end time.
        First any prefix greater than or equal to the inputted prefix is searched for
        (in the 'device_ip' table).

        Then the host table is queried.
        '''
        
        # We're counting all the host IPs by subnet
        select = ['count(distinct nip.ip)', 'dip.subnet']
        table = 'node_ip nip'

        # postgres allows us to do a join based on an IPs (type inet) membership
        # of a subnet (type cidr)
        joins = ['join device_ip dip on nip.ip <<= dip.subnet']

        # grouping by subnet is what gives us per-subnet host counts
        group_by = 'dip.subnet'

        # append all cli filtering options
        where = [f"dip.subnet <<= inet '{prefix}'"]
        if start_time and end_time:
            where.append(f"nip.time_last between timestamp '{start_time}' and timestamp '{end_time}'")
        elif start_time:
            where.append(f"nip.time_last > timestamp '{start_time}'")

        if active_only:
            where.append(f"nip.active = true")

        sql = self._build_select(select, table, joins=joins, where=where, group_by=group_by)
        return self._execute(sql)

    def neighbors(self, device=None):
        '''
        Queries the device_ip table in netdisco to get neighbors of a device.
        If no device is specified, all neighbors are pulled.
        The device input can be an IPv4 address or an FQDN.
        '''

        select = [ 'dp.ip as local_ip',
                   'ld.dns as local_dns',
                   'dp.port as local_port',
                   'dp.remote_ip',
                   'rd.dns as remote_dns',
                   'dp.remote_port']
        table = 'device d'
        joins = ['join device_port dp on d.ip = dp.ip',
                 'join device ld on dp.ip = ld.ip',
                 'join device rd on dp.remote_ip = rd.ip']

        where = ['dp.remote_ip is not null']
        if is_ip_address(device):
            where.append(f"d.ip = '{device}'")
        elif device:
            where.append(f"d.dns = '{device}'")

        sql = self._build_select(select, table, joins, where)
        return self._execute(sql)

    def get_devices(self, match_subnets=None, exclude_subnets=None):
        '''
        Queries netdisco for a list of devices.
        Optionally, limit it by a list of prefixes
        '''

        select = [ 'ip', 'dns', 'serial', 'model', 'vendor', 'os' ]
        table = 'device'

        where = []
        if match_subnets:
            where.append(" or\n".join([f"ip << inet '{s}'" for s in match_subnets]))
        
        if exclude_subnets:
            where.append("not\n" + " or\n".join([f"ip << inet '{s}'" for s in exclude_subnets]))

        sql = self._build_select(select, table, where=where)
        return self._execute(sql)
