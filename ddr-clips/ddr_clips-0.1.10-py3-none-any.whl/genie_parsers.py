import re
import sys
from lxml import etree
import xml.dom.minidom
import xml.etree.ElementTree as ET

def genie_str_to_class(classname):
    try:
        module = getattr(sys.modules[__name__], classname)
        return module()
    except Exception as e:
        return '%%%%% No genie module with name: ' + classname

# ==================================================
# Parser for 'show vlan id <vlan id> Get the ports associated if it exists
# ==================================================
class ShowVlanId():

    def parse(self, output=None):

    # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_vlan_ports', {})

    # VLAN Name Status Ports
    # ---- -------------------------------- --------- -------------------------------
    # 2 VLAN0002 active Gi1/0/1, Gi1/0/2

        p1 = re.compile(r'.*active(\s+)(?P<port>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                port = str(group["port"]).rstrip(",")
                port_dict = dict.setdefault(port, {})
                break
        return parsed_dict

# ==================================================
# Parser for 'show monitor capture CAP buffer brief
# ==================================================
class ShowMonitorCapture():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('bgp_keepalive', {})

        #   181 150.405563   10.1.12.1 -> 10.1.3.3 BGP 73 KEEPALIVE Message
        p1 = re.compile(r'.{17}(?P<localhost>(\S+)).{4}(?P<neighbor>(\S+))(\s+)BGP 73 KEEPALIVE Message')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                localhost = str(group["localhost"])
                host_dict = dict.setdefault(localhost, {})
                host_dict['neighbor'] = str(group['neighbor'])
                host_dict['message'] = "BGP_73_KEEPALIVE_Message"                
                break
        return parsed_dict

# ==================================================
# Parser for 'show ip route 10.1.12.1 Get the ip route if it exists
# ==================================================
class ShowIpRouteVlan():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_vlan', {})

        #   Local host: 10.1.12.1, Local port: 33984
        p1 = re.compile(r'.*directly connected,(\s+)via(\s+)(?P<vlan>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                vlan = str(group["vlan"])
                vlan_number = vlan.replace("Vlan", "")
                vlan_dict = dict.setdefault(vlan_number, {})
                break
        return parsed_dict


# ==================================================
# Parser for 'show ip bgp neighbor | include Local' - extract local IP address
# ==================================================
class ShowIpBgpNeighbor():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('bgp_neighbor', {})

        #   Local host: 10.1.12.1, Local port: 33984
        p1 = re.compile(r'Local host:.{1}(?P<local>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                host = str(group["local"].rstrip(','))
                host_dict = dict.setdefault(host, {})
                break
        return parsed_dict


# ==================================================
# Parser for 'show tech acl' - extract image name
# ==================================================
class ShowTechAclImage():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_image', {})

        #   System image file is "flash:cat9k_iosxe.2020-09-23_18.29_petervh.SSA.bin"
        p1 = re.compile(r'System image file is.{1}(?P<image>(\S+))')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                image = str(group["image"].lstrip('"').rstrip('"'))
                image_dict = acl_dict.setdefault(image, {})
                break
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract platform information
# ==================================================
class ShowTechAclPlatform():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_platform', {})

#        Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver.
#        ------  -----   ---------             -----------  --------------  -------       --------
#         1       41     C9300-24T             FCW2123L0H4  a0f8.490e.4a80  V01           17.05.01
        p0 = re.compile(r'Switch(\s+)Ports(\s+)Model(\s+)Serial.*')
        p1 = re.compile(r'(?P<switch>(\d+))(\s+)(\d+)(\s+)(?P<model>(\S+))(\s+)(?P<serial>(\S+))(\s+)(?P<mac>(.{14}))(\s+)(?P<hwver>(\S+))(\s+)(?P<swver>(\S+)).*')
        skip = 0
        for line in output.splitlines():
            line = line.strip()
    #
    # Find the line with the column headers for platform information then skip to the actual data
    #
            if skip == 2:
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    switch = str(group["switch"].lstrip('"').rstrip('"'))
                    switch_dict = acl_dict.setdefault(switch, {})
                    switch_dict['model'] = str(group['model'])
                    switch_dict['serial'] = str(group['serial'])
                    switch_dict['mac'] = str(group['mac'])
                    switch_dict['hwver'] = str(group['hwver'])
                    switch_dict['swver'] = str(group['swver'])
                    return parsed_dict

            if skip == 1:
                skip = 2
            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL names
# ==================================================
class ShowTechAclNames():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_names', {})

#------------------ show access-lists ------------------------
#
#
#Extended IP access list IP-Adm-V4-Int-ACL-global
#IPv6 access list implicit_permit_v6

        p0 = re.compile(r'-*(\s+)show(\s+)access-lists.*')
        p1 = re.compile(r'Extended(\s+)IP(\s+)access(\s+)list(\s+)(?P<v4acl>(\S+)).*')
        p2 = re.compile(r'IPv6(\s+)access(\s+)list(\s+)(?P<v6acl>(\S+)).*')
        skip = 0

        for line in output.splitlines():
            line = line.strip()
    #
    # Find the line with the column headers for ACL names then skip to the actual data
    #
            if skip == 3:
                mv4 = p1.match(line)
                if mv4:
                    group = mv4.groupdict()
                    acl_type = "ipv4"
                    switch_dict = acl_dict.setdefault(acl_type, {})
                    switch_dict['name'] = str(group['v4acl'])
                    continue

                mv6 = p2.match(line)
                if mv6:
                    group = mv6.groupdict()
                    acl_type = "ipv6"
                    switch_dict = acl_dict.setdefault(acl_type, {})
                    switch_dict['name'] = str(group['v6acl'])
                    continue

            if skip == 2:
                skip = 3
            if skip == 1:
                skip = 2
            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL counters
# ==================================================
class ShowTechAclCounters():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_counters', {})

#=========== Cumulative Stats Across All Asics ===========
#Ingress IPv4 Forward             (0x12000003):         873 frames

        p0 = re.compile(r'=========== Cumulative Stats Across All Asics.*')
        p1 = re.compile(r'(?P<counter>(\S+\s+\S+\s+\S+))\s+\((?P<mask>(.{10})).{2}\s+(?P<frames>(\d+)).*')
        skip = 0

        for line in output.splitlines():
            line = line.strip()
    #
    # Find the ACL counter header line then skip to the actual data
    #
            if skip == 1:
                cnt = p1.match(line)
                if cnt:
                    group = cnt.groupdict()
                    if int(group['frames']) != 0:
                        counter = str(group['counter'])
                        switch_dict = acl_dict.setdefault(counter, {})
                        switch_dict['mask'] = str(group['mask'])
                        switch_dict['frames'] = str(group['frames'])
                continue

            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL Exception Statistics
# ==================================================
class ShowTechAclExceptions():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_exceptions', {})

#****EXCEPTION STATS ASIC INSTANCE 0 (asic/core 0/0)****
#=================================================================================
# Asic/core |                NAME                  |   prev   |  current  |  delta
#=================================================================================
#0  0  NO_EXCEPTION                                   0          277         277

        p0 = re.compile(r'.*EXCEPTION STATS ASIC INSTANCE.*')
        p1 = re.compile(r'(?P<asic>(\d+))(\s+)(?P<core>(\d+))(\s+)(?P<name>(.{40}))(\s+)(?P<prev>(\d+))(\s+)(?P<current>(\d+))(\s+)(?P<delta>(\d+)).*')
        skip = 0
        record = 1
        for line in output.splitlines():
            line = line.strip()
    #
    # Find the ACL counter header line then skip to the actual data
    #
            try:
                if skip == 1:
                    cnt = p1.match(line)
                    if cnt:
                        group = cnt.groupdict()
                        if int(group['current']) != 0:
                            switch_dict = acl_dict.setdefault(str(record), {})
                            switch_dict['asic'] = int(group['asic'])
                            switch_dict['core'] = int(group['core'])
                            switch_dict['name'] = str(group['name']).rstrip().replace(" ", "_")
                            switch_dict['prev'] = int(group['prev'])
                            switch_dict['current'] = int(group['current'])
                            switch_dict['delta'] = int(group['delta'])
                            record = record + 1
                    continue

                if skip == 0:
                    match = p0.match(line)
                    if match:
                        skip = 1
            except Exception as e:
                print("%%%% DDR Error: ShowTechAclExceptions parser: " + str(e))
        return parsed_dict

# ==================================================
# Parser for 'show mac address-table dynamic'
# ==================================================
class ShowMatm():

    ''' Parser for "show mac address-table dynamic" '''

    cli_command = ['show mac address-table dynamic',
                   'show mac address-table dynamic vlan {vlan_id}']

    def parse(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
                out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        #   50    0000.063b.9e74    DYNAMIC     pw100007
        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>([a-z0-9A-Z]+))(\s+)'
                        '(?P<ports>(\S+))')

        # Total Mac Addresses for this criterion: 5 
        p2 = re.compile(r'Total +Mac +Addresses +for +this +criterion: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            #   50    0000.063b.9e74    DYNAMIC     pw100007
            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['ports'] = group['ports']
                continue

            # Total Mac number of addresses:: 1
            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

class ShowInterfaces():
    def print_class_name():
        print("here is the class name: ShowInterfaces")

class ShowProcessesMemoryPlatformSorted():

    ''' Parser for "show processes memory platform sorted" '''

    cli_command = 'show processes memory platform sorted'

    def test():
        print("this is a test from ShowProcessesMemoryPlatformSorted")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mem_dict = parsed_dict.setdefault('system_memory', {})
            procmem_dict = mem_dict.setdefault('per_process_memory', {})

        # System memory: 7703908K total, 3863776K used, 3840132K free, 
        p1 = re.compile(r'System +memory: +(?P<total>(\d+\w?)) +total,'
                        ' +(?P<used>(\d+\w?)) +used,'
                        ' +(?P<free>(\d+\w?)) +free,')

        # Lowest: 3707912K
        p2 = re.compile(r'Lowest: (?P<lowest>(\d+\w?))')


        #    Pid    Text      Data   Stack   Dynamic       RSS              Name
        # ----------------------------------------------------------------------
        #  16994  233305    887872     136       388    887872   linux_iosd-imag
        p3 = re.compile(r'(?P<pid>(\d+))(\s+)(?P<text>(\d+))(\s+)(?P<data>(\d+))'
                        '(\s+)(?P<stack>(\d+))(\s+)(?P<dynamic>(\d+))'
                        '(\s+)(?P<RSS>(\d+))(\s+)(?P<name>([\w-])+)')

        for line in out.splitlines():
            line = line.strip()
 
            m = p1.match(line)
            if m:
                group = m.groupdict()
                mem_dict['total'] = str(group['total'])
                mem_dict['used'] = str(group['used'])
                mem_dict['free'] = str(group['free'])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mem_dict['lowest'] = str(group['lowest'])
                continue

            m = p3.match(line)
            if m:
                group = m.groupdict()
                name = str(group['name'])
                one_proc_dict = procmem_dict.setdefault(name, {})
                one_proc_dict['pid'] = int(group['pid'])
                one_proc_dict['text'] = int(group['text'])
                one_proc_dict['data'] = int(group['data'])
                one_proc_dict['stack'] = int(group['stack'])
                one_proc_dict['dynamic'] = int(group['dynamic'])
                one_proc_dict['RSS'] = int(group['RSS'])
                continue

        return parsed_dict


class ShowPlatformSoftwareMemoryCallsite():
    """ Parser for show platform software memory <process> switch active <R0> alloc callsite brief """

    cli_command = 'show platform software memory {process} switch active {slot} alloc callsite brief'

    def parse(self, process, slot, output=None):

        if output is None:
            print("Error: Please provide output from the device")
            return None        
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            callsite_dict = parsed_dict.setdefault('callsites', {})

        # The current tracekey is   : 1#2315ece11e07bc883d89421df58e37b6
        p1 = re.compile(r'The +current +tracekey +is\s*: +(?P<tracekey>[#\d\w]*)')

        # callsite      thread    diff_byte               diff_call
        # ----------------------------------------------------------
        # 1617611779    31884     57424                   2
        p2 = re.compile(r'(?P<callsite>(\d+))\s+(?P<thread>(\d+))\s+(?P<diffbyte>(\d+))\s+(?P<diffcall>(\d+))')

        max_diff_call = 0
        for line in out.splitlines():
            line = line.strip()
 
            # The current tracekey is   : 1#2315ece11e07bc883d89421df58e37b6
            m = p1.match(line)
            if m:
                group = m.groupdict()
                parsed_dict['tracekey'] = str(group['tracekey'])
                continue

            # callsite      thread    diff_byte               diff_call
            # ----------------------------------------------------------
            # 1617611779    31884     57424                   2
            m = p2.match(line)
            if m:
                group = m.groupdict()
                callsite = int(group['callsite'])
                diff_call = int(group['diffcall'])
                one_callsite_dict = callsite_dict.setdefault(callsite, {})
                one_callsite_dict['thread'] = int(group['thread'])
                one_callsite_dict['diff_byte'] = int(group['diffbyte'])
                one_callsite_dict['diff_call'] = diff_call
                # print_log("&&diff_call = " + str(diff_call) + " callsite = " + str(callsite))
                if diff_call > max_diff_call:
                    max_diff_call = diff_call
                    max_callsite = callsite
                continue
        parsed_dict['max_diff_call_callsite'] = max_callsite
        # print_log("&&&&&&max_diff_call_callsite = " + str(max_callsite) + " process = " + process)
        return parsed_dict


class ShowPlatformSoftwareMemoryBacktrace():
    """ Parser for show platform software memory <process> switch active <R0> alloc backtrace """

    cli_command = 'show platform software memory {process} switch active {slot} alloc backtrace'

    def parse(self, process, slot, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None 
        else:
            out = output

         # Init vars
        parsed_dict = {}
        if out:
            backtraces_dict = parsed_dict.setdefault('backtraces', {})

        # backtrace: 1#2315ece11e07bc883d89421df58e37b6   maroon:7F740DEDC000+61F6 tdllib:7F7474D05000+B2B46 ui:7F74770E4000+4639A ui:7F74770E4000+4718C cdlcore:7F7466A6B000+37C95 cdlcore:7F7466A6B000+37957 uipeer:7F747A7A8000+24F2A evutil:7F747864E000+7966 evutil:7F747864E000+7745
        p1 = re.compile(r'backtrace: (?P<backtrace>[\w#\d\s:+]+)$')

        #   callsite: 2150603778, thread_id: 31884
        p2 = re.compile(r'callsite: +(?P<callsite>\d+), +thread_id: +(?P<thread_id>\d+)')

        #   allocs: 1, frees: 0, call_diff: 1
        p3 = re.compile(r'allocs: +(?P<allocs>(\d+)), +frees: +(?P<frees>(\d+)), +call_diff: +(?P<call_diff>(\d+))')

        for line in out.splitlines():
            line = line.strip()
 
            # backtrace: 1#2315ece11e07bc883d89421df58e37b6   maroon:7F740DEDC000+61F6 tdllib:7F7474D05000+B2B46 ui:7F74770E4000+4639A ui:7F74770E4000+4718C cdlcore:7F7466A6B000+37C95 cdlcore:7F7466A6B000+37957 uipeer:7F747A7A8000+24F2A evutil:7F747864E000+7966 evutil:7F747864E000+7745
            m = p1.match(line)
            if m:
                group = m.groupdict()
                backtrace = str(group['backtrace'])#.replace(" ", "*")
                one_backtrace_dict = backtraces_dict.setdefault(backtrace, {})
                continue

            #   callsite: 2150603778, thread_id: 31884
            m = p2.match(line)
            if m:
                group = m.groupdict()
                one_backtrace_dict['callsite'] = int(group['callsite'])
                one_backtrace_dict['thread_id'] = int(group['thread_id'])
                continue

            #   allocs: 1, frees: 0, call_diff: 1
            m = p3.match(line)
            if m:
                group = m.groupdict()
                one_backtrace_dict['allocs'] = int(group['allocs'])
                one_backtrace_dict['frees'] = int(group['frees'])
                one_backtrace_dict['call_diff'] = int(group['call_diff'])
                continue

        return parsed_dict


class ShowMemoryDebugLeaksChunks():
    """ Parser for show show memory debug leaks chunks """

    cli_command = 'show memory debug leaks chunks'

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None 
        else:
            out = output

         # Init vars
        parsed_dict = {}
        section = ""
        match_found = False
        if out:
            addresses_dict = parsed_dict.setdefault('addresses', {})


        #   Address        Size    Parent     Name                Alloc_pc
        # 7EFFCC9AB728    28 7EFFCA3DF410 (MallocLite)     :55FAE8AC9000+897EB09
        p1 = re.compile(r'^(?P<address>\w+) +(?P<size>\d+) +(?P<parent>\w+) +(?P<name>\S+)\s* (?P<alloc_pc>:\w+\+\w+)')

        # Tracekey : 1#2b336c808e968add0d0ca6a35d7a1d82
        p2 = re.compile(r'Tracekey : (?P<tracekey>[#\w]+)')

        
        for line in out.splitlines():
            line = line.strip()
 
            m = p2.match(line)
            if m:
                group = m.groupdict()
                tracekey = str(group['tracekey'])
                parsed_dict["tracekey"] = tracekey
                continue

            if 'reserve Processor memory' in line:
                section = "reserve_processor_memory"
                continue
            elif 'lsmpi_io memory' in line:
                section = "lsmpi_io_memory"
                continue
            elif 'Processor memory' in line:
                section = "processor_memory"
                continue


            m = p1.match(line)
            if m:
                group = m.groupdict()
                address = str(group['address'])
                one_address_dict = addresses_dict.setdefault(address, {})
                one_address_dict["size"] = group['size']
                one_address_dict["parent"] = str(group['parent'])
                one_address_dict["name"] = str(group['name'])
                one_address_dict["alloc_pc"] = str(group['alloc_pc'])
                one_address_dict["memory_type"] = section
                one_address_dict["tracekey"] = tracekey
                match_found = True
                continue

        if match_found:
            return parsed_dict
        else:
            return {}

#####################################################################################
#
#  Parser for TCAM memory use
#
#  Sample show command data to match:
#
#  Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
#  ------------------------------------------------------------------------------------------------------
#  Mac Address Table      EM           I       32768       22       0%        0        0        0       22
#  Mac Address Table      TCAM         I        1024       21       2%        0        0        0       21
#  L3 Multicast           EM           I        8192        0       0%        0        0        0        0
#
#####################################################################################
class ShowPlatformHardwareFedSwActiveFwdasicResourceTcamUtilization():

    ''' Parser for "show platform hardware fed sw active fwd-asic resource tcam utilization" '''

    cli_command = 'show platform hardware fed sw active fwd-asic resource tcam utilization'

    def test():
        print("this is a test from ShowPlatformHardwareFedSwActiveFwdasicResourceTcamUtilization")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output
#            out = '''MacAddressTable      TCAM         I        1024       21       2%        0        0        0       21'''

        # Init vars
        parsed_dict = {}

        if out:
            tcam_dict = parsed_dict.setdefault('tcam_table', {})
            app_dict = tcam_dict.setdefault('application', {})

        #Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
        #------------------------------------------------------------------------------------------------------
        # Mac Address Table      EM           I       32768       26       0%        0        0        0       26

        try:
            p1 = re.compile(r'(?P<table>.{27})(\s+)(?P<dir>(\S+))(\s+)(?P<max>(\d+))(\s+)(?P<used>(\d+))(\s+)(?P<pused>(\d))\..{4}(\s+)(?P<v4>(\d+))(\s+)(?P<v6>(\d+))(\s+)(?P<mpls>(\d+))(\s+)(?P<other>(\d+)).*')
        except Exception as e:
            print("%%%% DDR Error: ShowPlatformHardwareFedSwActiveFwdasicResourceTcamUtilization parser: " + str(e))

        for line in out.splitlines():
            line = line.strip()
    #
    # remove % characters from line which prevent pattern match
    #
            line = line.replace('%', '')

            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = str(group['table'])
                if "Label" in name:
                    name = 'CTSCellMatrixVPN' + name
                one_proc_dict = app_dict.setdefault(name.replace(' ', ''), {})
                one_proc_dict['dir'] = str(group['dir'])
                one_proc_dict['max'] = int(group['max'])
                one_proc_dict['used'] = int(group['used'])
                one_proc_dict['percent-used'] = int(group['pused'])
                one_proc_dict['v4'] = int(group['v4'])
                one_proc_dict['v6'] = int(group['v6'])
                one_proc_dict['mpls'] = int(group['mpls'])
                one_proc_dict['other'] = int(group['other'])
                continue
        return parsed_dict

########################################################################################
#
# ParseXRSyslogMessage parses an XR syslog message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseXRSyslogMessage():

    def syslog(self, message=None):
        ''' Parser for XR Syslog messages with the form:
            RP/0/RSP0/CPU0:Apr 26 20:30:07.568 UTC: ifmgr[257]: %PKT_INFRA-LINEPROTO-5-UPDOWN : Line protocol Up 

            Syslog FACTS will have the form 'source':'date':'time':'component':'syslog':'content' '''
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('syslog-message', {})

        try:
            p1 = re.compile(r'(?P<source>([^:]+))(?P<date>.{7})(?P<time>(.*:))'
                             '(\s+)(?P<component>(.*:))(\s+)(?P<syslog>(.*:))(\s+)(?P<content>(.*))')
        except Exception as e:
            print("%%%% DDR Error: ParseXRSyslogMessage: " + str(e))
        m = p1.match(message)
        if m:
            group = m.groupdict()
            one_proc_dict['source'] = str(group['source']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['date'] = str(group['date']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['source'] = str(group['source']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['time'] = str(group['time']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['component'] = str(group['component']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['syslog'] = str(group['syslog']).lstrip().rstrip().rstrip(":").lstrip(":").replace(" ", "_").rstrip("_")
            one_proc_dict['content'] = str(group['content']).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")

        return parsed_dict


########################################################################################
#
# ParseXESyslogMessage parses an XR syslog message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseXESyslogMessage():

    def syslog(self, message=None):
        ''' Parser for Xe Syslog messages with the form:
             *Apr 27 11:12:14.549: %SYS-5-CONFIG_I: Configured from console by admin on vty5 (10.24.105.165)
             *Apr 27 11:12:45.184: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback222, changed state to up
             *Apr 27 11:12:46.394: %SYS-5-CONFIG_I: Configured from console by admin on vty5 (10.24.105.165)

            Syslog FACTS will have the form 'source':'date':'time':'component':'syslog':'content' '''
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('syslog-message', {})

        try:
            p1 = re.compile(r'(?P<date>.{8})(?P<time>(.*:))(\s+)()(?P<syslog>(.*:))(\s+)(?P<content>(.*))')

        except Exception as e:
            print("%%%% DDR Error: ParseXESyslogMessage: " + str(e))
        m = p1.match(message)
        if m:
            group = m.groupdict()
            one_proc_dict['source'] = 'source'
            one_proc_dict['date'] = str(group['date']).lstrip().lstrip("*").rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['time'] = str(group['time']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['component'] = 'xe-syslog'
            one_proc_dict['syslog'] = str(group['syslog']).lstrip().rstrip().rstrip(":").lstrip(":").replace(" ", "_").rstrip("_")
            one_proc_dict['content'] = str(group['content']).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")

        return parsed_dict

########################################################################################
#
# ParseRFC5277Message parses a NETCONF RFC5277 notification message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseRFC5277Message():

    def rfc5277(self, message=None):
        messagexml = xml.dom.minidom.parseString(message)
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('rfc5277-message', {})

        try:
            one_proc_dict['source'] = 'source'
            one_proc_dict['datetime'] = str(messagexml.getElementsByTagName('eventTime')[0].firstChild.nodeValue)
            one_proc_dict['component'] = str(messagexml.getElementsByTagName('clogHistFacility')[0].firstChild.nodeValue)
            one_proc_dict['severity'] = str(messagexml.getElementsByTagName('clogHistSeverity')[0].firstChild.nodeValue)            
            one_proc_dict['msgname'] = str(messagexml.getElementsByTagName('clogHistMsgName')[0].firstChild.nodeValue).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")
            one_proc_dict['msgcontent'] = str(messagexml.getElementsByTagName('clogHistMsgText')[0].firstChild.nodeValue).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")
        except Exception as e:
            print("%%%% DDR Error: ParseRFC5277Message: " + str(e))

        return parsed_dict

# ==================================================
# Parser for 'show platform software fed active matm macTable'
# ==================================================
class ShowPlatformSoftwareFedActiveMatmMactable():

    ''' Parser for "show platform software fed active matm macTable vlan {vlan_id}" '''

    cli_command = ['show platform software fed active matm macTable',
                   'show platform software fed active matm macTable vlan {vlan_id}']

    def parse(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        # 1      7488.bb78.37ff         0x1      2      0      0  0x7fde0972eb88      0x7fde0972e7d8      0x0                 0x7fde0899f078            300       17  HundredGigE1/0/11               Yes

        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>(0[xX][a-f0-9A-F]+))(\s+)'
                        '(?P<seq>(\d+))(\s+)(?P<ec_bits>(\d+))(\s+)(?P<flags>(\d+))(\s+)'
                        '(?P<mac_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<si_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<ri_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<di_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<a_time>(\d+))(\s+)(?P<e_time>(\d+))(\s+)'
                        '(?P<ports>(\S+))(\s+)(?P<consistency>([a-zA-Z]+))')

        # Total Mac number of addresses:: 1
        p2 = re.compile(r'Total +Mac +number +of +addresses:: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                #one_mac_dict['vlan'] = int(group['vlan'])
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['seq'] = int(group['seq'])
                one_mac_dict['ec_bits'] = int(group['ec_bits'])
                one_mac_dict['flags'] = int(group['flags'])
                one_mac_dict['mac_handle'] = group['mac_handle']
                one_mac_dict['si_handle'] = group['si_handle']
                one_mac_dict['ri_handle'] = group['ri_handle']
                one_mac_dict['di_handle'] = group['di_handle']
                one_mac_dict['a_time'] = int(group['a_time'])
                one_mac_dict['e_time'] = int(group['e_time'])
                one_mac_dict['ports'] = group['ports']
                one_mac_dict['consistency'] = group['consistency']
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

# ==================================================
# Parser for 'show platform software fed switch active matm macTable'
# ==================================================
class ShowPlatformSoftwareFedSwitchActiveMatmMactable():

    ''' Parser for "show platform software fed switch active matm macTable vlan {vlan_id}" '''

    cli_command = ['show platform software fed switch active matm macTable',
                   'show platform software fed switch active matm macTable vlan {vlan_id}']

    def parse(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        # 1      7488.bb78.37ff         0x1      2      0      0  0x7fde0972eb88      0x7fde0972e7d8      0x0                 0x7fde0899f078            300       17  HundredGigE1/0/11               Yes

        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>(0[xX][a-f0-9A-F]+))(\s+)'
                        '(?P<seq>(\d+))(\s+)(?P<ec_bits>(\d+))(\s+)(?P<flags>(\d+))(\s+)'
                        '(?P<mac_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<si_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<ri_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<di_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<a_time>(\d+))(\s+)(?P<e_time>(\d+))(\s+)'
                        '(?P<ports>(\S+))(\s+)(?P<consistency>([a-zA-Z]+))')

        # Total Mac number of addresses:: 1
        p2 = re.compile(r'Total +Mac +number +of +addresses:: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                #one_mac_dict['vlan'] = int(group['vlan'])
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['seq'] = int(group['seq'])
                one_mac_dict['ec_bits'] = int(group['ec_bits'])
                one_mac_dict['flags'] = int(group['flags'])
                one_mac_dict['mac_handle'] = group['mac_handle']
                one_mac_dict['si_handle'] = group['si_handle']
                one_mac_dict['ri_handle'] = group['ri_handle']
                one_mac_dict['di_handle'] = group['di_handle']
                one_mac_dict['a_time'] = int(group['a_time'])
                one_mac_dict['e_time'] = int(group['e_time'])
                one_mac_dict['ports'] = group['ports']
                one_mac_dict['consistency'] = group['consistency']
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

class ShowHardwareAccessListResourceUtilization():

    ''' Parser for "show hardware access-list resource utilization" '''

    cli_command = 'show hardware access-list resource utilization'

    def test():
        print("this is a test from ShowHardwareAccessListResourceUtilization")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_tcam_dict = parsed_dict.setdefault('acl_tcam', {})

#    Protocol CAM                            0       246     0.00   
#    Mac Etype/Proto CAM                     0       14      0.00   
#    L4 op labels, Tcam 0                    0       1023    0.00   

        try:
            p1 = re.compile(r'(?P<type>.{40})(?P<used>(\d+))(\s+)(?P<free>(\d+))(\s+)(?P<percentused>\d*\.?\d*$)')

        except Exception as e:
            print("%%%% DDR Error: ShowHardwareAccessListResourceUtilization: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = str(group['type'])
                name = name.replace(' ', '').replace(',', '').replace('/', '')
                one_proc_dict = acl_tcam_dict.setdefault(name, {})
                one_proc_dict['used'] = int(group['used'])
                one_proc_dict['free'] = int(group['free'])
                one_proc_dict['percentused'] = float(group['percentused'])
                continue
        return parsed_dict
# ==================================================
# Parser for 'show vlan id <vlan id> Get first port associated if it exists
# ==================================================
class ShowSinglePortVlanId():

    def parse(self, output=None):

    # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_ports', {})

    # VLAN Name Status Ports
    # ---- -------------------------------- --------- -------------------------------
    # 2 VLAN0002 active Gi1/0/1, Gi1/0/2

    # Expected dictionary output: {'connected_ports': {'Gi1/0/2': {'port': 'Gi1/0/2'}}}
    
        p1 = re.compile(r'.*active(\s+)(?P<port>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                port = str(group["port"]).rstrip(",")
                port_dict = dict.setdefault(port, {})
                port_dict['port'] = port
                break
        return parsed_dict
        # ==================================================
# Parser for 'show lisp instance {instance_id} ipv4'
# Used when LISP instance is initialized and active
# ==================================================
class ShowLoggingLast():

    ''' Parser for "show logging last {num_lines}" '''

    cli_command = 'show logging last {num_lines}'

##################################################################
#
# Selected fields from show command response
#
##################################################################

    def test(self):
        test_message = '''
Syslog logging: enabled (0 messages dropped, 2 messages rate-limited, 0 flushes, 0 overruns, xml disabled, filtering disabled)

    Console logging: level debugging, 258 messages logged, xml disabled,
                     filtering disabled, discriminator(nosel), 
                     0 messages rate-limited, 98 messages dropped-by-MD
    Monitor logging: level debugging, 218 messages logged, xml disabled,
                     filtering disabled, discriminator(nosel), 
                     0 messages rate-limited, 98 messages dropped-by-MD
    Buffer logging:  level debugging, 358 messages logged, xml disabled,
                    filtering disabled
    Exception Logging: size (4096 bytes)
    Count and timestamp logging messages: disabled
    File logging: disabled
    Persistent logging: disabled


Showing last 4 lines

Log Buffer (102400 bytes):

*Mar 29 17:01:20.953: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021
*Mar 29 17:03:26.255: %SYS-6-LOGOUT: User admin has exited tty session 4(172.20.86.186)
*Mar 29 17:25:20.330: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 10.24.15.5] [localport: 22] at 17:25:20 UTC Mon Mar 29 2021
*Mar 29 17:26:49.017: %SYS-5-CONFIG_I: Configured from console by admin on vty3 (10.24.15.5)
'''
        expected_result='''{'log_instance': {'1': {'datetime': 'Mar 29 17:01:20.953: ', 'facility': 'SEC_LOGIN', 'level': 5, 'message': 'LOGIN_SUCCESS', 'note': ' Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021'}, '2': {'datetime': 'Mar 29 17:03:26.255: ', 'facility': 'SYS', 'level': 6, 'message': 'LOGOUT', 'note': ' User admin has exited tty session 4(172.20.86.186)'}, '3': {'datetime': 'Mar 29 17:25:20.330: ', 'facility': 'SEC_LOGIN', 'level': 5, 'message': 'LOGIN_SUCCESS', 'note': ' Login Success [user: admin] [Source: 10.24.15.5] [localport: 22] at 17:25:20 UTC Mon Mar 29 2021'}, '4': {'datetime': 'Mar 29 17:26:49.017: ', 'facility': 'SYS', 'level': 5, 'message': 'CONFIG_I', 'note': ' Configured from console by admin on vty3 (10.24.15.5)'}}}
'''

        print("\n******* ShowLoggingLast Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned ShowLoggingLast data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing ShowLoggingLast Parser\n")
                print("\nExpected ShowLoggingLast data: \n", expected_result)
                print("\nGenerated ShowLoggingLast data: \n", parsed_fact)
            else:
                print("\n%%%% ShowLoggingLast Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing ShowLoggingLast Parser: \n" + str(e))
#
# *Mar 29 17:01:20.953: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021
#
    def parse(self, num_lines=None, output=None, test=None, facility_filter=None):
        if output is None:
            if num_lines:
                cmd = self.cli_command[1].format(num_lines=num_lines)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = output
        else:
            out = output
#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            log_number = 1
            parsed_dict = {}
            instance_dict = parsed_dict.setdefault('log_instance', {}) # This is the name of the deftemplate that will contain the FACT
            for line in out.splitlines():
                line = line.strip()
                if num_lines != None:
                    if log_number > num_lines: break
#
# Compile regex for each of the lines in the output that contain required data
#
                p1 = re.compile(r'\*(?P<datetime>[^%]*)%(?P<facility>[^-]*)\-(?P<level>(\d+))\-(?P<message>[^:]*):(?P<note>.*$)') # Syslog message (see above) 
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()
 #
 # Create a parsed dictionary instnace if the facility in the logging message matches the facility_filter
 #
                    if (str(group['facility']) == str(facility_filter)) or (facility_filter == None):
                        per_instance_dict = instance_dict.setdefault(str(log_number), {})
                        per_instance_dict['datetime'] = str(group['datetime']).rstrip(': ').replace(' ','_')
                        per_instance_dict['facility'] = str(group['facility'])
                        per_instance_dict['level'] = int(group['level'])
                        per_instance_dict['message'] = str(group['message'])
                        per_instance_dict['note'] = str(group['note']).replace(' ','_').replace('"','').replace("'","")
                        log_number = log_number + 1
                    continue

            return parsed_dict
        except Exception as e:
            print("\n%%%% Error processing ShowLoggingLast: " + str(e))
            print(instance_dict)

# ==================================================
# Parser for dmiauthd btrace log - extract %DMI-5-AUTH_PASSED actions
# ==================================================

class BtraceDmiauthdConfigI():
#
# show command run to save dmiauthd log:
#   "show logging process dmiauthd start last 20 minutes to-file flash:ddr-btrace-auth"
#
# Sample log message decoded from btrace file:
#
#   "2022/05/19 18:46:45.299345847 {dmiauthd_R0-0}{1}: [errmsg] [17229]: (note): %DMI-5-AUTH_PASSED: R0/0: dmiauthd: User 'admin' authenticated successfully from 10.82.252.254:61074  for netconf over ssh. External groups: PRIV15"
#
# Parser test function
#
    def test(self):
        test_message = '''
2021/03/19 02:22:51.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3237
2021/03/19 02:22:52.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3238'''

        expected_result='''{'config_transaction': {'3237': {'transaction_id': '3237', 'date': '2021/03/19', 'time': '02:22:51.665178', 'method': 'NETCONF/RESTCONF', 'config_by': 'admin'}, '3238': {'transaction_id': '3238', 'date': '2021/03/19', 'time': '02:22:52.665178', 'method': 'NETCONF/RESTCONF', 'config_by': 'admin'}}}'''

        print("\n******* BtraceDmiauthdConfigI Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned BtraceDmiauthdConfigI data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing BtraceDmiauthdConfigI Parser\n")
                print("\nExpected BtraceDmiauthdConfigI: \n", expected_result)
                print("\nGenerated BtraceDmiauthdConfigI: \n", parsed_fact)
            else:
                print("\n%%%% BtraceDmiauthdConfigI Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing BtraceDmiauthdConfigI Parser: \n" + str(e))
#
# parser for btrace log for configurations applied to the device
#
    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        trans_dict = parsed_dict.setdefault('auth_transaction', {})

        try:
            p1 = re.compile(r'(?P<date>(\d{4}\/\d{2}\/\d{2})) (?P<time>(\S{18})).*%DMI-5-AUTH_PASSED.*User.\'(?P<auth_by>(\S+))\' authenticated successfully.*for (?P<method>(\S+)).*')
        except Exception as e:
            print("%%%% DDR Parser Error: BtraceDmiauthdConfigI: regex error: " + str(e))
        
        auth_oper_id = 1 # Use to generate unique key for each dmiauthd successful authorization action in btrace log
        for line in output.splitlines():
            line = line.strip()
            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict = trans_dict.setdefault(str(auth_oper_id), {})
                    per_instance_dict['date'] = str(group['date'])
                    per_instance_dict['time'] = str(group['time'])
                    per_instance_dict['method'] = str(group['method'])
                    per_instance_dict['auth_by'] = str(group['auth_by']).rstrip(",")
                    auth_oper_id = auth_oper_id + 1
            except Exception as e:
                print("%%%% DDR Parser Error: BtraceDmiauthdConfigI: line processing: " + str(e))
                    
        return parsed_dict
        
# ==================================================
# Parser for dmiauthd btace log - extract %DMI-5-CONFIG_I actions
# ==================================================

class BtraceDmiauthdConfigMode():
#
# show command run to save dmiauthd log:
#   "show platform software trace message dmiauthd switch active R0 | redirect flash:/guest-share/btrace-file"
#
# Sample log message decoded from btrace file:
#
#   "2021/04/12 04:45:30.449522340 {dmiauthd_R0-0}{1}: [dmid] [7897]: UUID: 0, ra: 0, TID: 0 (note): [iosp_thread] cli config mode handler: CLI config mode enter event (ttynum=14, mytty=64)"
#
# Parser test function
#
    def test(self):
        test_message = '''
2021/04/12 04:45:30.449522340 {dmiauthd_R0-0}{1}: [dmid] [7897]: UUID: 0, ra: 0, TID: 0 (note): [iosp_thread] cli config mode handler: CLI config mode enter event (ttynum=14, mytty=64)'''

        expected_result='''{'config_mode_event': {'1': {'date': '2021/04/12', 'time': '04:45:30.449522', 'event': 'CLI config mode enter event (ttynum=14, mytty=64)'}}}'''

        print("\n******* BtraceDmiauthdConfigMode Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned ShowLispInstanceActive data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing BtraceDmiauthdConfigMode Parser\n")
                print("\nExpected BtraceDmiauthdConfigMode: \n", expected_result)
                print("\nGenerated BtraceDmiauthdConfigMode: \n", parsed_fact)
            else:
                print("\n%%%% BtraceDmiauthdConfigMode Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing BtraceDmiauthdConfigI Parser: \n" + str(e))
#
# parser for btrace log for configurations applied to the device
#
    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        trans_dict = parsed_dict.setdefault('config_mode_event', {})

        p1 = re.compile(r'(?P<datetime>[^{]*) .*config mode handler: (?P<event>[^(]*)\(ttynum=(?P<ttynum>(\d+)).*')

        counter = 1
        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = trans_dict.setdefault(str(counter), {})
                per_instance_dict['datetime'] = str(group['datetime'])
                per_instance_dict['event'] = str(group['event'])
                per_instance_dict['ttynum'] = str(group['ttynum'])
                counter = counter + 1
        return parsed_dict

# ==================================================
# Parser for 'show interface {name}'
# ==================================================
class ShowInterfaceState():

    ''' Parser for "show interface {name}" '''

    cli_command = 'show interface {name}'

##################################################################
#
# Selected fields from show command response
#
##################################################################

    test_message = '''
GigabitEthernet0/0 is up, line protocol is up 
  Hardware is RP management port, address is a0f8.490e.4a80 (bia a0f8.490e.4a80)
  Internet address is 172.27.255.24/24
  MTU 1500 bytes, BW 100000 Kbit/sec, DLY 100 usec, 
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full Duplex, 100Mbps, link type is auto, media type is RJ45
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:00, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/12474/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 2000 bits/sec, 4 packets/sec
  5 minute output rate 2000 bits/sec, 2 packets/sec
     2215841 packets input, 147836031 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles 
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     297938 packets output, 49190986 bytes, 0 underruns
     Output 0 broadcasts (0 IP multicasts)
     0 output errors, 0 collisions, 0 interface resets
     1 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
     0 carrier transitions
'''
#
# The parse method inserts parameters if required into the show command and
# executes the show command and parses the response into a python dictionary
# 
    def parse(self, instance_id=None, output=None, test=None):
        if output is None:
            if instance_id:
                cmd = self.cli_command[1].format(instance_id=instance_id)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = self.device.execute(cmd)
        else:
            out = output
#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            parsed_dict = {}
            for line in out.splitlines():
                line = line.strip()
#
# Compile regex for each of the lines in the output that contain required data
#
                p1 = re.compile(r'(?P<intf_name>(\S+)).is\s(?P<admin_state>[^,]*).\sline protocol is\s(?P<line_state>(\S+))') # interface, admin and line state
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    parsed_dict['intf_name'] = group['intf_name']
                    parsed_dict['admin_state'] = group['admin_state']
                    parsed_dict['line_state'] = group['line_state']
                    break

            return parsed_dict
        except Exception as e:
            print("%%%% Error processing ShowInterfaceState: " + str(e))

class ShowIpInterfaceBrief():

    ''' Parser for "show ip interface brief <interface>" '''

    cli_command = 'show ip interface brief {interface}'

    def test():
        print("this is a test from ShowIpInterfaceBrief")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            intf_dict = parsed_dict.setdefault('interface_ip_address', {})

        #ddmi-cat9300-2#
        #Interface              IP-Address      OK? Method Status                Protocol
        #Vlan1                  19.1.1.1        YES manual up                    up

        try:
            p1 = re.compile(r'^(?P<interface>\S+)\s+(?P<ip>\S+)\s+(?P<ok>(YES|NO))\s+(?P<method>\w+)\s+(?P<status>\w+)\s+(?P<protocol>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpInterfaceBrief: " + str(e))

        for line in out.splitlines():
            line = line.strip()
            
            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = str(group["interface"].lstrip('"').rstrip('"'))
                interface_dict = intf_dict.setdefault(interface, {})
                interface_dict['ip'] = str(group['ip'])
                interface_dict['ok'] = str(group['ok'])
                interface_dict['method'] = str(group['method'])
                interface_dict['status'] = str(group['status'])
                interface_dict['protocol'] = str(group['protocol'])
                continue

        return parsed_dict

class ShowIpInterfaceBriefXR():

    ''' Parser for "show ip interface brief <interface>" 
    Interface                      IP-Address      Status          Protocol Vrf-Name
    Loopback0                      2.2.2.2         Up              Up       default 
    Loopback100                    15.1.1.1        Up              Up       default 
    
    RP/0/RP0/CPU0:ios#show ip interface brief GigabitEthernet0/0/0/0
    Interface                      IP-Address      Status                Protocol
    GigabitEthernet0/0/0/0         20.20.20.2      Up                    Up      
    '''

    cli_command = 'show ip interface brief {interface}'

    def test():
        print("this is a test from ShowIpInterfaceBriefXR")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            intf_dict = parsed_dict.setdefault('ip_interface', {})

        try:
            p1 = re.compile(r'(?P<interface>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<status>\S+)\s+(?P<protocol>\S+).*')

        except Exception as e:
            print("%%%% DDR Error: ShowIpInterfaceBriefXR: " + str(e))

        for line in out.splitlines():
            line = line.strip()
            
            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = str(group["interface"].lstrip('"').rstrip('"'))
                interface_dict = intf_dict.setdefault(interface, {})
                interface_dict['interface'] = str(group['interface'])
                interface_dict['ip'] = str(group['ip'])
                interface_dict['status'] = str(group['status'])
                interface_dict['protocol'] = str(group['protocol'])
                continue
        return parsed_dict

class ShowBGPNeighborBriefXR():

    ''' Parser for "show bgp neighbor brief" 
    Neighbor        Spk    AS Description                          Up/Down  NBRState
    20.20.20.4        0     1                                      00:01:16 Established 

    Neighbor        Spk    AS Description                          Up/Down  NBRState
    20.20.20.4        0     2                                      00:00:56 Idle        
    '''

    cli_command = 'show bgp neighbor brief'

    def test():
        print("this is a test from ShowBGPNeighborBriefXR")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            intf_dict = parsed_dict.setdefault('bgp_neighbor', {})

        try:
            p1 = re.compile(r'(?P<neighbor>\d+\.\d+\.\d+\.\d+)\s+(?P<speaker>\d+)\s+(?P<as>\d+)\s+(?P<time>\S+)\s+(?P<state>\S+).*')

        except Exception as e:
            print("%%%% DDR Error: ShowBGPNeighborBriefXR: " + str(e))

        for line in out.splitlines():
            line = line.strip()
            
            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = str(group["neighbor"].lstrip('"').rstrip('"'))
                interface_dict = intf_dict.setdefault(interface, {})
                interface_dict['neighbor'] = str(group['neighbor'])
                interface_dict['speaker'] = int(group['speaker'])
                interface_dict['as'] = int(group['as'])
                interface_dict['time'] = str(group['time'])
                interface_dict['state'] = str(group['state'])
                continue
        return parsed_dict

class ShowIpInterfaceVlan():

    ''' Parser for "show ip interface vlan <vlan>" '''

    cli_command = 'show ip interface vlan {vlan}'

    def test():
        print("this is a test from ShowIpInterfaceVlan")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output



        if out:
            intf_dict = parsed_dict.setdefault('interf_ip_address', {})

       	#ddmi-cat9300-2#
	#Vlan1 is up, line protocol is up
  	# Internet address is 19.1.1.1/24
  	# Broadcast address is 255.255.255.255
  	# Address determined by setup command
  	# MTU is 1500 bytes
  	# Helper address is not set
  	# Directed broadcast forwarding is disabled 

        try:
            p1 = re.compile(r'^(?P<interface>[\w\/\.\-\:]+)\s+is\s+(?P<enabled>\w+)\,\s+line\s+protocol\sis\s(?P<status>\w+)')
            p2 = re.compile(r'^.*Internet\s+[A|a]ddress\s+is\s+(?P<ipv4>.*)\/(?P<prefix>[0-9]+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpInterfaceVlan: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    interface = str(group["interface"].lstrip('"').rstrip('"'))
                    interface_dict = intf_dict.setdefault(interface, {})
                    interface_dict['enable'] = str(group["enabled"])
                    continue
	
                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    interface_dict['ipv4'] = str(group['ipv4'])
                    interface_dict['prefix'] = str(group['prefix'])
                    continue
            except Exception as e:
                print("%%%% DDR Error: ShowIpInterfaceVlan: " + str(e))
            
        return parsed_dict

class ShowTunnelIpMaDatabase():

    ''' Parser for "show tunnel ip ma database tunnel-ip 100" '''

    cli_command = 'show tunnel ip ma database tunnel-ip {id}'


##################################################################
#
# Selected fields from show command response
#
##################################################################

    def test(self):
        test_message = '''
interface tunnel-ip100
 tunnel base flags: 0x83670
 tunnel keepalive disabled
 tunnel mode gre ipv4
 tunnel transport IPv4
 tunnel source 2.2.2.2
 tunnel source state UP
 tunnel destination 3.3.3.3/32
 tunnel latest reachability TRUE
 tunnel converged reachability TRUE
 tunnel transport vrf name default
 tunnel transport vrf id 0x60000000
 tunnel ifhandle 0x14
 tunnel interface state UP
 tunnel base caps state UP
 tunnel bfd state DOWN
 tunnel mtu 1500        '''

        expected_result='''{'tunnel_interface': {'per_tunnel_dict': {'tunnel-name': 'tunnel-ip100', 'base-flags': '0x83670', 'keepalive': 'disabled', 'mode': 'gre', 'mode-type': 'ipv4', 'transport-type': 'IPv4', 'source-ip': '2.2.2.2', 'source-state': 'UP', 'destination': '3.3.3.3/32', 'reachability': 'TRUE', 'converged': 'TRUE', 'vrf-name': 'default', 'vrf-id': '0x60000000', 'ifhandle': '0x14', 'interface-state': 'UP', 'base-state': 'UP', 'bfd-state': 'DOWN', 'mtu': 1500}}}'''

        print("\n******* SShowTunnelIpMaDatabase Parser Test Function Result **************\n")
        try:
            parsed_fact = self.cli(output=test_message)
            print("\n%%%% Parsed canned ShowTunnelIpMaDatabase data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing ShowTunnelIpMaDatabase Parser\n")
                print(f"\nExpected ShowTunnelIpMaDatabase data: {expected_result} \n")
                print(f"\nGenerated ShowTunnelIpMaDatabase data: {parsed_fact} \n")
            else:
                print("\n%%%% ShowTunnelIpMaDatabase Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing ShowTunnelIpMaDatabase: \n" + str(e))
#
# If the cli method is invoked with a lisp instance_id, insert the instance_id into the show command
# If there is no instance_id provided, execute the show command in the first index of the cli_command list
# If the data has already been read, the output variable will contain the show command data
# If the data has not been read from the device, execute the show command using the device.execute function
# 
    def parse(self, instance_id=None, output=None, test=None):
        if output is None:
            if instance_id:
                cmd = self.cli_command[1].format(instance_id=instance_id)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = self.device.execute(cmd)
        else:
            out = output

#
# Compile regex for each of the lines in the output that contain required data
#
        try:
            p1 = re.compile(r'interface\s+(?P<tunnel_name>\S+).*') # interface tunnel-ip100
            p2 = re.compile(r'.*tunnel base flags:\s+(?P<base_flags>\S+).*') # tunnel base flags: 0x83670
            p3 = re.compile(r'.*tunnel keepalive\s+(?P<keepalive>\S+).*') # tunnel keepalive disabled
            p4 = re.compile(r'.*tunnel mode\s+(?P<mode>\S+)\s+(?P<mode_type>\S+).*') # tunnel mode gre ipv4
            p5 = re.compile(r'.*tunnel transport (?P<transport_type>(\S+[IPv46])).*') # tunnel transport IPv4
            p6 = re.compile(r'.*tunnel source (?P<source_ip>(\d+\.\d+\.\d+\.\d+))') # tunnel source 2.2.2.2
            p7 = re.compile(r'.*tunnel source state (?P<source_state>(\S+[UPDOWN])).*') # tunnel source state UP
            p8 = re.compile(r'.*tunnel destination\s+(?P<destination>.+)') # tunnel destination 3.3.3.3/32
            p9 = re.compile(r'.*tunnel latest reachability\s+(?P<reachability>.+)') # tunnel latest reachability TRUE
            p10 = re.compile(r'.*tunnel converged reachability\s+(?P<converged>.+)') # tunnel converged reachability TRUE
            p11 = re.compile(r'.*tunnel transport vrf name\s+(?P<vrf_name>.+)') # tunnel transport vrf name default
            p12 = re.compile(r'.*tunnel transport vrf id\s+(?P<vrf_id>.+)') # tunnel transport vrf id 0x60000000
            p13 = re.compile(r'.*tunnel ifhandle\s+(?P<ifhandle>.+)') # tunnel ifhandle 0x14
            p14 = re.compile(r'.*tunnel interface state\s+(?P<interface_state>.+)') # tunnel interface state UP
            p15 = re.compile(r'.*tunnel base caps state\s+(?P<base_state>.+)') # tunnel base caps state UP
            p16= re.compile(r'.*tunnel bfd state\s+(?P<bfd_state>\S+).*') # tunnel bfd state DOWN
            p17 = re.compile(r'.*tunnel mtu\s+(?P<mtu>.+)') # tunnel mtu 1500  

        except Exception as e:
            print("%%%% Error processing regex in ShowTunnelIpMaDatabase: " + str(e))

#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            parsed_dict = {}
            tunnel_dict = parsed_dict.setdefault('tunnel_interface', {}) 
            t_dict = tunnel_dict.setdefault('per_tunnel_dict', {})

            for line in out.splitlines():
                line = line.strip()
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()                   
                    t_dict['tunnel-name'] = name = str(group['tunnel_name'].lstrip('"').rstrip('"'))
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['base-flags'] = str(group['base_flags'])
                    continue
                    
                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['keepalive'] = str(group['keepalive'])
                    continue
                    
                m = p4.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['mode'] = str(group['mode'])
                    t_dict['mode-type'] = str(group['mode_type'])
                    continue
                    
                m = p5.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['transport-type'] = str(group['transport_type'])
                    continue
                    
                m = p6.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['source-ip'] = str(group['source_ip'])
                    continue
                    
                m = p7.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['source-state'] = str(group['source_state'])
                    continue
                    
                m = p8.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['destination'] = str(group['destination'])
                    continue

                m = p9.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['reachability'] = str(group['reachability'])
                    continue

                m = p10.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['converged'] = str(group['converged'])
                    continue

                m = p11.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['vrf-name'] = str(group['vrf_name'])
                    continue

                m = p12.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['vrf-id'] = str(group['vrf_id'])
                    continue

                m = p13.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['ifhandle'] = str(group['ifhandle'])
                    continue

                m = p14.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['interface-state'] = str(group['interface_state'])
                    continue

                m = p15.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['base-state'] = str(group['base_state'])
                    continue

                m = p16.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['bfd-state'] = str(group['bfd_state'])
                    continue

                m = p17.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['mtu'] = int(group['mtu'])
                    continue
                    
            print(parsed_dict)
            return parsed_dict
        except Exception as e:
            print("%%%% Error processing ShowTunnelIpMaDatabase: " + str(e))


class ShowCtsRolebasedSgtmapVrfAll():

    ''' Parser for "show cts role-based sgt-map vrf <vrf> all" '''

    cli_command = 'show cts role-based sgt-map vrf {vrf} all'

    def test():
        print("this is a test from ShowCtsRolebasedSgtmapVrfAll")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('ipv4_sgt_binding', {})

	#ddmi-cat9300-2#
	#Active IPv4-SGT Bindings Information
	#
	#IP Address              SGT     Source
	#============================================
	#19.0.0.0/24             35          CLI
	#19.100.100.100/24       36          LISP


        try:
            p1 = re.compile(r'^(?P<ip>.\d+\.\d+\.\d+\.\d+)\/(?P<prefix>.\d+)\s+(?P<sgt>\d+)\s+(?P<src>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowCtsRolebasedSgtmapVrfAll: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    id = f"bind{i}"
                    sgtbind_dict = sgt_dict.setdefault(id, {})
                    sgtbind_dict['ip'] = str(group["ip"])
                    sgtbind_dict['prefix'] = str(group["prefix"])
                    sgtbind_dict['sgt'] = str(group["sgt"])
                    sgtbind_dict['src'] = str(group["src"])
                    i += 1
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowCtsRolebasedSgtmapVrfAll: " + str(e))
        
        return parsed_dict

class ShowGrouppolicyTrafficsteeringPermissionsFromTo():

    ''' Parser for "show group-policy traffic-steering permissions from <no> to <no>" '''

    cli_command = 'show group-policy traffic-steering permissions from {no} to {no}'

    def test():
        print("this is a test from ShowGrouppolicyTrafficsteeringPermissionsFromTo")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            grppolicy_dict = parsed_dict.setdefault('group_policy_traffic_steering_permissions', {})

	#ddmi-cat9300-2#
	#Group Policy traffic-steering permissions
	#
	#Source SGT      Destination SGT      Steering Policy
	#-----------------------------------------------------
    	#35                36              contract_eng1-02

        try:
            p1 = re.compile(r'^(?P<srcsgt>\d+)\s+(?P<destsgt>\d+)\s+(?P<policy>.*)')

        except Exception as e:
            print("%%%% DDR Error: ShowGrouppolicyTrafficsteeringPermissionsFromTo: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict = grppolicy_dict.setdefault('per_instance_dict', {})
                    per_instance_dict['srcsgt'] = str(group["srcsgt"])
                    per_instance_dict['destsgt'] = str(group["destsgt"])
                    per_instance_dict['policy'] = str(group["policy"])
                    continue        

            except Exception as e:
                print("%%%% DDR Error: ShowGrouppolicyTrafficsteeringPermissionsFromTo: " + str(e))
        
        return parsed_dict

class ShowGrouppolicyTrafficsteeringPolicySgt():

    ''' Parser for "show group-policy traffic-steering policy sgt <sgt>" '''

    cli_command = 'show group-policy traffic-steering policy sgt {sgt}'

    def test():
        print("this is a test from ShowGrouppolicyTrafficsteeringPermissions")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_policy', {})

	#ddmi-cat9300-2#
	#Traffic-Steering SGT Policy
	#===========================
	#SGT: 35-01
	#SGT Policy Flag: 0x41400001
	#Traffic-Steering Source List:
	#  Source SGT: 35-01, Destination SGT: 36-01
	#  steer_type = 80
	#  steer_index = 1
	#  name   = contract_eng1-02
	#  IP protocol version = IPV4
	#  refcnt = 1
	#  flag   = 0x41400000
	#  stale  = FALSE
	#  Traffic-Steering ACEs:
	#    1 redirect 6 any 23 service service_ENG1
	#    2 redirect 17 any 123 service service_ENG1

	#Traffic-Steering Destination List: Not exist
	#Traffic-Steering Multicast List: Not exist
	#Traffic-Steering Policy Lifetime = 86400 secs
	#Traffic-Steering Policy Last update time = 15:29:30 UTC Wed Jul 7 2021
	#Policy expires in 0:11:26:03 (dd:hr:mm:sec)
	#Policy refreshes in 0:11:26:03 (dd:hr:mm:sec)

        try:
            p1 = re.compile(r'^(?P<idx1>\d+)\s+redirect\s+(?P<idx2>\d+)\s+any\s+(?P<idx3>\d+)\s+service\s+(?P<ace>.*)')

        except Exception as e:
            print("%%%% DDR Error: ShowGrouppolicyTrafficsteeringPolicySgt: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    id = f"ACE{i}"
                    one_proc_dict = sgt_dict.setdefault(id, {})
                    one_proc_dict['idx1'] = str(group['idx1'])
                    one_proc_dict['idx2'] = str(group['idx2'])
                    one_proc_dict['idx3'] = str(group['idx3'])
                    one_proc_dict['ace'] = str(group['ace'])
                    i += 1
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowGrouppolicyTrafficsteeringPolicySgt: " + str(e))
        
        return parsed_dict

class ShowPdmSteeringPolicy():

    ''' Parser for "show pdm steering policy <policy>" '''

    cli_command = 'show pdm steering policy {policy}'

    def test():
        print("this is a test from ShowPdmSteeringPolicy")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            policy_dict = parsed_dict.setdefault('steering_policy', {})

	#ddmi-cat9300-2#
	#Steering Policy contract_eng1-02
	#    1 redirect protocol 6 src-port any dst-port eq 23 service service_ENG1 (625 matches)
	#    2 redirect protocol 17 src-port any dst-port eq 123 service service_ENG1 (0 match)

        try:
            p1 = re.compile(r'^Steering\s+Policy\s+(?P<name>.*)')

        except Exception as e:
            print("%%%% DDR Error: ShowPdmSteeringPolicy: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict = policy_dict.setdefault('per_instance_dict', {})
                    per_instance_dict['policy-name'] = str(group['name'])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPdmSteeringPolicy: " + str(e))
        
        return parsed_dict

class ShowPdmSteeringService():

    ''' Parser for "show pdm steering service" '''

    cli_command = 'show pdm steering service'

    def test():
        print("this is a test from ShowPdmSteeringService")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            pdm_dict = parsed_dict.setdefault('steering_service', {})

        #9400-vijacob#show pdm steering service
        #Steering Service service_ENG1  >>>> This has the VN name encoded
        #    mode routed address 192.102.0.2 selector 255 vnid 4099

        try:
            p1 = re.compile(r'^Steering\s+Service\s+(?P<svc>\w+)')
            p2 = re.compile(r'^.*mode\s+routed\s+address\s+(?P<ip>.\d+\.\d+\.\d+\.\d+).*(?P<vnid>\d{4})')

        except Exception as e:
            print("%%%% DDR Error: ShowPdmSteeringService: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    ste_service = str(group["svc"])
                    stebind_dict = pdm_dict.setdefault(ste_service, {})
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    stebind_dict['vnid'] = str(group["vnid"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPdmSteeringService: " + str(e))
        
        return parsed_dict

class ShowLispInstanceIdVnid():

    ''' Parser for "show lisp instance-id <vnid> ipv4 | i EID table" '''

    cli_command = 'show lisp instance-id {vnid} ipv4 | i EID table '

    def test():
        print("this is a test from ShowLispInstanceIdVnid")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            vnid_dict = parsed_dict.setdefault('vnid_vrf', {})

        #9400-vijacob#show lisp instance-id 4099 ipv4 | i EID table 
        #   EID table:                                vrf ENG1

        try:
            p = re.compile(r'^.*vrf\s+(?P<vrf>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowLispInstanceIdVnid: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict = vnid_dict.setdefault('per_instance_dict', {})
                    per_instance_dict['vrf'] = str(group["vrf"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowLispInstanceIdVnid: " + str(e))

        return parsed_dict

class ShowPdmSteeringServiceDetail():

    ''' Parser for "show pdm steering service <service> detail " '''

    cli_command = 'show pdm steering service {service} detail  '

    def test():
        print("this is a test from ShowPdmSteeringServiceDetail")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_detail', {})

        #9400-vijacob#show pdm steering service service_ENG1 detail
        #Service Name   : service_ENG1
        #Service ID     : 1419704521
        #Ref count      : 4
        #Stale          : FALSE
        #   Firewall mode      : routed
        #   Service IP         : 192.102.0.2
        #   Service Locator    : 255
        #   VRF ID             : 4
        #   Vnid               : 4099
        #   RLOC Status        : Received
        #   no.of rlocs        : 1
        #       *1. RLOC IP: 172.16.5.11    Weight: 10    Priority: 0
        #   Owner              : GPP

        try:
            p1 = re.compile(r'^Service\sName\s+:\s+(?P<srv_name>\w+)')
            p2 = re.compile(r'^Service\s+ID\s+:\s+(?P<srv_id>\d+)')
            p3 = re.compile(r'.RLOC\s+IP:\s+(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPdmSteeringServiceDetail: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    service_name = str(group["srv_name"])
                    per_instance_dict = steering_dict.setdefault(service_name, {})
                    per_instance_dict['service_name'] = str(group["srv_name"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict['service_id'] = str(group["srv_id"])

                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict['rloc_ip'] = str(group["ip"])

            except Exception as e:
                print("%%%% DDR Error: ShowPdmSteeringServiceDetail: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal():

    ''' Parser for "show platform software steering-policy forwarding-manager R0 global " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 global'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_global', {})

        #9400-vijacob#show platform software steering-policy forwarding-manager R0 global
        #Global Enforcement: On

        try:
            p = re.compile(r'^Global\s+Enforcement:\s+(?P<mode>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    per_instance_dict = steering_dict.setdefault('per_instance_dict', {})
                    per_instance_dict['mode'] = str(group["mode"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId():

    ''' Parser for "show platform software steering-policy forwarding-manager R0
        service-id <service_id>  " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 service-id {service_id} '

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_service', {})

        #9400-vijacob#show platform software steering-policy forwarding-manager R0 service-id 1419704521 
        #Forwarding Manager policy-defn Redirect action metadata

        #Service ID: 1419704521, Service VRF ID: 4, Firewall mode: Routed
        #Service Selector: 255, Service IP address: 192.102.0.2
        #Number of RLOCs: 1
        #Priority    Weightage    VNID        RLOC IP address                      
        #------------------------------------------------------------------------
        #0                      10           4099        172.16.5.11               

        try:
            p1 = re.compile(r'^Service\s+ID:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^.*Service\s+IP\s+address:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+)')
            p3 = re.compile(r'\d.+\d\d\d\d\s+(?P<rloc_ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    ste_service = str(group["svc_id"])
                    stebind_dict = steering_dict.setdefault(ste_service, {})
                    stebind_dict['service_id'] = str(group["svc_id"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['service_ip'] = str(group["svc_ip"])
                    continue

                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['rloc_ip'] = str(group["rloc_ip"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed():

    ''' Parser for "show platform software fed active security-fed sis-redirect
        firewall service-id <service-id> detailed " '''

    cli_command = 'show platform software fed active security-fed sis-redirect firewall service-id {service-id} detailed '

    def test():
        print("this is a test from ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            security_dict = parsed_dict.setdefault('service_detail', {})

        #9400-vijacob#show platform software fed active security-fed sis-redirect firewall service-id 1419704521 detailed 
        #Service ID               : 1419704521
        #VRF ID                   : 4
        #IP                       : 192.102.0.2/32
        #Redirect Hdl             : 0x7f7e664452e8
        #HTM Hdl                  : 0x7f7e664455c8
        #Route Prefix             : 192.102.0.0/30 
        #Next Hop                 : 172.16.5.11 
        #Adj Last Modified        : 2021-07-30,13:32:07           

        try:
            p1 = re.compile(r'^Service\s+ID\s+:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^IP\s+:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+\/\d+)')
            p3 = re.compile(r'^Route\s+Prefix\s+:\s+(?P<rt_prefix>\d+\.\d+\.\d+\.\d+\/\d+)')
            p4 = re.compile(r'^Next\s+Hop\s+:\s+(?P<nxt_hop>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    ste_service = str(group["svc_id"])
                    stebind_dict = security_dict.setdefault(ste_service, {})
                    stebind_dict['service_id'] = str(group["svc_id"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['service_ip'] = str(group["svc_ip"])
                    continue

                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['route_prefix'] = str(group["rt_prefix"])
                    continue

                m = p4.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['next_hop'] = str(group["nxt_hop"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed():

    ''' Parser for "show platform software fed standby security-fed sis-redirect
        firewall service-id <service-id> detailed " '''

    cli_command = 'show platform software fed standby security-fed sis-redirect firewall service-id {service-id} detailed '

    def test():
        print("this is a test from ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            security_dict = parsed_dict.setdefault('service_detail', {})

        #9400-vijacob#show platform software fed standby security-fed sis-redirect firewall service-id 1419704521 detailed 
        #Service ID               : 1419704521
        #VRF ID                   : 4
        #IP                       : 192.102.0.2/32
        #Redirect Hdl             : 0x7ff6fa445e18
        #HTM Hdl                  : 0x7ff6fa446028
        #Route Prefix             : 192.102.0.0/30 
        #Next Hop                 : 172.16.5.11 
        #Adj Last Modified        : 2021-07-30,13:32:07

        try:
            p1 = re.compile(r'^Service\s+ID\s+:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^IP\s+:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+\/\d+)')
            p3 = re.compile(r'^Route\s+Prefix\s+:\s+(?P<rt_prefix>\d+\.\d+\.\d+\.\d+\/\d+)')
            p4 = re.compile(r'^Next\s+Hop\s+:\s+(?P<nxt_hop>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    ste_service = str(group["svc_id"])
                    stebind_dict = security_dict.setdefault(ste_service, {})
                    stebind_dict['service_id'] = str(group["svc_id"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['service_ip'] = str(group["svc_ip"])
                    continue

                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['route_prefix'] = str(group["rt_prefix"])
                    continue

                m = p4.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['next_hop'] = str(group["nxt_hop"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4():

    ''' Parser for "show platform software steering-policy forwarding-manager R0
        permissions IPV4 <sgt> <dgt>  " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 permissions IPV4 {sgt} {dgt}'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_dgt_policy', {})

        #9400-vijacob# show platform software steering-policy forwarding-manager R0 permissions IPV4 100 36
        #Forwarding Manager steering-policy cell Information
        #
        #  sgt       dgt      Policy ID
        #--------------------------------
        #  100        36      1419703961
        
        try:
            p = re.compile(r'(?P<sgt>\d+)\s+(?P<dgt>\d{1,3})\s+(?P<policy_id>\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict = sgt_dict.setdefault('per_instance_dict', {})
                    stebind_dict['sgt'] = str(group["sgt"])
                    stebind_dict['dgt'] = str(group["dgt"])
                    stebind_dict['policy_id'] = str(group["policy_id"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4():

    ''' Parser for "show platform software steering-policy forwarding-manager F0 cell-info IPV4" '''

    cli_command = 'show platform software steering-policy forwarding-manager F0 cell-info IPV4'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_dgt_policy', {})
            stebind_dict = sgt_dict.setdefault('per_instance_dict', {})


        #9400-vijacob show platform software steering-policy forwarding-manager F0 cell-info IPV4
        #Forwarding Manager FP steering-policy cell Information
        #
        #SGT: 100, DGT: 36
        #Template name: V4GRPPLC996?, No.of Policies: 1
        #  Policy IDs
        #  -----------
        #  1419703961
        
        try:
            p1 = re.compile(r'^SGT:\s+(?P<sgt>\d+),\s+DGT:\s+(?P<dgt>\d+)')
            p2 = re.compile(r'^(?P<policy_id>\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['sgt'] = str(group["sgt"])
                    stebind_dict['dgt'] = str(group["dgt"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['policy_id'] = str(group["policy_id"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll():

    ''' Parser for "show platform software fed active security-fed sis-redirect acl all" '''

    cli_command = 'show platform software fed active security-fed sis-redirect acl all'

    def test():
        print("this is a test from ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_dict = parsed_dict.setdefault('acl_all', {})

        #9400-vijacob#show platform software fed active security-fed sis-redirect acl all       
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419703961   1         1419704521    0x5d0000e8                      0
        # 1419703961   2         1419704521    0x270000e9                      8
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419704481   1         1419704521    0x520000ce                      0
        # 1419704481   2         1419704521    0x750000cf                     41
        #--------------------------------------------------------------------------
        #Number of ACE's: 4
        #Number of ACL's: 2

        try:
            p = re.compile(r'.(?P<acl_id>\d+)\s+(?P<seq_no>\d+)\s+\d+\s+\w+\s+(?P<frame_cnt>\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    id = f"ACL{i}"
                    stebind_dict = acl_dict.setdefault(id, {})
                    stebind_dict['acl_id'] = str(group["acl_id"])
                    stebind_dict['seq_no'] = str(group["seq_no"])
                    stebind_dict['frame_count'] = str(group["frame_cnt"])
                    i += 1
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll: " + str(e))

        return parsed_dict

class ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll():

    ''' Parser for "show platform software fed standby security-fed sis-redirect acl all" '''

    cli_command = 'show platform software fed standby security-fed sis-redirect acl all'

    def test():
        print("this is a test from ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_dict = parsed_dict.setdefault('acl_all', {})

        #9400-vijacob#show platform software fed standby security-fed sis-redirect acl all       
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419703961   1         1419704521    0x5d0000e8                      0
        # 1419703961   2         1419704521    0x270000e9                      0
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419704481   1         1419704521    0x520000ce                      0
        # 1419704481   2         1419704521    0x750000cf                      0
        #--------------------------------------------------------------------------
        #Number of ACE's: 4
        #Number of ACL's: 2

        try:
            p = re.compile(r'.(?P<acl_id>\d+)\s+(?P<seq_no>\d+)\s+\d+\s+\w+\s+(?P<frame_cnt>\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    id = f"ACL{i}"
                    stebind_dict = acl_dict.setdefault(id, {})
                    stebind_dict['acl_id'] = str(group["acl_id"])
                    stebind_dict['seq_no'] = str(group["seq_no"])
                    stebind_dict['frame_count'] = str(group["frame_cnt"])
                    i += 1
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll: " + str(e))

        return parsed_dict

class ShowRunLispInterface():

    ''' Parser for "show run interface lisp.<no> " '''

    cli_command = 'show run interface lisp {no}'

    def test():
        print("this is a test from ShowRunLispInterface")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_interface', {})


        #interface LISP0.4099
        # ip policy route-map ssi_redirect_route_map-ENG1-8fba43e7        
        
        try:
            p = re.compile(r'ip\s+policy\s+route-map\s+(?P<policy_name>.+)')

        except Exception as e:
            print("%%%% DDR Error: ShowRunLispInterface: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict = lisp_dict.setdefault('per_int_dict', {})
                    stebind_dict['policy_name'] = str(group["policy_name"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowRunLispInterface: " + str(e))

        return parsed_dict

class ShowLispSiteInstanceid():

    ''' Parser for "show lisp site <ip> instance-id <id> " '''

    cli_command = 'show lisp site {ip} instance-id {id}'

    def test():
        print("this is a test from ShowLispSiteInstanceid")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9500H-FB1#show lisp site 48.1.1.100 instance-id 4099
        #LISP Site Registration Information
        #
        #Site name: site_uci
        #Description: map-server configured from Cisco DNA-Center
        #Allowed configured locators: any
        #Requested EID-prefix:
        #
        #  EID-prefix: 48.1.1.100/32 instance-id 4099 
        #    First registered:     23:51:28
        #    Last registered:      07:18:20
        #    Routing table tag:    0
        #    Origin:               Dynamic, more specific of 48.1.1.0/24
        #    Merge active:         No
        #    Proxy reply:          Yes
        #    Skip Publication:     No
        #    Force Withdraw:       No
        #    TTL:                  1d00h
        #    State:                complete
        #    Extranet IID:         Unspecified
        #    SGT:                  100
        #    Registration errors:  
        #      Authentication failures:   0
        #      Allowed locators mismatch: 0
        #    ETR 172.16.201.30:25784, last registered 07:18:20, proxy-reply, map-notify
        #                             TTL 1d00h, no merge, hash-function sha1, nonce 0x288FE03A-0x65D8E7C2
        #                             state complete, no security-capability
        #                             xTR-ID 0x3CD76593-0x5ADC928C-0xBC60FACE-0x52795862    
        #                             site-ID unspecified
        #                             Domain-ID 1953204162
        #                             Multihoming-ID unspecified
        #                             sourced by reliable transport
        #      Locator        Local  State      Pri/Wgt  Scope
        #      172.16.201.30  yes    up          10/10   IPv4 none
        
        try:
            p1 = re.compile(r'SGT:\s+(?P<sgt>\d+)')
            p2 = re.compile(r'^(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowLispSiteInstanceid: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['sgt'] = str(group["sgt"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowLispSiteInstanceid: " + str(e))

        return parsed_dict

class ShowIpLispMapserver():

    ''' Parser for "show ip lisp | i Map-Server " '''

    cli_command = 'show ip lisp | i Map-Server'

    def test():
        print("this is a test from ShowIpLispMapserver")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9400-vijacob#sh ip lisp | i Map-Server
        #  ETR Map-Server(s):                        172.16.5.11  

        try:
            p1 = re.compile(r'SGT:\s+(?P<sgt>\d+)')
            p2 = re.compile(r'^(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpLispMapserver: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['sgt'] = str(group["sgt"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowIpLispMapserver: " + str(e))

        return parsed_dict

class ExecutePing():

    ''' Parser for "ping <ip> source <int> " '''

    cli_command = 'ping {ip} source {int}'

    def test():
        print("this is a test from ExecutePing")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            ping_dict = parsed_dict.setdefault('ping_instance', {})
            stebind_dict = ping_dict.setdefault('per_ping_dict', {})

        #9400-vijacob#ping 172.16.5.11 source loop0
        #Type escape sequence to abort.
        #Sending 5, 100-byte ICMP Echos to 172.16.5.11, timeout is 2 seconds:
        #Packet sent with a source address of 172.16.201.30 
        #!!!!!
        #Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms    

        try:
            p = re.compile(r'Success\s+rate\s+is\s+(?P<percent>\d+)\s+percent')

        except Exception as e:
            print("%%%% DDR Error: ExecutePing: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ping_percent'] = str(group["percent"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ExecutePing: " + str(e))

        return parsed_dict

class ShowLispSession():

    ''' Parser for "show lisp session " '''

    cli_command = 'show lisp session'

    def test():
        print("this is a test from ShowLispSession")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_session_dict', {})

        #xtr1#sh lisp session
        #Sessions for VRF default, total: 1, established: 1
        #Peer                           State      Up/Down        In/Out    Users
        #15.15.15.15:4342               Up         21:59:07      117/37     8

        try:
            p = re.compile(r'(?P<peer_ip>\d+\.\d+\.\d+\.\d+):(?P<peer_port>\d+)\s+(?P<state>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowLispSession: " + str(e))
    
        i = 1
        for line in output.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    id = f'session_{i}_dict'
                    stebind_dict = lisp_dict.setdefault(id, {})
                    stebind_dict['peer_ip'] = str(group["peer_ip"])
                    stebind_dict['peer_port'] = str(group["peer_port"])
                    stebind_dict['lisp_state'] = str(group["state"])
                    i += 1
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowLispSession: " + str(e))

        return parsed_dict

class ShowIpRouteVrf():

    ''' Parser for "show ip route vrf <vrf> <ip>" '''

    cli_command = 'show ip route vrf {vrf} {ip}'

    def test():
        print("this is a test from ShowIpRouteVrf")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            route_dict = parsed_dict.setdefault('route_instance', {})
            stebind_dict = route_dict.setdefault('per_vrf_dict', {})

        #9500H-FB1#show ip route vrf ENG1 192.102.0.4   >>> subnet of firewall
        #
        #Routing Table: ENG1
        #Routing entry for 192.102.0.4/30
        #  Known via "connected", distance 0, metric 0 (connected, via interface)
        #  Routing Descriptor Blocks:
        #  * directly connected, via Vlan2001
        #      Route metric is 0, traffic share count is 1

        try:
            p = re.compile(r'^Routing\s+entry\s+for\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\/(?P<prefix>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpRouteVrf: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    stebind_dict['prefix'] = str(group["prefix"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowIpRouteVrf: " + str(e))

        return parsed_dict

class ShowIpCefVrf():

    ''' Parser for "show ip cef vrf <vrf> <ip>" '''

    cli_command = 'show ip cef vrf {vrf} {ip}'

    def test():
        print("this is a test from ShowIpCefVrf")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            cef_dict = parsed_dict.setdefault('cef_instance', {})
            stebind_dict = cef_dict.setdefault('per_cef_dict', {})

        #9500H-FB1#show ip cef vrf ENG1 192.102.0.6    >>>> IP address of firewall
        #192.102.0.6/32
        #  attached to Vlan2001

        try:
            p1 = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)\/(?P<prefix>\w+)')
            p2 = re.compile(r'attached\s+to\s(?P<vlan>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpCefVrf: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    stebind_dict['prefix'] = str(group["prefix"])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['vlan'] = str(group["vlan"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowIpCefVrf: " + str(e))

        return parsed_dict

class ShowIpCefVrfInt():

    ''' Parser for "show ip cef vrf <vrf> <ip> int" '''

    cli_command = 'show ip cef vrf {vrf} {ip} int'

    def test():
        print("this is a test from ShowIpCefVrfInt")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            cef_dict = parsed_dict.setdefault('cefint_instance', {})
            stebind_dict = cef_dict.setdefault('per_cef_dict', {})

        #9500H-FB1#show ip cef vrf ENG1 192.102.0.6 int
        #192.102.0.6/32, epoch 0, flags [att, sc], refcnt 6, per-destination sharing
        #  sources: Adj, RR
        #  subblocks:
        #    SC inherited: LISP generalised SMR - [disabled, not inheriting, 0x7F0E7DC0F4E8 locks: 5]
        #    Adj source: IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600
        #      Dependent covered prefix type adjfib, cover 192.102.0.4/30
        #    1 RR source [no flags]
        #  ifnums:
        #    Vlan2001(98): 192.102.0.6
        #  path list 7F0E83ED9630, 2 locks, per-destination, flags 0x49 [shble, rif, hwcn]
        #    path 7F0E83E96870, share 1/1, type adjacency prefix, for IPv4
        #      attached to Vlan2001, IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600
        #  output chain:
        #    IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600 >>>> Will be populated with an outgoing interface if ARP is resolved for next hop ( VLAN interface should be the same number selected during the DNAC Hawkeye workflow i.e 2001 has to be picked from DNAC)

        try:
            p = re.compile(r'IP\s+adj\s+out\s+of\s+(?P<vlan>\w+)')

        except Exception as e:
            print("%%%% DDR Error: ShowIpCefVrfInt: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['vlan'] = str(group["vlan"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowIpCefVrfInt: " + str(e))

        return parsed_dict

class ShowLispInstanceidIpv4Server():

    ''' Parser for "show lisp instance-id <id> ipv4 server <ip>" '''

    cli_command = 'show lisp instance-id {id} ipv4 server {ip}'

    def test():
        print("this is a test from ShowLispInstanceidIpv4Server")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9500H-FB1#show lisp instance-id 4099 ipv4 server 192.102.0.4/30 >>> subnet of firewall
        #LISP Site Registration Information
        # 
        #Site name: site_uci
        #Description: map-server configured from Cisco DNA-Center
        #Allowed configured locators: any
        #Requested EID-prefix:
        # 
        #  EID-prefix: 192.102.0.4/30 instance-id 4099
        #    First registered:     1d01h
        #    Last registered:      1d01h
        #    Routing table tag:    0
        #    Origin:               Dynamic, more specific of 0.0.0.0/0
        #    Merge active:         No
        #    Proxy reply:          Yes
        #    Skip Publication:     No
        #    Force Withdraw:       No
        #    TTL:                  1d00h
        #    State:                complete
        #    Extranet IID:         Unspecified
        #    Registration errors: 
        #      Authentication failures:   0
        #      Allowed locators mismatch: 0
        #    ETR 172.16.5.11:21963, last registered 1d01h, proxy-reply, map-notify
        #                           TTL 1d00h, no merge, hash-function sha1, nonce 0xB75416A8-0x095D4D9C
        #                           state complete, no security-capability
        #                           xTR-ID 0x9B8717A7-0x90A6783E-0xA81C6987-0x1C0C3459
        #                           site-ID unspecified
        #                           Domain-ID 3988969097
        #                           Multihoming-ID 54921
        #                           sourced by reliable transport
        #                           ETR Type Service-ETR
        #                           SI Type Service-ETR Firewall Service Insertion
        #                           SI ID 1
        #      Locator      Local  State      Pri/Wgt  Scope
        #      172.16.5.11  yes    up          10/10   IPv4 none  >>>>> Should be Loopback 0 IP address of the SSN node ( that is the node connected to the firewall)
    
        try:
            p = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+')

        except Exception as e:
            print("%%%% DDR Error: ShowLispInstanceidIpv4Server: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['ip'] = str(group["ip"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowLispInstanceidIpv4Server: " + str(e))

        return parsed_dict

class ShowLispRemotelocatorsetServiceetrs():

    ''' Parser for "show lisp remote-locator-set service-etrs" '''

    cli_command = 'show lisp remote-locator-set service-etrs'

    def test():
        print("this is a test from ShowLispRemotelocatorsetServiceetrs")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lispremote_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #pxtr#sh lisp remote-locator-set service-etrs 
        #LISP remote-locator-set default-etr-locator-set-ipv4 Information
        #
        #Codes:
        #ETR = ETR Type (Default = Default-ETR, Service = Service-ETR)
        #SI  = Service Insertion Type
        #ID  = Service Insertion ID
        #-   = No service insertion config type defined
        #DS  = Default-ETR Firewall Service Insertion
        #SS  = Service-ETR Firewall Service Insertion
        #P   = Primary/Direct in use, Backup not available
        #PB  = Primary/Direct in use, Backup available
        #B   = Backup in use, Primary/Direct not available
        #BP  = Backup in use, Primary/Direct available
        # * = This locator has multiple service EID configured.
        #
        # RLOC         Pri/Wgt/Metric     Inst       Domain-ID/MH-ID  ETR       SI/ID          
        # 15.15.15.15   10/10 /-          4099               0/0      Service   SS/1

        try:
            p = re.compile(r'(?P<rloc_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<priority>\w+)\/')

        except Exception as e:
            print("%%%% DDR Error: ShowLispRemotelocatorsetServiceetrs: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            try:
                m = p.match(line)
                if m:
                    group = m.groupdict()
                    stebind_dict['rloc_ip'] = str(group["rloc_ip"])
                    stebind_dict['priority'] = str(group["priority"])
                    continue

            except Exception as e:
                print("%%%% DDR Error: ShowLispRemotelocatorsetServiceetrs: " + str(e))

        return parsed_dict

class ShowInterfacesSchema():
    """schema for show interfaces
                  show interfaces <interface>

    schema = {
            Any(): {
                Optional('oper_status'): str,
                Optional('line_protocol'): str,
                Optional('enabled'): bool,
                Optional('connected'): bool,
                Optional('err_disabled'): bool,
                Optional('suspended'): bool,
                Optional('description'): str,
                Optional('type'): str,
                Optional('link_state'): str,
                Optional('port_speed'): str,
                Optional('duplex_mode'): str,
                Optional('link_type'): str,
                Optional('media_type'): str,
                Optional('mtu'): int,
                Optional('maximum_active_vcs'): str,
                Optional('vcs_per_vp'): str,
                Optional('vc_idle_disconnect_time'): str,
                Optional('vc_auto_creation'): str,
                Optional('current_vccs'): str,
                Optional('aal5_crc_errors'): int,
                Optional('aal5_oversized_sdus'): int,
                Optional('aal5_sar_timeouts'): int,
                Optional('vaccess_status'): str,
                Optional('vaccess_loopback'): str,
                Optional('base_pppoatm'): str,
                Optional('dtr_pulsed'): str,
                Optional('sub_mtu'): int,
                Optional('medium'): str,
                Optional('reliability'): str,
                Optional('txload'): str,
                Optional('rxload'): str,
                Optional('mac_address'): str,
                Optional('phys_address'): str,
                Optional('delay'): int,
                Optional('carrier_delay'): int,
                Optional('carrier_delay_up'): int,
                Optional('carrier_delay_down'): int,
                Optional('keepalive'): int,
                Optional('auto_negotiate'): bool,
                Optional('arp_type'): str,
                Optional('arp_timeout'): str,
                Optional('last_input'): str,
                Optional('last_output'): str,
                Optional('output_hang'): str,
                Optional('autostate'): bool,
                Optional('queues'): {
                    Optional('input_queue_size'): int,
                    Optional('input_queue_max'): int,
                    Optional('input_queue_drops'): int,
                    Optional('input_queue_flushes'): int,
                    Optional('total_output_drop'): int,
                    Optional('queue_strategy'): str,
                    Optional('output_queue_size'): int,
                    Optional('output_queue_max'): int,
                    Optional('threshold'): int,
                    Optional('drops'): int,
                },
                Optional('flow_control'):
                    {Optional('receive'): bool,
                    Optional('send'): bool,
                },
                Optional('port_channel'):
                    {Optional('port_channel_member'): bool,
                    Optional('port_channel_int'): str,
                    Optional('port_channel_member_intfs'): list,
                    Optional('active_members'): int,
                    Optional('num_of_pf_jumbo_supported_members'): int,
                },
                Optional('bandwidth'): int,
                Optional('counters'):
                    {Optional('rate'):
                       {Optional('load_interval'): int,
                        Optional('in_rate'): int,
                        Optional('in_rate_pkts'): int,
                        Optional('out_rate'): int,
                        Optional('out_rate_pkts'): int,
                        Optional('in_rate_bps'): int,
                        Optional('in_rate_pps'): int,
                        Optional('out_rate_bps'): int,
                        Optional('out_rate_pps'): int,
                        },
                    Optional('in_multicast_pkts'): int,
                    Optional('in_broadcast_pkts'): int,
                    Optional('in_crc_errors'): int,
                    Optional('in_giants'): int,
                    Optional('in_pkts'): int,
                    Optional('in_frame'): int,
                    Optional('in_runts'): int,
                    Optional('in_overrun'): int,
                    Optional('in_ignored'): int,
                    Optional('in_watchdog'): int,
                    Optional('in_with_dribble'): int,
                    Optional('in_octets'): int,
                    Optional('in_errors'): int,
                    Optional('in_abort'): int,
                    Optional('in_no_buffer'): int,
                    Optional('in_throttles'): int,
                    Optional('in_mac_pause_frames'): int,
                    Optional('out_pkts'): int,
                    Optional('out_octets'): int,
                    Optional('out_multicast_pkts'): int,
                    Optional('out_broadcast_pkts'): int,
                    Optional('out_errors'): int,
                    Optional('out_collision'): int,
                    Optional('out_interface_resets'): int,
                    Optional('out_unknown_protocl_drops'): int,
                    Optional('out_babbles'): int,
                    Optional('out_deferred'): int,
                    Optional('out_underruns'): int,
                    Optional('out_late_collision'): int,
                    Optional('out_lost_carrier'): int,
                    Optional('out_no_carrier'): int,
                    Optional('out_babble'): int,
                    Optional('out_mac_pause_frames'): int,
                    Optional('out_buffer_failure'): int,
                    Optional('out_buffers_swapped'): int,
                    Optional('last_clear'): str,
                    },
                Optional('encapsulations'):
                    {Optional('encapsulation'): str,
                     Optional('first_dot1q'): str,
                     Optional('second_dot1q'): str,
                     Optional('native_vlan'): int,
                    },
                Optional('ipv4'):
                    {Any():
                        {Optional('ip'): str,
                         Optional('prefix_length'): str,
                         Optional('secondary'): bool
                    },
                    Optional('unnumbered'): {
                        'interface_ref': str,
                },
            },
        },
    }
"""
        
class ShowInterfaces():
    """parser for show interfaces
                  show interfaces <interface>"""

    cli_command = ['show interfaces','show interfaces {interface}']
    exclude = ['in_octets', 'in_pkts', 'out_octets', 'out_pkts',
               'in_rate', 'in_rate_pkts', 'out_rate', 'out_rate_pkts',
               'input_queue_size', 'in_broadcast_pkts', 'in_multicast_pkts',
               'last_output', 'out_unknown_protocl_drops', 'last_input',
               'input_queue_drops', 'out_interface_resets', 'rxload',
               'txload', 'last_clear', 'in_crc_errors', 'in_errors',
               'in_giants', 'unnumbered', 'mac_address', 'phys_address',
               'out_lost_carrier', '(Tunnel.*)', 'input_queue_flushes',
               'reliability']

    def parse(self, output):
        out = output

        # GigabitEthernet1 is up, line protocol is up
        # Port-channel12 is up, line protocol is up (connected)
        # Vlan1 is administratively down, line protocol is down , Autostate Enabled
        # Dialer1 is up (spoofing), line protocol is up (spoofing)
        # FastEthernet1 is down, line protocol is down (err-disabled)
        # GigabitEthernet1/0/2 is up, line protocol is down (suspended)

        try:
            p1 = re.compile(r'^(?P<interface>[\w\/\.\-\:]+) +is +(?P<enabled>[\w\s]+)(?: '
                        r'+\S+)?, +line +protocol +is +(?P<line_protocol>\w+)(?: '
                        r'*\((?P<attribute>\S+)\)|( +\, +Autostate +(?P<autostate>\S+)))?.*$')
            p1_1 = re.compile(r'^(?P<interface>[\w\/\.\-\:]+) +is'
                          r' +(?P<enabled>[\w\s]+),'
                          r' +line +protocol +is +(?P<line_protocol>\w+)'
                          r'( *, *(?P<attribute>[\w\s]+))?$')

        # Hardware is Gigabit Ethernet, address is 0057.d2ff.428c (bia 0057.d2ff.428c)
        # Hardware is Loopback
            p2 = re.compile(r'^Hardware +is +(?P<type>[a-zA-Z0-9\-\/\s\+]+)'
                        r'(, *address +is +(?P<mac_address>[a-z0-9\.]+)'
                        r' *\(bia *(?P<phys_address>[a-z0-9\.]+)\))?$')

        # Hardware is LTE Adv CAT6 - Multimode LTE/DC-HSPA+/HSPA+/HSPA/UMTS/EDGE/GPRS
            p2_2 = re.compile(r'Hardware +is +(?P<type>[a-zA-Z0-9\-\/\+ ]+)'
                          r'(?P<mac_address>.*)(?P<phys_address>.*)')

        # Description: desc
        # Description: Pim Register Tunnel (Encap) for RP 10.186.1.1
            p3 = re.compile(r'^Description: *(?P<description>.*)$')

        # Secondary address 10.2.2.2/24
            p4 = re.compile(r'^Secondary +Address +is +(?P<ipv4>(?P<ip>[0-9\.]+)'
                        r'\/(?P<prefix_length>[0-9]+))$')

        # Internet address is 10.4.4.4/24
            p5 = re.compile(r'^Internet +[A|a]ddress +is +(?P<ipv4>(?P<ip>[0-9\.x]+)'
                        r'\/(?P<prefix_length>[0-9]+))$')

        # MTU 1500 bytes, BW 768 Kbit/sec, DLY 3330 usec,
        # MTU 1500 bytes, BW 10000 Kbit, DLY 1000 usec,
        # MTU 1600 bytes, sub MTU 1600, BW 3584 Kbit/sec, DLY 410 usec,
        # MTU 1500 bytes, BW 5200 Kbit/sec, RxBW 25000 Kbit/sec, DLY 100 usec,
            p6 = re.compile(r'^MTU +(?P<mtu>\d+) +bytes(, +sub +MTU +'
                        r'(?P<sub_mtu>\d+))?, +BW +(?P<bandwidth>[0-9]+) +Kbit(\/sec)?'
                        r'(, +RxBW +[0-9]+ +Kbit(\/sec)?)?, +'
                        r'DLY +(?P<delay>[0-9]+) +usec,$')

        # reliability 255/255, txload 1/255, rxload 1/255
            p7 = re.compile(r'^reliability +(?P<reliability>[\d\/]+),'
                        r' +txload +(?P<txload>[\d\/]+), +rxload'
                        r' +(?P<rxload>[\d\/]+)$')

        # Encapsulation LOOPBACK, loopback not set
        # Encapsulation 802.1Q Virtual LAN, Vlan ID 20, medium is p2p
        # Encapsulation ARPA, medium is broadcast
        # Encapsulation QinQ Virtual LAN, outer ID  10, inner ID 20
        # Encapsulation 802.1Q Virtual LAN, Vlan ID  1., loopback not set
        # Encapsulation 802.1Q Virtual LAN, Vlan ID  105.
        # Encapsulation(s): AAL5
            p8 = re.compile(r'^Encapsulation(\(s\):)? +(?P<encapsulation>[\w\s\.]+)'
                r'(, +(?P<rest>.*))?$')

        # Keepalive set (10 sec)
            p10 = re.compile(r'^Keepalive +set +\((?P<keepalive>[0-9]+)'
                        r' +sec\)$')


        # Auto-duplex, 1000Mb/s, media type is 10/100/1000BaseTX
        # Full-duplex, 1000Mb/s, link type is auto, media type is
        # Full Duplex, 1000Mbps, link type is auto, media type is RJ45
        # Full Duplex, Auto Speed, link type is auto, media type is RJ45
        # Full Duplex, 10000Mbps, link type is force-up, media type is unknown media type
        # full-duplex, 1000 Mb/s
        # auto-duplex, auto-speed
        # auto-duplex, 10 Gb/s, media type is 10G
        # Full Duplex, 10000Mbps, link type is force-up, media type is SFP-LR
        # Full-duplex, 100Gb/s, link type is force-up, media type is QSFP 100G SR4
        # Full-duplex, 10Gb/s, media type is 100/1000/2.5G/5G/10GBaseTX
            p11 = re.compile(r'^(?P<duplex_mode>\w+)[\-\s]+[d|D]uplex\, '
                         r'+(?P<port_speed>[\w\s\/]+|[a|A]uto-[S|s]peed|Auto '
                         r'(S|s)peed)(?:(?:\, +link +type +is '
                         r'+(?P<link_type>\S+))?(?:\, *(media +type +is| )'
                         r'*(?P<media_type>[\w\/\-\. ]+)?)(?: +media +type)?)?$')

        # input flow-control is off, output flow-control is unsupported
            p12 = re.compile(r'^(input|output) +flow-control +is +(?P<receive>\w+), +'
                          '(output|input) +flow-control +is +(?P<send>\w+)$')

        # ARP type: ARPA, ARP Timeout 04:00:00
            p13 = re.compile(r'^ARP +type: +(?P<arp_type>\w+), +'
                          'ARP +Timeout +(?P<arp_timeout>[\w\:\.]+)$')

        # Last input never, output 00:01:05, output hang never
            p14 = re.compile(r'^Last +input +(?P<last_input>[\w\.\:]+), +'
                          'output +(?P<last_output>[\w\.\:]+), '
                          'output +hang +(?P<output_hang>[\w\.\:]+)$')

        # Members in this channel: Gi1/0/2
        # Members in this channel: Fo1/0/2 Fo1/0/4
            p15 = re.compile(r'^Members +in +this +channel: +'
                          '(?P<port_channel_member_intfs>[\w\/\.\s\,]+)$')

        # No. of active members in this channel: 12
            p15_1 = re.compile(r'^No\. +of +active +members +in +this +'
                            'channel: +(?P<active_members>\d+)$')

        # Member 2 : GigabitEthernet0/0/10 , Full-duplex, 900Mb/s
            p15_2 = re.compile(r'^Member +\d+ +: +(?P<interface>\S+) +,'
                            ' +\S+, +\S+$')

        # No. of PF_JUMBO supported members in this channel : 0
            p15_3 = re.compile(r'^No\. +of +PF_JUMBO +supported +members +'
                            'in +this +channel +: +(?P<number>\d+)$')

        # Last clearing of "show interface" counters 1d02h
            p16 = re.compile(r'^Last +clearing +of +\"show +interface\" +counters +'
                          '(?P<last_clear>[\w\:\.]+)$')

        # Input queue: 0/375/0/0 (size/max/drops/flushes); Total output drops: 0
            p17 = re.compile(r'^Input +queue: +(?P<size>\d+)\/(?P<max>\d+)\/'
                          '(?P<drops>\d+)\/(?P<flushes>\d+) +'
                          '\(size\/max\/drops\/flushes\); +'
                          'Total +output +drops: +(?P<output_drop>\d+)$')

        # Queueing strategy: fifo
        # Queueing strategy: Class-based queueing
            p18 = re.compile(r'^Queueing +strategy: +(?P<queue_strategy>\S+).*$')

        # Output queue: 0/0 (size/max)
        # Output queue: 0/1000/64/0 (size/max total/threshold/drops)
            p19 = re.compile(r'^Output +queue: +(?P<size>\d+)\/(?P<max>\d+)'
                          '(?:\/(?P<threshold>\d+)\/(?P<drops>\d+))? '
                          '+\(size\/max(?: +total\/threshold\/drops\))?.*$')

        # 5 minute input rate 0 bits/sec, 0 packets/sec
            p20 = re.compile(r'^(?P<load_interval>[0-9\#]+)'
                          ' *(?P<unit>(minute|second|minutes|seconds)) *input *rate'
                          ' *(?P<in_rate>[0-9]+) *bits/sec,'
                          ' *(?P<in_rate_pkts>[0-9]+) *packets/sec$')

        # 5 minute output rate 0 bits/sec, 0 packets/sec
            p21 = re.compile(r'^(?P<load_interval>[0-9\#]+)'
                          ' *(minute|second|minutes|seconds) *output *rate'
                          ' *(?P<out_rate>[0-9]+) *bits/sec,'
                          ' *(?P<out_rate_pkts>[0-9]+) *packets/sec$')

        # 0 packets input, 0 bytes, 0 no buffer
        # 13350 packets input, 2513375 bytes
            p22 = re.compile(r'^(?P<in_pkts>[0-9]+) +packets +input, +(?P<in_octets>[0-9]+) '
                          '+bytes(?:, +(?P<in_no_buffer>[0-9]+) +no +buffer)?$')

        # Received 4173 broadcasts (0 IP multicasts)
        # Received 535996 broadcasts (535961 multicasts)
            p23 = re.compile(r'^Received +(?P<in_broadcast_pkts>\d+) +broadcasts +'
                          '\((?P<in_multicast_pkts>\d+) *(IP)? *multicasts\)$')

        # 0 runts, 0 giants, 0 throttles
            p24 = re.compile(r'^(?P<in_runts>[0-9]+) *runts,'
                          ' *(?P<in_giants>[0-9]+) *giants,'
                          ' *(?P<in_throttles>[0-9]+) *throttles$')

        # 0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
        # 0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
            p25 = re.compile(r'^(?P<in_errors>[0-9]+) +input +errors, +'
                          '(?P<in_crc_errors>[0-9]+) +CRC, +'
                          '(?P<in_frame>[0-9]+) +frame, +'
                          '(?P<in_overrun>[0-9]+) +overrun, +'
                          '(?P<in_ignored>[0-9]+) +ignored'
                          '(, *(?P<in_abort>[0-9]+) +abort)?$')

        # 0 watchdog, 535961 multicast, 0 pause input
            p26 = re.compile(r'^(?P<in_watchdog>[0-9]+) +watchdog, +'
                          '(?P<in_multicast_pkts>[0-9]+) +multicast, +'
                          '(?P<in_pause_input>[0-9]+) +pause +input$')

        # 0 input packets with dribble condition detected
            p27 = re.compile(r'^(?P<in_with_dribble>[0-9]+) +input +packets +with +'
                          'dribble +condition +detected$')

        # 23376 packets output, 3642296 bytes, 0 underruns
        # 13781 packets output, 2169851 bytes
            p28 = re.compile(r'^(?P<out_pkts>[0-9]+) +packets +output, +(?P<out_octets>[0-9]+) '
                          r'+bytes(?:\, +(?P<out_underruns>[0-9]+) +underruns)?$')

        # Output 0 broadcasts (55 multicasts)
            p29 = re.compile(r'^Output +(?P<out_broadcast_pkts>\d+) +broadcasts +'
                          r'\((?P<out_multicast_pkts>\d+) *(IP)? *multicasts\)$')

        # 0 output errors, 0 collisions, 2 interface resets
        # 0 output errors, 0 interface resets
            p30 = re.compile(r'^(?P<out_errors>[0-9]+) +output +errors,'
                          r'( *(?P<out_collision>[0-9]+) +collisions,)? +'
                          r'(?P<out_interface_resets>[0-9]+) +interface +resets$')

        # 0 unknown protocol drops
            p31 = re.compile(r'^(?P<out_unknown_protocl_drops>[0-9]+) +'
                          'unknown +protocol +drops$')

        # 0 babbles, 0 late collision, 0 deferred
            p32 = re.compile(r'^(?P<out_babble>[0-9]+) +babbles, +'
                         r'(?P<out_late_collision>[0-9]+) +late +collision, +'
                         r'(?P<out_deferred>[0-9]+) +deferred$')

        # 0 lost carrier, 0 no carrier, 0 pause output
        # 0 lost carrier, 0 no carrier
            p33 = re.compile(r'^(?P<out_lost_carrier>\d+) +lost +carrier, +'
                r'(?P<out_no_carrier>\d+) +no +carrier(, +(?P<out_pause_output>\d+) +'
                r'pause +output)?$')

        # 0 output buffer failures, 0 output buffers swapped out
            p34 = re.compile(r'^(?P<out_buffer_failure>[0-9]+) +output +buffer +failures, +'
                          '(?P<out_buffers_swapped>[0-9]+) +output +buffers +swapped +out$')

        # Interface is unnumbered. Using address of Loopback0 (10.4.1.1)
        # Interface is unnumbered. Using address of GigabitEthernet0/2.1 (192.168.154.1)
            p35 = re.compile(r'^Interface +is +unnumbered. +Using +address +of +'
                          '(?P<unnumbered_intf>[\w\/\.]+) +'
                          '\((?P<unnumbered_ip>[\w\.\:]+)\)$')

        # 8 maximum active VCs, 1024 VCs per VP, 1 current VCCs
            p36 = re.compile(r'^(?P<maximum_active_vcs>\d+) +maximum +active +VCs, +'
                r'(?P<vcs_per_vp>\d+) +VCs +per +VP, +(?P<current_vccs>\d+) +current +VCCs$')

        # VC Auto Creation Disabled.
            p37 = re.compile(r'^VC +Auto +Creation +(?P<vc_auto_creation>\S+)\.$')

        # VC idle disconnect time: 300 seconds
            p38 = re.compile(r'^VC +idle +disconnect +time: +(?P<vc_idle_disconnect_time>\d+) +'
                r'seconds$')

        # AAL5 CRC errors : 0
            p39 = re.compile(r'^(?P<key>\S+ +CRC +errors) +: +(?P<val>\d+)$')

        # AAL5 SAR Timeouts : 0
            p40 = re.compile(r'^(?P<key>\S+ +SAR +Timeouts) +: +(?P<val>\d+)$')

        # AAL5 Oversized SDUs : 0
            p41 = re.compile(r'^(?P<key>\S+ +Oversized +SDUs) +: +(?P<val>\d+)$')

        # LCP Closed
        # LCP Closed, loopback not set
            p42 = re.compile(r'^LCP\s+(?P<state>\S+)(,\s+loopback\s+(?P<loopback>[\S\s]+))?$')

        # Base PPPoATM vaccess
            p43 = re.compile(r'^Base PPPoATM +(?P<base_pppoatm>\S+)$')

        # Vaccess status 0x44, loopback not set
            p44 = re.compile(r'^Vaccess\s+status\s+(?P<status>\S+),\s+'
                r'loopback\s+(?P<loopback>[\S\s]+)$')

        # DTR is pulsed for 5 seconds on reset
            p45 = re.compile(r'^DTR +is +pulsed +for +(?P<dtr_pulsed>\d+) +'
                r'seconds +on +reset$')

        except Exception as e:
            print("%%%% DDR Error: ShowLispRemotelocatorsetServiceetrs: " + str(e))

        interface_dict = {}
        unnumbered_dict = {}
        for line in out.splitlines():
            line = line.strip()

            # GigabitEthernet1 is up, line protocol is up
            # Port-channel12 is up, line protocol is up (connected)
            # Vlan1 is administratively down, line protocol is down , Autostate Enabled
            # Dialer1 is up (spoofing), line protocol is up (spoofing)
            # FastEthernet1 is down, line protocol is down (err-disabled)
            # GigabitEthernet1/0/2 is up, line protocol is down (suspended)

            m = p1.match(line)
            m1 = p1_1.match(line)
            m = m if m else m1
            if m:
                interface = m.groupdict()['interface']
                enabled = m.groupdict()['enabled']
                line_protocol = m.groupdict()['line_protocol']
                line_attribute = m.groupdict()['attribute']
                if m.groupdict()['autostate']:
                    autostate = m.groupdict()['autostate'].lower()
                else:
                    autostate = None

                if interface not in interface_dict:
                    interface_dict[interface] = {}
                    interface_dict[interface]['port_channel'] = {}
                    interface_dict[interface]['port_channel']\
                        ['port_channel_member'] = False

                if 'administratively down' in enabled or 'delete' in enabled:
                    interface_dict[interface]['enabled'] = False
                else:
                    interface_dict[interface]['enabled'] = True

                if line_protocol:
                    interface_dict[interface]\
                                ['line_protocol'] = line_protocol
                    interface_dict[interface]\
                                ['oper_status'] = line_protocol

                if line_attribute:
                    interface_dict[interface]['connected'] = True if line_attribute == 'connected' else False
                    interface_dict[interface]['err_disabled'] = True if line_attribute == 'err-disabled' else False
                    interface_dict[interface]['suspended'] = True if line_attribute == 'suspended' else False

                if autostate:
                    interface_dict[interface]['autostate'] = True if autostate == 'enabled' else False

                continue

            # Hardware is Gigabit Ethernet, address is 0057.d2ff.428c (bia 0057.d2ff.428c)
            # Hardware is Loopback
            m = p2.match(line)

            # Hardware is LTE Adv CAT6 - Multimode LTE/DC-HSPA+/HSPA+/HSPA/UMTS/EDGE/GPRS
            m1 = p2_2.match(line)
            m = m if m else m1
            if m:
                types = m.groupdict()['type']
                mac_address = m.groupdict()['mac_address']
                phys_address = m.groupdict()['phys_address']
                interface_dict[interface]['type'] = types
                if mac_address:
                    interface_dict[interface]['mac_address'] = mac_address
                if phys_address:
                    interface_dict[interface]['phys_address'] = phys_address
                continue
            # Description: desc
            # Description: Pim Register Tunnel (Encap) for RP 10.186.1.1
            m = p3.match(line)
            if m:
                description = m.groupdict()['description']

                interface_dict[interface]['description'] = description
                continue

            # Secondary address 10.2.2.2/24
            m = p4.match(line)
            if m:
                ip_sec = m.groupdict()['ip']
                prefix_length_sec = m.groupdict()['prefix_length']
                address_sec = m.groupdict()['ipv4']

                if 'ipv4' not in interface_dict[interface]:
                    interface_dict[interface]['ipv4'] = {}
                if address_sec not in interface_dict[interface]['ipv4']:
                    interface_dict[interface]['ipv4'][address_sec] = {}

                interface_dict[interface]['ipv4'][address_sec]\
                    ['ip'] = ip_sec
                interface_dict[interface]['ipv4'][address_sec]\
                    ['prefix_length'] = prefix_length_sec
                interface_dict[interface]['ipv4'][address_sec]\
                    ['secondary'] = True
                continue

            # Internet Address is 10.4.4.4/24
            m = p5.match(line)
            if m:
                ip = m.groupdict()['ip']
                prefix_length = m.groupdict()['prefix_length']
                address = m.groupdict()['ipv4']

                if 'ipv4' not in interface_dict[interface]:
                    interface_dict[interface]['ipv4'] = {}
                if address not in interface_dict[interface]['ipv4']:
                    interface_dict[interface]['ipv4'][address] = {}

                interface_dict[interface]['ipv4'][address]\
                ['ip'] = ip
                interface_dict[interface]['ipv4'][address]\
                ['prefix_length'] = prefix_length
                continue

            # MTU 1500 bytes, BW 768 Kbit/sec, DLY 3330 usec,
            # MTU 1500 bytes, BW 10000 Kbit, DLY 1000 usec,
            m = p6.match(line)
            if m:
                mtu = m.groupdict()['mtu']
                sub_mtu = m.groupdict().get('sub_mtu', None)
                bandwidth = m.groupdict()['bandwidth']
                if m.groupdict()['delay']:
                    interface_dict[interface]['delay'] = int(m.groupdict()['delay'])
                if mtu:
                    interface_dict[interface]['mtu'] = int(mtu)
                if sub_mtu:
                    interface_dict[interface]['sub_mtu'] = int(sub_mtu)
                if bandwidth:
                    interface_dict[interface]['bandwidth'] = int(bandwidth)
                continue

            # reliability 255/255, txload 1/255, rxload 1/255
            m = p7.match(line)
            if m:
                reliability = m.groupdict()['reliability']
                txload = m.groupdict()['txload']
                rxload = m.groupdict()['rxload']
                interface_dict[interface]['reliability'] = reliability
                interface_dict[interface]['txload'] = txload
                interface_dict[interface]['rxload'] = rxload
                continue

            # Encapsulation LOOPBACK, loopback not set
            # Encapsulation 802.1Q Virtual LAN, Vlan ID 20, medium is p2p
            # Encapsulation ARPA, medium is broadcast
            # Encapsulation QinQ Virtual LAN, outer ID  10, inner ID 20
            # Encapsulation 802.1Q Virtual LAN, Vlan ID  1., loopback not set
            # Encapsulation 802.1Q Virtual LAN, Vlan ID  105.
            m = p8.match(line)
            if m:
                encapsulation = m.groupdict()['encapsulation']
                encapsulation = m.groupdict()['encapsulation'].lower()
                encapsulation = encapsulation.replace("802.1q virtual lan","dot1q")
                if 'encapsulations' not in interface_dict[interface]:
                    interface_dict[interface]['encapsulations'] = {}

                interface_dict[interface]['encapsulations']\
                    ['encapsulation'] = encapsulation

                rest = m.groupdict()['rest']
                if not rest:
                    continue
                # Vlan ID 20, medium is p2p
                m1 = re.compile(r'(Vlan +ID +(?P<first_dot1q>[0-9]+),)?'
                                 ' *medium +is +(?P<medium>[a-z0-9]+)$').match(rest)
                # will update key when output is valid
                m2 = re.compile(r'loopback +(?P<loopback>[\w\s]+)$').match(rest)

                #  outer ID  10, inner ID 20
                m3 = re.compile(r'outer +ID +(?P<first>[0-9]+), +'
                                 'inner +ID (?P<second>[0-9]+)$').match(rest)

                # Vlan ID  1., loopback not set
                # Vlan ID  105.
                m4 = re.compile(r'Vlan +ID +(?P<first_dot1q>\d+).'
                                 '|(?:,(?P<rest>[\s\w]+))$').match(rest)

                if m1:
                    first_dot1q = m1.groupdict()['first_dot1q']
                    if first_dot1q:
                        interface_dict[interface]['encapsulations']\
                            ['first_dot1q'] = first_dot1q
                    interface_dict[interface]['medium'] = m.groupdict()['medium']
                elif m3:
                    first_dot1q = m3.groupdict()['first']
                    second_dot1q = m3.groupdict()['second']
                    interface_dict[interface]['encapsulations']\
                        ['first_dot1q'] = first_dot1q
                    interface_dict[interface]['encapsulations']\
                        ['second_dot1q'] = second_dot1q
                elif m4:
                    first_dot1q = m4.groupdict()['first_dot1q']
                    if first_dot1q:
                        interface_dict[interface]['encapsulations']\
                            ['first_dot1q'] = first_dot1q

                continue

            # Keepalive set (10 sec)
            m = p10.match(line)
            if m:
                keepalive = m.groupdict()['keepalive']
                if keepalive:
                    interface_dict[interface]['keepalive'] = int(keepalive)
                continue

            # Auto-duplex, 1000Mb/s, media type is 10/100/1000BaseTX
            # Full-duplex, 1000Mb/s, link type is auto, media type is
            # Full Duplex, 1000Mbps, link type is auto, media type is RJ45
            # Full Duplex, Auto Speed, link type is auto, media type is RJ45
            # Full Duplex, 10000Mbps, link type is force-up, media type is unknown media type
            # full-duplex, 1000 Mb/s
            # auto-duplex, auto-speed
            # auto-duplex, 10 Gb/s, media type is 10G
            # Full Duplex, 10000Mbps, link type is force-up, media type is SFP-LR
            # Full-duplex, 100Gb/s, link type is force-up, media type is QSFP 100G SR4
            m = p11.match(line)
            if m:
                duplex_mode = m.groupdict()['duplex_mode'].lower()
                port_speed = m.groupdict()['port_speed'].lower().replace('-speed', '')
                link_type = m.groupdict()['link_type']
                media_type = m.groupdict()['media_type']
                interface_dict[interface]['duplex_mode'] = duplex_mode
                interface_dict[interface]['port_speed'] = port_speed

                if link_type:
                    interface_dict[interface]['link_type'] = link_type
                    if 'auto' in link_type:
                        interface_dict[interface]['auto_negotiate'] = True
                    else:
                        interface_dict[interface]['auto_negotiate'] = False
                if media_type:
                    unknown = re.search(r'[U|u]nknown',media_type)
                    if unknown:
                        interface_dict[interface]['media_type'] = 'unknown'
                    else:
                        interface_dict[interface]['media_type'] = media_type
                continue

            # input flow-control is off, output flow-control is unsupported
            m = p12.match(line)
            if m:
                receive = m.groupdict()['receive'].lower()
                send = m.groupdict()['send'].lower()
                if 'flow_control' not in interface_dict[interface]:
                    interface_dict[interface]['flow_control'] = {}
                if 'on' in receive:
                    interface_dict[interface]['flow_control']['receive'] = True
                elif 'off' in receive or 'unsupported' in receive:
                    interface_dict[interface]['flow_control']['receive'] = False

                if 'on' in send:
                    interface_dict[interface]['flow_control']['send'] = True
                elif 'off' in send or 'unsupported' in send:
                    interface_dict[interface]['flow_control']['send'] = False
                continue

            # Carrier delay is 10 sec
            p_cd = re.compile(r'^Carrier +delay +is +(?P<carrier_delay>\d+).*$')
            m = p_cd.match(line)
            if m:
                group = m.groupdict()
                sub_dict = interface_dict.setdefault(interface, {})
                sub_dict['carrier_delay'] = int(group['carrier_delay'])

            # Asymmetric Carrier-Delay Up Timer is 2 sec
            # Asymmetric Carrier-Delay Down Timer is 10 sec
            p_cd_2 = re.compile(r'^Asymmetric +Carrier-Delay +(?P<type>Down|Up)'
                                 ' +Timer +is +(?P<carrier_delay>\d+).*$')
            m = p_cd_2.match(line)
            if m:
                group = m.groupdict()
                tp = group['type'].lower()
                sub_dict = interface_dict.setdefault(interface, {})
                if tp == 'up':
                    sub_dict['carrier_delay_up'] = int(group['carrier_delay'])
                else:
                    sub_dict['carrier_delay_down'] = int(group['carrier_delay'])

            # ARP type: ARPA, ARP Timeout 04:00:00
            m = p13.match(line)
            if m:
                arp_type = m.groupdict()['arp_type'].lower()
                arp_timeout = m.groupdict()['arp_timeout']
                interface_dict[interface]['arp_type'] = arp_type
                interface_dict[interface]['arp_timeout'] = arp_timeout
                continue

            # Last input never, output 00:01:05, output hang never
            m = p14.match(line)
            if m:
                last_input = m.groupdict()['last_input']
                last_output = m.groupdict()['last_output']
                output_hang = m.groupdict()['output_hang']
                interface_dict[interface]['last_input'] = last_input
                interface_dict[interface]['last_output'] = last_output
                interface_dict[interface]['output_hang'] = output_hang
                continue

            # Members in this channel: Gi1/0/2
            # Members in this channel: Fo1/0/2 Fo1/0/4
            m = p15.match(line)
            if m:
                interface_dict[interface]['port_channel']\
                    ['port_channel_member'] = True
                intfs = m.groupdict()['port_channel_member_intfs'].split(' ')
                intfs = [Common.convert_intf_name(i.strip()) for i in intfs]
                interface_dict[interface]['port_channel']\
                    ['port_channel_member_intfs'] = intfs

                # build connected interface port_channel
                for intf in intfs:
                    if intf not in interface_dict:
                        interface_dict[intf] = {}
                    if 'port_channel' not in interface_dict[intf]:
                        interface_dict[intf]['port_channel'] = {}
                    interface_dict[intf]['port_channel']['port_channel_member'] = True
                    interface_dict[intf]['port_channel']['port_channel_int'] = interface
                continue

            # No. of active members in this channel: 12
            m = p15_1.match(line)
            if m:
                group = m.groupdict()
                active_members = int(group['active_members'])
                interface_dict[interface]['port_channel']\
                    ['port_channel_member'] = True
                interface_dict[interface]['port_channel']\
                    ['active_members'] = active_members
                continue

            # Member 2 : GigabitEthernet0/0/10 , Full-duplex, 900Mb/s
            m = p15_2.match(line)
            if m:
                group = m.groupdict()
                intf = group['interface']
                if 'port_channel_member_intfs' not in interface_dict[interface]['port_channel']:
                    interface_dict[interface]['port_channel']\
                            ['port_channel_member_intfs'] = []

                interface_dict[interface]['port_channel']\
                    ['port_channel_member_intfs'].append(intf)

                continue

            # No. of PF_JUMBO supported members in this channel : 0
            m = p15_3.match(line)
            if m:
                group = m.groupdict()
                number = int(group['number'])
                interface_dict[interface]['port_channel']\
                    ['num_of_pf_jumbo_supported_members'] = number
                continue

            # Last clearing of "show interface" counters 1d02h
            m = p16.match(line)
            if m:
                last_clear = m.groupdict()['last_clear']
                continue

            # Input queue: 0/375/0/0 (size/max/drops/flushes); Total output drops: 0
            m = p17.match(line)
            if m:
                if 'queues' not in interface_dict[interface]:
                    interface_dict[interface]['queues'] = {}

                interface_dict[interface]['queues']['input_queue_size'] = \
                    int(m.groupdict()['size'])
                interface_dict[interface]['queues']['input_queue_max'] = \
                    int(m.groupdict()['max'])
                interface_dict[interface]['queues']['input_queue_drops'] = \
                    int(m.groupdict()['drops'])
                interface_dict[interface]['queues']['input_queue_flushes'] = \
                    int(m.groupdict()['flushes'])
                interface_dict[interface]['queues']['total_output_drop'] = \
                    int(m.groupdict()['output_drop'])
                continue

            # Queueing strategy: fifo
            # Queueing strategy: Class-based queueing
            m = p18.match(line)
            if m:
                if 'queues' not in interface_dict[interface]:
                    interface_dict[interface]['queues'] = {}
                interface_dict[interface]['queues']['queue_strategy'] = \
                    m.groupdict()['queue_strategy']
                continue

            # Output queue: 0/0 (size/max)
            # Output queue: 0/1000/64/0 (size/max total/threshold/drops)
            m = p19.match(line)
            if m:
                if 'queues' not in interface_dict[interface]:
                    interface_dict[interface]['queues'] = {}
                interface_dict[interface]['queues']['output_queue_size'] = \
                    int(m.groupdict()['size'])
                interface_dict[interface]['queues']['output_queue_max'] = \
                    int(m.groupdict()['max'])
                if m.groupdict()['threshold'] and m.groupdict()['drops']:
                    interface_dict[interface]['queues']['threshold'] = \
                        int(m.groupdict()['threshold'])
                    interface_dict[interface]['queues']['drops'] = \
                        int(m.groupdict()['drops'])
                continue

            # 5 minute input rate 0 bits/sec, 0 packets/sec
            m = p20.match(line)
            if m:
                load_interval = int(m.groupdict()['load_interval'])
                in_rate = int(m.groupdict()['in_rate'])
                in_rate_pkts = int(m.groupdict()['in_rate_pkts'])
                unit = m.groupdict()['unit']
                # covert minutes to seconds
                if 'minute' in unit:
                    load_interval = load_interval * 60

                if 'counters' not in interface_dict[interface]:
                    interface_dict[interface]['counters'] = {}

                if 'rate' not in interface_dict[interface]['counters']:
                    interface_dict[interface]['counters']['rate'] = {}

                interface_dict[interface]['counters']['rate']\
                    ['load_interval'] = load_interval
                interface_dict[interface]['counters']['rate']\
                    ['in_rate'] = in_rate
                interface_dict[interface]['counters']['rate']\
                    ['in_rate_pkts'] = in_rate_pkts

                if 'last_clear' not in interface_dict[interface]['counters']:
                    try:
                        last_clear
                    except Exception:
                        pass
                    else:
                        interface_dict[interface]['counters']\
                            ['last_clear'] = last_clear
                continue

            # 5 minute output rate 0 bits/sec, 0 packets/sec
            m = p21.match(line)
            if m:
                if 'counters' not in interface_dict[interface]:
                    interface_dict[interface]['counters'] = {}
                    interface_dict[interface]['counters']['rate'] = {}

                out_rate = int(m.groupdict()['out_rate'])
                out_rate_pkts = int(m.groupdict()['out_rate_pkts'])

                interface_dict[interface]['counters']['rate']\
                    ['out_rate'] = out_rate
                interface_dict[interface]['counters']['rate']\
                    ['out_rate_pkts'] = out_rate_pkts
                continue

            # 0 packets input, 0 bytes, 0 no buffer
            m = p22.match(line)
            if m:
                if 'counters' not in interface_dict[interface]:
                    interface_dict[interface]['counters'] = {}

                interface_dict[interface]['counters']['in_pkts'] = \
                    int(m.groupdict()['in_pkts'])
                interface_dict[interface]['counters']['in_octets'] = \
                    int(m.groupdict()['in_octets'])
                if m.groupdict()['in_no_buffer']:
                    interface_dict[interface]['counters']['in_no_buffer'] = \
                        int(m.groupdict()['in_no_buffer'])
                continue

            # Received 4173 broadcasts (0 IP multicasts)
            # Received 535996 broadcasts (535961 multicasts)
            m = p23.match(line)
            if m:
                interface_dict[interface]['counters']['in_multicast_pkts'] = \
                    int(m.groupdict()['in_multicast_pkts'])
                interface_dict[interface]['counters']['in_broadcast_pkts'] = \
                    int(m.groupdict()['in_broadcast_pkts'])
                continue

            # 0 runts, 0 giants, 0 throttles
            m = p24.match(line)
            if m:
                interface_dict[interface]['counters']['in_runts'] = \
                    int(m.groupdict()['in_runts'])
                interface_dict[interface]['counters']['in_giants'] = \
                    int(m.groupdict()['in_giants'])
                interface_dict[interface]['counters']['in_throttles'] = \
                    int(m.groupdict()['in_throttles'])
                continue

            # 0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
            # 0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
            m = p25.match(line)
            if m:
                interface_dict[interface]['counters']['in_errors'] = \
                    int(m.groupdict()['in_errors'])
                interface_dict[interface]['counters']['in_crc_errors'] = \
                    int(m.groupdict()['in_crc_errors'])
                interface_dict[interface]['counters']['in_frame'] = \
                    int(m.groupdict()['in_frame'])
                interface_dict[interface]['counters']['in_overrun'] = \
                    int(m.groupdict()['in_overrun'])
                interface_dict[interface]['counters']['in_ignored'] = \
                    int(m.groupdict()['in_ignored'])
                if m.groupdict()['in_abort']:
                    interface_dict[interface]['counters']['in_abort'] = \
                        int(m.groupdict()['in_abort'])
                continue

            # 0 watchdog, 535961 multicast, 0 pause input
            m = p26.match(line)
            if m:
                interface_dict[interface]['counters']['in_watchdog'] = \
                    int(m.groupdict()['in_watchdog'])
                interface_dict[interface]['counters']['in_multicast_pkts'] = \
                    int(m.groupdict()['in_multicast_pkts'])
                interface_dict[interface]['counters']['in_mac_pause_frames'] = \
                    int(m.groupdict()['in_pause_input'])
                continue

            # 0 input packets with dribble condition detected
            m = p27.match(line)
            if m:
                interface_dict[interface]['counters']['in_with_dribble'] = \
                    int(m.groupdict()['in_with_dribble'])
                continue

            # 23376 packets output, 3642296 bytes, 0 underruns
            m = p28.match(line)
            if m:
                interface_dict[interface]['counters']['out_pkts'] = \
                    int(m.groupdict()['out_pkts'])
                interface_dict[interface]['counters']['out_octets'] = \
                    int(m.groupdict()['out_octets'])
                if m.groupdict()['out_underruns']:
                    interface_dict[interface]['counters']['out_underruns'] = \
                        int(m.groupdict()['out_underruns'])
                continue

            # Output 0 broadcasts (55 multicasts)
            m = p29.match(line)
            if m:
                interface_dict[interface]['counters']['out_broadcast_pkts'] = \
                    int(m.groupdict()['out_broadcast_pkts'])
                interface_dict[interface]['counters']['out_multicast_pkts'] = \
                    int(m.groupdict()['out_multicast_pkts'])
                continue

            # 0 output errors, 0 collisions, 2 interface resets
            # 0 output errors, 0 interface resets
            m = p30.match(line)
            if m:
                interface_dict[interface]['counters']['out_errors'] = \
                    int(m.groupdict()['out_errors'])
                interface_dict[interface]['counters']['out_interface_resets'] = \
                    int(m.groupdict()['out_interface_resets'])
                if m.groupdict()['out_collision']:
                    interface_dict[interface]['counters']['out_collision'] = \
                        int(m.groupdict()['out_collision'])
                continue

            # 0 unknown protocol drops
            m = p31.match(line)
            if m:
                interface_dict[interface]['counters']['out_unknown_protocl_drops'] = \
                    int(m.groupdict()['out_unknown_protocl_drops'])
                continue

            # 0 babbles, 0 late collision, 0 deferred
            m = p32.match(line)
            if m:
                interface_dict[interface]['counters']['out_babble'] = \
                    int(m.groupdict()['out_babble'])
                interface_dict[interface]['counters']['out_late_collision'] = \
                    int(m.groupdict()['out_late_collision'])
                interface_dict[interface]['counters']['out_deferred'] = \
                    int(m.groupdict()['out_deferred'])
                continue

            # 0 lost carrier, 0 no carrier, 0 pause output
            m = p33.match(line)
            if m:
                interface_dict[interface]['counters']['out_lost_carrier'] = \
                    int(m.groupdict()['out_lost_carrier'])
                interface_dict[interface]['counters']['out_no_carrier'] = \
                    int(m.groupdict()['out_no_carrier'])
                out_pause_output = m.groupdict().get('out_pause_output', None)
                if out_pause_output:
                    interface_dict[interface]['counters']['out_mac_pause_frames'] = \
                        int(m.groupdict()['out_pause_output'])
                continue

            # 0 output buffer failures, 0 output buffers swapped out
            m = p34.match(line)
            if m:
                interface_dict[interface]['counters']['out_buffer_failure'] = \
                    int(m.groupdict()['out_buffer_failure'])
                interface_dict[interface]['counters']['out_buffers_swapped'] = \
                    int(m.groupdict()['out_buffers_swapped'])
                continue

            # Interface is unnumbered. Using address of Loopback0 (10.4.1.1)
            # Interface is unnumbered. Using address of GigabitEthernet0/2.1 (192.168.154.1)
            m = p35.match(line)
            if m:
                unnumbered_dict[interface] = {}
                unnumbered_dict[interface]['unnumbered_intf'] = m.groupdict()['unnumbered_intf']
                unnumbered_dict[interface]['unnumbered_ip'] = m.groupdict()['unnumbered_ip']
                continue

            # 8 maximum active VCs, 1024 VCs per VP, 1 current VCCs
            m = p36.match(line)
            if m:
                group = m.groupdict()
                maximum_active_vcs = group['maximum_active_vcs']
                vcs_per_vp = group['vcs_per_vp']
                current_vccs = group['current_vccs']
                interface_dict[interface].update({'maximum_active_vcs': maximum_active_vcs})
                interface_dict[interface].update({'vcs_per_vp': vcs_per_vp})
                interface_dict[interface].update({'current_vccs': current_vccs})
                continue

            # VC Auto Creation Disabled.
            m = p37.match(line)
            if m:
                group = m.groupdict()
                vc_auto_creation = group['vc_auto_creation']
                interface_dict[interface].update({'vc_auto_creation': vc_auto_creation})
                continue

            # VC idle disconnect time: 300 seconds
            m = p38.match(line)
            if m:
                group = m.groupdict()
                vc_idle_disconnect_time = group['vc_idle_disconnect_time']
                interface_dict[interface].update({'vc_idle_disconnect_time': vc_idle_disconnect_time})
                continue

            # AAL5 CRC errors : 0
            m = p39.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'aal5_crc_errors': int(group['val'])})
                continue

            # AAL5 SAR Timeouts : 0
            m = p40.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'aal5_oversized_sdus': int(group['val'])})
                continue

            # AAL5 Oversized SDUs : 0
            m = p41.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'aal5_sar_timeouts': int(group['val'])})
                continue

            # LCP Closed
            m = p42.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'lcp_state': group['state']})
                loopback = group.get('loopback', None)
                if loopback:
                    interface_dict[interface].update({'lcp_loopack': loopback})
                continue

            # Base PPPoATM vaccess
            m = p43.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'base_pppoatm': group['base_pppoatm']})
                continue

            # Vaccess status 0x44, loopback not set
            m = p44.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'vaccess_status': group['status']})
                interface_dict[interface].update({'vaccess_loopback': group['loopback']})
                continue

            # DTR is pulsed for 5 seconds on reset
            m = p45.match(line)
            if m:
                group = m.groupdict()
                interface_dict[interface].update({'dtr_pulsed': group['dtr_pulsed']})
                continue

        # create strucutre for unnumbered interface
        if not unnumbered_dict:
            return(interface_dict)

        for intf in unnumbered_dict:
            unnumbered_intf = unnumbered_dict[intf]['unnumbered_intf']
            unnumbered_ip = unnumbered_dict[intf]['unnumbered_ip']
            if unnumbered_intf in interface_dict:
                if 'ipv4' in interface_dict[unnumbered_intf]:
                    for ip in interface_dict[unnumbered_intf]['ipv4']:
                        if unnumbered_ip in ip:
                            if 'ipv4' not in interface_dict[intf]:
                                interface_dict[intf]['ipv4'] = {}
                            if ip not in interface_dict[intf]['ipv4']:
                                interface_dict[intf]['ipv4'][ip] = {}
                            m = re.search('([\w\.\:]+)\/(\d+)', ip)
                            interface_dict[intf]['ipv4'][ip]['ip'] = m.groups()[0]
                            interface_dict[intf]['ipv4'][ip]['prefix_length'] = m.groups()[1]
                            interface_dict[intf]['ipv4']['unnumbered'] = {}
                            interface_dict[intf]['ipv4']['unnumbered']\
                                ['interface_ref'] = unnumbered_intf

        return(interface_dict)
        
class ShowTunnelIpMaDatabase():

    ''' IOS-XR Parser for "show tunnel ip ma database tunnel-ip 100" '''

    cli_command = 'show tunnel ip ma database tunnel-ip {id}'


##################################################################
#
# Selected fields from show command response
#
##################################################################

    def parse(self, instance_id=None, output=None, test=None):
        if output is None:
            if instance_id:
                cmd = self.cli_command[1].format(instance_id=instance_id)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = self.device.execute(cmd)
        else:
            out = output

#
# Compile regex for each of the lines in the output that contain required data
#
        try:
            p1 = re.compile(r'interface\s+(?P<tunnel_name>\S+).*') # interface tunnel-ip100
            p2 = re.compile(r'.*tunnel base flags:\s+(?P<base_flags>\S+).*') # tunnel base flags: 0x83670
            p3 = re.compile(r'.*tunnel keepalive\s+(?P<keepalive>\S+).*') # tunnel keepalive disabled
            p4 = re.compile(r'.*tunnel mode\s+(?P<mode>\S+)\s+(?P<mode_type>\S+).*') # tunnel mode gre ipv4
            p5 = re.compile(r'.*tunnel transport (?P<transport_type>(\S+[IPv46])).*') # tunnel transport IPv4
            p6 = re.compile(r'.*tunnel source (?P<source_ip>(\d+\.\d+\.\d+\.\d+))') # tunnel source 2.2.2.2
            p7 = re.compile(r'.*tunnel source state (?P<source_state>(\S+[UPDOWN])).*') # tunnel source state UP
            p8 = re.compile(r'.*tunnel destination\s+(?P<destination>.+)') # tunnel destination 3.3.3.3/32
            p9 = re.compile(r'.*tunnel latest reachability\s+(?P<reachability>.+)') # tunnel latest reachability TRUE
            p10 = re.compile(r'.*tunnel converged reachability\s+(?P<converged>.+)') # tunnel converged reachability TRUE
            p11 = re.compile(r'.*tunnel transport vrf name\s+(?P<vrf_name>.+)') # tunnel transport vrf name default
            p12 = re.compile(r'.*tunnel transport vrf id\s+(?P<vrf_id>.+)') # tunnel transport vrf id 0x60000000
            p13 = re.compile(r'.*tunnel ifhandle\s+(?P<ifhandle>.+)') # tunnel ifhandle 0x14
            p14 = re.compile(r'.*tunnel interface state\s+(?P<interface_state>.+)') # tunnel interface state UP
            p15 = re.compile(r'.*tunnel base caps state\s+(?P<base_state>.+)') # tunnel base caps state UP
            p16= re.compile(r'.*tunnel bfd state\s+(?P<bfd_state>\S+).*') # tunnel bfd state DOWN
            p17 = re.compile(r'.*tunnel mtu\s+(?P<mtu>.+)') # tunnel mtu 1500  

        except Exception as e:
            print("%%%% Error processing regex in ShowTunnelIpMaDatabase: " + str(e))

#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            parsed_dict = {}
            tunnel_dict = parsed_dict.setdefault('tunnel_interface', {}) 
            t_dict = tunnel_dict.setdefault('per_tunnel_dict', {})

            for line in out.splitlines():
                line = line.strip()
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()                   
                    t_dict['name'] = str(group['tunnel_name'])
                    continue

                m = p2.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['base-flags'] = str(group['base_flags'])
                    continue
                    
                m = p3.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['keepalive'] = str(group['keepalive'])
                    continue
                    
                m = p4.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['mode'] = str(group['mode'])
                    t_dict['mode-type'] = str(group['mode_type'])
                    continue
                    
                m = p5.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['transport-type'] = str(group['transport_type'])
                    continue
                    
                m = p6.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['source-ip'] = str(group['source_ip'])
                    continue
                    
                m = p7.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['source-state'] = str(group['source_state'])
                    continue
                    
                m = p8.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['destination'] = str(group['destination'])
                    continue

                m = p9.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['reachability'] = str(group['reachability'])
                    continue

                m = p10.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['converged'] = str(group['converged'])
                    continue

                m = p11.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['vrf-name'] = str(group['vrf_name'])
                    continue

                m = p12.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['vrf-id'] = str(group['vrf_id'])
                    continue

                m = p13.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['ifhandle'] = str(group['ifhandle'])
                    continue

                m = p14.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['interface-state'] = str(group['interface_state'])
                    continue

                m = p15.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['base-state'] = str(group['base_state'])
                    continue

                m = p16.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['bfd-state'] = str(group['bfd_state'])
                    continue

                m = p17.match(line)
                if m:
                    group = m.groupdict()
                    t_dict['mtu'] = int(group['mtu'])
                    continue
                    
            return parsed_dict
        except Exception as e:
            print("%%%% Error processing ShowTunnelIpMaDatabase: " + str(e))
