#!/usr/bin/env python
# v1.5c    23/5/2022 First version 
# usage ./alteon2f5.py <input file name> [partition]


#Exporting a Private Key
#>> TAC-APAC - Certificate Repository# /c/slb/ssl/certs/export
#The component type for export can be one of the following: key|certificate|cert+key|request|intermca|trustca
#Enter component type to export: key
 
#Select component to export: TAC-Test
#Enter passphrase:
#Reconfirm passphrase:
#Export to text or file in PEM format [text|file]: file
#Enter hostname (and IP version) or IP address of SCP server: 10.20.240.12
#Enter name of file on SCP server: TAC-Test-Key
#Enter username for SCP server: root
#Enter password for username on SCP server:
 
#TAC-Test-Key successfully transferred to 10.20.240.12
 
#>> TAC-APAC - Certificate Repository#


import sys
import re
import time
import ipaddress
import argparse
import logging

try:
  basestring
except NameError:
  basestring = str

def config_to_array (cfg):
    # Take a config string and converts it into a config array
    # Example 'if 5\n\tena\n\tipver v4\n\taddr 10.230.253.199\n\tmask 255.255.255.240\n\tbroad 10.230.253.207\n\tvlan 1199\n', '\tvlan 1199\n'
    config = {}
    configArray = cfg.split("\n")
    for line in configArray:
        if line == '':
            continue
        line = line.lstrip()
        vars = line.split(' ')
        if len(vars) == 1:
            # No value available
            index,value = vars[0].lstrip(),True
        elif len(vars) == 2:
            # Index and value available
            index,value = vars[0].lstrip(),vars[1].rstrip().strip('\"')
            if index in config:
                # Already an index there
                #print "Type:" + type(config[index])
                if isinstance(config[index],basestring):
                    # Convert it to be a list
                    value = [config[index],value]
                elif isinstance(config[index],list):
                    # Append the value to the list
                    config[index].append(value)
                    continue
        else:
            # Multiple values so concatenate them all together
            index = vars[0].lstrip()
            value = ' '.join(vars[1:])
        config[index] = value
    return config
    
def convertmask (mask):
    return sum([bin(int(x)).count('1') for x in mask.split('.')])    
    
def array_add(a,d):
    # Function to safely add to an array
    #global a
    if not len(a):
        a = [ d ]
    else:
        a.append( d )
    return a
    

def is_ipv6(ip):
    if ':' in ip:
        return True
    else:
        return False



# Handle arguments
parser = argparse.ArgumentParser(description='Alteon Config Converter to F5 Syntax')

parser.add_argument('inputfile', help='File containing Alteon Configuration')
parser.add_argument('partition', default="/Common/", nargs='?', help='Optional partition name eg MyPartition')
parser.add_argument('--csv', help='CSV-formatted modification file')
parser.add_argument('--disable', default=False, action='store_true', help='Set all Virtual Addresses to disabled')
parser.add_argument('--debug', default=False, action='store_true', help='Turn on debugging')
parser.add_argument('--virtual', default=False, help='Output a single virtual server')
args = parser.parse_args()

# Set the partition
if args.partition != "/Common/":
    partition = "/" + args.partition + "/"
else:
    partition = args.partition

# Setup debug logging
logging.basicConfig(filename = args.inputfile.rstrip('.txt') + '.log',
                    filemode = "w",
                    format = "%(asctime)s:%(levelname)s - %(message)s", 
                    level = logging.DEBUG)

logger = logging.getLogger()
if args.debug:
    logger.debug('inputfile:' + args.inputfile)
    logger.debug('partition:' + args.partition)
    logger.debug('CSV file:' + str(args.csv))
    logger.debug('disable:' + str(args.disable))
    logger.debug('debug:' + str(args.debug))
    logger.debug('virtual:' + str(args.virtual))

# Check input file
try:
    with open(args.inputfile,"r") as fh:
        rawfile = fh.read()
except FileNotFoundError:
    logger.critical("Cannot open file " + args.inputfile)
    exit("Cannot open file " + args.inputfile)


# Remove all comments from file
file = re.sub(r'\/c\/dump.+?^\/c','',rawfile)
# Change /r/n to /n
file = re.sub('\r\n','\n',file)

# Handle CSV formatted modification file
modificationDict = {'virtual':{},'node':{}, 'nodename':{}}
if args.csv:
    import csv
    # File is formatted as type eg virtual or node,source IP,source port,destination ip,destination port
    # eg 
    # virtual,1.2.3.4,443,5.6.7.8,443
    # node,10.20.30.40,50.60.70.80

    with open(args.csv,'r') as csvfile:
        for row in csv.reader(csvfile):
            if row[0] == 'virtual':
                if len(row) < 5:
                    row[4] = row[2]
                modificationDict['virtual'][row[1]+":"+row[2]] = row[3]+":"+row[4]
            elif row[0] == 'node':
                modificationDict['node'][row[1]] = row[2]
            elif row[0] == 'nodename':
                modificationDict['nodename'][row[1]] = row[2]
    if args.debug:
        logger.debug('Modification Array Virtual:')
        for row in modificationDict['virtual']:
            logger.debug(str(row))
        logger.debug('Modification Array Node:')
        for row in modificationDict['node']:
            logger.debug(str(row))
        logger.debug('Modification Array Nodename:')
        for row in modificationDict['nodename']:
            logger.debug(str(row))

config = {}
warnings = []

### Define functions to return F5-syntax output

def output_virtual_addresses (config,modificationDict,virtual=False):
    ##### Virtual Addresses ############
    # 
    output = []
    for vsName in config['virtual-addresses']:
        if virtual != False and vsName != virtual:
            # If a single virtual server is specified, only output that
            continue
        if 'vip' in config['virtual-addresses'][vsName]:
            # The virtual address is the IP address
            vip = config['virtual-addresses'][vsName]['vip']
            if vip in modificationDict['virtual']:
                vip = modificationDict['virtual'][vip]
            output.append("ltm virtual-address " + partition + vip + " {")
            output.append("\taddress " + vip)
            output.append("\tdescription \"" + vsName + "\"")
            if args.disable:
                # Disable all virtual addresses
                output.append("\tenabled no")
                output.append("\tarp disabled")
                output.append("\ticmp-echo disabled")
            elif 'dis' in config['virtual-addresses'][vsName]:
                # This Virtual Address is disabled
                output.append("\tenabled no")
            output.append("}")
    if args.debug:
        logger.debug(output)
    return output

##### Virtual Servers ###############
def output_virtual_servers(config,modificationDict,virtual=False):
    output = { 'config':[], 'destination':[], 'pool':[], 'profiles': [], 'irules': [] }
    for vsName in config['virtual-servers']:
        if virtual != False and vsName != virtual:
            # If a single virtual server is specified, only output that
            continue
        for port in config['virtual-servers'][vsName]:
            vscfg = []
            vs = config['virtual-servers'][vsName][port]
            destination = config['virtual-addresses'][vsName]['vip'] + ":" + port
            vscfg.append("ltm virtual " + partition + vsName + "-" + port + " {")
            # Modify the IP address if it is in the modificationDict['virtual'] dictionary
            if destination in modificationDict['virtual']:
                vscfg.append("\tdestination " + modificationDict['virtual'][destination])
                output['destination'].append(modificationDict['virtual'][destination])
            else:
                vscfg.append("\tdestination " + destination)
                output['destination'].append(destination)
            
            # Manage the pool
            pool = ''
            if 'group' in vs and vs['group'] in config['pools']:
                # Specify the pool
                vscfg.append("\tpool " + partition + vs['group'])
                output['pool'].append(vs['group'])
                pool = vs['group']
            elif 'group' in vs and vs['group'] in pool2name:
                newName = pool2name[vs['group']]
                if newName in config['pools']:
                    vscfg.append("\tpool " + partition + config['pools'][newName]['name'])
                    output['pool'].append(config['pools'][newName]['name'])
                    pool = config['pools'][newName]['name']
                else:
                    vscfg.append("\t # ERROR Cannot find pool")
                    output['pool'].append('')
            output['config'].append(vscfg)
            # Manage profiles
            profiles = []
            if 'type' in vs:
                if vs['type'] == 'basic-slb':
                    # FastL4
                    profiles.append('/Common/fastL4 {}')
                elif vs['type'] == 'http' or vs['type'] == 'https':
                    # HTTP/HTTPS
                    profiles.append('/Common/f5-tcp-wan { context clientside }')
                    profiles.append('/Common/f5-tcp-lan { context serverside }')
                    if 'xforward' in vs and vs['xforward'] == 'ena' and 'http_'+vsName in config['profiles']['http']:
                        # This requires X-FORWARDED-FOR
                        profiles.append('http_'+vsName+' {}' )
                    elif vs['type'] == 'http':
                        # Only add the standard HTTP profile to non-HTTPS
                        profiles.append('/Common/http {}' )
                        profiles.append('/Common/oneconnect {}' )

                    if 'srvrcert' in vs and 'clientssl_'+vsName in config['profiles']['client-ssl']:
                        # Client SSL
                        profiles.append('clientssl_'+vsName+' { context clientside }' )
                    # Check the server port/ ssl to detect serverssl use
                    if pool in config['pools'] and 'port' in config['pools'][pool] and config['pools'][pool]['port'] == '443':
                        profiles.append('/Common/serverssl { context serverside }' )                
                elif vs['type'] == 'imap':
                    # IMAP
                    profiles.append('/Common/f5-tcp-wan { context clientside }')
                    profiles.append('/Common/f5-tcp-lan { context serverside }')
                    profiles.append('imap {}')
                elif vs['type'] == 'pop3':
                    # POP3
                    profiles.append('/Common/f5-tcp-wan { context clientside }')
                    profiles.append('/Common/f5-tcp-lan { context serverside }')
                    profiles.append('/Common/pop3 {}')
                elif vs['type'] == 'ftp':
                    # FTP
                    profiles.append('/Common/f5-tcp-wan { context clientside }')
                    profiles.append('/Common/f5-tcp-lan { context serverside }')
                    profiles.append('/Common/ftp {}')
                elif vs['type'] == 'ip':
                    if 'protocol' in vs:
                        if vs['protocol'] == 'udp':
                            profiles.append('/Common/udp')
                            vscfg.append('\tip-protocol udp')
                        else:
                            profiles.append('/Common/tcp')
                    else:
                        profiles.append('/Common/ipother {}')        
                else:
                    profiles.append('/Common/ipother {}')
            output['profiles'].append(profiles)
            # Manage iRules
            if 'irules' in vs and len(vs['irules']):
                output['irules'].append(vs['irules'])
            else:
                output['irules'].append('')
    if args.debug:
        logger.debug(output)
    return output
        

#############################################################################
##### Retrieve elements from the configuration using regular expressions ####
#############################################################################


##### Non-Floating Self-IPs ###########
# /c/l3/if 1
#        ena
#        ipver v4
#        addr 192.168.0.219
#        vlan 4

# self-ip to network to vlan mapping
ip2vlan = { }

##### Non-Floating Self-IPs ###########
config['self-ips'] = []
for line in re.finditer(r'\/c\/l3\/(if \d+\n(\s.+?\n)+)',file,re.MULTILINE|re.DOTALL):
    cfg = config_to_array(line.group(1))
    config['self-ips'].append(cfg)
    if args.debug:
        logger.debug('self-ip:' + str(cfg))

    if 'addr' in cfg and 'mask' in cfg and 'vlan' in cfg:
        addr = ipaddress.ip_network(u'' + cfg['addr'] + '/' + cfg['mask'],strict=False)
        ip2vlan[addr] = { 'vlan': cfg['vlan'], 'mask': cfg['mask'] }
    
##### Floating Self-IPs ###########
config['self-ips-floating'] = []
for line in re.finditer(r'\/c\/l3\/vrrp\/(vr \d+\n(\s.+?\n)+)',file,re.MULTILINE|re.DOTALL):
    cfg = config_to_array(line.group(1))
    config['self-ips-floating'].append(cfg)
    if args.debug:
        logger.debug('self-ips-floating:' + str(cfg))
        
    
##### Routes ###########
config['routes'] = []
for line in re.finditer(r'\/c\/l3\/(gw \d+\n(\s.+?\n)+)',file,re.MULTILINE|re.DOTALL):
    cfg = config_to_array(line.group(1))
    config['routes'].append(cfg)   
    if args.debug:
        logger.debug('routes:' + str(cfg))

##### SSL Certs ###########
config['ssl-certs'] = {}
for line in re.finditer(r'\/c\/slb\/ssl\/certs\/import (\S+) (\S+) text\n(-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----)',file,re.MULTILINE|re.DOTALL):
    type,name,text = line.group(1),line.group(2).strip('\"'),line.group(3)
    config['ssl-certs'][name] = {'type': type, 'text': text}
    if args.debug:
        logger.debug('ssl-certs' + str(cfg))

##### Nodes ###########
# Note that config can be a number, in which case it has a name, or a name in which case it doesn't:
#/c/slb/real 400
#        name "csdd04.pr"

#/c/slb/real Agile_CSR_P_1

config['nodes'] = {}
node2name = {}
for line in re.finditer(r'\/c\/slb\/real (\S+)\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    cfg = config_to_array(line.group(2))
    if 'name' in cfg:
        cfg['description'] = cfg['name']
    name = line.group(1)
    config['nodes'][name] = cfg
    if args.debug:
        logger.debug('nodes:' + str(cfg))

##### Pools ###########
# Note that config can be a number, in which case it has a name, or a name in which case it doesn't:
#/c/slb/group 44
#        name "ASR"

# /c/slb/group INT_CSR_P_TMP_TEST

config['pools'] = {}
pool2name = {}
for line in re.finditer(r'\/c\/slb\/group (\S+)\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name = line.group(1)
    cfg = config_to_array(line.group(2))
    if 'name' in cfg:
        cfg['description'] = cfg['name']
    ## If there is only a single pool member then create it as an array
    if 'add' in cfg and not isinstance(cfg['add'],list):
        cfg['add'] = [ cfg['add'] ]
    config['pools'][name] = cfg
    if args.debug:
        logger.debug('pools:' + str(cfg))
    

##### Monitors - HTTP ###########
#/c/slb/advhc/health monitor_name HTTP/http
#	host "www.example.com"
#	path "nesp/app/heartbeat"
#	response 200 incl "Success"
#   ssl enabled

config['monitors'] = {'http':{},'tcp':{}}
for line in re.finditer(r'\/c\/slb\/advhc\/health (\S+) HTTP(/http)*\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name = line.group(1)
    cfg = config_to_array(line.group(3))
    if 'name' in cfg:
        cfg['description'] = cfg['name']
    cfg['name'] = name
    # If there is another instance of this monitor, this may need to update rather than replace
    if name in config['monitors']['http']:
        config['monitors']['http'][name].update(cfg)
    else:
        config['monitors']['http'][name] = cfg
    if args.debug:
        logger.debug('monitor-http:' + str(cfg))

# TCP
for line in re.finditer(r'\/c\/slb\/advhc\/health (\S+) TCP\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name = line.group(1)
    cfg = config_to_array(line.group(3))
    if 'name' in cfg:
        cfg['description'] = cfg['name']
    cfg['name'] = name
    # If there is another instance of this monitor, this may need to update rather than replace
    if name in config['monitors']['tcp']:
        config['monitors']['tcp'][name].update(cfg)
    else:
        config['monitors']['tcp'][name] = cfg
    if args.debug:
        logger.debug('monitor-tcp:' + str(cfg))


# Find non-HTTP monitors and give a warning
for line in re.finditer(r'\/c\/slb\/advhc\/health (\S+) (\S+/\S+)*\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name = line.group(1)
    type = line.group(2)
    cfg = config_to_array(line.group(3))
    if type != "HTTP/http":
        logger.warning("non-HTTP monitor found of type " + type + " name " + name + " config:" + str(cfg))
    if args.debug:
        logger.debug('monitor-non-HTTP:' + str(cfg))

# Virtual servers are first defined with the virtual address, then have services added such as HTTP or SSL:

#c/slb/virt CUSTLOGIN_EXAMPLE_PUBLIC_HTTPS_VIP
#	ena
#	ipver v4
#	vip 165.27.248.158 <- virtual address
#	vname "custlogin.example.com"
#/c/slb/virt CUSTLOGIN_EXAMPLE_PUBLIC_HTTPS_VIP/service 443 https
#	group CUSTLOGIN_EXAMPLE_VIP_FARM_HTTPS <-- pool name
#	rport 443
#	dbind forceproxy
#	ptmout 60
#/c/slb/virt CUSTLOGIN_EXAMPLE_PUBLIC_HTTPS_VIP/service 443 https/http
#	secwa CUSTLOGIN_EXAMPLE_WAF <-- WAF
#	xforward ena <-- enable X-FORWARDED-FOR
#/c/slb/virt CUSTLOGIN_EXAMPLE_PUBLIC_HTTPS_VIP/service 443 https/ssl
#	srvrcert cert custlogin_example_com_2021 <-- SSL certificate/key name
#	sslpol custlogin_example_POL <-- SSL policy ( where chain certs are defined )
#/c/slb/virt CUSTLOGIN_EXAMPLE_PUBLIC_HTTPS_VIP/service 443 https/pip
#	mode nwclss
#	nwclss v4 SNAT persist disable


##### Virtual Servers ###########
config['virtual-addresses'] = {}
config['virtual-servers'] = {}
config['profiles'] = { 'tcp':{},'http':{},'client-ssl':{} }
###### Virtual Addresses ############
for line in re.finditer(r'\/c\/slb\/virt (\S+)\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name = line.group(1)
    cfg = config_to_array(line.group(2))
    if 'vname' in cfg:
        cfg['description'] = cfg['vname']
    config['virtual-addresses'][name] = cfg
    if args.debug:
        logger.debug('virtual-addresses:' + str(cfg))

##### Virtual Servers ###########

for line in re.finditer(r'\/c\/slb\/virt (\S+)/service (\d+) (\S+)(/\S+)?\n((\s+\S+\s.+\n)*)',file,re.MULTILINE):
    name,port,type = line.group(1),line.group(2),line.group(3)
    cfg = config_to_array(line.group(5))
    cfg['type'] = type.split('/')[0]
    # Add required profiles such as HTTP for XFF, or SSL
    if 'xforward' in cfg and cfg['xforward'] == 'ena':
        # HTTP
        config['profiles']['http']['http_'+name] = { 'defaults-from': 'http', 'insert-xforwarded-for': 'enabled' }
    
    if 'srvrcert' in cfg and cfg['srvrcert'] != '':
        # Client SSL
        cert = cfg['srvrcert'].split(" ")[1]
        config['profiles']['client-ssl']['clientssl_'+name] = {  'defaults-from': 'clientssl', 
                                                                'cert': cert+'.crt', 
                                                                'key': cert+'.key' }
    if 'sslpol' in cfg and cfg['sslpol'] != '':
        logger.warning('ClientSSL profile clientssl_'+name+' has an SSL policy applied. Requires manual conversion' )

    if 'action' in cfg and cfg['action'] == 'redirect':
        # This is a redirect - probably 80 to 44
        if 'redirect' in cfg and cfg['redirect'] == 'https://$HOST/$PATH?$QUERY':
            cfg['irules'] = ['/Common/_sys_https_redirect']
        else:
            logger.warning('Virtual Server ' + name + ' has a redirect action. Manual intervention is required')
    # Manage pool ports
    if 'rport' in cfg and cfg['rport'] != '' and 'group' in cfg:
        # rport is the port for the pool members
        if cfg['group'] in config['pools']:
            config['pools'][cfg['group']]['port'] = cfg['rport']
        else:
            logger.warning('Virtual Server ' + name + ' has an rport set but cannot find pool ' + cfg['group'])


    if name in config['virtual-servers'] and port in config['virtual-servers'][name]:
        config['virtual-servers'][name][port].update(cfg)
    elif name in config['virtual-servers']:
        config['virtual-servers'][name][port] = cfg
    else:
        config['virtual-servers'][name] = { port: cfg }
    if args.debug:
        logger.debug('virtual-servers:' + str(cfg))


##########################################################################
#
# We have collected all of the relevant information. Now to print it out  
#
#


if args.virtual != False:
    # Specify a single virtual server
    virtual_server_list = [ args.virtual ]
else:
    # Print out all virtual servers
    virtual_server_list = config['virtual-servers'].keys()

print ("# Configuration created on " + time.strftime("%c") )
print ("# Input filename: " + args.inputfile )
print ("# Partition: " + partition )
# Stats
print("# -- Number of input objects --")
print("# Type\t\t\tNumber")
print("# ----------------------------")
print("# SSL certs\t\t" + str(len(config['ssl-certs'])))
print("# Self-IPs\t\t" + str(len(config['self-ips'])))
print("# Floating Self-IPs\t" + str(len(config['self-ips-floating'])))
print("# Nodes\t\t\t" + str(len(config['nodes'])))
print("# Monitors - HTTP\t" + str(len(config['monitors']['http'])))
print("# Monitors - TCP\t" + str(len(config['monitors']['tcp'])))
print("# Pools\t\t\t" + str(len(config['pools'])))
print("# Virtual Addresses\t" + str(len(config['virtual-addresses'])))
print("# Virtual Servers\t" + str(len(config['virtual-servers'])))

print("# ----------------------------\n\n")
print("# -- Number of virtual servers to output:" + str(len(virtual_server_list)) + " --")
print ("\n#-------------------------------------------------------")
print ("#----- Configuration below this line   -----------------\n")    
print ("\n\n")

# Create master list of used certificates
cert_load_list = []

for virtualserver in virtual_server_list:

    print("# " + virtualserver )
    if not virtualserver in config['virtual-servers']:
        # virtual server is not found in confi
        print("# ERROR! Cannot find virtual server " + virtualserver + " in config file " + args.inputfile)
    # Note that the virtual server can have a single name but multiple ports eg port 80 and 443
    # Start with printing out virtual server config, then loop through pool/profiles etc
    
    virtual_address_config = output_virtual_addresses(config,modificationDict,virtualserver)
    virtual_server_config = output_virtual_servers(config,modificationDict,virtualserver)
    
    #print('# Virtual Address')
    for index in range(0,len(virtual_address_config)):
        print(virtual_address_config[index])
    
    #print("# Virtual Server " + virtualserver )
    for index in range(0,len(virtual_server_config['config'])):
        # Print the destination
        for line in virtual_server_config['config'][index]:
            print(line)
        # Print the pool
        if len(virtual_server_config['pool']) < index:
            print('\t# WARNING No pool assigned')
        else:
            if len(virtual_server_config['pool']) > index:
                pool = virtual_server_config['pool'][index]
            else:
                pool = ''
            if pool and pool != '':
                if pool in config['pools']:
                    # Print out pool
                    pool_config = config['pools'][pool]
                    #print(' Pool config:' + str(pool_config))
                else:
                    print('# WARNING Pool ' + pool + ' is not in config')
            else:
                # No pool assigned
                print('# WARNING No pool assigned')

        # Profiles
        print('\tprofiles {')
        profiles = []
        for profile in virtual_server_config['profiles'][index]:
            if profile.startswith('/Common/'):
                print('\t\t' + profile)
            else:    
                print('\t\t' + partition + profile)
            profiles.append(profile)
        print('\t}')

        # Print out iRules
        if virtual_server_config['irules'][index]:
            print('\trules {')
            for rule in virtual_server_config['irules'][index]:
                print('\t\t' + rule)
            print('\t}')
        # Close VS
        print('}')

        # Print pool
        print('# Pool ' + pool)
        print("ltm pool " + partition + pool + " {")
        if 'group' in pool_config:
            print("\tdescription \"group " + pool_config['group'] + "\"" )
        monitor_list = []
        if 'health' in pool_config:
            if not pool_config['health'] in config['monitors']:
                print("\t# WARNING! Cannot find monitor " + pool_config['health'])
            else:
                print("\tmonitor min 1 of { " + partition + pool_config['health'] + " }")
                monitor_list.append(pool_config['health'])
        # Manage pool members
        if 'port' in pool_config:
            port = pool_config['port']
        else:
            port = '0'
            logger.warning("No port found for pool " + pool)
        if 'add' in pool_config:
            print("\tmembers {")
            node_list = []
            for poolMember in pool_config['add']:
                # Check it exists in the node config. If not, check node2name for the new name
                if poolMember in config['nodes']:
                    # Note that this is the nodeId, there is no port number
                    # So we are going to add the node name and port 0 and leave the VS to sort it out
                    if poolMember in modificationDict['nodename']:
                        print ("\t\t" + partition + modificationDict['nodename'][poolMember] + ":" + port)
                    else:
                        print ("\t\t" + partition + poolMember + ":" + port)
                    node_list.append(poolMember)
                else:
                    print ("# Error - cannot find node for " + poolMember)
            print("\t}")
        print("}")
        # Nodes
        for node in node_list:
            if node in config['nodes']:
                if node in modificationDict['nodename']:
                    print('ltm node ' + partition + modificationDict['nodename'][node] + ' {')
                else:
                    print('ltm node ' + partition + node + ' {')
                if 'rip' in config['nodes'][node]:
                    if config['nodes'][node]['rip'] in modificationDict['node']:
                        print("\taddress " + modificationDict['node'][config['nodes'][node]['rip']])
                    else:
                        print("\taddress " + config['nodes'][node]['rip'])
                else:
                    print('\t#WARNING Node has no IP address assigned')
                if 'ena' in config['nodes'][node] and config['nodes'][node]['ena'] == 'False':
                    # Node is disabled
                    print('\tenabled no')
                if 'description' in config['nodes'][node]:
                    print('\tdescription "' + config['nodes'][node]['description'] + '"')

                print('}')

        # Monitors
        for monitor in monitor_list:
            if monitor in config['monitors']['http']:
                if 'ssl' in config['monitors']['http'][monitor] and config['monitors']['http'][monitor]['ssl'] == 'enabled':
                    # This is an HTTPS monitor
                    print('ltm monitor https ' + partition + monitor + ' {')
                else:
                    # HTTP monitor
                    print('ltm monitor http ' + partition + monitor + ' {')
                if 'description' in config['monitors']['http'][monitor]:
                    print('\tdescription "' + config['monitors']['http'][monitor]['description'] + '"')
                if 'path' in config['monitors']['http'][monitor]:
                    print('\tsend GET /' + config['monitors']['http'][monitor]['path'] + ' HTTP/0.9\\r\\n\\r\\n')
                print('}')
            else:
                print('# WARNING Cannot find monitor ' + monitor)


        # Profiles
        certs = []
        standard_profiles = {   '/Common/http', 
                                '/Common/oneconnect', 
                                '/Common/f5-tcp-wan', 
                                '/Common/f5-tcp-lan', 
                                '/Common/udp',
                                '/Common/fastL4',
                                '/Common/serverssl'
                            }
        for profile in profiles:
            if profile.split(' ')[0] in standard_profiles:
                continue
            if profile.startswith('http'):
                profilename = profile.rstrip(' {}')
                if profilename in config['profiles']['http']:
                    print('ltm profile http ' + partition + profilename + ' {')
                    for i,v in config['profiles']['http'][profilename].items():
                        print('\t' + i + ' ' + v)
                    print('}')
            elif profile.startswith('clientssl'):
                profilename = profile.rstrip('context { clientside }')
                if profilename in config['profiles']['client-ssl']:
                    print('ltm profile client-ssl ' + partition + profilename + ' {')

                    for i,v in config['profiles']['client-ssl'][profilename].items():
                        if i == 'cert':
                            certs.append(v.rstrip('.crt'))
                        print('\t' + i + ' ' + v)
                    print('}')
                else:
                    print('# WARNING Cannot find client-ssl profile ' + profilename + 'in config')
        # SSL certs
        if len(certs):
            for cert in certs:
                if not cert in config['ssl-certs']:
                    print('# WARNING Cannot find text for cert ' + cert)
                    continue
                print ("# -- Writing SSL cert " + cert)
                with open(cert + ".crt",'w') as certFile:
                    certFile.write(config['ssl-certs'][cert]['text'])
                    cert_load_list.append(cert)
                print("# -- Finished creating SSL cert " + cert + " --")
        # Create a separator line
        print("\n\n### ----------------------------------------------\n\n")


# Create load_certs.sh script to load the certs
with open(args.inputfile.rstrip('.txt') + "_load_certs.sh",'w') as loadFile:
    loadFile.write("#!/bin/bash\n# Script to load SSL certs to F5\n")
    for cert in cert_load_list:
        loadFile.write("tmsh install sys crypto cert " + partition + cert + ".crt from-local-file /var/tmp/" + cert + ".crt\n")
    print ("#!! Copy *.crt files to /var/tmp directory on BIG-IP and run load_certs.sh script !!")

#
# Create export_keys.txt
with open("export_keys.txt",'w') as loadFile:
    loadFile.write("# This is a list of keys to export\n")
    loadFile.write("# Exporting a Private Key Example:\n\n")
    loadFile.write("# >> TAC-APAC - Certificate Repository# /c/slb/ssl/certs/export\n")
    loadFile.write("# The component type for export can be one of the following: key|certificate|cert+key|request|intermca|trustca\n")
    loadFile.write("# Enter component type to export: key\n")
 
    loadFile.write("# Select component to export: TAC-Test\n")
    loadFile.write("# Enter passphrase:\n")
    loadFile.write("# Reconfirm passphrase:\n")
    loadFile.write("# Export to text or file in PEM format [text|file]: file\n")
    loadFile.write("# Enter hostname (and IP version) or IP address of SCP server: 10.20.240.12\n")
    loadFile.write("# Enter name of file on SCP server: TAC-Test-Key\n")
    loadFile.write("# Enter username for SCP server: root\n")
    loadFile.write("# Enter password for username on SCP server:\n\n")
    loadFile.write("# TAC-Test-Key successfully transferred to 10.20.240.12\n\n\n")
    loadFile.write("# List of keys to export:\n")
    for cert in cert_load_list:
        loadFile.write(cert + "\n")
            

##### No-Floating Self-IPs ########
for ip in config['self-ips']:
    if 'ena' not in ip:
        continue
    if 'ipver' in ip and ip['ipver'] == "v6":
        continue
    if 'if' in ip:
        # Self-IP interface is specified, retrieve the mask of the self-IP
        for a in ip2vlan:
            # Handle IPv4 and IPv6 addresses
            #print(ip['addr'])
            if ':' in str(a):
                #print("IPv6")
                if ipaddress.IPv6Address(u'' + ip['addr']) in a:
                    if 'vlan' in ip2vlan[a]:
                        vlan = ip2vlan[a]['vlan']
                    else:
                        logger.warning("No VLAN found for " + ip['addr'])
                        vlan = "#"

                    if 'mask' in ip2vlan[a]:
                        mask = str(convertmask(ip2vlan[a]['mask']))
                    else:
                        logger.warning("No VLAN found for " + ip['addr'])
                        mask = "24"
                    break
            else:
                #print("IPv4")
                if ipaddress.IPv4Address(u'' + ip['addr']) in a:
                    if 'vlan' in ip2vlan[a]:
                        vlan = ip2vlan[a]['vlan']
                    else:
                        logger.warning("No VLAN found for " + ip['addr'])
                        vlan = "#"

                    if 'mask' in ip2vlan[a]:
                        mask = str(convertmask(ip2vlan[a]['mask']))
                    else:
                        logger.warning("No VLAN found for " + ip['addr'])
                        mask = "24"
                    break
        else:
            vlan = "# Cannot find VLAN"
            mask = "24 # Cannot find mask, check this is correct"
            logger.warning("Cannot find vlan or mask for " + ip['addr'])
    print ("net self IP_" + ip['addr'] + " {")
    print ("\taddress " + ip['addr'] + "/" + mask)
    print ("\ttraffic-group traffic-group-local-only")
    print ("\tvlan " + vlan)
    print ("}")

# To Do - print out non-floating self-IPs