import html,pymysql,sys,os,re,socket,random
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict

import xml.sax.saxutils as saxutils


class XSS:

    @staticmethod
    def escape(s):
        return html.escape(s,quote=True)

    @staticmethod
    def unescape(s):
        return saxutils.unescape(s)

    @staticmethod
    def escape_form(obj):
        d={}
        for x in dict(obj.form):
            d.update({x:XSS.escape(dict(obj.form)[x][0])}) if  sys.version_info < (3,0) else d.update({x:XSS.escape(dict(obj.form)[x])})
        return ImmutableMultiDict(d)

    @staticmethod
    def escape_args(obj):
        d={}
        for x in dict(obj.args):
            d.update({x:XSS.escape(dict(obj.args)[x][0])}) if  sys.version_info < (3,0) else d.update({x:XSS.escape(dict(obj.args)[x])})
        return ImmutableMultiDict(d)


class CSRF:

    @staticmethod
    def validate_flask(obj,allowed_domains=[]):
        domains=[obj.host] if (not allowed_domains or len(allowed_domains)==0) else allowed_domains
        referer=obj.headers.get('Referer','')
        if referer.strip()=="" or referer.strip().lower()=="null":
            return False
        a=referer.split("://")[1].split("/")[0]
        if a not in domains:
            return False
        return True

    @staticmethod
    def validate(referer,allowed_domains):
        if referer.strip()=="" or referer.strip().lower()=="null":
            return False
        a=referer.split("://")[1].split("/")[0]
        if a not in allowed_domains:
            return False
        return True


class SQLI:

    @staticmethod
    def escape(s):
        return "'"+pymysql.converters.escape_string(s)+"'"

    @staticmethod
    def escape_for_search(s,operator_left,operator_right):
        return ["'"+operator_left+pymysql.converters.escape_string(x)+operator_right+"'" for x in s.split()]

    @staticmethod
    def unescape(s):
        if s[:1]=="'" and s[-1]=="'":
            s=s[1:-1]
        s = s.replace('\\\\', '\\')
        s = s.replace('\\0', '\0')
        s = s.replace('\\n', '\n')
        s = s.replace('\\r', '\r')
        s = s.replace('\\Z', '\032')
        s = s.replace("\\'", "'")
        s = s.replace('\\"', '"')
        return s.strip()

    @staticmethod
    def escape_form(obj):
        d={}
        for x in dict(obj.form):
            d.update({x:SQLI.escape(dict(obj.form)[x][0])}) if  sys.version_info < (3,0) else d.update({x:SQLI.escape(dict(obj.form)[x])})
        return ImmutableMultiDict(d)

    @staticmethod
    def escape_args(obj):
        d={}
        for x in dict(obj.args):
            d.update({x:SQLI.escape(dict(obj.args)[x][0])}) if  sys.version_info < (3,0) else d.update({x:SQLI.escape(dict(obj.args)[x])})
        return ImmutableMultiDict(d)


class FILE_UPLOAD:

    @staticmethod
    def validate_form(obj,allowed_extensions=['png','jpg','jpeg','gif','pdf'],allowed_mimetypes=["application/pdf","application/x-pdf","image/png","image/jpg","image/jpeg"]):
        for x in dict(obj.files):
            if FILE_UPLOAD.check_file(obj.files[x],allowed_extensions=allowed_extensions,allowed_mimetypes=allowed_mimetypes)==False:
                return False
        return True

    @staticmethod
    def check_file(f,allowed_extensions=['png','jpg','jpeg','gif','pdf'],allowed_mimetypes=["application/pdf","application/x-pdf","image/png","image/jpg","image/jpeg"]):
        return FILE_UPLOAD.valid_file(f,allowed_extensions,allowed_mimetypes)

    @staticmethod
    def valid_extension(f,extentions):
        try:
            return f.split(".")[1].lower() in extentions
        except:
            return False

    @staticmethod
    def valid_mimetype(f,mimetypes):
        try:
            return f.content_type.lower() in mimetypes
        except:
            return False

    @staticmethod
    def valid_file(f,extentions,mimetypes):
        return FILE_UPLOAD.valid_extension(FILE_UPLOAD.secure_filename(f),extentions) and FILE_UPLOAD.valid_mimetype(f,mimetypes)

    @staticmethod
    def secure_filename(f,random_ids=True):
        name= secure_filename(".".join(f.filename.split(".")[:2]))
        if random_ids==True:
            name_parts=name.split('.')
            return '{}_{}_{}.{}'.format(random.randint(1000,1000000),name_parts[0],random.randint(1000,1000000),name_parts[1])
        return name

    @staticmethod
    def save_file(f,path="",random_ids=True):
        os.makedirs(path, exist_ok=True)
        file_path=path+FILE_UPLOAD.secure_filename(f,random_ids=random_ids) if (path[-1]=="/" or path[-1]=="\\") else (path+'/'+FILE_UPLOAD.secure_filename(f,random_ids=random_ids) if sys.platform.startswith('win')==False else path+'\\'+FILE_UPLOAD.secure_filename(f,random_ids=random_ids))    
        f.save(file_path)
        return file_path


class FORM_INPUTS:

    @staticmethod
    def alphabet(s,length=(1,25)):
        return all(x.isalpha() for x in s.strip().split()) and (len(s.strip())<=length[1] and len(s.strip())>=length[0])

    @staticmethod
    def alphanumeric(s,length=(1,25)):
        return all(x.isalnum() for x in s.strip().split()) and (len(s.strip())<=length[1] and len(s.strip())>=length[0])

    @staticmethod
    def numeric(s,length=(1,15)):
        return all(x.isnumeric() for x in s.strip().split()) and (len(s.strip())<=length[1] and len(s.strip())>=length[0])

    @staticmethod
    def email(s,regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',length=(6,25)):
        return True if (re.fullmatch(regex, s.strip()) and (len(s.strip())<=length[1] and len(s.strip())>=length[0])) else False

    @staticmethod
    def password(s,length=(6,25)):
        return (len(s.strip())<=length[1] and len(s.strip())>=length[0])

    @staticmethod
    def passwords_match(a,b,length=(6,25)):
        return FORM_INPUTS.password(a,length=length) and FORM_INPUTS.password(b,length=length) and a==b

    @staticmethod
    def regex_match(s,rg,length=(1,25)):
        return True if (re.fullmatch(rg, s.strip()) and (len(s.strip())<=length[1] and len(s.strip())>=length[0])) else False

    @staticmethod
    def phone_number(s,length=(8,15),replace_mines=True):
        return s.strip()[0]=="+" and FORM_INPUTS.numeric(s.strip()[1:] if replace_mines==False else s.strip()[1:].replace('-',' '),length=length)


class PATH_TRAVERSAL:

    @staticmethod
    def check(path,files_location=''):
        return os.path.realpath(files_location+path).startswith(os.getcwd())


class RCE:

    safe_command_characters=["-","+","/","*","_",",","'",'"','.','\\',':',"#","!","?","%","[","]","{","}","=","~","<",">","^"]
    safe_eval_characters=["-","+","/","*","%",".","(","[","]",",","{","}","=","<",">","'",'"','!',':']
    
    @staticmethod
    def command(cmd,length=(1,100),replaced_value=" "):
        for x in RCE.safe_command_characters:
            cmd=cmd.replace(x,replaced_value)
        return FORM_INPUTS.alphanumeric(cmd,length=length)

    @staticmethod
    def eval(cmd,length=(1,20),replaced_value=" "):
        for x in RCE.safe_eval_characters:
            cmd=cmd.replace(x,replaced_value)
        return FORM_INPUTS.alphanumeric(cmd,length=length)

class SSRF:
    
    possible_protocols=["http://","https://"]

    @staticmethod
    def validate(adr):
        adr=adr.split(":")[0] if adr.startswith(tuple(SSRF.possible_protocols))==False else adr.split("://")[1].split('/')[0].split(":")[0]
        try:
            a=socket.gethostbyname(adr.split(':')[0]).split('.')
        except:
            return False
        f=[169,172,198,192]
        o1=int(a[0])
        o2=int(a[1])
        if o1 in [127,10,0]:
            return False
        if o1 in f:
            if ((o1==192)and(o2==168)):
                return False
            if ((o1==172)and((o2>15)and(o2<33))):
                return False
            if((o1==100)and(o2==64)):
                return False
            if((o1==169)and (o2==254)):
                return False
            if((o1==198)and(o2==18)):
                return False
        else:
            return True
        return True