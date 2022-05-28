
import os
import re
import jinja2
from jinja2 import meta
from .constants import *
from .providers import KeyValueStoreProvider, Providers
from .parameters import Parameters
from .secrets import Secrets
from .logger import Logger
from .dict_utils import merge_dicts, deflatten_dict
from .exceptions import DSOException
from .stages import Stages
from .configs import Config, ContextMode


key_regex_pattern = r"^[a-zA-Z]([./a-zA-Z0-9_-]*[a-zA-Z0-9])?$"

class TemplateProvider(KeyValueStoreProvider):
    def list(self, uninherited=False, include_contents=False, filter=None):
        raise NotImplementedError()
    def add(self, key, contents, render_path):
        raise NotImplementedError()
    def get(self, key, revision=None):
        raise NotImplementedError()
    def history(self, key, include_contents=False):
        raise NotImplementedError()
    def delete(self, key):
        raise NotImplementedError()


class TemplateService():
    
    @property
    def default_render_path(self):
        return Config.working_dir

    def validate_key(self, key):
        Logger.info(f"Validating template key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(key_regex_pattern, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, key_regex_pattern))
        ### the regex does not check adjacent special chars
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

        if '//' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '//'))

    def get_template_render_path(self, key):
        result = Config.get_template_render_paths(key)
        if result:
            return result[key]

        return f'.{os.sep}' + os.path.relpath(os.path.join(self.default_render_path, key), Config.working_dir) 

    def get_all_params(self, silent=False):
        if not silent:
            Logger.info("Loading secrets...")
        secrets = Secrets.list(uninherited=False, decrypt=True)
        if not silent:
            Logger.info("Loading parameters...")
        parameters = Parameters.list(uninherited=False)
        merged = deflatten_dict({x['Key']: x['Value'] for x in secrets['Secrets']})
        merge_dicts(deflatten_dict({x['Key']: x['Value'] for x in parameters['Parameters']}), merged)
        merge_dicts(Config.meta_vars, merged)
        return merged


    def list(self, uninherited=False, include_contents=False, filter=None):
        provider = Providers.TemplateProvider()
        Logger.info(f"Listing templates: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        response = provider.list(uninherited, include_contents, filter)
        for template in response:
            key = template['Key']
            template['RenderPath'] = self.get_template_render_path(key)
        from operator import itemgetter
        return {'Templates': sorted(response, key=itemgetter('Key'))}        
        
        return response

    def add(self, key, contents, render_path):
        self.validate_key(key)
        provider = Providers.TemplateProvider()
        Logger.info(f"Adding template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        Logger.debug(f"Template: key={key}, render_path={render_path}")
        result = provider.add(key, contents)
        result['RenderPath'] = render_path
        if os.path.abspath(render_path) == os.path.abspath(os.path.join(self.default_render_path, key)):
            Config.unregister_template_custom_render_path(key)
        else:
            Config.register_template_custom_render_path(key, render_path)
        return result

    def get(self, key, revision=None, rendred=True):
        provider = Providers.TemplateProvider()
        Logger.info(f"Getting template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        result = provider.get(key, revision)
        if rendred:
            Logger.info("Rendering...")
            template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(result['Contents'])
            result['Contents'] = template.render(self.get_all_params())
        result['RenderPath'] = self.get_template_render_path(key)
        return result

    def history(self, key, include_contents=False):
        provider = Providers.TemplateProvider()
        Logger.info(f"Fetching history of template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.history(key, include_contents)

    def delete(self, key):
        provider = Providers.TemplateProvider()
        Logger.info(f"Deleting template '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        result = provider.delete(key)
        Config.unregister_template_custom_render_path(key)
        return result

    def render(self, filter=None):

        Logger.info(f"Rendering templates: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")

        merged = self.get_all_params()
        
        Logger.info("Loading templates...")
        templates = self.list(filter=filter)['Templates']

        loader = jinja2.FileSystemLoader(Config.working_dir)
        jinja_env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)

        rendered = []
        if len(templates) == 0:
            Logger.warn("No template found to render.")
            return rendered

        Logger.info("Rendering templates...")
        for template in templates:
            key = template['Key']

            renderPath = template['RenderPath']
            if os.path.isdir(renderPath):
                raise DSOException("There is an existing directory at the template render path '{renderPath}'.")
            if os.path.dirname(renderPath):
                os.makedirs(os.path.dirname(renderPath), exist_ok=True)

            try:
                jinjaTemplate = jinja_env.from_string(self.get(key, rendred=False)['Contents'])
            except:
                Logger.error(f"Failed to load template: {key}")
                raise
            # undeclaredParams = jinja2.meta.find_undeclared_variables(env.parse(template))
            # if len(undeclaredParams) > 0:
            #     Logger.warn(f"Undecalared parameter(s) found:\n{set(undeclaredParams)}")
            try:
                Logger.debug(f"Rendering template: key={key}, render_path={renderPath}")
                if len(loader.searchpath) > 1: loader.searchpath.pop(-1)
                loader.searchpath.append(os.path.dirname(os.path.join(Config.working_dir, renderPath)))
                renderedContent = jinjaTemplate.render(merged)
            
            except Exception as e:
                Logger.error(f"Failed to render template: {key}")
                msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
                raise DSOException(msg)

            with open(renderPath, 'w', encoding='utf-8') as f:
                f.write(renderedContent)
            
            rendered.append({
                        'Key':key, 
                        'Scope': template['Scope'],
                        # 'Context': template['Context'],
                        'RenderPath': renderPath,
                        })

        return rendered


Templates = TemplateService()