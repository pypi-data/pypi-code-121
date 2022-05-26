#coding=utf-8

'''
author gonewind.he@gmail.com
2020/02/05
architecture

        L7Server  L7Client
--------------------------
L3Node         L7Node   
--------------------------
        Node                        Brain
-------------------------------------------
SafeEngine DataEngine CommEngine MsgEngine
'''

import logging
import socket
import struct
import time
import traceback




class PPMessage(object):
    '''
    MessageFormat：
    version     messagetype messagelength   TLVs
    1byte       2bytes      4bytes          any

    msg = PPMessage(dictdata={})  or msg

    '''
    #messagetype
    REGISTER = 1
    INQUERY  = 3
    INQUERY_RES = 4


    def __init__(self, **kwargs):
        '''
        dictdata  bindata or dict self
        '''
        self.dict_data = {}
        self.bin_length = 0

        if "dictdata" in kwargs:
            self.dict_data = kwargs["dictdata"].copy()
        elif "bindata" in kwargs:
            self.load(kwargs["bindata"])
        else:
            self.dict_data = kwargs
        pass

    def get(self, kw):
        return self.dict_data.get(kw, None)

    def set(self, kw, value):
        self.dict_data[kw] = value
        return

    def load(self, bindata):
        try:
            result = struct.unpack("BHI", bindata[:8])
    
            self.dict_data["version"] = result[0]
            self.dict_data["messagetype"] = result[1]
            self.dict_data["messagelength"] = result[2]
            bintlvs_length = result[2]
            self.bin_length = 8 + bintlvs_length
            self.dict_data["bintlvs"] = struct.unpack("%ds" % bintlvs_length, bindata[8:8+bintlvs_length])[0]
        except Exception as exp:
            logging.warning("Error when decode ppmessage:\n     (%d)%s \n    %s" %(len(bindata),''.join('{:02x} '.format(x) for x in bindata[:7]),exp))
            return None
        return self

    def dump(self):
        # logging.debug("%s"%self.dict_data)
        bintlvs_length = len(self.dict_data["bintlvs"])
        data = struct.pack("BHI%ds" % bintlvs_length,
                           self.dict_data.get("version",1),
                           self.dict_data["messagetype"],
                           bintlvs_length,
                           self.dict_data["bintlvs"],
                           )
        self.bin_length = 8 + bintlvs_length
        return data

    @staticmethod
    def unpackip(bin_ip):
        return socket.inet_ntoa(struct.pack('I', socket.htonl(struct.unpack("I",bin_ip)[0])))    
    @staticmethod 
    def packip(ip):
        return struct.pack("I",socket.ntohl(struct.unpack("I", socket.inet_aton(ip))[0]))     

class AppMessage(PPMessage):
    '''
    Message
    '''
    def __init__(self, **kwargs):
        self.tag_names = kwargs.get("tag_names",{})
        self.tag_types = kwargs.get("tag_types",{})
        super().__init__(**kwargs)
        

    def load(self, bindata):
        try:
            if not super().load(bindata):
                return None
            start_pos = 0
            data = bindata[8:]
            tlvs = {}
            while start_pos < self.dict_data["messagelength"]:
                tlv = AppTLV(tag_names=self.tag_names,tag_types=self.tag_types).load(data[start_pos:])
                tlvs.update(tlv.get_namevalue_dict())
                start_pos += tlv.bin_length
            self.dict_data.update({"body":tlvs})
        except Exception as exp:
            logging.warning("Message decode error:%s \n %s"%(exp,str(self.dict_data)))
            logging.warning(traceback.format_exc())
        return self

    def dump(self):
        bodydata = b""
        for (name,value) in self.dict_data["body"].items():
            tlv = AppTLV(tag_names=self.tag_names,tag_types=self.tag_types).set_namevalue(name,value)
            bodydata += tlv.dump()
        self.dict_data["bintlvs"] = bodydata
        return super().dump()
    
class TLV(object):
    def __init__(self,tag=0,length=0,value=None):
        '''
        dictdata  bindata or tag,length,value
        '''
        self.tag = 0
        self.length =0
        self.value = None
        self.bin_length = 0
        self.set(tag,length,value)
        pass

    def dict(self):
        return {"tag":self.tag,"length":self.length,"value":self.value,}

    def set(self,tag,length,value):
        self.tag,self.length,self.value = tag,length,value
        self.bin_length = 8 + self.length
        return self

    def load(self, bindata):
        try:
            tag, length = struct.unpack("BI", bindata[:8])
            value = struct.unpack("%ds" % length, bindata[8:8 + length])[0]
            self.set(tag,length,value)
            return self
        except:
            logging.debug("error when decode tlv %s" % bindata[:5])
            return None

    def dump(self):
        """
        (tag,length,value)  value is bytes
        """
        bindata = struct.pack("BI%ds" % self.length,
                            self.tag, self.length, self.value)
        return bindata

class AppTLV(TLV):
    '''
    atlv = AppTLV(1,1,b"1")
    atlv.set_namevalue(name="ip",value="192.168.1.5")
    atlv.dump()

    tag_name={1:"node_id",2:"local_ip",3:"local_port",4:"nodes",5:"external_ip",6:"external_port"}
    tag_type={1:"str",2:"ip",3:"H",4:"str",5:"ip",6:"H"}  可选 IBH str ip
    '''
    
    def __init__(self,tag=0,length=0,value=None,tag_names={},tag_types={}):
        self.tag_name = tag_names
        self.tag_type = tag_types

        self._name_tag()
        super().__init__(tag,length,value)
        pass
    
    def _name_tag(self):
        self.name_tag={}
        for (tag,name) in self.tag_name.items():
            self.name_tag.update({name:tag})
        return

    def get_name(self):
        return self.tag_name.get(self.tag,str(self.tag))

    def get_namevalue_dict(self):
        vtype =self.tag_type.get(self.tag,"bytes")
        if  vtype == "str":
            return {self.get_name():self.value.decode()}
        elif vtype == "ip":
            return {self.get_name():socket.inet_ntoa(self.value)}
        elif vtype in ("I", "H", "B"):
            return {self.get_name():struct.unpack(vtype, self.value)[0]}
        else:
            return {self.get_name():self.value}

    
    def set_namevalue(self,name,value):
        if name is None or value is None:
            return
        if name:
            self.tag = self.name_tag.get(name,0)

        vtype =self.tag_type.get(self.tag,"bytes")
        if  vtype == "str":
            self.value = value.encode()
        elif vtype == "ip":
            self.value = socket.inet_aton(value)
        elif vtype in ("I", "H", "B"):
            self.value = struct.pack(vtype, value)
        else :
            self.value = value
        self.length = len(self.value)
        
            
        return self

class User(object):
    '''
    user' authentication authorization accounting
    authtype = "password"|"signature"|"one time password"
    '''
    PASSWORD = 1
    def __init__(self,org_id,user_id,auth_type=1):
        self.user_id,self.auth_type = user_id,auth_type
        pass

    def authentication(self,credentials):
        return True

    def sendOTP(self):
        pass

    


    

class Service(object):
    def __init__(self,service_id,ip,port):
        self.service_id,self.ip,self.port = service_id,ip,port
        pass

 

class MsgEngine(object):

    def __init__(self,msgtypes={},msghandle={},tag_names={},tag_types={}):
        '''
        msgtypes is a dict of {type：name}: {1:"regist_req",2:"regist_res",3:"inquire_req",4:"inquire_res",5:"connect_req",6:"connect_res",11:"deregist_req",12:"deregist_res"}
        msghandle is a dict of {type: handle}:{1:registreq,2:registres}
        '''
        self._msghandle = msghandle 
        self._msgtypes = {}
        self.msgtypes = msgtypes
        self.tag_names = tag_names
        self.tag_types = tag_types

        

    @property
    def msgtypes(self):
        return self._msgtypes

    @msgtypes.setter
    def msgtypes(self,msgtypes):
        # self.msgtypes={1:"regist_req",2:"regist_res",3:"inquire_req",4:"inquire_res",5:"connect_req",6:"connect_res",11:"deregist_req",12:"deregist_res"}
        self._msgtypes.update(msgtypes)
        self.rmsgtypes={}
        for (k,v) in self.msgtypes.items():
            self.rmsgtypes.update({v:k})
    
    @property 
    def msghandle(self):
        return self._msghandle

    @msghandle.setter
    def msghandle(self,msghandle):
        return self._msghandle.update(msghandle)



    def process(self,bindata,addr,sock):
        if b"" == bindata or addr == None:
            return
        try:
            msgtype,body = self.decode(bindata)
            logging.debug("received msgtype {} message:\n    {}".format(msgtype,body))
            if not msgtype:
                return
            # if messagetype in self.msg_process:
            if time.time()-int(body.get("timestamp","1581337371"))>100:
                logging.warning("May someone attack by replay from %s:%d \n%s"%(addr[0],addr[1],body))            
            self.msghandle[msgtype](body,addr)
        except Exception as exp:
            logging.warning(str(traceback.format_exc()))    

    def encode(self,messagetype,reqbody):
        logging.debug("to be send msgtype {} message:\n     {}".format(messagetype,reqbody))
        appmsg = AppMessage(dictdata={"messagetype":self.rmsgtypes[messagetype],"body":reqbody},tag_names=self.tag_names,tag_types=self.tag_types)
        return appmsg.dump()
    
    def decode(self,bindata):
        '''
        messagetype and messagebody

        Args:
            bindata (_type_): _description_

        Returns:
            str,dict: messagetype and messagebody
        '''
        try:
            appmsg = AppMessage(bindata=bindata,tag_names=self.tag_names,tag_types=self.tag_types)
            logging.debug("received :\n    %s"%appmsg.dict_data)
            bin_messagetype = appmsg.dict_data.get("messagetype",None)
            if bin_messagetype==None:
                return "",{}
            messagetype = self.msgtypes[bin_messagetype]
            return messagetype,appmsg.dict_data.get("body","")
        except Exception as exp:
            logging.warning(repr(exp)) 
        return "",{}

