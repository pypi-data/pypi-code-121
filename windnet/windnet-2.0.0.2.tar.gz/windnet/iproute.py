
#coding=utf-8

# /*
#  * @Author: Guofeng He 
#  * @Date: 2022-05-20 14:52:28 
#  * @Last Modified by:   Guofeng He 
#  * @Last Modified time: 2022-05-20 14:52:28 
#  */



class IPTool(object):
    int2ip = lambda x: '.'.join([str(int(x / (256 ** i) % 256)) for i in range(3, -1, -1)])
    ip2int = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])
    @staticmethod
    def get_ip_mask(ip_string):
        ipmask = ip_string.split("/")
        ip = IPTool.ip2int(ipmask[0] if len(ipmask) else "0.0.0.0")
        mask = int(ipmask[1] if len(ipmask)>1 else "32")
        return ip,mask
    @staticmethod
    def net_range(ip_string):
        ip,mask = IPTool.get_ip_mask(ip_string)
        start = (ip >> (32-mask) << (32-mask)) +1
        end = start + 2**(32-mask) -2
        return start,end

    @staticmethod
    def include(net1:str,net2:str)->bool:
        '''
        判断是否net1 是否包含 net2

        Args:
            net1 (str): 192.168.1.1/32
            net2 (str): 192.168.1.0/24

        Returns:
            bool: _description_
        '''
        net1_start,net1_end = IPTool.net_range(net1)
        net2_start,net2_end = IPTool.net_range(net2)
        if net1_start<=net2_start and net1_end>=net2_end:
            #  or \
            # net1_start>=net2_start and net1_end<=net2_end:
            return True
        return False


class Host(object):
    def __init__(self,id:str,ip:str="0.0.0.0/0") -> None:
        self.id = id
        self.ip,self.mask = IPTool.get_ip_mask(ip)
        pass

    @property
    def ip_string(self):
        return IPTool.int2ip(self.ip)+"/"+str(self.mask)

    def load(self,host_dict:dict):
        self.ip,self.mask = IPTool.get_ip_mask(host_dict.get("ip",""))
        return self
    
    def dump(self)->dict:
        return {"ip":self.ip_string}


class RouteEntry(object):
    def __init__(self,net,peer_id="local",distance=0) -> None:
        self.net = net
        self.peer_id = peer_id
        self.distance = distance
        pass

    def load(self,entry_dict:dict):
        self.net = entry_dict.get("net",self.net)
        self.peer_id = entry_dict.get("peer",self.peer_id)
        self.distance = entry_dict.get("distance",self.distance)
        return self

    def dump(self):
        return {"net":self.net,"peer":self.peer_id,"distance":self.distance}

    def set(self,peer_id,distance):
        '''
        _summary_

        Args:
            peer_id (_type_): _description_
            distance (_type_): _description_

        Returns:
            RouteEntry: None 没有变化
                        
        '''
        if distance < self.distance:
            self.peer_id = peer_id
            self.distance = distance
            return self
        return None

    def clone(self):
        return RouteEntry(self.net,self.sae_id,self.distance)
    
    # def copy_neighbor(self):
    #     return RouteEntry(self.net,self.sae_id,self.distance+1)
        
class Router(object):
    def __init__(self,router_id,router_ip="",transit:bool=False) -> None:
        self.entrys = {}  # {entry:routeentry}
        self.router_id = router_id

        self.neighbors = {} #{router_id:router}
        self.transit = transit
        self.router_ip = router_ip
        self.add(self.router_ip)
        pass

    def load(self,route_dict:dict):
        self.entrys = {}
        for net,entry in route_dict.items():
            self.entrys[net] = RouteEntry(net).load(entry)
        return self

    def dump(self):
        data = {}
        for entry in self.entrys.values():
            data[entry.net] = entry.dump()
        return data

    def add(self,net:str,peer_id="local",distance:int=0)->RouteEntry:
        '''
        _summary_

        Args:
            net (str): _description_
            peer_id (str, optional): _description_. Defaults to "local".
            distance (int, optional): _description_. Defaults to 0.

        Returns:
            RouteEntry: 成功添加后的RouteEntry，如果没有变化则返回None
        '''
        
        route_entry:RouteEntry = self.entrys.get(net,None)
        if route_entry:
            current_entry = route_entry.set(peer_id,distance)
        else:
            current_entry = RouteEntry(net,peer_id,distance)
            self.entrys[net] = current_entry
        if current_entry:
            self.check_duplication()
            if self.get_route_entry(net):
                self.cast_add(current_entry)
        return current_entry

    def check_duplication(self):
        for net1 in list(self.entrys.keys()):
            for net2 in list(self.entrys.keys()):
                if net1 == net2 :
                    continue
                entry1 = self.get_route_entry(net1)
                entry2 = self.get_route_entry(net2)
                if entry1 and entry2:
                    if IPTool.include(net1,net2) and entry1.peer_id == entry2.peer_id:
                        self.del_route_entry(entry2)
                    if IPTool.include(net2,net1) and entry1.peer_id == entry2.peer_id:
                        self.del_route_entry(entry1)
        return 
                    
    def delete(self,net:str,peer_id="local")->RouteEntry:
        '''
        _summary_

        Args:
            net (str): _description_
            peer_id (str, optional): _description_. Defaults to "local".

        Returns:
            RouteEntry: 成功删除后的RouteEntry，如果没有变化则返回None
        '''

        route_entry:RouteEntry = self.entrys.get(net,None)
        if route_entry:
            if route_entry.peer_id == peer_id:
                re = self.entrys.pop(net)
                self.cast_delete(route_entry)
                return re
        else:
            return None

    def add_entrys(self,entrys:set,peer_id="local",distance:int=0):
        for net in entrys:
            self.add(net,peer_id,distance)
        return self

    def del_entrys(self,entrys:set):
        for net in entrys:
            self.delete(net)
        return self       

    def add_route_entry(self,route_entry:RouteEntry):
        return self.add(route_entry.net,route_entry.peer_id,route_entry.distance)

    def get_route_entry(self,net:str)->RouteEntry:
        return self.entrys.get(net,None)

    def del_route_entry(self,route_entry:RouteEntry)->RouteEntry:
        return self.delete(route_entry.net,route_entry.peer_id)
        
    def add_neighbor_route_entrys(self,neighbor):
        for entry in neighbor.entrys.values():
            self.add(entry.net,neighbor.router_id,entry.distance+1)
        return self

    def del_neighbor_route_entrys(self,neighbor):
        for entry in self.entrys.values():
            self.delete(entry.net,neighbor.router_id)
        return self

    def add_neighbor(self,neighbor,both:bool=True):
        if neighbor in self.neighbors.values():
            return self
        self.neighbors[neighbor.router_id]=neighbor
        if self.transit:
            self.add_neighbor_route_entrys(neighbor)
        if both:
            neighbor.add_neighbor(self,False)
        return self

    def del_neighbor(self,neighbor,both:bool=True):
        router_id = neighbor.router_id
        if router_id in self.neighbors.keys():
            self.pop(router_id)
            self.del_neighbor_route_entrys(neighbor)
        if both:
            neighbor.del_neighbor(self,False)
        return 

    def clear_neighbors(self):
        for neighbor in self.neighbors.values():
            self.del_neighbor(neighbor,both=True)
        return 
    
    def cast_add(self,route_entry):
        for router in self.neighbors.values():
            if router.transit:
                router.add(route_entry.net,self.router_id,route_entry.distance+1)
        return 

    def cast_delete(self,route_entry:RouteEntry):
        for router in self.neighbors.values():
            if router.transit:
                router.delete(route_entry.net,self.router_id)
        return 

    def get_route(self,net:str="")->str:
        '''
        获得指定网段的路由字符串

        Args:
            net (str, optional): _description_. Defaults to "".

        Returns:
            str: _description_
        >>> router1 = Router("router1","192.168.1.1/32",transit=True)
        >>> router2 = Router("router2","192.168.2.4/32")
        >>> router3 = Router("router3","192.168.3.1/32",transit=True)
        >>> re = router1.add("192.168.1.0/24") 
        >>> re = router2.add("192.168.2.0/24")
        >>> r = router1.add_neighbor(router2)
        >>> router1.get_route("192.168.1.0/24")
        {'net': '192.168.1.0/24', 'peer': 'local', 'distance': 0}
        >>> router1.get_route("192.168.2.0/24")
        {'net': '192.168.2.0/24', 'peer': 'router2', 'distance': 1}
        >>> router1.get_entrys()
        ['192.168.1.0/24', '192.168.2.0/24']
        >>> router1.get_entrys("router2")
        ['192.168.2.0/24']
        >>> router2.get_entrys()
        ['192.168.2.0/24']
        >>> r = router3.add_neighbor(router1)
        >>> re = router3.add("192.168.3.0/24")
        >>> router3.get_route("192.168.2.0/24")
        {'net': '192.168.2.0/24', 'peer': 'router1', 'distance': 2}
        >>> router1.dump()
        {'192.168.1.0/24': {'net': '192.168.1.0/24', 'peer': 'local', 'distance': 0}, '192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'router2', 'distance': 1}, '192.168.3.0/24': {'net': '192.168.3.0/24', 'peer': 'router3', 'distance': 1}}
        >>> router2.dump()
        {'192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'local', 'distance': 0}}
        >>> router3.dump()
        {'192.168.1.0/24': {'net': '192.168.1.0/24', 'peer': 'router1', 'distance': 1}, '192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'router1', 'distance': 2}, '192.168.3.0/24': {'net': '192.168.3.0/24', 'peer': 'local', 'distance': 0}}
        >>> re = router2.delete("192.168.2.0/24")
        >>> router1.get_entrys()
        ['192.168.1.0/24', '192.168.3.0/24']


        '''
        re = self.get_route_entry(net)
        return re.dump() if re else {}

    def get_entrys(self,peer_id:str=""):
        if peer_id:
            return list(x.net for x in self.entrys.values() if x.peer_id == peer_id)
        else:
            return list(self.entrys.keys())

    def get_neighbors(self)->list:
        return list(self.neighbors.keys())
        


class IPTable(object):
    def __init__(self,pool) -> None:
        self.set_pool(pool)
        self.hosts = {}  #{host_id:host}
        pass

    def load(self,hosts:dict={}):
        self.hosts = {}
        for host_id,host_info in hosts.items():
            self.hosts[host_id]=Host(host_id).load(host_info)
        return self
    
    def dump(self,hosts:list=[]):
        hosts_dict = {}
        for host_id,host in self.hosts.items():
            hosts_dict[host_id]=host.dump()
        return hosts_dict

    def set_pool(self,pool:str):
        self.pool = pool
        ip,mask = IPTool.get_ip_mask(pool)
        self.mask = mask
        self._start = (ip >> (32-mask) << (32-mask)) +1
        self._end = self._start + 2**(32-mask) -2
        return 

    def ip_in_use(self,ip:int)->bool:
        for host in self.hosts.values():
            if host.ip == ip:
                return True
        return False

    def add_host(self,host:Host)->Host:
        self.hosts[host.id]=host
        return host

    def get_host(self,host_id:str)->Host:
        return self.hosts.get(host_id,None)
    
    def del_host(self,host_id:str)->Host:
        return self.release(host_id)

    def assign(self,host_id:str,ip:str=None)->str:
        '''
        分配地址或查询该主机地址

        Args:
            host_id (str): 主机id
            ip (str, optional): ip地址为空，则分配一个，否则指定ip。 Defaults to None.

        Returns:
            str: host_id 对应的地址

        >>> iptable = IPTable("192.0.1.0/24")
        >>> iptable.assign("test")
        '192.0.1.1/32'
        >>> iptable.assign("sae","192.0.1.254/32")
        '192.0.1.254/32'
        >>> iptable.dump()
        {'test': {'ip': '192.0.1.1/32'}, 'sae': {'ip': '192.0.1.254/32'}}
        '''
        if ip:
            self.hosts[host_id]=Host(host_id,ip)
            return ip
        elif host_id in self.hosts.keys():
            return self.hosts[host_id].ip_string
        else:
            return self.dhcp(host_id)
        return None
    
    def dhcp(self,host_id:str)->str:
        for ip in range(self._start,self._end):
            if not self.ip_in_use(ip):
                ip_s = IPTool.int2ip(ip)+"/32"
                self.hosts[host_id]=Host(host_id,ip_s)
                return ip_s
        return None

    def release(self,host_id:str):
        return  self.hosts.pop(host_id,None)



if __name__== '__main__':
    router1 = Router("router1","192.168.1.1/32",transit=True)
    router2 = Router("router2","192.168.2.1/32")
    router3 = Router("router3","192.168.3.1/32",transit=True)
    re = router1.add("192.168.1.0/24") 
    re = router2.add("192.168.2.0/24")
    r = router1.add_neighbor(router2)
    print(router1.get_route("192.168.1.0/24"))
    # {'net': '192.168.1.0/24', 'peer': 'local', 'distance': 0}
    print(router1.get_route("192.168.2.0/24"))
    # {'net': '192.168.2.0/24', 'peer': 'router2', 'distance': 1}
    print(router1.get_entrys())
    # ['192.168.1.0/24', '192.168.2.0/24']
    print(router1.get_entrys("router2"))
    # ['192.168.2.0/24']
    print(router2.get_entrys())
    # ['192.168.2.0/24']
    r = router3.add_neighbor(router1)
    re = router3.add("192.168.3.0/24")
    print(router3.get_route("192.168.2.0/24"))
    # {'net': '192.168.2.0/24', 'peer': 'router1', 'distance': 2}
    print(router1.dump())
    # {'192.168.1.0/24': {'net': '192.168.1.0/24', 'peer': 'local', 'distance': 0}, '192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'router2', 'distance': 1}, '192.168.3.0/24': {'net': '192.168.3.0/24', 'peer': 'router3', 'distance': 1}}
    print(router2.dump())
    # {'192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'local', 'distance': 0}}
    print(router3.dump())
    # {'192.168.1.0/24': {'net': '192.168.1.0/24', 'peer': 'router1', 'distance': 1}, '192.168.2.0/24': {'net': '192.168.2.0/24', 'peer': 'router1', 'distance': 2}, '192.168.3.0/24': {'net': '192.168.3.0/24', 'peer': 'local', 'distance': 0}}
    re = router2.delete("192.168.2.0/24")
    print(router1.get_entrys())
    # ['192.168.1.0/24', '192.168.3.0/24']