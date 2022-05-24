import json , uuid , os
from base64 import b64encode
from http.client import HTTPSConnection
from MedatechUK.oDataConfig import Config
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response

#region "Form Class"
class SerialF :

    #region Properties
    @property
    def fname(self):    
        return self._fname
    @fname.setter
    def fname(self, value):
        self._fname = value

    @property
    def rt(self):    
        return str(self._rt)
    @rt.setter
    def rt(self, value):
        self._rt = value

    @property
    def typename(self):    
        return str(self._typename)
    @typename.setter
    def typename(self, value):
        self._typename = value

    @property
    def bubbleid(self):    
        return str(self._bubbleid)

    #endregion

    #region "ctor"
    def __init__(self, **kwargs):
        self.fname = ''
        self.rt = 1
        self._bubbleid = uuid.uuid4()
        self.typename = ""

        for arg in kwargs.keys():    
            if ( hasattr( self , arg ) ):
                setattr( self , arg , kwargs[arg] )   
    
    #endregion

#endregion

#region "Type Class"
class SerialT :
    
    #region Propereties
    @property
    def pType(self):    
        return self._pType
    @pType.setter
    def pType(self, value):
        self._pType = value

    @property
    def Len(self):    
        return self._Len
    @Len.setter
    def Len(self, value):
        self._Len = value

    @property
    def pCol(self):    
        return self._pCol
    @pCol.setter
    def pCol(self, value):
        self._pCol = value

    #endregion

    #region "ctor"
    def __init__(self, this, att , **kwargs):
        
        self.pCol = att
        self.pType = 'CHAR'
        self.Len = 40
        
        for arg in kwargs.keys():    
            if ( hasattr( self , arg ) ):
                setattr( self , arg , kwargs[arg] )              

        if (att=="rt"):
            self.pCol="RECORDTYPE" 
            self.pType="CHAR"
        
        if (att=="bubbleid"):
            self.pCol="BUBBLEID" 
            self.pType="CHAR"
        
        if (att=="typename"):
            self.pCol="TYPENAME" 
            self.pType="CHAR"
            self.len = 3

        this.props[att] = self
    
    #endregion

    #region "Methods"
    def oData(self, this):
        return {
            'CHAR': chr(34) + self.pCol + chr(34) + " : " + chr(34) + str(this) + chr(34) ,
            'INT': chr(34) + self.pCol + chr(34) + " : " + str(this) ,
            'REAL': chr(34) + self.pCol + chr(34) + " : " + str(this) ,
        }.get(self._pType.upper(), chr(34) + self.pCol + chr(34) + " : " + chr(34) + str(this) + chr(34))
    
    #endregion

#endregion 

#region "Base Class"
class SerialBase :

    #region Properies
    @property
    def props(self):    
        return self._props
    @props.setter
    def props(self, value):
        self._props = value

    #endregion

    #region "ctor"
    def __init__(self, form , **kwargs):
        self.form = form
        self.props = {}
        self.log = mLog() 
        for arg in kwargs.keys():            
            if ( hasattr( self , arg ) ) :
                try:
                    setattr( self , arg , kwargs[arg] )
                except:
                    pass
    
    #endregion

    #region "Output Methods"

    def toFile(self, fn , method):
        self.log.logger.debug("Writing file [{}] {}".format( fn , method()))                         
        with open(fn, 'w') as the_file:            
            the_file.write(method()) 

    def toJSON(self):        
        return json.dumps(self, default=lambda o: {
            key.lstrip('_'): 
            value for key, value in o.__dict__.items() if key !="_props" and key !="form" and key !="log"}, 
            sort_keys=False, indent=4)   

    def toOdata(self , this = 0):         
        ret = ""  
        l = 0     
        if (this==0):            
            l = 1
            this = self
            ret +=("{ ") 

        if isinstance(this, list):
            ret +=("[ ")
            for i in this:
                ret +=("{ ")
                ret +=self.toOdata(i)
                ret +=(" }")
                if(this[-1]!=i):
                    ret += (" , ")
            ret +=(" ]")
            
        else:
            f = 0
            for key in this.__dict__ :  
                if (key != "_props" and key !="form"and key !="log"):
                    if isinstance(this.__dict__[key], list):      
                        ret += ' , ' +chr(34)+ (this.__dict__[key][-1].form.fname) +chr(34)+ ' : '
                        ret += self.toOdata(this.__dict__[key])
                    
                    else:
                        if(hasattr(this,"props")) :
                            if(f==0):
                                f = 1
                            else :
                                ret +=(", ")
                            ret +=(this.props[key.lstrip('_')].oData(this.__dict__[key]))            

        if(l!=0):
            ret += " }"

        return ret

    def toFlatOdata(self , this = 0):         
        ret = ""  
        l = 0     
        if (this==0):            
            l = 1
            this = self
            ret +=("{ ") 
            ret +=(this.props["bubbleid"].oData(this.form.bubbleid) )  + ", "            
            ret +=(this.props["typename"].oData(this.form.typename) )  + ", " + chr(34) + "ZODA_LOAD_SUBFORM" + chr(34) + " : ["            

        if isinstance(this, list):            
            for i in this:                               
                ret +=self.toFlatOdata(i)    
                ret += " } "            
                if(this[-1]!=i):
                    ret += (",")            
            
        else:
            f = 0
            ret += " { "
            if(this.props.__contains__("rt")) :
                if(f==0): 
                    f = 1
                else :
                    ret +=(", ")
                ret +=(this.props["rt"].oData(this.form.rt) ) 

            
            for key in this.__dict__ :  
                if (key != "_props" and key !="form" and key !="log"):
                    if isinstance(this.__dict__[key], list):      
                        ret+=" } ,"
                        ret += self.toFlatOdata(this.__dict__[key])
                    
                    else:
                        if(hasattr(this,"props")) and this.props.__contains__(key.lstrip('_')):
                            if(f==0):
                                f = 1
                            else :
                                ret +=(", ")
                            ret +=(this.props[key.lstrip('_')].oData(this.__dict__[key]))                        
            
            # Iterate through readonly properties
            for key in this.props:
                if (key != "rt" and key !="bubbleid" and key !="formname" and key !="typename"):
                    if not this.__dict__.__contains__("_" + key):
                        if(f==0):
                            f = 1
                        else :
                            ret +=(", ")
                        ret +=(this.props[key.lstrip('_')].oData(getattr(this, key)))                  
                
        if(l!=0):
            ret += "] }"

        return ret
    
    def toPri(self, config, method, **kwargs):            
        
        ## This function will PATCH a completion request ONLY
        ## if the fornname of the upper level is 'ZODA_TRANS'

        # Set the response object
        if kwargs.__contains__("request"):
            # The call contains a request - populate it's response
            ret = kwargs["request"].response
        elif kwargs.__contains__("response"):
            # The call contains a response - populate directly
            ret = kwargs["response"]
            
        url = '/odata/priority/{}/{}/{}'.format(config.tabulaini , config.environment , self.form.fname)
        headers= { 
                'Authorization' : 'Basic %s' %  b64encode(bytearray(config.ouser + ":" + config.opass,'ascii')).decode("ascii") ,
                'Content-Type': 'application/json',
                "User-Agent": "MedatechUK Python Client",
            }
        data = json.loads(method())
        self.log.logger.debug("POSTing to [{}{}] ".format( config.oDataHost, url ))                 
        self.log.logger.debug("Headers:\n{}".format( json.dumps(headers ,  indent = 4) ))
        self.log.logger.debug("Data:\n{}".format( json.dumps(data, indent = 4) ))        

        r = HTTPSConnection(config.oDataHost)  
        r.request( 
            'POST', 
            url , 
            json.dumps(data),
            headers,              
        )
        res = r.getresponse()             
        if res.status == 201: # Created
            self.log.logger.debug("[{}] OK".format( res.status ))

            # If we're using the oData loading form, send a PATCH
            # to identify that all data has been sent.
            if self.form.fname == 'ZODA_TRANS':
                self.log.logger.debug("[{}] {}".format( res.status , res.reason ))
                ret.Status = res.status
                ret.Message = res.reason
                ret.data = json.load(res)
                self.log.logger.debug("Result: {}".format( json.dumps(ret.data  , indent = 4 )))

            else:
                data = json.loads(res.read())    

                patch = {}
                patch['COMPLETE'] = "Y"

                r.request( 
                    'PATCH', 
                    url + "(BUBBLEID='"+ data['BUBBLEID'] + "',LOADTYPE=" + str(data['LOADTYPE']) + ")", 
                    headers=headers, 
                    body=json.dumps(patch) 
                )
                
                self.log.logger.debug("PATCHing to [{}] ... ".format( url + "(BUBBLEID='"+ data['BUBBLEID'] + "',LOADTYPE=" + str(data['LOADTYPE']) + ")" ))  
                res = r.getresponse()

                if res.status != 200: # PATCHed
                    self.log.logger.critical("[{}] Fail: {}".format( res.status , res.reason ))
                    ret.Status = res.status   
                    ret.Message = "PATCH Failed: " + res.reason  
                    
                    # If the response is text, create a response with the text         
                    if res.getheader("Content-Type","").find("text/plain") > -1:                             
                        er = str(res.read().decode('utf-8'))
                        ret.data = {"error": er }     
                        self.log.logger.critical("{}".format( er ))              

                    elif res.getheader("Content-Type","").find("text/html") > -1:
                            ret.data = {"error": "Priority service not responding." }     
                            self.log.logger.critical("{}".format( "Priority service not responding." ))   

                    else:
                        # Create reponse from json 
                        Response.data = json.load(res)  
                        self.log.logger.critical( "{}".format( json.dumps(Response.data  , indent = 4 ) ) )

                else:
                    ## Sucsess!
                    self.log.logger.debug("[{}] {}".format( res.status , res.reason ))
                    ret.Status = res.status
                    ret.Message = res.reason
                    ret.data = json.load(res)
                    self.log.logger.debug("Result: {}".format( json.dumps(ret.data  , indent = 4 ) ))

        else:   
            ret.Status = res.status
            ret.Message = "POST Failed: " + res.reason   
            self.log.logger.critical( "[{}] Fail: {}".format( res.status , res.reason ) )            

            # If the response is text, create a response with the text         
            if res.getheader("Content-Type","").find("text/plain") > -1:                             
                er = str(res.read().decode('utf-8'))
                ret.data = {"error": er }     
                self.log.logger.critical("{}".format( er ))              

            elif res.getheader("Content-Type","").find("text/html") > -1:
                    ret.data = {"error": "Priority service not responding." }     
                    self.log.logger.critical("{}".format( "Priority service not responding." ))   

            else:
                # Create reponse from json 
                Response.data = json.load(res)  
                self.log.logger.critical( "{}".format( json.dumps(Response.data  , indent = 4 ) ) )

    #endregion

#endregion
