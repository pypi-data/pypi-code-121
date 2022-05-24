# Kage Park
# Inteligent BMC Tool
# Version 2

import os
from distutils.spawn import find_executable
import time
import sys
import kmisc as km
import json
import re
import threading

class Ipmitool:
    def __init__(self,**opts):
        self.__name__='ipmitool'
        self.tool_path=None
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status'],'shutdown':['chassis power soft']})
        self.ipmitool=True
        if find_executable('ipmitool') is False:
            self.ipmitool=False

    def cmd_str(self,cmd,**opts):
        if not self.ipmitool:
            km.logging('Install ipmitool package(yum install ipmitool)',log=self.log,log_level=1,dsp='e')
            return False,'ipmitool file not found',{}
        cmd_a=cmd.split()
        option=opts.get('option','lanplus')
        if km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'power',1) and km.get_value(cmd_a,2) in self.power_mode:
            cmd_a[0] = 'chassis'
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'reset',1):
            cmd_a=['mc','reset','cold']
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'lan',1):
            if len(cmd_a) == 3 and cmd_a[2] in ['mac','dhcp','gateway','netmask']:
                cmd_a=['lan','print']
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'sensor',1):
            cmd_a=['sdr','type','Temperature']
        return True,{'base':'''ipmitool -I %s -H {ip} -U {user} -P '{passwd}' '''%(option),'cmd':'''%s'''%(' '.join(cmd_a))},None,{'ok':[0],'fail':[1]},None


class Smcipmitool:
    def __init__(self,**opts):
        self.__name__='smc'
        self.smc_file=opts.get('smc_file',None)
        if self.smc_file and not os.path.isfile(self.smc_file):
            self.smc_file=None
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['ipmi power up'],'off':['ipmi power down'],'reset':['ipmi power reset'],'off_on':['ipmi power down','ipmi power up'],'on_off':['ipmi power up','ipmi power down'],'cycle':['ipmi power cycle'],'status':['ipmi power status'],'shutdown':['ipmi power softshutdown']})

    def cmd_str(self,cmd,**opts):
        cmd_a=cmd.split()
        if not self.smc_file:
            km.logging('- SMCIPMITool({}) not found'.format(self.smc_file),log=self.log,log_level=1,dsp='e')
            return False,'SMCIPMITool file not found',{}
        if km.check_value(cmd_a,'chassis',0) and km.check_value(cmd_a,'power',1):
            cmd_a[0] == 'ipmi'
        elif km.check_value(cmd_a,'mc',0) and km.check_value(cmd_a,'reset',1) and km.check_value(cmd_a,'cold',2):
            cmd_a=['ipmi','reset']
        elif km.check_value(cmd_a,'lan',0) and km.check_value(cmd_a,'print',1):
            cmd_a=['ipmi','lan','mac']
        elif km.check_value(cmd_a,'sdr',0) and km.check_value(cmd_a,'Temperature',2):
            cmd_a=['ipmi','sensor']
        return True,{'base':'''sudo java -jar %s {ip} {user} '{passwd}' '''%(self.smc_file),'cmd':'''%s'''%(' '.join(cmd_a))},None,{'ok':[0,144],'error':[180],'err_bmc_user':[146],'err_connection':[145]},None

class Redfish:
    def __init__(self,**opts):
        self.__name__='redfish'
        self.log=opts.get('log',None)
        if isinstance(opts.get('path'),dict):
            self.path=opts['path']
        else:
            self.path={
                'virtualmedia':'/redfish/v1/Managers/1/VirtualMedia',
                'floppyimage':'/redfish/v1/Managers/1/VirtualMedia/Floppy1',
                'Marvell':'Systems/1/Storage/MRVL.HA-RAID/Volumes/Controller.0.Volume.0',
                'LSI3108':'Systems/1/Storage/HA-RAID',
                'EthernetCount':'Systems/1/EthernetInterfaces',
                'PsuCount':'Chassis/1/Power',
                'BootOption':'Systems/1/BootOptions',
            }
        self.user=opts.get('user','ADMIN')
        self.passwd=opts.get('passwd','ADMIN')
        self.host=opts.get('host')

    def Cmd(self,cmd,host=None):
        if not host: host=self.host
        if cmd.startswith('/redfish/v1'):
            return "https://{}{}".format(host,cmd)
        elif cmd.startswith('redfish/v1'):
            return "https://{}/{}".format(host,cmd)
        elif cmd.startswith('https:') and 'redfish' in cmd.split('/') and host is None:
            return "{}".format(cmd)
        elif cmd.startswith('/'):
            return "https://{}/redfish/v1{}".format(host,cmd)
        else:
            return "https://{}/redfish/v1/{}".format(host,cmd)

    def Get(self,cmd,host=None):
        if not host: host=self.host
        if not isinstance(cmd,str): return False
        data = km.web_req(self.Cmd(cmd,host=host),auth=(self.user, self.passwd))
        if data[0] and data[1].status_code == 200:
            return json.loads(data[1].text)
        return False

    def Post(self,cmd,host=None,json=None,data=None,files=None,mode='post'):
        if not host: host=self.host
        if not isinstance(cmd,str): return False
        data = km.web_req(self.Cmd(cmd,host=host),auth=(self.user, self.passwd),mode=mode,json=json,data=data,files=files)
        if data[0] and data[1].status_code == 200:
            return True
        return False

    def Data(self,data):
        ndata={}
        if isinstance(data,dict):
            ndata['child']={}
            for xx in data:
                if xx == '@odata.id':
                    ndata['path']=data.get(xx)
                elif xx == 'Name':
                    ndata['name']=data.get(xx)
                elif xx == 'UUID':
                    ndata['uuid']=data.get(xx)
                elif xx == 'RedfishVersion':
                    ndata['version']=data.get(xx)
                elif xx == 'Description':
                    ndata['desc']=data.get(xx)
                elif xx == 'Members':
                    for ii in data.get('Members'):
                        ndata['child'][os.path.basename(ii.get('@odata.id'))]=ii.get('@odata.id')
                else:
                    if isinstance(data[xx],dict):
                        ndata[xx]=data[xx].get('@odata.id')
        return ndata


    def Power(self,cmd='status',pxe=False,pxe_keep=False):
        def get_current_power_state():
            current_power='unknown'
            aa=self.Get('Systems/1')
            if aa and aa.get('PowerState'):
                current_power=aa.get('PowerState')
            if current_power is None:
                aa=self.Get('Managers/1/Oem/Supermicro/SmartPower')
                if aa:
                    current_power=aa.get('PowerStatus')
            return current_power
        current_power=get_current_power_state().lower()
        if cmd == 'status':
            return current_power
        if cmd in ['on','off','shutdown','reboot','reset','off_on']:
            def cmd_state(cmd,on_s=['on'],off_s=['off','shutdown']):
                if cmd in on_s:
                    return 'on'
                elif cmd in off_s:
                    return 'off'
                return None
            if cmd_state(cmd) == current_power: return True
            if pxe and cmd in ['on','reset','reboot','off_on']:
                if pxe_keep:
                    self.Boot(boot='Pxe',keep='keep')
                else:
                    self.Boot(boot='Pxe')
            if cmd == 'on':
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'On'})
            elif cmd == 'off':
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'ForceOff'})
            elif cmd == 'shutdown':
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'GracefulShutdown'})
            elif cmd == 'reset':
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'ForceRestart'})
            elif cmd == 'reboot':
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'GracefulRestart'})
            elif cmd == 'off_on':
                if current_power != 'off':
                    aa=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'ForceOff'})
                    for i in range(0,600):
                        current_power=get_current_power_state().lower()
                        if current_power == 'off':
                            time.sleep(2)
                            break
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        time.sleep(1)
                rt=self.Post('/Systems/1/Actions/ComputerSystem.Reset',json={'Action': 'Reset', 'ResetType': 'On'})
            for i in range(0,600):
                sys.stdout.write('-')
                sys.stdout.flush()
                if cmd_state(cmd,on_s=['reset','on','reboot','off_on']) == get_current_power_state().lower():
                    time.sleep(1)
                    return True
                time.sleep(1)
            return False
        else:
            if cmd == 'info':
                naa={}
                aa=self.Get('Managers/1/Oem/Supermicro/SmartPower')
                if aa:
                    naa['status']=aa.get('PowerStatus')
                    naa['max']=aa.get('MaxPower')
                    naa['cap']=aa.get('PowerCapping')
                aa=self.Get('Chassis/1/Power')
                if aa:
                    naa['psu']={}
                    if aa.get('PowerControl'):
                        interval='{}m'.format(aa.get('PowerControl')[0].get('PowerMetrics',{}).get('IntervalInMin'))
                        naa['psu'][interval]={}
                        #naa['psu']['cap']=aa.get('PowerControl')[0].get('PowerCapacityWatts')
                        #naa['psu']['output']=aa.get('PowerControl')[0].get('PowerConsumedWatts')
                        naa['psu'][interval]['max']=aa.get('PowerControl')[0].get('PowerMetrics',{}).get('MaxConsumedWatts')
                        naa['psu'][interval]['min']=aa.get('PowerControl')[0].get('PowerMetrics',{}).get('MinConsumedWatts')
                        naa['psu'][interval]['avg']=aa.get('PowerControl')[0].get('PowerMetrics',{}).get('AverageConsumedWatts')
                    for psu in aa.get('PowerSupplies'):
                        idx=psu.get('MemberId')
                        naa['psu'][idx]={}
                        naa['psu'][idx]['model']=psu.get('Model')
                        naa['psu'][idx]['watt']=psu.get('PowerCapacityWatts')
                        naa['psu'][idx]['output']=psu.get('LastPowerOutputWatts')
                        naa['psu'][idx]['firmware']=psu.get('FirmwareVersion')
                        naa['psu'][idx]['sn']=psu.get('SerialNumber')
                        naa['psu'][idx]['type']=psu.get('PowerSupplyType')
                        naa['psu'][idx]['health']=psu.get('Status',{}).get('Health')
                        input_source=psu.get('LineInputVoltageType')
                        input_volt=psu.get('LineInputVoltage')
                        if input_source=='Unknown':
                            input_source=input_source+'(Maybe unpluged cable)'
                        else:
                            input_source=input_source+'({}V)'.format(input_volt)
                        naa['psu'][idx]['input']=input_source
                return naa
            elif cmd == 'ID_LED':
                aa=self.Get('Chassis/1')
                if aa:
                    return aa.get('IndicatorLED')
    
    def Boot(self,boot=None,mode='auto',keep='once',simple_mode=False):
        if isinstance(boot,str) and boot.lower() in ['efi_shell','uefi_shell','shell','pxe','ipxe','cd','usb','hdd','floppy','bios','setup','biossetup']:
            if boot.lower() in ['efi_shell','uefi_shell','shell']:
                keep='Continuous'
                mode='UEFI'
                boot='BiosSetup'
            else:
                aa=self.Get('Systems/1')
                if not aa:
                    return False
                boot_info=aa.get('Boot',{})
                if boot.lower() == 'ipxe':
                    boot='pxe'
                    mode='UEFI'
                if mode.lower() in ['uefi','efi']:
                    mode='UEFI'
                elif mode.lower() == 'legacy':
                    mode='Legacy'
                else:
                    bios_mode=self.Get('Systems/1/Bios')
                    if bios_mode and not km.IsNone(bios_mode.get('Attributes',{}).get('BootModeSelect')):
                        mode=bios_mode.get('Attributes',{}).get('BootModeSelect')
                    elif not km.IsNone(boot_info.get('BootSourceOverrideMode')):
                        mode=boot_info.get('BootSourceOverrideMode')
                if km.IsNone(mode): mode='Legacy'
                if keep in [None,False,'disable','del','disabled']:
                    keep='Disabled'
                elif keep in ['keep','continue','force','continuous']:
                    keep='Continuous'
                else:
                    keep='Once'
                if boot.lower() in ['pxe']:
                    boot='Pxe'
                elif boot.lower() in ['cd']:
                    boot='Cd'
                elif boot.lower() in ['usb']:
                    boot='Usb'
                elif boot.lower() in ['hdd']:
                    boot='Hdd'
                elif boot.lower() in ['floppy']:
                    boot='Floppy'
                elif boot.lower() in ['bios','setup','biossetup']:
                    mode='Legacy'
                    boot='BiosSetup'
                    keep='Once'
                if mode == 'Dual': mode='Legacy'
                if 'BootSourceOverrideTarget@Redfish.AllowableValues' in boot_info and 'BootSourceOverrideMode@Redfish.AllowableValues' in boot_info:
                    if boot not in boot_info.get('BootSourceOverrideTarget@Redfish.AllowableValues') or mode not in boot_info.get('BootSourceOverrideMode@Redfish.AllowableValues'):
                        print('!!WARN: BOOT({}) not in {} or MODE({}) not in {}'.format(boot,boot_info.get('BootSourceOverrideTarget@Redfish.AllowableValues'),mode,boot_info.get('BootSourceOverrideMode@Redfish.AllowableValues')))
            boot_db={'Boot':{ 
                 'BootSourceOverrideEnabled':keep,
                 'BootSourceOverrideMode':mode,
                 'BootSourceOverrideTarget':boot
                 } 
            }
            return self.Post('Systems/1',json=boot_db,mode='patch')
        else:
            if simple_mode:
                aa=self.Get('Systems/1/Bios')
                if aa:
                    return aa.get('Attributes',{}).get('BootModeSelect')
            else:
                naa={'order':{},'bios':{}}
                aa=self.Get('Systems/1')
                if aa:
                    boot_info=aa.get('Boot',{})
                    if boot_info:
                        naa['order']['mode']=boot_info.get('BootSourceOverrideMode')
                        naa['order']['1']=boot_info.get('BootSourceOverrideTarget')
                        naa['order']['enable']=boot_info.get('BootSourceOverrideEnabled')
                        naa['order']['help']={}
                        if 'BootSourceOverrideMode@Redfish.AllowableValues' in boot_info: naa['order']['help']['mode']=boot_info.get('BootSourceOverrideMode@Redfish.AllowableValues')
                        if 'BootSourceOverrideTarget@Redfish.AllowableValues' in boot_info: naa['order']['help']['boot']=boot_info.get('BootSourceOverrideTarget@Redfish.AllowableValues')
                aa=self.Get('Systems/1/Bios')
                if aa:
                    boot_info=aa.get('Attributes',{})
                    naa['bios']['mode']=boot_info.get('BootModeSelect')
                    naa['bios']['order']=[]
                    for ii in boot_info:
                        if ii.startswith('BootOption#1$') or ii in ['BootOption#1']:
                            naa['bios']['order'].append(boot_info[ii])
                    naa['bios']['OnboardVideoOptionROM']=boot_info.get('OnboardVideoOptionROM')
                if isinstance(boot,str) and boot.lower() == 'order':
                    return '''Boot Flags :
   - BIOS {} boot
   - Options apply to {}
   - Boot Device Selector : {}
   - Boot with {}
'''.format(naa['bios']['mode'],'all future boots' if naa['order']['enable'] == 'Continuous' else naa['order']['enable'],naa['order']['1'],naa['order']['mode'])
                return naa

    def IsUp(self,timeout=300):
        for ii in range(0,timeout):
            aa=self.Get('Systems')
            if aa is False:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(2)
                continue
            else:
                return True
        return False

    def BmcVer(self):
        #UUID.split('-')[-1] <== BMC Mac
        aa=self.Get('UpdateService/FirmwareInventory/BMC')
        if aa: return aa.get('Version')
        aa=self.Get('Managers/1')
        if aa: return aa.get('FirmwareVersion')

    def BiosVer(self):
        #UUID.split('-')[-1] <== LAN1 Mac
        aa=self.Get('UpdateService/FirmwareInventory/BIOS')
        if aa: return aa.get('Version')
        aa=self.Get('Systems/1')
        if aa: return aa.get('BiosVersion')

    def RedfishHI(self):
        aa=self.Get('Systems/1/EthernetInterfaces/ToManager')
        naa={}
        if aa:
            ipv4=aa.get('IPv4Addresses')[0]
            naa['ip']=ipv4.get('Address')
            naa['netmask']=ipv4.get('SubnetMask')
            naa['gateway']=ipv4.get('Gateway')
            naa['mtu']=aa.get('MTUSize')
            naa['full_duplex']=aa.get('FullDuplex')
            naa['auto']=aa.get('AutoNeg')
            naa['speed']=aa.get('SpeedMbps')
            naa['mac']=aa.get('PermanentMACAddress')
            naa['enable']=aa.get('InterfaceEnabled')
            naa['status']=aa.get('Status',{}).get('Health')
        return naa

    def BaseMac(self):
        naa={}
        aa=self.Get('Managers/1')
        if aa:
            naa['bmc']=km.str2mac(aa.get('UUID').split('-')[-1])
        aa=self.Get('Systems/1')
        if aa:
            naa['lan']=km.str2mac(aa.get('UUID').split('-')[-1])
        return naa 

    def Network(self):
        naa={}
        aa=self.Get('Chassis/1/NetworkAdapters')
        if aa:
            for ii in aa.get('Members',[]):
                ai=self.Get(ii.get('@odata.id'))
                naa[ai.get('Id')]={}
                naa[ai.get('Id')]['model']=ai.get('Model')
                naa[ai.get('Id')]['sn']=ai.get('SerialNumber')
                if ai.get('Controllers'):
                    naa[ai.get('Id')]['firmware']=ai.get('Controllers')[0].get('FirmwarePackageVersion')
                    naa[ai.get('Id')]['pci']='{}({})'.format(ai.get('Controllers')[0].get('PCIeInterface',{}).get('PCIeType'),ai.get('Controllers')[0].get('PCIeInterface',{}).get('LanesInUse'))
                    naa[ai.get('Id')]['max_pci']='{}({})'.format(ai.get('Controllers')[0].get('PCIeInterface',{}).get('MaxPCIeType'),ai.get('Controllers')[0].get('PCIeInterface',{}).get('MaxLanes'))
                naa[ai.get('Id')]['port']={}
                port=self.Get(ai.get('NetworkPorts').get('@odata.id'))
                for pp in port.get('Members'):
                    port_q=self.Get(pp.get('@odata.id'))
                    naa[ai.get('Id')]['port'][os.path.basename(pp.get('@odata.id'))]=port_q.get('AssociatedNetworkAddresses')[0]
        return naa

    def Memory(self):
        naa={}
        aa=self.Get('Systems/1/Memory')
        if aa:
            for ii in aa.get('Members',[]):
                ai=self.Get(ii.get('@odata.id'))
                idx=ai.get('Id')
                naa[idx]={}
                naa[idx]['dimm']=ai.get('DeviceLocator')
                naa[idx]['speed']=ai.get('AllowedSpeedsMHz')[0]
                naa[idx]['size']=ai.get('LogicalSizeMiB')
                naa[idx]['ecc']=ai.get('ErrorCorrection')
                naa[idx]['brand']=ai.get('Manufacturer')
                naa[idx]['partnumber']=ai.get('PartNumber')
                naa[idx]['sn']=ai.get('SerialNumber')
        return naa

    def Cpu(self):
        naa={}
        aa=self.Get('Systems/1/Processors')
        if aa:
            for ii in aa.get('Members',[]):
                ai=self.Get(ii.get('@odata.id'))
                idx=ai.get('Id')
                naa[idx]={}
                naa[idx]['watt']=ai.get('MaxTDPWatts')
                naa[idx]['type']=ai.get('Location',{}).get('PartLocation',{}).get('LocationType')
                naa[idx]['location']=ai.get('Location',{}).get('PartLocation',{}).get('ServiceLabel')
                naa[idx]['model']=ai.get('Model')
                naa[idx]['speed']=ai.get('MaxSpeedMHz')
                naa[idx]['step']=ai.get('ProcessorId',{}).get('Step')
                naa[idx]['cores']=ai.get('TotalCores')
        return naa

    def Info(self):
        naa={}
        naa['version']={'bios':self.BiosVer(),'bmc':self.BmcVer()}
        naa['network']=self.Network()
        naa['redfish_hi']=self.RedfishHI()
        naa['power']=self.Power('info')
        naa['memory']=self.Memory()
        naa['cpu']=self.Cpu()
        aa=self.Get('Managers/1')
        naa['mac']={}
        if aa:
            naa['mac']['bmc']=km.str2mac(aa.get('UUID').split('-')[-1])
        aa=self.Get('Systems/1')
        if aa:
            naa['mac']['lan']=km.str2mac(aa.get('UUID').split('-')[-1])
        aa=self.Get('Chassis/1')
        if aa:
            manufacturer=aa.get('Manufacturer')
            naa['manufacturer']=manufacturer
            naa['boardid']=aa.get('Oem',{}).get(manufacturer,{}).get('BoardID')
            naa['sn']=aa.get('Oem',{}).get(manufacturer,{}).get('BoardSerialNumber')
            naa['guid']=aa.get('Oem',{}).get(manufacturer,{}).get('GUID')
        return naa

    def BiosPassword(self,new,old=''):
        #Not perfectly work now
        passwd_db={
            'PasswordName':'AdminPassword',
            'OldPassword':old,
            'NewPassword':new,
        }
        return self.Post('Systems/1/Bios/Actions/Bios.ChangePassword',json=passwd_db)

    def FactoryDefaultBios(self):
        return self.Post('Systems/1/Bios/Actions/Bios.ResetBios')

    def VirtualMedia(self,mode='floppy'):
        vv=self.Get('Managers/1/VirtualMedia')
        mode=mode.lower()
        info=[]
        for ii in vv.get('Members',[]):
            redfish_path=None
            if mode == 'floppy' and os.path.basename(ii.get('@odata.id')).startswith('Floppy'):
                redfish_path=ii.get('@odata.id')
            elif mode == 'cd' and os.path.basename(ii.get('@odata.id')).startswith('CD'):
                redfish_path=ii.get('@odata.id')
            elif mode == 'all':
                redfish_path=ii.get('@odata.id')
            if redfish_path:
                aa=self.Get(redfish_path)
                if aa:
                    if aa.get('Inserted'):
                        if aa.get('ConnectedVia') == 'URI':
                            info.append('SUM:{}'.format(aa.get('Id')))
                        elif aa.get('ConnectedVia') == 'Applet':
                            info.append('KVM:{}'.format(aa.get('Id')))
        if info:
            return ','.join(info)
        return False

    def IsEnabled(self,timeout=10):
        old=km.now()
        while km.now() - old < timeout:
            aa=self.Get('Systems')
            if aa is False:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
                continue
            else:
                return True
        return False

class kBmc:
    def __init__(self,*inps,**opts):
        self.ip=opts.get('ipmi_ip')
        if not self.ip: self.ip=opts.get('ip')
        self.port=opts.get('ipmi_port',(623,664,443))
        self.mac=opts.get('mac')
        if not self.mac: self.mac=opts.get('bmc_mac')
        if not self.mac: self.mac=opts.get('ipmi_mac')
        self.eth_mac=opts.get('eth_mac')
        self.eth_ip=opts.get('eth_ip')
        self.user=opts.get('ipmi_user')
        if not self.user: self.user=opts.get('user','ADMIN')
        self.passwd=opts.get('ipmi_pass')
        if not self.passwd:  self.passwd=opts.get('passwd','ADMIN') # current password
        self.upasswd=opts.get('ipmi_upass')
        if not self.upasswd: self.upasswd=opts.get('upasswd')
        self.redfish_hi=opts.get('redfish_hi')
        self.err={}
        self.warning={}
        self.canceling={}
        self.cancel_func=opts.get('cancel_func',None)
        self.mac2ip=opts.get('mac2ip',None)
        self.log=opts.get('log',None)
        self.org_user='{}'.format(self.user)
        self.default_passwd=opts.get('default_passwd')
        self.org_passwd='{}'.format(self.passwd)
        self.test_user=opts.get('test_user')
        if not self.test_user: self.test_user=['ADMIN','Admin','admin','root','Administrator']
        self.test_passwd=opts.get('test_pass')
        if not self.test_passwd: self.test_passwd=opts.get('test_passwd')
        if not self.test_passwd: self.test_passwd=['ADMIN','Admin','admin','root','Administrator']
        for ii in ['ADMIN','Admin','admin','root','Administrator']:
            if ii not in self.test_passwd: self.test_passwd.append(ii)
        if self.user in self.test_user: self.test_user.remove(self.user)
        if self.passwd in self.test_passwd: self.test_passwd.remove(self.passwd)
        self.mode=opts.get('mode',[Ipmitool()])
        self.log_level=opts.get('log_level',5)
        self.timeout=opts.get('timeout',1800)
        self.checked_ip=False
        self.checked_port=False
        self.org_ip='{}'.format(self.ip)
        if opts.get('redfish') == 'auto':
            ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
            if ok:
                rf=Redfish(host=ip,user=user,passwd=passwd)
                self.redfish=rf.IsEnabled()
        if self.__dict__.get('redfish') is None:
            self.redfish=True if True in [self.redfish_hi,opts.get('redfish')] else False
        self.power_monitor_stop=False

    def sensor_data(self,cmd_str,name):
        krc=self.run_cmd(cmd_str)
        if km.krc(krc[0],chk=True):
            sensor_stat='unknown'
            for ii in krc[1][1].split('\n'):
                ii_a=ii.split('|')
                find=''
                if name == 'smc' and len(ii_a) > 2:
                    find=ii_a[1].strip().upper()
                    tmp=ii_a[2].strip()
                elif len(ii_a) > 4:
                    find=ii_a[0].strip().upper()
                    tmp=ii_a[4].strip()
                if '_' not in find and ('CPU' in find or 'SYSTEM ' in find) and 'TEMP' in find:
                    if sensor_stat =='unknown' and tmp == 'No Reading':
                        self.warn(_type='sensor',msg="Can not read sensor data")
                    elif tmp in ['N/A','Disabled','0C/32F']:
                        sensor_stat='down'
                    elif 'degrees C' in tmp or ('C/' in tmp and 'F' in tmp): # Up state
                        return 'up'
            return sensor_stat
        return 'error'

    def get_power_status(self):
        # _: Down, -: Up, .: Unknown sensor data, !: ipmi sensor command error
        out=['unknown','unknown','unknown'] # [Sensor(ipmitool/SMCIPMITool), Redfish, ipmitool/SMCIPMITool]
        if self.redfish:
            rf=Redfish(host=self.ip,user=self.user,passwd=self.passwd)
            rt=rf.Power(cmd='status')
            if rt in ['on','off']:
                out[1]=rt
        for mm in self.mode:
            rt=self.run_cmd(mm.cmd_str('ipmi power status'))
            if km.krc(rt,chk=True):
                aa=rt[1][1].split()[-1]
                if aa in ['on','off']:
                    out[2]=aa
                    break
        for mm in self.mode:
            rt=self.sensor_data(mm.cmd_str('ipmi sensor'),mm.__name__)
            out[0]='on' if rt == 'up' else 'off' if rt == 'down' else rt
            break 
        return out

    def power_status_monitor(self,data,monitor_status,get_current_power_status,keep_off=0,keep_on=0,sensor_on=600,sensor_off=0,status_log=True,monitor_interval=5,timeout=1200):
        if not isinstance(data,dict):
            data={'power_monitor_status':{},'repeat':{'num':0,'time':[],'status':[]},'stop':False,'count':0}
        if 'timeout' not in data:
            data['timeout']=timeout if isinstance(timeout,int) else 1200
        def reset_monitor(data,cid,get_current_power):
            data['repeat']['num']+=1
            data['repeat']['time'].append(km.now())
            data['repeat']['status'].append('{}->{}'.format(monitor_status[cid],get_current_power))
            # Reset data to re-monitor
            for i in monitor_status:
                data['power_monitor_status'][i]={}

        def keep_on_off_monitor(mid,data,cid,keep_time):
            if isinstance(data['power_monitor_status'][monitor_status[cid]].get('time'),int):
                if keep_time > 0 and km.now() - data['power_monitor_status'][monitor_status[cid]]['time'] > keep_time:
                    data['power_monitor_status'][monitor_status[cid]]['time_keep']=km.now()
                    cid+=1
                    if cid >=  mid:
                        data['done']={km.now():'Monitor Done'}
                    return cid
            else:
                data['power_monitor_status'][monitor_status[cid]]['time']=km.now()
                if keep_time == 0:
                    data['power_monitor_status'][monitor_status[cid]]['time_keep']=data['power_monitor_status'][monitor_status[cid]]['time']
                    cid+=1
                    if cid >=  mid:
                        data['done']={km.now():'Monitor Done'}
                    return cid
            return -1

        cid=0
        mid=len(monitor_status)
        state_sym='.'
        start_time=None
        if data.get('start') is True:
            start_time=km.now()
        get_current_power=get_current_power_status()
        data['current']={'state':(km.now(),get_current_power),'check':(cid,monitor_status[cid])}
        if 'init' not in data:
            data['init']={'time':km.now(),'status':get_current_power}
            if monitor_status[0] in get_current_power:
                data['power_monitor_status'][monitor_status[0]]={'time':data['init'].get('time')}
                cid+=1
        if isinstance(data.get('timeout'),int) and data.get('timeout') != timeout:
            timeout=data.get('timeout')
        while cid < len(monitor_status):
            if data.get('start') is False:
                time.sleep(1)
                continue
            else:
                if start_time is None:
                    start_time=km.now()
            while True:
                #Update parameters
                if isinstance(data.get('timeout'),int) and data.get('timeout') != timeout:
                    timeout=data.get('timeout')
                remain_time=timeout - (km.now() - start_time)
                data['remain_time']=remain_time
                if remain_time <= 0:
                    data['done']={km.now():'Timeout'}
                    return
                if isinstance(data.get('sensor_off_monitor'),int) and data.get('sensor_off_monitor') != sensor_off:
                    sensor_off=data.get('sensor_off_monitor')
                if isinstance(data.get('sensor_on_monitor'),int) and data.get('sensor_on_monitor') != sensor_on:
                    sensor_on=data.get('sensor_on_monitor')

                if data.get('stop'):
                    data['done']={km.now():'Got STOP'}
                    return

                # Get current power status
                get_current_power=get_current_power_status()
                # Update the current status at data
                data['current']={'state':(km.now(),get_current_power),'check':(cid,monitor_status[cid])}

                # Initialize the 
                if monitor_status[cid] not in data['power_monitor_status']:
                    data['power_monitor_status'][monitor_status[cid]]={}

                # off case
                if monitor_status[cid] == 'off' and (monitor_status[cid] in get_current_power or (data['init']['status'][0] == 'on' and get_current_power[0] in ['unknown','off'])):
                    data['count']+=1
                    if get_current_power[0] == 'off' or sensor_off == 0:
                        state_sym='_'
                        cid_tmp=keep_on_off_monitor(mid,data,cid,keep_off)
                        if cid_tmp > 0:
                            #Go to next cid, because omit goal
                            cid=cid_tmp
                            break
                    elif sensor_off > 0: # check sensor data until sensor_monitor time
                        # Suddenly changed sensor data (reset/cycle) then repeat check
                        if 'off' in data['power_monitor_status'] and data['power_monitor_status']['off'].get('time'):
                            if monitor_status[cid] not in ['on'] and get_current_power[0] in ['on']:
                                state_sym='-'
                                reset_monitor(data,cid,get_current_power)
                                cid=0
                                break
                        # Overtime for sensor monitoring but other(redfish/ipmitool or smcipmitool) are ON
                        elif km.now() - data['power_monitor_status'].get(monitor_status[cid],{}).get('time',km.now()) > sensor_off:
                            data['power_monitor_status'][monitor_status[cid]]['sensor_data']=get_current_power[0]
                            cid_tmp=keep_on_off_monitor(mid,data,cid,keep_off)
                            if cid_tmp > 0:
                                cid=cid_tmp
                                break
                # on case
                elif monitor_status[cid] == 'on' and monitor_status[cid] in get_current_power:
                    # if sensor data is ON  or sensor_on == 0(sensor on condition monitor time) then just update
                    data['count']+=1
                    if get_current_power[0] == 'on' or sensor_on == 0:
                        state_sym='-'
                        cid_tmp=keep_on_off_monitor(mid,data,cid,keep_on)
                        if cid_tmp > 0:
                            cid=cid_tmp
                            break
                    elif sensor_on > 0: # check sensor data until sensor_monitor time
                        # Suddenly changed sensor data (reset/cycle) then repeat check
                        if 'on' in data['power_monitor_status'] and data['power_monitor_status']['on'].get('time'):
                            if monitor_status[cid] not in ['off'] and get_current_power[0] in ['unknown','off']:
                                state_sym='_'
                                reset_monitor(data,cid,get_current_power)
                                cid=0
                                break
                        # Overtime for sensor monitoring but other(redfish/ipmitool or smcipmitool) are ON
                        elif km.now() - data['power_monitor_status'].get(monitor_status[cid],{}).get('time',km.now()) > sensor_on:
                            data['power_monitor_status'][monitor_status[cid]]['sensor_data']=get_current_power[0]
                            cid_tmp=keep_on_off_monitor(mid,data,cid,keep_on)
                            if cid_tmp > 0:
                                cid=cid_tmp
                                break
                # for reset /cycle command monitoring : it changed only sensor data, redfish and ipmitool power status still on(not changed)
                else: # suddenly changed different status
                    if data['power_monitor_status'].get(monitor_status[cid],{}).get('time'):
                        if get_current_power[0] == 'unknown': # suddenly changed status during on
                           if monitor_status[cid] == 'on':
                               if status_log:
                                   sys.stdout.write('+')
                                   sys.stdout.flush()
                               reset_monitor(data,cid,get_current_power)
                               cid=0
                               data['count']+=1
                               time.sleep(monitor_interval)
                               break
                        elif monitor_status[cid] not in get_current_power or \
                           (monitor_status[cid] == 'on' and sensor_on > 0 and data['power_monitor_status'].get('on',{}).get('time',0) > 0 and get_current_power[0] not in ['on']) or \
                           (monitor_status[cid] == 'off' and sensor_off > 0 and data['power_monitor_status'].get('off',{}).get('time',0) > 0 and get_current_power[0] not in ['off','unknown']):
                            if status_log:
                                sys.stdout.write('+')
                                sys.stdout.flush()
                            reset_monitor(data,cid,get_current_power)
                            cid=0
                            data['count']+=1
                            time.sleep(monitor_interval)
                            break
                data['count']+=1
                if status_log:
                    sys.stdout.write(state_sym)
                    sys.stdout.flush()
                time.sleep(monitor_interval)

    def power_monitor(self,timeout=1200,monitor_status=['off','on'],keep_off=0,keep_on=0,sensor_on_monitor=600,sensor_off_monitor=0,monitor_interval=5,start=True):
        #timeout: monitoring timeout
        #monitor_status: monitoring status off -> on : ['off','on'], on : ['on'], off:['off']
        #keep_off: off state keeping time : 0: detected then accept
        #keep_on: on state keeping time : 0: detected then accept, 30: detected and keep same condition during 30 seconds then accept
        #sensor_on_monitor: First Temperature sensor data(cpu start) monitor time, if passed this time then use ipmitool's power status data(on)
        #sensor_off_monitor: First Temperature sensor data(not good) monitor time, if passed this time then use ipmitool's power status(off)
        timeout=timeout if isinstance(timeout,int) else 1200
        rt={'power_monitor_status':{},'repeat':{'num':0,'time':[],'status':[]},'stop':False,'count':0,'start':start,'timeout':timeout}
        if rt.get('worker') and rt['worker'].isAlive():
            print('Already running')
            return rt
        rt['worker']=threading.Thread(target=self.power_status_monitor,args=(rt,monitor_status,self.get_power_status,keep_off,keep_on,sensor_on_monitor,sensor_off_monitor,False,monitor_interval,timeout))
        rt['worker'].start()
        return rt

    def check(self,mac2ip=None,cancel_func=None):
        if cancel_func is None: cancel_func=self.cancel_func
        chk=False
        ip='{}'.format(self.ip)
        for i in range(0,2):
            if self.checked_ip is False:
                if mac2ip and self.mac:
                    ip=mac2ip(self.mac)
                    chk=True
                    self.checked_port=False
            if km.ping(ip,count=0,timeout=self.timeout,log=self.log):
                if self.checked_port is False:
                    #if km.is_port_ip(ip,self.port):
                    if km.IP(ip).IsOpenPort(self.port):
                        self.checked_port=True
                    else:
                        self.error(_type='ip',msg="{} is not IPMI IP".format(ip))
                        km.logging(ip,log=self.log,log_level=1,dsp='e')
                        return False,self.ip,self.user,self.passwd
                self.checked_ip=True
                ok,user,passwd=self.find_user_pass(ip)
                if ok:
                    if chk:
                        mac=self.get_mac(ip,user=user,passwd=passwd)
                        if mac != self.mac:
                            self.error(_type='net',msg='Can not find correct IPMI IP')
                            return False,self.ip,self.user,self.passwd
                    self.ip=ip
                    self.user=user
                    self.passwd=passwd
                    return True,ip,user,passwd
            self.checked_ip=False
        self.checked_ip=True
        self.error(_type='net',msg='Destination Host({}) Unreachable/Network problem'.format(ip))
        km.logging(ip,log=self.log,log_level=1,dsp='e')
        return False,self.ip,self.user,self.passwd

    def get_mode(self,name):
        for mm in self.mode:
            if mm.__name__ == name:
                return mm

    def find_uefi_legacy(self,bioscfg=None): # Get UEFI or Regacy mode
        def aa(a):
            if isinstance(a,list):
                if len(a)==1: return a[0]
                return ''
            return a

        def xml_find(data):
            onboard_video_rom=[]
            selected_option=[]
            default_option=[]
            first_option=[]
            count=0
            for i in range(0,len(data)):
                if '<Menu name="Boot">' in data[i]:
                    for j in range(i,len(data)):
                        if '<Setting name="Boot Mode Select"' in data[j]:
                            selected_option=re.compile('<Setting name="Boot Mode Select" selectedOption="(\w.*)" type="Option">').findall(data[j])
                            count+=1
                        elif not default_option and selected_option and '<DefaultOption>' in data[j]:
                            default_option=re.compile('<DefaultOption>(\w.*)</DefaultOption>').findall(data[j])
                            count+=1
                        elif '<Setting name="Boot Option #1" order="1"' in data[j]:
                            first_option=re.compile('<Setting name="Boot Option #1" order="1" selectedOption="(\w.*)" type="Option">').findall(data[j])
                            if first_option:
                                if 'EFI Network:' in first_option[0]:
                                    first_option='IPXE'
                                elif 'Network:' in first_option[0]:
                                    first_option='PXE'
                            count+=1
#                        elif selected_option and '</Setting>' in data[j]:
#                            break
                elif '<Setting name="Onboard Video Option ROM" selectedOption' in data[i]:
                    onboard_video_rom=re.compile(r'<Setting name=\"Onboard Video Option ROM\" selectedOption=\"(\w.*)\" type=\"Option\">').findall(data[i])
                    count+=1
                if count >= 4:
                    return aa(selected_option),aa(default_option),aa(first_option),aa(onboard_video_rom)
        def flat_find(data):
            for i in range(0,len(data)):
                if '[Boot]' in data[i]:
                    for j in range(i,len(data)):
                        if data[j].strip().startswith('Boot Mode Select'):
                            sop=data[j].strip().split()[2].split('=')[1]
                            if sop == '02':
                                return 'DUAL','','',''
                            elif sop == '01':
                                return 'UEFI','','',''
                            elif sop == '01':
                                return 'LEGACY','','',''

        def find_boot_mode(data):
            data_a=data.split('\n')
            for i in range(0,len(data_a)):
                if '<?xml version' in data_a[i]:
                    return xml_find(data_a[i:])
                elif '[Advanced' in data_a[i]:
                    return flat_find(data_a[i:])

        # Boot mode can automatically convert iPXE or PXE function
        # if power handle command in here then use bmc.power(xxxx,lanmode=self.bmc_lanmode) code
        if isinstance(bioscfg,str):
            if os.path.isfile(bioscfg):
                with open(bioscfg,'rb') as f:
                    bioscfg=f.read()
        if isinstance(bioscfg,str) and bioscfg:
            found=find_boot_mode(km._u_bytes2str(bioscfg))
            if found:
                return True,found
        return False,('','','','')

    def find_user_pass(self,ip=None,default_range=4,check_cmd='ipmi power status',cancel_func=None):
        if cancel_func is None: cancel_func=self.cancel_func
        if ip is None: ip=self.ip
        test_user=km.move2first(self.user,self.test_user[:])
        tt=1
        if len(self.test_passwd) > default_range: tt=2
        tested_user_pass=[]
        for mm in self.mode:
            cmd_str=mm.cmd_str(check_cmd)
            for t in range(0,tt):
                if t == 0:
                    test_pass_sample=self.test_passwd[:default_range]
                else:
                    test_pass_sample=self.test_passwd[default_range:]
                # Two times check for uniq,current,temporary password
                if self.upasswd: test_pass_sample=km.move2first(self.upasswd,test_pass_sample[:])
                if self.org_passwd: test_pass_sample=km.move2first(self.org_passwd,test_pass_sample[:])
                test_pass_sample=km.move2first(self.passwd,test_pass_sample)
                if self.default_passwd not in test_pass_sample: test_pass_sample.append(self.default_passwd)
                for uu in test_user:
                    for pp in test_pass_sample:
                        if uu is None or pp is None: continue
                        if km.ping(ip,count=1,keep_good=0,timeout=300): # Timeout :5min, count:2, just pass when pinging
                            tested_user_pass.append((uu,pp))
                            km.logging("""Try BMC User({}) and password({})""".format(uu,pp),log=self.log,log_level=7)
                            full_str=cmd_str[1]['base'].format(ip=ip,user=uu,passwd=pp)+' '+cmd_str[1]['cmd']
                            rc=km.rshell(full_str)
                            if rc[0] in cmd_str[3]['ok']:
                                if self.user != uu:
                                    km.logging("""[BMC]Found New User({})""".format(uu),log=self.log,log_level=3)
                                    self.user=uu
                                if self.passwd != pp:
                                    km.logging("""[BMC]Found New Password({})""".format(pp),log=self.log,log_level=3)
                                    self.passwd=pp
                                return True,uu,pp
                            if self.log_level < 7:
                                km.logging("""p""",log=self.log,direct=True,log_level=3)
                        else:
                            km.logging("""x""",log=self.log,direct=True,log_level=3)
        km.logging("""Can not find working BMC User or password from POOL""",log=self.log,log_level=1,dsp='e')
        self.error(_type='user_pass',msg="Can not find working BMC User or password from POOL\n{}".format(tested_user_pass))
        return False,None,None

    def recover_user_pass(self):
        mm=self.get_mode('smc')
        if not mm:
            km.logging("""SMCIPMITool module not found""",log=self.log,log_level=1)
            return False,'SMCIPMITool module not found'
        if self.user == self.org_user:
            if self.passwd == self.org_passwd:
                km.logging("""Same user and passwrd. Do not need recover""",log=self.log,log_level=6)
                return True,self.user,self.passwd
            else:
                #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
                #rc=self.run_cmd(mm.cmd_str("""user setpwd 2 '{}'""".format(self.org_passwd)))
                recover_cmd=mm.cmd_str("""user setpwd 2 '{}'""".format(self.org_passwd))
        else:
            #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
            #rc=self.run_cmd(mm.cmd_str("""user add 2 {} '{}' 4""".format(self.org_user,self.org_passwd)))
            recover_cmd=mm.cmd_str("""user add 2 {} '{}' 4""".format(self.org_user,self.org_passwd))
        #print('\n*kBMC: {}'.format(recover_cmd))
        km.logging("""Recover command: {}""".format(recover_cmd),log_level=7)
        rc=self.run_cmd(recover_cmd)
        
        if km.krc(rc[0],chk='error'):
            km.logging("""BMC Password: Recover fail""",log=self.log,log_level=1)
            self.warn(_type='ipmi_user',msg="BMC Password: Recover fail")
            return 'error',self.user,self.passwd
        if km.krc(rc[0],chk=True):
            km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password({})""".format(self.user,self.passwd,self.org_user,self.org_passwd),log=self.log,log_level=6)
            self.user='{}'.format(self.org_user)
            self.passwd='{}'.format(self.org_passwd)
            return True,self.user,self.passwd
        else:
            km.logging("""Not support {}. Looks need more length. So Try again with {}""".format(self.org_passwd,self.default_passwd),log=self.log,log_level=6)
            if self.user == self.org_user:
                #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
                recover_cmd=mm.cmd_str("""user setpwd 2 '{}'""".format(self.default_passwd))
            else:
                #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
                recover_cmd=mm.cmd_str("""user add 2 {} '{}' 4""".format(self.org_user,self.default_passwd))
        #    print('\n*kBMC2: {}'.format(recover_cmd))
            km.logging("""Recover command: {}""".format(recover_cmd),log_level=7)
            rrc=self.run_cmd(recover_cmd)
            if km.krc(rrc[0],chk=True):
                km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password({})""".format(self.user,self.passwd,self.org_user,self.default_passwd),log=self.log,log_level=6)
                self.user='{}'.format(self.org_user)
                self.passwd='{}'.format(self.default_passwd)
                return True,self.user,self.passwd
            else:
                self.warn(_type='ipmi_user',msg="Recover ERROR!! Please checkup user-lock-mode on the BMC Configure.")
                km.logging("""BMC Password: Recover ERROR!! Please checkup user-lock-mode on the BMC Configure.""",log=self.log,log_level=1)
                return False,self.user,self.passwd
                
    def run_cmd(self,cmd,append=None,path=None,retry=0,timeout=None,return_code={'ok':[0,True],'fail':[]},show_str=False,dbg=False,mode='app',cancel_func=None,peeling=False,progress=False,ip=None,user=None,passwd=None,cd=False,check_password_rc=[]):
        if cancel_func is None: cancel_func=self.cancel_func
        error=self.error()
        if error[0]:
            return 'error','''{}'''.format(error[1])
        while peeling:
            if type(cmd)is tuple and len(cmd) == 1:
                cmd=cmd[0]
            else:
                break
        if isinstance(cmd, (tuple,list)) and len(cmd) >= 2 and type(cmd[0]) is bool:
            #ok,cmd,path,return_code,timeout=tuple(km.get_value(cmd,[0,1,2,3,4]))
            ok,cmd,path,return_code,timeout_i=km.get_value(cmd,[0,1,2,3,4],err=True)
            if timeout_i: timeout=timeout_i
            if not ok:
                self.warn(_type='cmd',msg="command({}) format error".format(cmd))
                return False,(-1,'command format error(2)','command format error',0,0,cmd,path),'command({}) format error'.format(cmd)
        elif not isinstance(cmd,str):
            self.warn(_type='cmd',msg="command({}) format error".format(cmd))
            return False,(-1,'command format error(3)','command format error',0,0,cmd,path),'command({}) format error'.format(cmd)
        if not isinstance(return_code,dict):
            return_code={}
        rc_ok=return_code.get('ok',[0,True])
        rc_ignore=return_code.get('ignore',[])
        rc_fail=return_code.get('fail',[])
        rc_error=return_code.get('error',[127])
        rc_err_connection=return_code.get('err_connection',[])
        rc_err_key=return_code.get('err_key',[])
        rc_err_bmc_user=return_code.get('err_bmc_user',[])
        if ip is None: ip=self.ip
        if user is None: user=self.user
        if passwd is None: passwd=self.passwd
        if type(append) is not str:
            append=''
        rc=None
        for i in range(0,2+retry):
            if i > 1:
                km.logging('Re-try command [{}/{}]'.format(i,retry+1),log=self.log,log_level=1,dsp='d')
            if isinstance(cmd,dict):
                base_cmd=km.sprintf(cmd['base'],**{'ip':ip,'user':user,'passwd':passwd})
                cmd_str='{} {} {}'.format(base_cmd[1],cmd.get('cmd'),append)
            else:
                base_cmd=km.sprintf(cmd,**{'ip':ip,'user':user,'passwd':passwd})
                cmd_str='{} {}'.format(base_cmd[1],append)
            if not base_cmd[0]:
                return False,(-1,'Wrong commnd format','Wrong command format',0,0,cmd_str,path),'Command format is wrong'
            if dbg or show_str:
                km.logging('** Do CMD   : {}'.format(cmd_str),log=self.log,log_level=1,dsp='d')
                km.logging(' - Timeout  : %-15s  - PATH     : %s'%(timeout,path),log=self.log,log_level=1,dsp='d')
                km.logging(' - CHK_CODE : {}\n'.format(return_code),log=self.log,log_level=1,dsp='d')
            if self.cancel(cancel_func=cancel_func):
                km.logging(' !! Canceling Job',log=self.log,log_level=1,dsp='d')
                self.warn(_type='cancel',msg="Canceling")
                return False,(-1,'canceling','canceling',0,0,cmd_str,path),'canceling'
            try:
                #if mode == 'redfish': #Temporary remove
                #    return Redfish().run_cmd(cmd_str,**self.__dict__)
                #else:
                #    rc=km.rshell(cmd_str,path=path,timeout=timeout,progress=progress,log=self.log,progress_pre_new_line=True,progress_post_new_line=True,cd=cd)
                #    if km.Get(rc,0) == -2 : return False,rc,'Timeout({})'.format(timeout)
                rc=km.rshell(cmd_str,path=path,timeout=timeout,progress=progress,log=self.log,progress_pre_new_line=True,progress_post_new_line=True,cd=cd)
                if km.Get(rc,0) == -2 : return False,rc,'Timeout({})'.format(timeout)
                if (not check_password_rc and rc[0] != 0) or (rc[0] !=0 and rc[0] in check_password_rc):
                    km.logging('[WARN] Check ip,user,password again',log=self.log,log_level=4,dsp='f')
                    ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=cancel_func)
                    continue
            except:
                e = sys.exc_info()[0]
                km.logging('[ERR] Your command got error\n{}'.format(e),log=self.log,log_level=4,dsp='f')
                self.warn(_type='cmd',msg="Your command got error\n{}".format(e))
                return 'error',(-1,'{}'.format(e),'unknown',0,0,cmd_str,path),'Your command got error'
            if show_str:
                km.logging(' - RT_CODE : {}'.format(km.Get(rc,0)),log=self.log,log_level=1,dsp='d')
                if rc[0] !=0 :
                    km.logging(' - Output  : {}'.format(km.Get(rc,1)),log=self.log,log_level=1,dsp='d')
            if dbg:
                km.logging(' -DBGOutput: {}'.format(rc),log=self.log,log_level=1,dsp='d')
            if rc[0] == 1:
                return False,rc,'Command file not found'
            elif (not rc_ok and rc[0] == 0) or km.check_value(rc_ok,km.Get(rc,0)):
                return True,rc,'ok'
            elif km.check_value(rc_err_connection,km.Get(rc,0)): # retry condition1
                msg='err_connection'
                km.logging('Connection error condition:{}, return:{}'.format(rc_err_connection,km.Get(rc,0)),log=self.log,log_level=7)
                km.logging('Connection Error:',log=self.log,log_level=1,dsp='d',direct=True)
                #Check connection
                if km.is_lost(self.ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=self.cancel(cancel_func=cancel_func))[0]:
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    self.error(_type='net',msg="{} lost network(over 30min)".format(self.ip))
                    return False,rc,'Lost Network, Please check your server network(1)'
            elif km.check_value(rc_err_bmc_user,rc[0]): # retry condition1
                #Check connection
                if km.is_lost(self.ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=self.cancel(cancel_func=cancel_func))[0]:
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    self.error(_type='net',msg="{} lost network".format(self.ip))
                    return False,rc,'Lost Network, Please check your server network(2)'
                # Find Password
                ok,ipmi_user,ipmi_pass=self.find_user_pass()
                if not ok:
                    self.error(_type='ipmi_user',msg="Can not find working IPMI USER and PASSWORD")
                    return False,'Can not find working IPMI USER and PASSWORD','user error'
                if dbg:
                    km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                time.sleep(1)
            else:
                if 'ipmitool' in cmd_str and i < 1:
                    #Check connection
                    if km.is_lost(self.ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=self.cancel(cancel_func=cancel_func))[0]:
                        km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                        self.error(_type='net',msg="{} lost network".format(self.ip))
                        return False,rc,'Lost Network, Please check your server network(3)'
                    # Find Password
                    ok,ipmi_user,ipmi_pass=self.find_user_pass()
                    if not ok:
                        self.error(_type='ipmi_user',msg="Can not find working IPMI USER and PASSWORD")
                        return False,'Can not find working IPMI USER and PASSWORD','user error'
                    if dbg:
                        km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                    time.sleep(1)
                else:
                    try:
                        if km.check_value(rc_ignore,rc[0]):
                            return 'ignore',rc,'return code({}) is in ignore condition({})'.format(rc[0],rc_ignore)
                        elif km.check_value(rc_fail,rc[0]):
                            return 'fail',rc,'return code({}) is in fail condition({})'.format(rc[0],rc_fail)
                        elif km.check_value([127],rc[0]):
                            return False,rc,'no command'
                        elif km.check_value(rc_error,rc[0]):
                            return 'error',rc,'return code({}) is in error condition({})'.format(rc[0],rc_error)
                        elif km.check_value(rc_err_key,rc[0]):
                            return 'error',rc,'return code({}) is in key error condition({})'.format(rc[0],rc_err_key)
                        elif isinstance(rc,tuple) and rc[0] > 0:
                            return 'fail',rc,'Not defined return-condition, So it will be fail'
                    except:
                        return 'unknown',rc,'Unknown result'
        if rc is None:
            return False,(-1,'No more test','',0,0,cmd_str,path),'Out of testing'
        else:
            return False,rc,'Out of testing'

    def reset(self,retry=0,post_keep_up=20,pre_keep_up=0):
        rc=False,'Something issue'
        for i in range(0,1+retry):
            for mm in self.mode:
                if km.is_comeback(self.ip,keep=pre_keep_up,log=self.log,stop_func=self.error(_type='break')[0]):
                    km.logging('R',log=self.log,log_level=1,direct=True)
                    rc=self.run_cmd(mm.cmd_str('ipmi reset'))
                    if km.krc(rc[0],chk='error'):
                        return rc
                    if km.krc(rc[0],chk=True):
                        if km.is_comeback(self.ip,keep=post_keep_up,log=self.log,stop_func=self.error(_type='break')[0]):
                            return True,'Pinging to BMC after reset BMC'
                        else:
                            return False,'Can not Pinging to BMC after reset BMC'
                else:
                    return False,'Can not Pinging to BMC. I am not reset the BMC. please check the network first!'
                time.sleep(5)
        return rc
            

    def get_mac(self,ip=None,user=None,passwd=None):
        if self.mac:
            return True,self.mac
        if ip is None: ip=self.ip
        ok,user,passwd=self.find_user_pass()
        #if user is None: user=self.user
        #if passwd is None: passwd=self.passwd
        for mm in self.mode:
            name=mm.__name__
            cmd_str=mm.cmd_str('ipmi lan mac')
            full_str=cmd_str[1]['base'].format(ip=ip,user=user,passwd=passwd)+' '+cmd_str[1]['cmd']
            rc=km.rshell(full_str,log=self.log,progress_pre_new_line=True,progress_post_new_line=True)
            if km.krc(rc[0],chk=True):
              if name == 'smc':
                  self.mac=rc[1].lower()
                  return True,self.mac
              elif name == 'ipmitool':
                  for ii in rc[1].split('\n'):
                      ii_a=ii.split()
                      if km.check_value(ii_a,'MAC',0) and km.check_value(ii_a,'Address',1) and km.check_value(ii_a,':',2):
                          self.mac=ii_a[-1].lower()
                          return True,self.mac
        return False,None

    def dhcp(self):
        for mm in self.mode:
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan dhcp'))
            if km.krc(rc[0],chk='error'):
                return rc
            if km.krc(rc[0],chk=True):
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'IP',0) and km.check_value(ii_a,'Address',1) and km.check_value(ii_a,'Source',2):
                            return True,ii_a[-2]
        return False,None

    def gateway(self):
        for mm in self.mode:
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan gateway'))
            if km.krc(rc[0],chk='error'):
                return rc
            if km.krc(rc[0],chk=True):
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'Default',0) and km.check_value(ii_a,'Gateway',1) and km.check_value(ii_a,'IP',2):
                            return True,ii_a[-1]
        return False,None

    def netmask(self):
        for mm in self.mode:
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan netmask'))
            if km.krc(rc[0],chk='error'):
                return rc
            if km.krc(rc[0],chk=True):
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'Subnet',0) and km.check_value(ii_a,'Mask',1):
                            return True,ii_a[-1]
        return km.krc(rc[0]),None

    def bootorder(self,mode=None,ipxe=False,persistent=False,force=False,boot_mode={'smc':['pxe','bios','hdd','cd','usb'],'ipmitool':['pxe','ipxe','bios','hdd']},bios_cfg=None):
        rc=False,"Unknown boot mode({})".format(mode)
        ipmi_ip=self.ip
        for mm in self.mode:
            name=mm.__name__
            chk_boot_mode=boot_mode.get(name,{})
            if name == 'smc' and mode in chk_boot_mode:
                if mode == 'pxe':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 1'))
                elif mode == 'hdd':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 2'))
                elif mode == 'cd':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 3'))
                elif mode == 'bios':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 4'))
                elif mode == 'usb':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 6'))
                if km.krc(rc[0],chk=True):
                    return True,rc[1][1]
            elif name == 'ipmitool':
                if mode in [None,'order','status']:
                    if mode == 'order':
                        if self.redfish:
                            ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
                            rf=Redfish(host=ip,user=user,passwd=passwd)
                            return True,rf.Boot(boot='order')
                        else:
                            rc=self.run_cmd(mm.cmd_str('chassis bootparam get 5'))
# Boot Flags :
#   - Boot Flag Invalid
#   - Options apply to only next boot
#   - BIOS EFI boot 
#   - Boot Device Selector : Force PXE
#   - Console Redirection control : System Default
#   - BIOS verbosity : Console redirection occurs per BIOS configuration setting (default)
#   - BIOS Mux Control Override : BIOS uses recommended setting of the mux at the end of POST
                            if rc[0]:
                                rc=True,km.findstr(rc[1],'- Boot Device Selector : (\w.*)')[0]
                    elif mode == 'status':
                        status=False
                        efi=False
                        persistent=False
                        if self.redfish:
                            ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
                            rf=Redfish(host=ip,user=user,passwd=passwd)
                            rf_boot_info=rf.Boot()
                            efi=True if rf_boot_info.get('bios',{}).get('mode','') == 'UEFI' else False
                            persistent=True if rf_boot_info.get('order',{}).get('enable','') == 'Continuous' else False
                            status=rf_boot_info.get('order',{}).get('1','').lower()
                        else:
                            bios_cfg=self.find_uefi_legacy(bioscfg=bios_cfg)
                            if km.krc(rc,chk=True): # ipmitool bootorder
                                status='No override'
                                for ii in km.get_value(rc[1],1).split('\n'):
                                    if 'Options apply to all future boots' in ii:
                                        persistent=True
                                    elif 'BIOS EFI boot' in ii:
                                        efi=True
                                    elif 'Boot Device Selector :' in ii:
                                        status=ii.split(':')[1]
                                        break
                                if self.log:
                                    self.log("Boot mode Status:{}, EFI:{}, Persistent:{}".format(status,efi,persistent),log_level=7)
                            if km.krc(bios_cfg,chk=True): #BIOS CFG file
                                bios_uefi=km.get_value(bios_cfg,1)
                                if 'EFI' in bios_uefi[0:-1] or 'UEFI' in bios_uefi[0:-1] or 'IPXE' in bios_uefi[0:-1]:
                                    efi=True
                        return [status,efi,persistent]
                elif mode not in chk_boot_mode:
                    self.warn(_type='boot',msg="Unknown boot mode({}) at {}".format(mode,name))
                    return False,'Unknown boot mode({}) at {}'.format(mode,name)
                else:
                    if persistent:
                        if self.redfish:
                            ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
                            rf=Redfish(host=ip,user=user,passwd=passwd)
                            rf_boot=rf.Boot(boot=boot_mode,keep='keep')
                            rc=rf_boot,(rf_boot,'Persistently set to {}'.format(boot_mode))
                        else:
                            if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                                # ipmitool -I lanplus -H 172.16.105.74 -U ADMIN -P 'ADMIN' raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00
                                rc=self.run_cmd(mm.cmd_str('raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00'))
                                if self.log: self.log("Persistently Boot mode set to i{0} at {1}".format(boot_mode,ipmi_ip),date=True,log_level=7)
                            else:
                                rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=persistent'.format(mode)))
                                if self.log: self.log("Persistently Boot mode set to {0} at {1}".format(boot_mode,ipmi_ip),date=True,log_level=7)
                    else:
                        if self.redfish:
                            ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
                            rf=Redfish(host=ip,user=user,passwd=passwd)
                            rf_boot=rf.Boot(boot=boot_mode)
                            rc=rf_boot,(rf_boot,'Temporarily set to {}'.format(boot_mode))
                        else:
                            if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                                rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=efiboot'.format(mode)))
                            else:
                                if force and chk_boot_mode == 'pxe':
                                    rc=self.run_cmd(mm.cmd_str('chassis bootparam set bootflag force_pxe'.format(mode)))
                                else:
                                    rc=self.run_cmd(mm.cmd_str('chassis bootdev {0}'.format(mode)))
                if km.krc(rc[0],chk=True):
                    return True,rc[1][1]
            if km.krc(rc[0],chk='error'):
                return rc
        return False,rc[-1]

    def get_eth_mac(self):
        if self.eth_mac:
            return True,self.eth_mac
        rc=False,[]
        for mm in self.mode:
            name=mm.__name__
            if name == 'ipmitool':
                aaa=mm.cmd_str('''raw 0x30 0x21''')
                rc=self.run_cmd(aaa)
                if km.krc(rc[0],chk=True) and rc[1][1]:
                    mac_source=rc[1][1].split('\n')[0].strip()
                    if mac_source:
                        if len(mac_source.split()) == 10:  
                            self.eth_mac=':'.join(mac_source.split()[-6:]).lower()
                        elif len(mac_source.split()) == 16:
                            self.eth_mac=':'.join(mac_source.split()[-12:-6]).lower()
                        return True,self.eth_mac
            elif name == 'smc':
                rc=self.run_cmd(mm.cmd_str('ipmi oem summary | grep "System LAN"'))
                if km.krc(rc[0],chk=True):
                    #rrc=[]
                    #for ii in rc[1].split('\n'):
                    #    rrc.append(ii.split()[-1].lower())
                    #self.eth_mac=rrc
                    self.eth_mac=rc[1].split('\n')[0].strip().lower()
                    return True,self.eth_mac
            if km.krc(rc[0],chk='error'):
               return rc
        return False,None

    def ping(self,ip=None,test_num=3,retry=1,wait=1,keep=0,timeout=30): # BMC is on (pinging)
        if ip is None: ip=self.ip
        return km.ping(ip,count=retry,interval=wait,keep_good=keep,log=self.log,timeout=timeout)

    def summary(self): # BMC is ready(hardware is ready)
        if self.ping() is False:
            print('%10s : %s'%("Ping","Fail"))
            return False
        print('%10s : %s'%("Ping","OK"))
        self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
        print('%10s : %s'%("User",self.user))
        print('%10s : %s'%("Password",self.passwd))
        ok,mac=self.get_mac()
        print('%10s : %s'%("Bmc Mac",'{}'.format(mac)))
        ok,eth_mac=self.get_eth_mac()
        if ok:
            print('%10s : %s'%("Eth Mac",'{}'.format(eth_mac)))
        print('%10s : %s'%("Power",'{}'.format(self.power('status'))))
        print('%10s : %s'%("DHCP",'{}'.format(self.dhcp()[1])))
        print('%10s : %s'%("Gateway",'{}'.format(self.gateway()[1])))
        print('%10s : %s'%("Netmask",'{}'.format(self.netmask()[1])))
        print('%10s : %s'%("LanMode",'{}'.format(self.lanmode()[1])))
        print('%10s : %s'%("BootOrder",'{}'.format(self.bootorder()[1])))

    def node_state(self,state='up',**opts): # Node state
        timeout=km.integer(opts.get('timeout'),default=600)
        keep_up=km.integer(opts.get('keep_up'),default=0)
        keep_down=km.integer(opts.get('keep_down'),default=0)
        power_down=km.integer(opts.get('power_down'),default=0)
        keep_unknown=km.integer(opts.get('keep_unknown'),default=180)
        interval=km.integer(opts.get('interval'),default=0)
        check_down=opts.get('check_down',False)
        if km.compare(keep_up,'>=',timeout,ignore=0):
            timeout=int(keep_up) + 30
        if km.compare(keep_down,'>=',timeout,ignore=0):
            timeout=int(keep_down) + 30
        stop_func=opts.get('stop_func',False)
        cancel_func=opts.get('cancel_func',self.cancel_func)
        km.logging('Node state: timeout:{}, keep_up:{}, keep_down:{} power_down:{}, keep_unknown:{}, check_down:{}'.format(timeout,keep_up,keep_down,power_down,keep_unknown,check_down),log=self.log,log_level=7)
        # _: Down, -: Up, .: Unknown sensor data, !: ipmi sensor command error
        #def sensor_data(cmd_str,name):
        #    krc=self.run_cmd(cmd_str)
        #    if km.krc(krc[0],chk='error'):
        #       return 'error'
        #    if km.krc(krc[0],chk=True):
        #        sensor_stat='unknown'
        #        for ii in krc[1][1].split('\n'):
        #            ii_a=ii.split('|')
        #            find=''
        #            if name == 'smc' and len(ii_a) > 2:
        #                find=ii_a[1].strip().upper()
        #                tmp=ii_a[2].strip()
        #            elif len(ii_a) > 4:
        #                find=ii_a[0].strip().upper()
        #                tmp=ii_a[4].strip()
        #            if '_' not in find and ('CPU' in find or 'SYSTEM ' in find) and 'TEMP' in find:
        #                if sensor_stat =='unknown' and tmp == 'No Reading':
        #                    self.warn(_type='sensor',msg="Can not read sensor data")
        #                    #return 'unknown'
        #                elif tmp in ['N/A','Disabled','0C/32F']:
        #                    sensor_stat='down'
        #                    #return 'down'
        #                else: # Up state
        #                    return 'up'
        #        return sensor_stat
        #    return 'error'

        def power_data():
            pwr_info=self.power(cmd='status')
            if isinstance(pwr_info,str):
                return km.Get(pwr_info.split(),-1)
            return km.Get(pwr_info,-1)

        bmc_modules_num=len(self.mode)
        bmc_modules_chk=0
        system_down=False
        tmp=''
        ping_out_init=None

        for mm in self.mode:
            init_time=0
            up_time=0
            down_time=0
            no_read=0
            no_read_try=0
            power_down_time=0
            unknown_time=0
            bmc_modules_chk+=1
            name=mm.__name__
            cmd_str=mm.cmd_str('ipmi sensor')
            while True:
                if self.cancel(cancel_func=stop_func):
                    km.logging('Got STOP Signal',log=self.log,log_level=1,dsp='e')
                    return True,'Got STOP Signal'            
                if self.cancel(cancel_func=cancel_func):
                    km.logging('Got Cancel Signal',log=self.log,log_level=1,dsp='e')
                    return False,'Got Cancel Signal'            

                if not km.ping(self.ip,timeout=4,log=self.log):
                    km.logging('*',log=self.log,direct=True,log_level=2)
                    time.sleep(2)
                    ping_out,ping_out_init=km.Timeout(timeout,ping_out_init)
                    if ping_out:
                        return False,'Ping Timeout over {} seconds at the Node state'.format(timeout)
                    continue
                ping_out_init=km.now()

                if up_time > 0:
                    out,init_time=km.Timeout(timeout+(keep_up*3),init_time)
                else:
                    out,init_time=km.Timeout(timeout,init_time)
                if out:
                    if bmc_modules_chk >= bmc_modules_num:
                        self.warn(_type='timeout',msg="node_state()")
                        km.logging('Node state Timeout',log=self.log,log_level=1,dsp='e')
                        if sensor_state == 'unknown':
                            self.error(_type='sensor',msg="Unknown Sensor state")
                        return False,'Node state Timeout over {} seconds'.format(timeout)
                    else:
                        # Change to Next checkup module
                        km.logging('{} state Timeout'.format(name),log=self.log,log_level=1,dsp='e')
                        break
                sensor_state=self.sensor_data(cmd_str,name)
                pwr_state=power_data()
                km.logging('Module:{}, Sensor state:{}, power_state:{}'.format(name,sensor_state,pwr_state),log=self.log,log_level=8)
                if state == 'up':
                    if sensor_state == 'up':
                        down_time=0
                        up_ok,up_time=km.Timeout(keep_up,up_time)
                        if up_ok:
                            if check_down:
                                if system_down:
                                    km.logging('Good, Node is UP after down',log=self.log,log_level=7)
                                    return True,'up'
                                else:
                                    km.logging('Bad, Still UP',log=self.log,log_level=7)
                                    return False,'up'
                            else:
                                km.logging('Good, Node is UP',log=self.log,log_level=7)
                                return True,'up'
                    else:
                        up_time=0
                        if pwr_state == 'off':
                            system_down=True
                            dn_pw_ok,power_down_time=km.Timeout(power_down,power_down_time)
                            if dn_pw_ok:
                                km.logging('Bad, Power is off (power_down over {}s)'.format(power_down),log=self.log,log_level=7)
                                return False,'down'
                        else:
                            power_down_time=0
                        up_pw_ok,down_time=km.Timeout(keep_down,down_time)
                        if up_pw_ok:
                            if pwr_state == 'on':
                                km.logging('Bad, Power is on',log=self.log,log_level=7)
                                return False,'init'
                            else:
                                km.logging('Bad, Power is off (keep down over {}s)'.format(keep_down),log=self.log,log_level=7)
                                return False,'down'
                elif state == 'down':
                    if sensor_state == 'up':
                        power_down_time=0
                        down_time=0
                        dn_ok,up_time=km.Timeout(keep_up,up_time)
                        if dn_ok:
                            km.logging('Bad, Node still up',log=self.log,log_level=7)
                            return False,'up'
                    elif pwr_state == 'off':
                        system_down=True
                        if power_down == 0: return True,'down'
                        dn_pw_ok,power_down_time=km.Timeout(power_down,power_down_time)
                        if dn_pw_ok:
                            km.logging('Good, Node is down',log=self.log,log_level=7)
                            return True,'down'
                    else:
                        if keep_down == 0: return True,'down'
                        dn_pw_ok,down_time=km.Timeout(keep_down,down_time)
                        if dn_pw_ok:
                            if pwr_state == 'on' and not system_down:
                                km.logging('Bad, Power is up',log=self.log,log_level=7)
                                return False,'up' # Not real down
                            else:
                                km.logging('Good, Power is down',log=self.log,log_level=7)
                                return True,'down' # Real down

                if sensor_state == 'unknown': # No reading data
                    km.logging('Unknown state : keep check : {} < {}, no_read_try: {}, unknown_time:{} '.format(keep_unknown,km.now()-unknown_time,no_read_try,unknown_time),log=self.log,log_level=7)
                    if keep_unknown > 0 and no_read_try < 2:
                        unknown_ok,unknown_time=km.Timeout(keep_unknown,unknown_time)
                        km.logging('Unknown Timeout: {} < {} : {}'.format(keep_unknown,km.now()-unknown_time,unknown_ok),log=self.log,log_level=7)
                        if unknown_ok:
                             km.logging('[',log=self.log,direct=True,log_level=2)
                             rrst=self.reset()
                             km.logging(']',log=self.log,direct=True,log_level=2)
                             unknown_time=0
                             timeout=timeout+200
                             no_read_try+=1
                             if km.krc(rrst[0],chk=True):
                                 km.logging('O',log=self.log,direct=True,log_level=2)
                             else:
                                 km.logging('X',log=self.log,direct=True,log_level=2)
                    up_time=0
                    down_time=0
                    km.logging('.',log=self.log,direct=True,log_level=2)
                else:
                    km.logging('sensor_state: {}, unknown_time: {}'.format(sensor_state,unknown_time),log=self.log,log_level=7)
                    unknown_time=0
                    if sensor_state == 'up':
                        km.logging('-',log=self.log,direct=True,log_level=2)
                    elif sensor_state == 'down':
                        km.logging('_',log=self.log,direct=True,log_level=2)
                    else: # error
                        up_time=0
                        down_time=0
                        km.logging('!',log=self.log,direct=True,log_level=2)
                time.sleep(interval)
            time.sleep(interval)

    def is_up(self,timeout=1200,keep_up=60,keep_down=240,power_down=30,interval=8,check_down=False,keep_unknown=300,**opts): # Node state
        return self.node_state(state='up',timeout=km.integer(timeout,default=1200),keep_up=km.integer(keep_up,default=60),keep_down=km.integer(keep_down,default=240),power_down=km.integer(power_down,default=60),interval=km.integer(interval,default=8),check_down=check_down,keep_unknown=km.integer(keep_unknown,default=300),**opts) # Node state

    def is_down(self,timeout=1200,keep_up=240,keep_down=30,interval=8,power_down=30,**opts): # Node state
        return self.node_state(state='down',timeout=km.integer(timeout,default=1200),keep_up=km.integer(keep_up,default=240),interval=km.integer(interval,default=8),power_down=km.integer(power_down,default=60),**opts) # Node state

    def get_boot_mode(self):
        return self.bootorder(mode='status')

    #def get_boot_mode(self,ipmi_ip=None,ipmi_user=None,ipmi_pass=None,log_file=None,log=None):
    #    if ipmi_ip is None: ipmi_ip=self.ip
    #    if ipmi_user is None: ipmi_user=self.user
    #    if ipmi_pass is None: ipmi_pass=self.passwd
    #    if log is None: log=self.log
    #    status='No override'
    #    rc=self.run_cmd(mm.cmd_str('chassis bootparam get 5'))
    #    if rc[0] == 0:
    #        efi=False
    #        persistent=False
    #        for ii in rc[1].split('\n'):
    #            if 'Options apply to all future boots' in ii:
    #                persistent=True
    #            elif 'BIOS EFI boot' in ii:
    #                efi=True
    #            elif 'Boot Device Selector :' in ii:
    #                status=ii.split(':')[1]
    #                break
    #        if log:
    #            log("Boot mode Status:{}, EFI:{}, Persistent:{}".format(status,efi,persistent),log_level=7)
    #        return [status,efi,persistent]
    #    else:
    #        return [False,False,False]


    #def set_boot_mode(self,boot_mode,ipmi_ip=None,ipmi_user=None,ipmi_pass=None,ipxe=False,persistent=False,log_file=None,log=None,force=False):
    #    if ipmi_ip is None: ipmi_ip=self.ip
    #    if ipmi_user is None: ipmi_user=self.user
    #    if ipmi_pass is None: ipmi_pass=self.passwd
    #    if log is None: log=self.log
    #    boot_mode_d=['pxe','ipxe','bios','hdd']
    #    if not boot_mode in boot_mode_d:
    #        return
    #    if persistent:
    #        if boot_mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
    #            # ipmitool -I lanplus -H 172.16.105.74 -U ADMIN -P 'ADMIN' raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00
    #            rc=self.run_cmd(mm.cmd_str('raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00'))
    #            logging("Persistently Boot mode set to i{0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)
    #        else:
    #            #ipmi_cmd(cmd='chassis bootdev {0} options=persistent'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
    #            rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=persistent'.format(boot_mode)))
    #            logging("Persistently Boot mode set to {0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)
    #    else:
    #        if boot_mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
    #            #ipmi_cmd(cmd='chassis bootdev {0} options=efiboot'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
    #            rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=efiboot'.format(boot_mode)))
    #        else:
    #            if force and boot_mode == 'pxe':
    #                #ipmi_cmd(cmd='chassis bootparam set bootflag force_pxe'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
    #                rc=self.run_cmd(mm.cmd_str('chassis bootparam set bootflag force_pxe'.format(boot_mode)))
    #            else:
    #                #ipmi_cmd(cmd='chassis bootdev {0}'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
    #                rc=self.run_cmd(mm.cmd_str('chassis bootdev {0}'.format(boot_mode)))
    #        logging("Temporary Boot mode set to {0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)


    def power(self,cmd='status',retry=0,boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False,mode=None,verify=True,post_keep_up=20,pre_keep_up=0,timeout=3600,lanmode=None,fail_down_time=240):
        retry=km.integer(retry,default=0)
        timeout=km.integer(timeout,default=1200)
        pre_keep_up=km.integer(pre_keep_up,default=0)
        post_keep_up=km.integer(post_keep_up,default=20)
        if cmd == 'status':
            return self.do_power('status',verify=verify)[1]
        if boot_mode:
            if boot_mode == 'ipxe':
                ipxe=True
                boot_mode='pxe'
            ipxe=True if ipxe in ['on','On',True,'True'] else False
            km.logging('Set Boot mode to {} with iPXE({})\n'.format(boot_mode,ipxe),log=self.log,log_level=3)
            for ii in range(0,retry+1):
                # Find ipmi information
                ok,ip,user,passwd=self.check(mac2ip=self.mac2ip,cancel_func=self.cancel_func)
                #self.set_boot_mode(boot_mode,self.ip,self.user,self.passwd,persistent=order,ipxe=ipxe,log_file=log_file,log=self.log,force=force)
                rf_fail=True
                if self.redfish:
                    rf=Redfish(host=ip,user=user,passwd=passwd)
                    ipxe=True if rf.Boot(simple_mode=True) in ['UEFI','EFI'] else False
                    rf_boot_mode='pxe' if boot_mode in ['ipxe','pxe'] else boot_mode
                    rf_boot=rf.Boot(boot=rf_boot_mode,keep='keep')
                    rf_fail=False if rf_boot else True
                if rf_fail or not self.redfish:
                    self.bootorder(mode=boot_mode,ipxe=ipxe,persistent=force,force=force) 
                #boot_mode_state=self.get_boot_mode(self.ip,self.user,self.passwd,log_file=log_file,log=log)
                boot_mode_state=self.bootorder(mode='status')
                if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                    break
                km.logging(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii),log=self.log,log_level=6)
                time.sleep(2)
        return self.do_power(cmd,retry=retry,verify=verify,timeout=timeout,post_keep_up=post_keep_up,lanmode=lanmode,fail_down_time=fail_down_time)

    def do_power(self,cmd,retry=0,verify=False,timeout=1200,post_keep_up=40,pre_keep_up=0,lanmode=None,cancel_func=None,fail_down_time=300):
        timeout=km.integer(timeout,default=1200)
        def lanmode_check(mode):
            # BMC Lan mode Checkup
            cur_lan_mode=self.lanmode()
            if cur_lan_mode[0]:
                if self.lanmode_convert(mode) == self.lanmode_convert(cur_lan_mode[1]):
                    km.logging(' Already {}'.format(self.lanmode_convert(mode,string=True)),log=self.log,log_level=7)
                    return self.lanmode_convert(cur_lan_mode[1],string=True)
                else:
                    rc=self.lanmode(mode)
                    if rc[0]:
                        km.logging(' Set to {}'.format(km.Get(rc,1)),log=self.log,log_level=5)
                        return km.Get(rc,1)
                    else:
                        km.logging(' Can not set to {}'.format(self.lanmode_convert(mode,string=True)),log=self.log,log_level=1)
        chkd=False
        for mm in self.mode:
            name=mm.__name__
            if cmd not in ['status','off_on'] + list(mm.power_mode):
                self.warn(_type='power',msg="Unknown command({})".format(cmd))
                return False,'Unknown command({})'.format(cmd)

            power_step=len(mm.power_mode[cmd])-1
            for ii in range(1,int(retry)+2):
                checked_lanmode=None
                if verify or cmd == 'status':
                    init_rc=self.run_cmd(mm.cmd_str('ipmi power status'))
                    if km.krc(init_rc[0],chk='error'):
                        return init_rc[0],init_rc[1],ii
                    if init_rc[0] is False:
                        if init_rc[-1] == 'canceling':
                            return True,'canceling',ii
                        else:
                            self.warn(_type='power',msg="Power status got some error ({})".format(init_rc[-1]))
                            km.logging('Power status got some error ({})'.format(init_rc[-1]),log=self.log,log_level=3)
                            time.sleep(3)
                            continue
                    if cmd == 'status':
                        if init_rc[0]:
                            if cmd == 'status':
                                return True,init_rc[1][1],ii
                        time.sleep(3)
                        continue
                    init_status=km.get_value(km.get_value(km.get_value(init_rc,1,[]),1,'').split(),-1)
                    if init_status == 'off' and cmd in ['reset','cycle']:
                        cmd='on'
                    # keep command
                    if pre_keep_up > 0 and self.is_up(timeout=timeout,keep_up=pre_keep_up,cancel_func=cancel_func,keep_down=fail_down_time)[0] is False:
                        time.sleep(3)
                        continue
                km.logging('Power {} at {} (try:{}/{}) (limit:{} sec)'.format(cmd,self.ip,ii,retry+1,timeout),log=self.log,log_level=3)
                chk=1
                for rr in list(mm.power_mode[cmd]):
                    verify_status=rr.split(' ')[-1]
                    km.logging(' + Verify Status: "{}" from "{}"'.format(verify_status,rr),log=self.log,log_level=8)
                    if verify:
                        if chk == 1 and init_rc[0] and init_status == verify_status:
                            if chk == len(mm.power_mode[cmd]):
                                return True,verify_status,ii
                            chk+=1
                            continue
                        # BMC Lan mode Checkup before power on/cycle/reset
                        if checked_lanmode is None and self.lanmode_convert(lanmode) in [0,1,2] and verify_status in ['on','reset','cycle']:
                           lanmode_check(lanmode)

                        if verify_status in ['reset','cycle']:
                             if init_status == 'off':
                                 self.warn(_type='power',msg="Can not set {} on the off mode".format(verify_status))
                                 km.logging(' ! can not {} the power'.format(verify_status),log=self.log,log_level=6)
                                 return False,'can not {} the power'.format(verify_status)
                    rc=self.run_cmd(mm.cmd_str(rr),retry=retry)
                    km.logging('rr:{} cmd:{} rc:{}'.format(rr,mm.cmd_str(rr),rc),log=self.log,log_level=8)
                    if km.krc(rc,chk='error'):
                        return rc
                    if km.krc(rc,chk=True):
                        km.logging(' + Do power {}'.format(verify_status),log=self.log,log_level=3)
                        if verify_status in ['reset','cycle']:
                            verify_status='on'
                            if verify:
                                time.sleep(10)
                    else:
                        self.warn(_type='power',msg="power {} fail".format(verify_status))
                        km.logging(' ! power {} fail'.format(verify_status),log=self.log,log_level=3)
                        time.sleep(5)
                        break
                    if verify:
                        if verify_status in ['on','up']:
                            is_up=self.is_up(timeout=timeout,keep_up=post_keep_up,cancel_func=cancel_func,keep_down=fail_down_time)
                            km.logging('is_up:{}'.format(is_up),log=self.log,log_level=7)
                            if is_up[0]:
                                if chk == len(mm.power_mode[cmd]):
                                    return True,'on',ii
                            elif is_up[1] == 'down' and not chkd:
                                chkd=True
                                self.warn(_type='power',msg="Something weird. Looks BMC issue")
                                km.logging(' Something weird. Try again',log=self.log,log_level=1)
                                retry=retry+1 
                                time.sleep(20)
                            time.sleep(3)
                        elif verify_status in ['off','down']:
                            is_down=self.is_down(cancel_func=cancel_func)
                            km.logging('is_down:{}'.format(is_down),log=self.log,log_level=7)
                            if is_down[0]:
                                if chk == len(mm.power_mode[cmd]):
                                    return True,'off',ii
                            elif is_down[1] == 'up' and not chkd:
                                chkd=True
                                self.warn(_type='power',msg="Something weird. Looks BMC issue")
                                km.logging(' Something weird. Try again',log=self.log,log_level=1)
                                retry=retry+1 
                                time.sleep(20)
                            time.sleep(3)
                        chk+=1
                    else:
                        return True,km.get_value(km.get_value(rc,1),1),ii
                time.sleep(3)
        if chkd:
            km.logging(' It looks BMC issue. (Need reset the physical power)',log=self.log,log_level=1)
            self.error(_type='power',msg="It looks BMC issue. (Need reset the physical power)")
            return False,'It looks BMC issue. (Need reset the physical power)',ii
        return False,'time out',ii

    def lanmode_convert(self,mode=None,string=False):
        if isinstance(mode,str):
            if mode.lower() in ['dedicate','dedicated','0']:
                mode=0
            elif mode.lower() in ['share','shared','onboard','1']:
                mode=1
            elif mode.lower() in ['failover','ha','2']:
                mode=2
        if string:
            if mode == 0:
                return 'Dedicated'
            elif mode == 1:
                return 'Shared'
            elif mode == 2:
                return 'Failover'
            else:
                return 'Unknown'
        else:
            return mode

    def lanmode(self,mode=None):
        mm=self.get_mode('smc')
        if not mm:
            km.logging(' - SMCIPMITool not found',log=self.log,log_level=1,dsp='e')
            return False,'SMCIPMITool not found'
        if self.lanmode_convert(mode) in [0,1,2]:
            rc=self.run_cmd(mm.cmd_str("""ipmi oem lani {}""".format(self.lanmode_convert(mode))),timeout=5)
            if km.krc(rc[0],chk=True):
                return True,self.lanmode_convert(mode,string=True)
            return rc
        else:
            rc=self.run_cmd(mm.cmd_str("""ipmi oem lani"""))
            if km.krc(rc[0],chk=True):
                if mode in ['info','support']:
                    return True,km.Get(km.Get(rc,1),1)
                else:
                    a=km.findstr(rc[1][1],'Current LAN interface is \[ (\w.*) \]')
                    if len(a) == 1:
                        return True,a[0]
            return False,None

    def error(self,_type=None,msg=None):
        if _type and msg:
            self.err.update({_type:{km.now():msg}})
        else:
            if not _type:
                if self.err: return True,self.err
                return False,'OK'
            else:
                get_msg=self.err.get(_type,None)
                if get_msg: return True,get_msg
                return False,None

    def warn(self,_type=None,msg=None):
        if _type and msg:
            self.warning.update({_type:{km.now():msg}})
        else:
            if not _type:
                if self.warning: return True,self.warning
                return False,None
            else:
                get_msg=self.warning.get(_type,None)
                if get_msg: return True,get_msg
                return False,None

    def cancel(self,cancel_func=None,msg=None,log_level=1):
        if cancel_func is None: cancel_func=self.cancel_func
        if self.canceling:
            return self.canceling
        else:
            if km.is_cancel(cancel_func):
                if msg :
                    km.logging(msg,log=self.log,log_level=log_level)
                    self.canceling.update({km.now():msg})
                else:
                    self.canceling.update({km.now():km.get_pfunction_name()})
                return 'canceling'
        return False

    def is_admin_user(self,**opts):
        admin_id=opts.get('admin_id',2)
        defined_user=self.__dict__.get('user')
        for mm in self.mode:
            #name=mm.__name__
            for j in range(0,2):
                rc=self.run_cmd(mm.cmd_str("""user list"""))
                if km.krc(rc,chk=True):
                    for i in km.get_value(km.get_value(rc,1),1).split('\n'):
                        i_a=i.strip().split()
                        if str(admin_id) in i_a:
                            if km.get_value(i_a,-1) == 'ADMINISTRATOR':
                                if defined_user == km.get_value(i_a,1):
                                    return True
                else:
                    ok,user,passwd=self.find_user_pass()
                    if not ok: break
        return False
        
if __name__ == "__main__":
    import SysArg
    import sys
    import os
    import pprint
    def KLog(msg,**agc):
        direct=agc.get('direct',False)
        log_level=agc.get('log_level',6)
        ll=agc.get('log_level',5)
        if direct:
            sys.stdout.write(msg)
            sys.stdout.flush()
        elif log_level < ll:
            print(msg)

    ats_version='2.2'
    arg=SysArg.SysArg(program='kBmc',desc='Inteligent BMC Tool',version=ats_version,cmd_id=1)
    arg.define('ip',short='-i',long='--ip',desc='BMC IP Address',params_name='BMC_IP',required=True)
    arg.define('ipmi_user',short='-u',long='--user',desc='BMC User',params_name='BMC_USER',default='ADMIN')
    arg.define('ipmi_pass',short='-p',long='--passwd',desc='BMC Password',params_name='BMC_PW',default='ADMIN')
    arg.define('tool_path',short='-t',desc='misc tool path',default=km.get_my_directory())
    arg.define('support_redfish',long='--support_redfish',desc='Support Redfish',default=False)
    arg.define('smc_file',short='-si',desc='SMC IPMITOOL file')
    arg.define(group_desc='Is node UP?',group='is_up',command=True)
    arg.define(group_desc='Show summary',group='summary',command=True)
    arg.define(group_desc='Show bootorder',group='bootorder',command=True)
    arg.define('bootorder_pxe',long='--pxe',group_desc='Set PXE boot mode',group='bootorder')
    arg.define('bootorder_ipxe',long='--ipxe',group_desc='Set iPXE boot mode',group='bootorder')
    arg.define('bootorder_bios',long='--bios',group_desc='Set BIOS setup mode',group='bootorder')
    arg.define('bootorder_hdd',long='--hdd',group_desc='Set HDD boot mode',group='bootorder')
    arg.define(group_desc='Check current user is ADMINISTRATOR user',group='is_admin_user',command=True)
    arg.define(group_desc='Get current lanmode',group='lanmode',command=True)
    arg.define(group_desc='Show info',group='info',command=True)
    arg.define(group_desc='Get BMC Mac Address',group='mac',command=True)
    arg.define(group_desc='Get Ethernet Mac Address',group='eth_mac',command=True)
    arg.define(group_desc='Reset BMC',group='reset',command=True)
    arg.define(group_desc='Send power signal',group='power',command=True)
    arg.define('power_status',short='-r',long='--reset',desc='Send reset signal',group='power')
    arg.define('power_off',short='-f',long='--off',desc='Send reset signal',group='power')
    arg.define('power_on',short='-o',long='--on',desc='Send on signal',group='power')
    arg.define('power_shutdown',short='-s',long='--shutdown',desc='Send shutdown signal',group='power')
    arg.define('power_cycle',short='-c',long='--cycle',desc='Send cycle signal',group='power')
    arg.define(group_desc='Send power signal and verify status',group='vpower',command=True)
    arg.define('vpower_reset',short='-vr',long='--vreset',desc='Send reset signal',group='power')
    arg.define('vpower_off',short='-vf',long='--voff',desc='Send off signal',group='power')
    arg.define('vpower_on',short='-vo',long='--von',desc='Send on signal',group='power')
    arg.define('vpower_off_on',short='-vfo',long='--voff_on',desc='Send off and on signal',group='power')
    arg.define('vpower_shutdown',short='-vs',long='--vshutdown',desc='Send shutdown signal',group='power')
    arg.define('vpower_cycle',short='-vc',long='--vcycle',desc='Send cycle signal',group='power')
    arg.define(group_desc='Redfish Command',group='redfish',command=True)
    arg.define('redfish_power',short='-rp',long='--rpower',desc='Send power signal(on/off)',params_name='PW',group='redfish')
    arg.define('redfish_info',short='-ri',long='--rinfo',desc='Get System Information', group='redfish')
    arg.define('redfish_reset_bmc',short='-rrb',long='--reset_bmc',desc='Reset BMC', group='redfish')
    arg.define('redfish_net_info',short='-rni',long='--net_info',desc='Show Network Interface', group='redfish')
    arg.Version()
    arg.Help()
    ipmi_ip=arg.Get('ipmi_ip') 
    ipmi_user=arg.Get('ipmi_user')
    ipmi_pass=arg.Get('ipmi_pass')
    ipxe=arg.Get('bootorder_ipxe')
    redfish=arg.Get('support_redfish')
    smc_file=arg.Get('smc_file')
#    if arg.Get('redfish_info',group='redfish'):
#        redfish_cmd='Systems/1'
#    elif arg.Get('redfish_reset_bmc',group='redfish'):
#        redfish_cmd='Managers/1/Actions/Manager.Reset'
#    elif arg.Get('redfish_net_info',group='redfish'):
#        redfish_cmd='Systems/1/EthernetInterfaces'
#    elif arg.Get('redfish_power',group='redfish'):
#        redfish_power=arg.Get('redfish_power',group='redfish')



    if km.is_ipv4(ipmi_ip) is False or km.get_value(sys.argv,1) in ['help','-h','--help']:
        help()

    #elif km.is_port_ip(ipmi_ip,(623,664,443)):
    elif km.IP(ipmi_ip).IsOpenPort((623,664,443)):
        print('Test at {}'.format(ipmi_ip))
        if smc_file and os.path.isfile('{}/{}'.format(tool_path,smc_file)):
            bmc=kBmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool(),Smcipmitool(tool_path=tool_path,smc_file=smc_file)])
        elif smc_file and os.path.isfile(smc_file):
            bmc=kBmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool(),Smcipmitool(tool_path=smc_path,smc_file=smc_file)])
        else:
            bmc=kBmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool()])

        cmd_2=km.get_value(sys.argv,-2)
        if cmd_2 == 'power':
            sub_cmd = km.get_value(sys.argv,-1)
            if sub_cmd == 'status':
                print(km.get_value(bmc.do_power(cmd=sub_cmd),1))
            elif sub_cmd in ['on','off','reset','cycle','shutdown']:
                print(km.get_value(bmc.do_power(cmd=sub_cmd),1))
            else:
                print('Unknown command "{}"'.format(sub_cmd))
        elif cmd_2 == 'vpower':
            sub_cmd = km.get_value(sys.argv,-1)
            if sub_cmd == 'status':
                print(bmc.power(cmd=sub_cmd))
            elif sub_cmd in ['on','off','off_on','reset','cycle','shutdown']:
                print(km.get_value(bmc.power(cmd=sub_cmd),1))
            else:
                print('Unknown command "{}"'.format(sub_cmd))
#        elif cmd_2 == 'redfish':
#            redfish_out=bmc.run_cmd(km.get_value(sys.argv,-1),mode='redfish')
#            if km.krc(redfish_out,chk=True):
#                pprint.pprint(km.get_value(redfish_out,1))
        elif cmd_2 == 'bootorder':
            mode=km.get_value(sys.argv,-1)
            if mode == 'ipxe':
                print(km.get_value(bmc.bootorder(mode='pxe',ipxe=True,persistent=True,force=True),1))
            elif mode=='status':
                print(bmc.bootorder(mode='status'))
            else:
                print(km.get_value(bmc.bootorder(mode=mode,persistent=True,force=True),1))
        else:
            cmd=km.get_value(sys.argv,-1)
            if cmd == 'is_up':
                print(km.get_value(bmc.is_up(),1))
            elif cmd == 'bootorder':
                print(km.get_value(bmc.bootorder(),1))
            elif cmd == 'summary':
                print(bmc.summary())
            elif cmd == 'is_admin_user':
                print(bmc.is_admin_user())
            elif cmd == 'lanmode':
                print(bmc.lanmode())
            elif cmd == 'info':
                pprint.pprint(bmc.__dict__)
            elif cmd == 'mac':
                print(km.get_value(bmc.get_mac(),1,default=['Can not get'])[0])
            elif cmd == 'eth_mac':
                print(km.get_value(bmc.get_eth_mac(),1,default=['Can not get'])[0])
            elif cmd == 'reset':
                print(km.get_value(bmc.reset(),1))
            else:
                print('Unknown command "{}"'.format(cmd))
                help()
    else:
        print('Looks the IP({}) is not BMC/IPMI IP or the BMC is not ready on network'.format(ipmi_ip))
