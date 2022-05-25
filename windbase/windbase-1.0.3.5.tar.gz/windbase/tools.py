# /*
#  * @Author: Guofeng He 
#  * @Date: 2022-05-14 08:52:33 
#  * @Last Modified by:   Guofeng He 
#  * @Last Modified time: 2022-05-14 08:52:33 
#  */

#coding=utf-8


'''
    tools 常用的工具
'''



import argparse
import getpass
import hashlib
import logging
import os
import time
import webbrowser


import yaml



class Tools(object):
    @staticmethod
    def getvalue(dict,item):
        if dict.get(item,"") == "":
            dict.update({item:input("please input your %s:"%item)})
        return dict.get(item)

    @staticmethod
    def input_items(org_dict:dict,items:list)->dict:
        '''
        
        输入相应的参数

        Args:
            org_dict (dict): the dictionary of items
            items (list): should check items list

        Returns:
            dict: updated dict
        
        
        '''
        for item in items:
            if not org_dict.get(item,None):
                org_dict[item]=input("please input your %s:"%item)
        return org_dict

    @staticmethod
    def input_password(org_dict:dict,items:list,salt="misas")->dict:
        '''
        
        输入相应的参数

        Args:
            org_dict (dict): the dictionary of items
            items (list): should check items list

        Returns:
            dict: updated dict
        
        >>> d={}
        >>> Tools.input_password(d,["password"],salt="aijieofof")
        >>> d["password"]
        dlasf
        '''
        for item in items:
            if not org_dict.get(item,None):
                while True:
                    temps1 = getpass.getpass("please input your %s: "%item)
                    temps2 = getpass.getpass("confirm again: ")
                    if temps1==temps2:
                        md5_value = hashlib.md5((salt+temps1).encode('utf8')).hexdigest()
                        org_dict[item] = md5_value
                        break
                    print("input is not match!")

        return org_dict

    @staticmethod
    def get_config_from_args(options):
        config = {"brain_ip":options.brain_ip,"brain_port":int(options.brain_port),
                  "org_id":options.org_id,"node_id":options.node_id}
        return config
    @staticmethod
    def check_path(path):
        if os.path.exists(path):
            return True
        else:
            try:
                dir,filename = os.path.split(path)
                os.mkdir(dir)
                return True
            except:
                return False
    @staticmethod
    def is_private_addr(addr):
        ips = addr[0].split(".")
        if ips[0] in ["127","192","10","172","224"]:
            return True
        return False
    @staticmethod
    def waitting(status,flag,timeout=10):
        count = 0
        while count < timeout:
            if status[flag]:
                break
            time.sleep(0.5)
            count += 1
        return status[flag]
    @staticmethod    

    def has_id(data:dict,id_chain:list)->bool:
        '''
        check does  item in dictionary with given key chain lists ,

        Args:
            data (dict): source dictionary
            id_chain (list): id list, such as ["first_key","son_key","grandson_key" ...]

        Returns:
            bool: True = has id_chain key in data 
                  False = id_chain not in data
        '''
        return False if len(id_chain)==0 else id_chain[0] in data.keys() if len(id_chain) == 1 else Tools.has_id(data.get(id_chain[0],{}),id_chain[1:])

    @staticmethod    
    def valid(data:dict,key_list:list)->bool:
        '''
        check give keys in item_dict,and not empty

        Args:
            item_dict (dict): data should be dict 
            key_list (list): keys ,such as [”ke1","Key2",...]

        Returns:
            bool: True = valid if has key and value is not empty
                  False = not valid
        '''
        for key in key_list:
            if not data.get(key,None):
                return False
        return True

    @staticmethod    
    def get_by_id(dict:dict,id_chain:list):
        '''
        get item for dictionary with given key chain lists ,

        Args:
            dict (dict): source dictionary
            id_list (list): id list, such as ["first_key","son_key","grandson_key" ...]

        Returns:
            dict: the selected item
        '''
        return {} if len(id_chain)==0 else dict.get(id_chain[0],{}) if len(id_chain) <= 1 else Tools.get_by_id(dict.get(id_chain[0],{}),id_chain[1:]) 

    int2ip = lambda x: '.'.join([str(int(x / (256 ** i) % 256)) for i in range(3, -1, -1)])

    ip2int = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])

    @staticmethod
    def load_config(configfile):
        config = yaml.load(open(configfile,"r"),Loader=yaml.FullLoader)
        return  config
    @staticmethod
    def set_debug_log(level,logfilename):
        debug_format = "%(asctime)-15s %(levelname)s %(filename)s %(funcName)s %(lineno)d %(thread)d %(message)s"
        info_format = "%(asctime)-15s %(levelname)s %(message)s"
        Tools.check_path(logfilename)
        if level == logging.DEBUG:
            logging.basicConfig(level=logging.DEBUG,format=debug_format,filename=logfilename)
        if level == logging.INFO:
            logging.basicConfig(level=logging.INFO,format=info_format,filename=logfilename)
        return

    @staticmethod
    def set_debug(debug_level=logging.INFO, filename="",filter=lambda record:True):
        '''
        set debug mode

        Args:
            debug_level (_type_, optional): _description_. Defaults to logging.INFO.
            filename (str, optional): if no filename will debug info on console. Defaults to "".
            filter (_type_, optional): a lambda function . Defaults to lambdarecord:True.
        '''
        console = logging.StreamHandler()
        console_filter = logging.Filter()
        console_filter.filter = filter
        console.addFilter(console_filter)
        if filename:
            logging.basicConfig(level=debug_level,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=filename,
                    filemode='w',
                    )
        else:
            logging.basicConfig(level=debug_level,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    handlers = [console,]
                    )

    @staticmethod
    def get_arguments(arg_dict:dict)->dict:
        '''
        command line argment define and get value

        Args:
            arg_dict (dict): the argment define .
                             {argname1:{"short":"","long":"","default":"","help":"","type":"str|bool"},
                             argname2:{"short":"","long":"","default":"","help":""}}

        Returns:
            dict: the commandline arg value s {argname:value,argname:value}
        '''
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter )
        for argname,arginfo in arg_dict.items():
            
            action_type="store_true" if arginfo.get("type","str")=="bool" else None
            if arginfo.get("short",""):
                parser.add_argument(arginfo.get("short",""),arginfo.get("long","--"+argname),
                        help=arginfo.get("help",argname),default=arginfo.get("default",None),action=action_type)
            else:
                parser.add_argument(arginfo.get("long","--"+argname),
                        help=arginfo.get("help",argname),default=arginfo.get("default",None),action=action_type)
        argvalues =  parser.parse_args()
        value_dict = {}
        for argname in arg_dict.keys():
            value_dict[argname] =  getattr(argvalues,argname,None)

        return value_dict

    @staticmethod
    def parser_argument()->argparse.ArgumentParser:
        '''
        deprecated , please use Tools.get_arguments() instead!

        Returns:
            argparse.ArgumentParser: argparse.ArgumentParser
        '''
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter )
        parser.add_argument('-d', '--debug', action='store_true',
                            default=True,
                            help='Enable debug logging' )
        parser.add_argument('--daemon', action='store_true',
                            default=False,
                            help='daemon mode' )
        parser.add_argument('-o','--org_id',
                            default="org",
                            help='org id' )
        parser.add_argument('-n','--node_id',
                            default="",
                            help='node id' )
        parser.add_argument('-p', '--password',
                            default="",
                            help='password for node' )
        parser.add_argument('--vpn_user',
                            default="",
                            help='vpn user id' )
        parser.add_argument('--vpn_password',
                        default="",
                        help='password for vpn' )
        parser.add_argument('--tcp',action='store_true',
                            default=False,
                            help='tcp mode' )
        parser.add_argument('-f', '--config',
                            default="",
                            help='config file' )
        parser.add_argument('--server_port',
                            default=9000,
                            help='remote port' )
        parser.add_argument('--server_ip',
                            default="127.0.0.1",
                            help='remote ip' )
        parser.add_argument('--brain_ip',
                            default="14.29.201.19",
                            help='brain ip' )
        parser.add_argument('--brain_port',
                            default="54320",
                            help='brain port' )

        parser.add_argument('--version', action='version', version= "1.0")
        return parser

    @staticmethod
    def run_interactive(prompt,command_handle):
        command = "help"
        while not command == "quit yes":
            try:
                print(command_handle(command))
                print("\n%s>"%prompt,end="")
            except Exception as exp:
                logging.debug(exp.__str__())
            command=input()
        return False

    @staticmethod
    def browse_markdown(markdown_filename):
        md2html='\n<!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="markdeep.min.js" charset="utf-8"></script><script src="https://casual-effects.com/markdeep/latest/markdeep.min.js" charset="utf-8"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>'
        if not os.path.exists(markdown_filename+".html"):
            with open(markdown_filename,"rt",encoding="utf-8") as f:
                content = f.read()
            with open(markdown_filename+".html","wt") as f1:
                f1.write(content+md2html)
                f1.close()
        webbrowser.open(markdown_filename+".html")
        pass


if __name__ == '__main__':
    d = {}
    Tools.input_password(d,["password","token"])
    print(d)