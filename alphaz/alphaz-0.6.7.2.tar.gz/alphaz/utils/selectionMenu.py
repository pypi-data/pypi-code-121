'''
Created on 24 juin 2018

@author: aurele
'''
import re, os, copy, traceback

from ..libs.converter_lib import to_int
from ..libs import py_lib, io_lib
from .logger import AlphaLogger

def reload_modules():
    reload_path = os.getcwd()
    #print('Reload modules at %s'%reload_path)
    py_lib.reload_modules(reload_path)
    reload_path = os.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-1])
    #print('Reload modules at %s'%reload_path)
    py_lib.reload_modules(reload_path)

def replace_name(name):
    return name.lower().replace(' ','_')

class SelectionMenu():
    name            = None
    save_directory  = None
    level           = 0
    commands        = []
    selected        = []
    selected_history= []
    record          = False
    in_command      = False
    sequence        = []

    def __init__(self, name, parameters, save_directory, config_file=None, config_folder='config/menus',log=None):
        if log is None:
            log = core.get_logger()

        self.name           = name
        self.save_directory = save_directory

        self.parameters     = parameters        
        self.returnValue    = None

        self.exit           = False
        self.log            = log

        self.config_folder  = config_folder
        self.config_file    = config_file
        
        self.load_default_values()
        
    def debug_print(self,string):
        if self.get_value("debug_menu"):
            print(__name__,string)
        
    def run(self):
        while not self.exit:
            self.level = 0
            self.execute(self.parameters)
        return self.returnValue
        
    def execute(self,conf):
        conf = copy.copy(conf)

        if type(conf) == list:
            for sub_conf in conf:
                self.execute(sub_conf)
            return

        conf = self.convert_parameters(conf)

        if 'command' in conf:
            self.in_command = True

        try:
            reload_modules()

            if "before" in conf:        self.execute(conf["before"])

            # BETWEEN
            if 'set' in conf:
                for key, value in conf['set'].items():
                    self.set_value(key, value) #,convert=self.get_parameter_value(config,'convert'))

            if 'switch' in conf:
                if type(conf['switch']) == dict:
                    for key in conf['switch']:
                        self.switch_value(key)
                else:
                    self.switch_value(conf['switch'])

            self.functions_evaluate(conf)
            self.printEvaluate(conf)

            if "input" in conf:
                value                                       = input("\nValue: ")
                self.set_value(conf['set'], self.convert_value(value,convert=self.get_parameter_value(conf,'convert')) )

            if "quit" in conf or "exit" in conf:
                self.exit                                   = True

            # set returning value
            if 'return' in conf:
                self.returnValue                            = self.convert_value(conf['return'])

            # SELECTIONS
            
            if "selections" in conf:    
                self.level += 1
                self.select(conf["selections"])

            if "after" in conf:         self.execute(conf["after"]) 

            if "selections" in conf:
                if len(self.selected) >= 1:
                    self.selected = self.selected[:-1]
                self.level -=1

            if "pause" in conf:
                input('Press enter to continue ...')
        except:
            text    = traceback.format_exc()
            print('ERROR:\n\n',str(text))

        """if self.get_parameter_value(executingConfig,'bypass') is not None:
            conf                                      = executingConfig  
        else:
            conf                                      = self.select(executingConfig)"""
             
        #self.valueEvaluate(conf)
              
        ### SELECTION MENU  
        """if 'selection' in MODE:
            selectionValues                             = self.get_parameter_value(conf,'selection_values')
            multiple                                    = 'selections'  in MODE
            key_mode                                    = 'key'         in MODE
            #             selectionValues = self.get_parameter_value(conf,'selection_values')
            if selectionValues is not None:
                newConfig                               = self.get_config_from_values(conf,selectionValues,multiple=multiple,key_mode=key_mode)
            else:
                newConfig                               = conf['selection_config']"""
           
        if 'command' in conf:
            self.in_command = False

    def select(self,selections_config):
        selections_config       = copy.copy(selections_config)

        commands_selections     = self.get_commands()
        formatStr               = '{:7} {:40} {:30} {}'
        header                  = '   '*self.level

        conf     = {}
        selected = None
        while selected is None:
            self.debug_print('      VALUES:\n%s'%str('\n'.join(["   {:20}:{}".format(x,y) for x,y in self.values.items()])))
            i                       = 0
            selections              = {x['key']:x for x in commands_selections if 'key' in x}
        
            select_list             = copy.copy(commands_selections)
            select_list.extend(self.selected)
            select_list.extend(selections_config)

            for conf in select_list:
                if type(conf) == dict:
                    if "txt_selection" in conf:
                        print(conf['txt_selection'])
                        continue

                    desc                = self.get_string(conf,'description')
                    name                = self.get_string(conf,'name')

                    if "header" in conf:
                        print("\n"+header+formatStr.format("","== " + conf['header'] + " ==","",desc)+"\n")
                        continue

                    #activate            = conf['mode'] == 'activate' if 'mode' in conf.keys() else False
                    #self.debug_print("name - select configuration: %s"%conf)

                    #self.valueEvaluate(conf,start=True)
                    #self.functions_evaluate(conf,start=True)

                    key                 = conf['key'] if 'key' in conf.keys() else str(i)
                    
                    # DEFAULT VALUE
                    #if not self.get_parameter_value(conf, 'no_default'):
                    default         = "" if not 'name' in conf else self.get_value(conf['name'])
                    if default is None and 'value' in conf:
                        default     = conf['value']
                    elif default is None:
                        default     = ""

                    if type(default) == bool:
                        switch      = 'switch' in conf.keys()
                        if switch:
                            default = 'ON' if default else 'OFF'
                        else:
                            default = "Y" if default else "N"

                    """if 'mode' in conf.keys() and conf['mode'] == 'activate':
                        default = str(key) in str(default).split(',')"""
                                                                    
                    show = True
                    if 'show' in conf.keys():
                        show            = conf['show']
                        vshow           = self.get_value(show)
                        show            = vshow if vshow is not None else show
                        

                    txt = formatStr.format(str(key),name,str(default),desc)
                    if not key in self.commands:
                        txt = header + txt
                    conf['txt_menu'] = txt
                    if show:
                        print(txt)
                    
                    self.printEvaluate(conf)
                    
                    selections[key]     = conf

                    if not 'key' in conf:
                        i += 1
                else:
                    selections[str(i)]     = {"set":{'selected': conf},"txt_menu":header + formatStr.format(str(i),conf,"","")}
                    print(selections[str(i)]['txt_menu'])
                    i += 1

            if len(self.sequence) != 0:
                selection       = self.sequence[0]
                self.sequence   = self.sequence[1:]
            else:
                selection            = input("\nSelection > ").lower()

            is_command           = re.match("(^[^0-9]+$)", str(selection))
            if is_command:
                commands            = [x['key'] for x in select_list if 'key' in x]

                if selection in commands:
                    conf            = [x for x in select_list if 'key' in x and x['key'] == selection][0]
                else:
                    commandFounds   = 0
                    for command in commands:
                        m           = re.match("("+selection+"[^0-9]+$)", command.lower())
                        if m:
                            selection  = m.groups()[0]
                            commandFounds += 1
                            
                    if commandFounds != 1:
                        print('\n>>>> ERROR: command not recognized be more specific !')
                        continue
                    else:
                        conf          = selections[selection]
            else:
                if not selection in selections.keys():
                    continue
                
                """if activate:    
                    activated_values = str(self.values[conf['set']]).split(',')
                    
                    if str(selection) in activated_values:
                        activated_values.remove(str(selection))
                        self.values[conf['set']] = ','.join(activated_values)
                    else:
                        old                         = self.values[conf['set']]
                        self.values[conf['set']]  = str(old) + ',' + str(selection) if str(old) != '' else str(selection)
                        
                    print('SELECTED: %s'%self.values[conf['set']])
                    continue
                else:"""
                conf = selections[selection]

            selected = True
        
        sel = {'key':selection}

        if 'txt_menu' in conf:
            sel['txt_selection'] = conf['txt_menu']
        self.selected.append(sel)

        if not self.in_command and not 'command' in conf:
            print('\n                > Save action: %s\n'%str(conf))
            self.selected_history.append(sel)
        else:
            print('\n                > Not in command\n')

        self.execute(conf)

    def get_commands(self):
        selections = [
            {'header':"COMMANDS"},
            {
                'key': 'mo', 'name': 'Modes',
                "selections": [
                    {'key':'dm',"value":False,'switch':'debug_menu','name':'Debug menu','description':"Turn ON/OFF the menu debug mode"},
                    {'key':'d',"value":False,'name':'Debug','switch':'debug','description':"Turn ON/OFF the debug mode"},
                ]
            },
            {
                'key':'c','name':'Configuration','description':"Configuration menu",
                "selections": [
                    {'key':'s','function':self.save_config,'name':'Save configuration','description':"Save the current configuration"},
                    {'key':'r','function':self.reset_config,'name':'Reset configuration','description':"Reset the current configuration"},
                ]
            },
            {
                'key':'m',
                'name':'Memorize','description':"Memorize the last selection",
                "selections": [
                    {'name':'memorize','description':'Memorize actions','set':{'memorize_action':'memorize'}},
                    {'name':'view','description':'View memorized actions','set':{'memorize_action':'view'}},
                    {'name':'reset','description':'Reset memorized actions action','set':{'memorize_action':'reset'}},
                ],
                "after": {
                    "function":{
                        'method':self.memorize,"kwargs":{'action':'{{memorize_action}}'}
                    }
                }
            },
            {'key':'e',"function":self.execute_memorize,'name':'Execute','description':"Execute the last selection"},
            {'key':'v','name':'Values','function':self.show_values,'description':'Show values'},
            {'key':'r','name':'Reload','description':"Reload modules","function":reload_modules},
            {'key':'b','name':'Back','description':"Go back"},
            {'key':'q','function':self.quit,'name':'Quit','description':"Quit the menu"},
            {'header':"SELECTIONS"},
        ]

        self.commands = []
        for s in selections:
            if 'value' in s and 'name' in s and replace_name(s['name']) not in self.values:
                self.set_value(s['name'], s['value'])
            if 'key' in s:
                self.commands.append(s['key'])
            s['command'] = True

        return selections

    def set_value(self,name,value,convert=True):
        name                = replace_name(name)
        self.values[name]   = self.convert_value(value) if convert else value
        self.debug_print('   Set value %s to %s'%(name,self.values[name]))
        print('   Set value %s to %s'%(name,self.values[name]))

    def switch_value(self,name):
        name = replace_name(name)
        if name in self.values and type(self.values[name]) == bool:
            self.debug_print('   Switch value %s from %s to %s'%(name,self.values[name],not self.values[name]))
            self.values[name] = not self.values[name]

    def functions_evaluate(self,conf):
        functions_config = []
        if 'function' in conf:
            functions_config.append(conf['function'])
        if 'functions' in conf:
            functions_config.extend(conf['functions'])

        if len(functions_config) != 0:
            for config in functions_config:
                args, kwargs = [], {}
                if type(config) == dict:
                    if 'args' in config.keys():
                        raw_args                                    = config['args']
                        args                                        = self.convert_list(raw_args)
                    if  'kwargs' in config.keys():
                        raw_kwargs                                  = config['kwargs']
                        kwargs                                      = self.convert_dict(raw_kwargs)
                    
                    if 'method' in config.keys():
                        fct                                         = config['method']
                        fct                                         = self.convert_value(fct) if type(fct) == str else fct
                else:
                    fct = config

                if fct is not None:
                    self.debug_print('Exec fct %s with args %s and kwargs %s'%(fct,args,kwargs))
                    print('Exec fct %s with args %s and kwargs %s'%(fct,args,kwargs))
                    functionReturn = fct(*args,**kwargs)
                    print('      return: %s'%(functionReturn))
                    self.set_value('returned',functionReturn,convert=False)

                    if type(config) == dict and 'name' in config:
                        self.set_value(config['name'],functionReturn)
        
    def convert_list(self,args):
        convertedArgs = []
        for value in args:
            convertedArgs.append(self.convert_value(value))
        return convertedArgs

    def convert_dict(self,args):
        convertedArgs = {}
        for key, value in args.items():
            convertedArgs[key] = self.convert_value(value)
        return convertedArgs

    def convert_value(self,rawValue,convert=None):
        value = copy.copy(rawValue)
        
        if type(rawValue) == dict:
            for key, v in rawValue.items():
                value[self.convert_value(key)] = self.convert_value(v)
            return value
        if type(rawValue) == list:
            new_list = []
            for v in rawValue:
                new_list.append(self.convert_value(v))
            return new_list

        # List
        elementList = False
        regex   = "\[\d+\]"
        m       = re.search(regex, str(rawValue))
        if m is not None:
            group       = m.group(0)
            positionRaw = group.replace('[','').replace(']','')
            position    = self.convert_value(positionRaw,convert=int)
            rawValue    = rawValue.replace(group,'')
            elementList = True

        # Range
        regex   = "\[[\d*]:[\d*]\]"
        m       = re.search(regex, str(rawValue))
        if m is not None:
            values  = m.group(0).replace('[','').replace(']','').split(':')
            v1      = self.convert_value(values[0],convert=int)
            v2      = self.convert_value(values[1],convert=int)
            value   = range(v1,v2)
            return value
        
        # Call dynamically a method from this class
        if "self." in str(rawValue) and rawValue.replace('self','') in dir(self):
            value = getattr(self, rawValue)
        
        value = self.convert_parameters(value)

        #if elementList:
        #    print("%s > %s %s"%(rawValue,value,self.values.keys()))

        if elementList:
            value = value[position]
                
        if convert == int:
            convertion, ok = to_int(value)
            if ok:
                value = convertion

        return value

    def convert_parameters(self,value):
        if type(value) != str:
            return value

        for key, val in self.values.items():
            if '{{%s}}'%key == str(value):
                return val
            if '{{%s}}'%key in str(value):
                value = value.replace('{{%s}}'%key,str(val))
        return value

    def quit(self):
        print('   QUIT')
        self.exit = True
            
    def get_value(self,name):
        name = replace_name(name)
        if not name in self.values.keys():
            return None
        return self.convert_value(self.values[name])
    
    def is_parameter(self,conf,name):
        for key, value in conf.items():
            if replace_name(key) == name:
                return self.convert_value(value)
        return replace_name(name) in conf.keys()

    def get_parameter_value(self,conf,name):
        name = replace_name(name)
        if self.is_parameter(conf,name):
            for key, value in conf.items():
                if replace_name(key) == name:
                    return self.convert_value(value)
        return None
            
    def get_string(self,conf,name):
        key = replace_name(name)
        if key in conf.keys():
            return self.format_string(conf[name])
        return ''

    def format_string(self,conf):
        if type(conf) == str:
            return conf
        args = self.convert_dict(conf['values']).values()
        return conf['str'].format(*args)
                
    def save_config(self):
        filename = self.save_directory + os.sep + self.name
        io_lib.archive_object(self.values,filename)

    def reset_config(self):
        self.values = {}
        self.save_config()

    def memorize(self,action=None):
        if action == 'view':
            for selection in self.selected_history:
                print(selection)
        elif action == "memorize":
            self.values['memorized_selection'] = self.selected_history
            self.save_config()
        elif action == 'reset':
            self.selected_history = []

    def execute_memorize(self):
        self.sequence = [x['key'] for x in self.selected_history]

    def load_default_values(self):
        defaults            = {}
        filename            = self.save_directory + os.sep + self.name

        values              = None
        try:
            values          = io_lib.unarchive_object(filename)
        except:
            print('ERROR with configuration file')

        if values is not None:
            defaults        = values
        else:
            self.log.error("No default values are specified")

        self.values         = defaults
        self.defaultskeys   = list(defaults.keys())

        if 'memorized_selection' in self.values:
            self.selected_history = self.values['memorized_selection']
        
    def show_values(self):
        for key, value in self.values.items():
            print(f"Menu values: {key}: {value}")

    def printEvaluate(self,conf):
        pass
        """
        key                                             = 'print'

        parameters                                      = conf.keys()
        ### PRINT
        if key in parameters:
            output                                      = self.format_string(conf[key])
            print("\nOUTPUT: " + output + "\n")
            
        key                                             = 'infos'
        if key in parameters:
            output                                      = self.format_string(conf[key])
            print(output + "\n")
        """
                            
    """def get_config_from_values(self,valuesConfig,values,multiple=False,key_mode=False):
        parameters = valuesConfig.keys()
        
        choices = {}
        i = 0
        if not type(values) == dict:
            for value in values:
                choices[i] = value
                i += 1
        else:
            choices = values
        
        conf = {}
        for key, value in choices.items():
            subConfig = dict()

            subConfig['value']      = value
            subConfig['key']        = key
            subConfig['no_default'] = not multiple
            if key_mode:
                subConfig['set_key']    = True 
            if multiple:
                subConfig['mode']       = 'activate'

            conf[value] = subConfig
            self.debug_print("sub configuration %s"%subConfig.keys())
        return conf"""