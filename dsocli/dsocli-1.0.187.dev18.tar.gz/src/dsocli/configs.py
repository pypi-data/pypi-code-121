
import os
from pickletools import read_uint1
import re
import sys
import imp
from functools import reduce
from urllib import response
from .constants import *
from .logger import Logger
from .dict_utils import *
from pathlib import Path
from .file_utils import *
from .exceptions import DSOException
from .stages import Stages
from .contexts import Context, ContextScope, ContextMode
from .enum_utils import OrderedEnum
from .remote_configs import RemoteConfig


class ConfigOrigin(OrderedEnum):
    All = 10
    Local = 20
    Remote = 30


_init_config = {
    'kind': 'dso/application',
    'version': 1,
    'namespace': 'generic',
    'application': '',
    'config': {
        'provider': {
            'id': 'local/v1',
            'spec': {}
        },
    },
    'parameter': {
        'provider': {
            'id': 'local/v1',
            'spec': {}

        },
    },
    'secret': {
        'provider': {
            'id': 'shell/v1',
            'spec': {}

        },
    },
    'template': {
        'provider': {
            'id': 'local/v1',
            'spec': {}

        },
    },    
}

_default_config = {
    'kind': 'dso/application',
    'version': 1,
    'namespace': 'generic',
    'application': '',
    'config': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'parameter': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'secret': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'template': {
        'provider': {
            'id': '',
            'spec': {}
        },
        'renderPath': {}
    },
    'artifactory': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'package': {
        'provider': {
            'id': '',
            'spec': {},
            'essential' : [],
            'optional': []
        },
    },
    'release': {
        'provider': {
            'id': '',
            'spec': {},
            'essential' : [],
            'optional': []
        },
    },
    'network':{
        'subnetPlanGroup': '',
        'subnetPlan': '',
        'selector': {}
    }, 

}

all_services = ['config', 'parameter', 'secret', 'template', 'artifactory', 'package', 'release']


def get_init_config():
    return _init_config.copy()


def get_default_config():
    return _default_config.copy()


class ConfigService:
    @property
    def config_dir(self):
        return '.dso'

    @property
    def config_file(self):
        return 'dso.yml'

    @property
    def install_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    context = Context() 
    original_context = Context()
    working_dir = ''
    local_config = {}
    local_config_rendered = {}
    local_config_file_path = ''
    local_config_dir_path = ''
    root_config = {}
    root_config_rendered = {}
    root_config_file_path = ''
    root_config_dir_path = ''
    overriden_config = {}
    merged_config = {}
    remote_config = {}
    remote_config_rendered = {}


    def load(self, working_dir, config_overrides_string='', stage=None, scope=ContextScope.App, ignore_errors=False):

        if stage is None: stage = 'default'
        stage = Stages.normalize(stage)

        self.working_dir = working_dir

        ### start off with given stage, scope, and overriden config to set meta_data for subsequent rendering
        self.context = Context('default', 'default', stage, scope)
        self.apply_config_overrides(config_overrides_string)

        ### load root and local configs only without rendering
        self.load_root_config(render=False)
        self.load_local_config(render=False)
        
        if not ignore_errors:
            if not self.merged_config['namespace']:
                raise DSOException("Namespace has not been set. Run 'dso config set namespace <name>' to do so.")
            if self.merged_config['namespace'] == 'default':
                raise DSOException("Namespace name cannot be 'default'.")
            if scope == ContextScope.Namespace and not Stages.is_default_env(stage):
                raise DSOException("Numbered environments are not allowd when using the namespace scope (for simplicity). Remove the number from the given satge and try again.")
            if scope == ContextScope.Global and not Stages.is_default_env(stage):
                raise DSOException("Numbered environments are not allowd when using the root scope (for simplicty). Remove the number from the given satge and try again.")

            if not self.merged_config['application']:
                raise DSOException("Application name has not been set. Run 'dso config set application <name>' to do so.")
            if self.merged_config['application'] == 'default':
                raise DSOException("Application name cannot be 'default'.")

            self.check_version()


    @property
    def meta_vars(self):
        return {'dso': self.merged_config}

    def apply_config_overrides(self, config_overrides):
        self.overriden_config = {}
        if config_overrides:
            if isinstance(config_overrides, str):
                config_overrides = self.config_string_to_dict(config_overrides)
            configs = flatten_dict(config_overrides)           
            not_alllowed_configs = ['stage', 'scope']  ### read-only configs
            check_default_configs = ['namespace', 'application']
            for key, value in configs.items():
                if key in not_alllowed_configs:
                    Logger.warn(f"Ignored overriding configuration '{key}', the following DSO configuration settings cannot be overriden: {not_alllowed_configs}")
                if key in check_default_configs: value = value or 'default'
                Logger.debug(f"DSO configuration '{key}' was overriden to '{value}'.")
                set_dict_value(self.overriden_config, key.split('.'), value)

        self.update_merged_config()

    def load_root_config(self, render=True):
        self.root_config = {}
        self.root_config_rendered = {}
        self.root_config_dir_path = os.path.join(Path.home(), self.config_dir)
        self.root_config_file_path = os.path.join(self.root_config_dir_path, self.config_file)

        if not os.path.exists(self.root_config_file_path):
            Logger.debug("Root configuration not found.")
            return

        Logger.debug(f"Root configuration found: path={self.root_config_file_path}")
        try:
            self.root_config = load_file(self.root_config_file_path)
        except DSOException:
            raise
        except:
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.root_config_file_path))

        if render:
            self.render_root_config()
        else:
            self.root_config_rendered = self.root_config.copy()

        self.update_merged_config()


    def load_local_config(self, silent_warnings=False, render=False):
        self.local_config = {}
        self.local_config_rendered = {}
        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)

        if not os.path.exists(self.local_config_file_path):
            if not silent_warnings: Logger.warn(MESSAGES['NoDSOConfigFound'])
            return

        Logger.debug(f"Local configuration found: path={self.local_config_file_path}")

        try:
            self.local_config = load_file(self.local_config_file_path)
        except DSOException:
            raise
        except:
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.local_config_file_path))

        if render:
            self.render_local_config()
        else:
            self.local_config_rendered = self.local_config.copy()

        self.update_merged_config()


    def load_remote_config(self, uninherited=False, filter=None):
        self.remote_config = {}
        self.remote_config = deflatten_dict({x['Key']: x['Value'] for x in RemoteConfig.list(uninherited=uninherited, filter=filter)})
        self.update_merged_config()


    def render_root_config(self, silent=False):
        ### call update using not rendered config for in-place rendering of the root config iteself
        self.update_merged_config(rendered=False)
        ### now do the rendering
        # self.root_config_rendered = load_file(self.root_config_file_path, pre_render_values=self.merged_config)
        self.root_config_rendered = render_dict_values(self.root_config, values=self.merged_config, silent=silent)
        # self.update_merged_config()


    def render_local_config(self, silent=False):
        ### call update using not rendered config for in-place rendering of the root config iteself
        self.update_merged_config(rendered=False)
        ### now do the rendering
        # self.local_config_rendered = load_file(self.local_config_rendered, pre_render_values=self.merged_config)
        self.local_config_rendered = render_dict_values(self.local_config, values=self.merged_config, silent=silent)
        # self.update_merged_config()


    def render_remote_config(self, silent=False):
        ### call update using not rendered config for in-place rendering of the remote config iteself
        self.update_merged_config(rendered=False)
        ### now do the rendering
        # self.local_config_rendered = load_file(self.local_config_rendered, pre_render_values=self.merged_config)
        self.remote_config_rendered = render_dict_values(self.remote_config, values=self.merged_config, silent=silent)
        # self.update_merged_config()


    def dict_to_config_string(self, dic):
        flat = flatten_dict(dic)
        return reduce(lambda x, y: f"{x[0]}={x[1]},{y[0]}={y[1]}", flat)


    def config_string_to_dict(self, config_string):
        if not config_string: return {}

        result = {}
        try:
            configs = config_string.split(',')
            for config in configs:
                if not config: continue
                key = config.split('=')[0].strip()
                value = config.split('=')[1].strip()
                set_dict_value(result, key.split('.'), value)
        except:
            raise DSOException(MESSAGES['InvalidDSOConfigOverrides'].format(config_string))

        return result

    def update_merged_config(self, use_defaults=True, use_calculated=True, use_root=True, use_local=True, use_remote=True, rendered=False):
        self.merged_config = {}
        if use_defaults:
            self.merged_config = get_default_config()

        if use_remote:
            if rendered:
                self.render_remote_config()                
                merge_dicts(self.remote_config_rendered, self.merged_config)
            else:
                merge_dicts(self.remote_config, self.merged_config)                
        if use_root:
            if rendered:
                self.render_root_config()
                merge_dicts(self.root_config_rendered, self.merged_config)
            else:
                merge_dicts(self.root_config, self.merged_config)                
        if use_local:
            if rendered:
                self.render_local_config()
                merge_dicts(self.local_config_rendered, self.merged_config)
            else:
                merge_dicts(self.local_config, self.merged_config)                
        
        if use_defaults:
            ### save provider ids set in app config before merging with service providers' default config
            saved_service_providers = {}
            for service in all_services:
                pid = self.get_provider_id(service)
                if pid:
                    saved_service_providers[service] = {
                        'id' : pid,
                        'spec' : self.get_provider_spec(service)
                    }

            ### add missing default specs for each service
            for service in all_services:
                pid = self.get_provider_id(service)
                if pid:
                    ### merge saved spec with the default if only same provider
                    if saved_service_providers[service]['id'] == pid:
                        self.merged_config[service]['provider']['spec'] = self.get_provider_default_spec(service, pid)
                        merge_dicts(saved_service_providers[service]['spec'], self.merged_config[service]['provider']['spec'])
                    else:
                        self.merged_config[service]['provider']['spec'] = self.get_provider_default_spec(service, pid)

        ### always apply provided overriding configs
        merge_dicts(self.overriden_config, self.merged_config)

        ### update context
        self.context = Context(self.merged_config.get('namespace', ''), self.merged_config.get('application', ''), self.stage, self.scope)

        ### add calculated configs on the fly at last
        if use_calculated:
            self.merged_config['context'] = {
                'effective': {
                    'namespace': self.namespace,
                    'application': self.application,
                    'stage': self.short_stage,
                    'env': self.env,
                    'scope': str(self.scope)
                },
                'target': {
                    'namespace': self.get_namespace(ContextMode.Target),
                    'application': self.get_application(ContextMode.Target),
                    'stage': self.get_stage(ContextMode.Target, short=True),
                    'env': Stages.parse_env(self.get_stage(ContextMode.Target)),
                    'scope': str(self.scope)
                },
            }
            self.merged_config['stage'] = self.get_stage(ContextMode.Target, short=True)
            self.merged_config['env'] = Stages.parse_env(self.get_stage(ContextMode.Target))
            self.merged_config['scope'] = str(self.scope)


    def check_version(self):
        if not int(self.merged_config['version']) == int(_default_config['version']):
            if int(self.merged_config['version']) > int(_default_config['version']):
                Logger.warn(MESSAGES['DSOConfigNewer'].format(_default_config['version'], self.merged_config['version']))
            else:
                Logger.warn(MESSAGES['DSOConfigOlder'].format(_default_config['version'], self.merged_config['version']))


    def get_provider_default_spec(self, provider, provider_id):
        if f'{provider}/{provider_id}' in sys.modules:
            provider = sys.modules[f'{provider}/{provider_id}']
        else:
            providerPackagePath = os.path.join(self.install_path, 'provider', f'{provider}/{provider_id}')
            if not os.path.exists(providerPackagePath):
                raise DSOException(f"Provider '{provider}/{provider_id}' not found.")
            provider = imp.load_package(f'{provider}/{provider_id}', providerPackagePath)
        
        return provider.get_default_spec()


    def save_local_config(self):
        os.makedirs(self.local_config_dir_path, exist_ok=True)
        save_data(self.local_config, self.local_config_file_path)

    def save_root_config(self):
        os.makedirs(self.root_config_dir_path, exist_ok=True)
        save_data(self.root_config, self.root_config_file_path)


    @property
    def namespace(self):
        return self.get_namespace()

    def get_namespace(self, source=ContextMode.Effective):
        if source == ContextMode.Target:
            result = self.context.target[0]
        elif source == ContextMode.Effective:
            result = self.context.effective[0]
        
        return result


    @property
    def application(self):
        return self.get_application()


    def get_application(self, source=ContextMode.Effective):
        if source == ContextMode.Target:
            result = self.context.target[1]
        elif source == ContextMode.Effective:
            result = self.context.effective[1]
        
        return result


    @property
    def stage(self):
        return self.get_stage()

    def get_stage(self, source=ContextMode.Effective, short=False):
        if source == ContextMode.Target:
            result = self.context.target[2]
        elif source == ContextMode.Effective:
            result = self.context.effective[2]
        
        if short:
            result = Stages.shorten(result)
        else:
            result = Stages.normalize(result)
        
        return result

    @property
    def short_stage(self):
        return self.get_stage(short=True)

    @property
    def env(self):
        return Stages.parse_env(self.get_stage())


    @property
    def scope(self):
        return self.context.scope


    def get_provider_id(self, service):
        try:
            result = self.merged_config[service]['provider']['id'] or os.getenv(f"DSO_{service.upper()}_PROVIDER")
        except:
            raise DSOException(f"Invalid dso configuration schema: {service}")
        return result

    @property
    def config_provider(self):
        return self.get_provider_id('config')

    @property
    def parameter_provider(self):
        return self.get_provider_id('parameter')

    @property
    def secret_provider(self):
        return self.get_provider_id('secret')

    @property
    def template_provider(self):
        return self.get_provider_id('template')

    @property
    def artifactory_provider(self):
        return self.get_provider_id('artifactory')

    @property
    def package_provider(self):
        return self.get_provider_id('package')


    @property
    def release_provider(self):
        return self.get_provider_id('release')


    def get_provider_spec(self, service, key=None):
        try:
            result = self.merged_config[service]['provider']['spec']
        except KeyError:
            raise DSOException("Invalid dso configuration schema.")
        if not key:
            return result
        elif key in result:
            return result[key]
        else:
            return ''

    def config_spec(self, key=None):
        return self.get_provider_spec('config', key)

    def parameter_spec(self, key=None):
        return self.get_provider_spec('parameter', key)

    def secret_spec(self, key=None):
        return self.get_provider_spec('secret', key)

    def template_spec(self, key):
        return self.get_provider_spec('template', key)

    def artifactory_spec(self, key):
        return self.get_provider_spec('artifactory', key)

    def package_spec(self, key):
        return self.get_provider_spec('package', key)

    def network(self, key=None):
        try:
            result = self.merged_config['network']
        except KeyError:
            raise DSOException("Invalid dso configuration schema.")
        if not key:
            return result
        elif key in result:
            return result[key]
        else:
            return ''

    def get_template_render_paths(self, key=None):
        result = get_dict_item(self.local_config, ['template', 'renderPath']) or {}
        if not key:
            return result
        else:
            return {x:result[x] for x in result if x==key}

    def register_template_custom_render_path(self, key, render_path):
        result = get_dict_item(self.local_config, ['template', 'renderPath']) or {}
        # if os.path.isabs(render_path):
        #     raise DSOException(MESSAGES['AbsTemplateRenderPath'].format(render_path))
        # if os.path.isdir(render_path):
        #     raise DSOException(MESSAGES['InvalidRenderPathExistingDir'].format(render_path))
        result[key] = render_path
        self.local_config['template']['renderPath'] = result
        self.save_local_config()

    def unregister_template_custom_render_path(self, key):
        result = get_dict_item(self.local_config, ['template', 'renderPath'])
        if key in result:
            self.local_config['template']['renderPath'].pop(key)
            self.save_local_config()


    def init(self, working_dir, custom_init_config, config_overrides_string, override_inherited=False):
        Logger.info("Initializing DSO configurations...")
        self.working_dir = working_dir
        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)
        self.root_config_dir_path = os.path.join(Path.home(), self.config_dir)
        self.root_config_file_path = os.path.join(self.root_config_dir_path, self.config_file)

        # if config_scope == ConfigScope.Local:
        if os.path.exists(self.local_config_file_path):
            Logger.warn("The working directory has already been initialized.")

        config = get_init_config()
        
        ### use init_config instead of local/inherited config
        if custom_init_config:
            merge_dicts(custom_init_config, config)
            ### merge with existing local configuration?
            # if override_inherited:
            #     Logger.debug("Merging local configuration...")
            #     self.load_local_config(silent_warnings=True, render=False)
            #     merge_dicts(self.local_config, config)
            Logger.debug("Merging exisintg configuration...")
            self.load_local_config(silent_warnings=True, render=False)
            merge_dicts(self.local_config, config)
        else:
            ### override locally inherited configuration?
            if override_inherited: 
                Logger.debug("Merging root configuration...")
                self.load_root_config(render=False)
                merge_dicts(self.root_config, config)

                # Logger.debug("Merging inherited configuration...")
                # self.load_inherited_config(render=False)
                # merge_dicts(self.inherited_config, config)
            
            ### do not show warning if directory is not initialized yet
            Logger.debug("Merging existing configuration...")
            self.load_local_config(silent_warnings=True, render=False)
            merge_dicts(self.local_config, config)

        ### if config overrides, merge them to local
        if config_overrides_string:
            Logger.debug("Merging configuration overrides...")
            self.apply_config_overrides(config_overrides_string)
            merge_dicts(self.overriden_config, config)

        self.local_config = config
        self.update_merged_config()

        self.save_local_config()


    def list_local(self, filter=None):
        self.update_merged_config(use_remote=False) 
        response = flatten_dict(self.merged_config)
        result = []
        for key, value in response.items():
            if filter and not re.match(filter, key): continue
            item = {
                'Key' : key,
                'Value': value,
                'Context': 'local',
                'Path': os.path.join(self.config_dir, self.config_file)
            }
            result.append(item)

        return result
    
    def list_remote(self, uninherited=False, filter=None):
        if self.config_provider:
            response = RemoteConfig.list(uninherited=uninherited, filter=filter)
        else:
            Logger.warn("Remote configiguration is not availbale because config provider has not been set.")
            response = []
        return response


    def list(self, uninherited=False, filter=None, rendered=False, source=ConfigOrigin.All):
        Logger.info(f"Listing configuration settings: namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
        if source == ConfigOrigin.Local:  
            response = self.list_local(filter=filter)
        elif source == ConfigOrigin.Remote:
            response = self.list_remote(uninherited=uninherited, filter=filter)
        elif source == ConfigOrigin.All:
            local_response = self.list_local(filter=filter)
            response = self.list_remote(uninherited=uninherited, filter=filter)
            key_index = {response[i]['Key']:i for i in range(len(response))}
            for item in local_response:
                if item['Key'] in key_index:
                    response[key_index[item['Key']]] = item
                    Logger.warn(f"'{item['Key']}' was overriden locally.")
                else:
                    response.append(item)

        if rendered:
            self.load_remote_config()
            self.load_root_config()
            self.load_local_config()
            response = render_dict_values(response, self.merged_config)

        from operator import itemgetter
        return {'Configuration': sorted(response, key=itemgetter('Key'))}


    def add(self, key, value, source=ConfigOrigin.Local):
        Logger.info(f"Adding configuration setting '{key}': namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
        if source == ConfigOrigin.Local:
            if not os.path.exists(self.local_config_file_path):
                raise DSOException("The working directory has not been intitialized yet. Run 'dso config init' to do so.")
            key = set_dict_value(self.local_config, key.split('.'), value, overwrite_parent=False, overwrite_children=False)
            self.save_local_config()
            return {
                'Key' : key,
                'Value' : value,
                'Context': 'local',
                'Path': os.path.join(self.config_dir, self.config_file)
            }            
            # self.load_local_config(render=False)
        elif source == ConfigOrigin.Remote:
            return RemoteConfig.add(key=key, value=value)
        else:
            raise NotImplementedError()



    def get_local(self, key):
        self.update_merged_config(use_remote=False)
        response = get_dict_item(self.merged_config, key.split('.'), create=False, leaf_only=True)
        if response:
            return {
                'Key' : key,
                'Value' : response,
                'Context': 'local',
                'Path': os.path.join(self.config_dir, self.config_file)
            }
        else:
            return {}

    def get_remote(self, key, revision, uninherited=False):
        result = RemoteConfig.get(key=key, revision=revision, uninherited=uninherited)
        if not result:
            raise DSOException(f"Configuration setting '{key}' not found in the given context: namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
        return result


    def get(self, key, revision=None, uninherited=False, rendered=True, source=ConfigOrigin.All):
        Logger.info(f"Getting configuration setting '{key}': namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
        if source == ConfigOrigin.All:
            result = self.get_local(key)
            if not result:
                Logger.debug(f"Configuration setting '{key}' not found locally.")   
                if self.config_provider:
                    result = self.get_remote(key=key, revision=revision, uninherited=uninherited)
                    if not result:
                        raise DSOException(f"Configuration setting '{key}' not found in the given context: namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
                else:
                    Logger.warn("Remote configiguration is not availbale because config provider has not been set.")
                    result = {}
        elif source == ConfigOrigin.Local:
            result = self.get_local(key)
            if not result:
                raise DSOException(f"Configuration setting '{key}' not found locally.")   
        elif source == ConfigOrigin.Remote:
            result = self.get_remote(key=key, revision=revision, uninherited=uninherited)

        if result and rendered:
            ### load everything for rendering purpose only
            self.load_remote_config()
            self.load_root_config()
            self.load_local_config()
            self.update_merged_config()
            result['Value'] = render_dict_values(result['Value'], values=self.merged_config, silent=False)

        return result
            

    def delete_remote(self, key):
        return RemoteConfig.delete(key=key)


    def delete_local(self, key):
        parent = get_dict_item(self.local_config, key.split('.')[:-1])
        lastKey = key.split('.')[-1]
        if parent and type(parent) in [dict, list, tuple] and lastKey:
            value = get_dict_item(dic=self.local_config, keys=key.split('.'), create=False, leaf_only=True)
            if value is None:
                raise DSOException(f"'{key}' not found in configuration settings locally.")
            del_dict_item(dic=self.local_config, keys=key.split('.'), leaf_only=True, silent=False)
            del_dict_empty_item(dic=self.local_config, keys=key.split('.')[:-1])
            self.save_local_config()
            self.load_local_config(render=False)
        else:
            raise DSOException(f"'{key}' not found in configuration settings locally.")
        
        return {
            'Key' : key,
            'Value': value,
            'Context': 'local',
            'Path': os.path.join(self.config_dir, self.config_file)
        }   
        

    def delete(self, key, source=ConfigOrigin.Local):
        Logger.info(f"Deleting configuration setting '{key}': namespace={self.get_namespace(ContextMode.Target)}, application={self.get_application(ContextMode.Target)}, stage={self.get_stage(ContextMode.Target)}, scope={self.scope}")
        if source == ConfigOrigin.Local:
            return self.delete_local(key)
        elif source == ConfigOrigin.Remote:
            return self.delete_remote(key)
        else:
            raise NotImplementedError()
  

Config = ConfigService()

