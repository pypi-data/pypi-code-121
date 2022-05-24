from .constants import *
from .logger import Logger
from .dict_utils import *
from .file_utils import *
from .stages import Stages
from .constants import *
from .enum_utils import OrderedEnum


class ContextScope(OrderedEnum):
    App = 10
    Namespace = 20
    Global = 30

class ContextMode(OrderedEnum):
    Target = 10
    Effective = 30

context_translation_matrix = {
    'default': {
        'default': {
            'default': {
                '0': "Global",
            },
            'stage': {
                '0': "Global Stage",
                'n': "Global Numbered Stage",
            },
        }
    },
    'namespace': {
        'default': {
            'default': {
                '0': "Namespace",
            },
            'stage': {
                '0': "Namespace Stage",
                'n': "Namespace Numbered Stage",
            },
        },
        'application': {
            'default': {
                '0': "Application",
            },
            'stage': {
                '0': "Application Stage",
                'n': "Application Numbered Stage",
            },
        },
    }
}


# _default_config = {
#     'kind': 'dso/config',
#     'version': 1,
#     # 'namespace': 'default',
#     # 'application': 'default',
#     # 'stage': 'default',
#     'contexts': [
#         {
#             'name': 'default',
#             'spec': {
#                 'namespace': 'default',
#                 'application': 'default',
#                 'stage': 'default',
#             }
#         },
#     ],
# }


# def get_default_config():
#     return _default_config.copy()



class Context():

    _namespace = 'default'
    _application = 'default'
    _stage = Stages.default_stage
    _short_stage = Stages.short_default_stage
    _scope = ContextScope.App
    
    def __init__(self, namespace=None, application=None, stage=None, scope=None):
        self.set_namespace(namespace)
        self.set_application(application)
        self.set_stage(stage)
        self.set_scope(scope)

    def __str__(self):
        return f"namespace={self.namespace}, application={self.application}, stage={self.stage}"


    def ToString(self, short=True):
        if short:
            return f"namespace={self.namespace}, application={self.application}, stage={self.short_stage}, scope={self.scope}"
        else:
            return f"namespace={self.namespace}, application={self.application}, stage={self.stage}, scope={self.scope}"


    @property
    def namespace(self):
        return self.get_namespace()


    def get_namespace(self, ignore_scope=False, silent=True):
        if ignore_scope:
            result = self._namespace
        else:
            if self._scope > ContextScope.Namespace:
                result = 'default'
                if not silent: Logger.warn("Switched to the global scope.")
            else:
                result = self._namespace
        return result

    def set_namespace(self, value):
        if self._namespace == value: return
        if value:
            self._namespace = value
        else:
            self._namespace = 'default'
        # self._namespace = value


    @property
    def application(self):
        return self.get_application()

    def get_application(self, ignore_scope=False, silent=True):
        if ignore_scope:
            result = self._application
        else:
            if self._scope > ContextScope.Namespace:
                result = 'default'
                if not silent: Logger.warn("Switched to the global scope.")
            elif self._scope > ContextScope.App:
                result = 'default'
                if not silent: Logger.warn("Switched to the namespace scope.")
            else:
                result = self._application
        
        return result


    def set_application(self, value):
        if self._application == value: return
        if value:
            self._application = value
        else:
            self._application = 'default'
        # self._application = value

    @property
    def stage(self):
        return self.get_stage()

    def get_stage(self, ignore_scope=False, silent=True):
        return self._stage

    def set_stage(self, value):
        if self._stage == value: return
        if value:
            self._stage = Stages.normalize(value)
        else:
            self._stage = Stages.default_stage
        self._short_stage = Stages.shorten(self._stage)
        # if value:
        #     self._stage = Stages.normalize(value)
        #     self._short_stage = Stages.shorten(value)



    @property
    def short_stage(self):
        return self._short_stage

    @property
    def env(self):
        return Stages.parse_env(self.stage)


    @property
    def scope(self):
        return self._scope


    def set_scope(self, value):
        if self._scope == value: return
        if value:
            self._scope = value
        else:
            self._scope = ContextScope.App



    @property
    def scope_translation(self):
        namespace_idx = 'default' if self.namespace == 'default' else 'namespace'
        application_idx = 'default' if self.application == 'default' else 'application'
        stage_idx = 'default' if Stages.is_default(self.stage) else 'stage'
        n_idx = '0' if Stages.is_default_env(self.stage) else 'n'
        return context_translation_matrix[namespace_idx][application_idx][stage_idx][n_idx]

    @property
    def path(self):
        return self.get_path()


    def get_path(self, key=None):
        result = f"/{self.namespace}/{self.application}/{self.stage}"
        if key:
            result += f"/{key}"
        return result

    @property
    def effective(self):
        return self.get_namespace(), self.get_application(), self.get_stage(), str(self.scope)

    @property
    def target(self):  ### ns/app/stage/
        return self.get_namespace(ignore_scope=True), self.get_application(ignore_scope=True), self.get_stage(ignore_scope=True), str(self.scope)


class ContextService():


    def parse_path(self, path):
        """
            path is in the form of [/]namespace/application/stage/env/[key]
        """
        parts = path.split('/')
        if not parts[0]: parts.pop(0)
        namespace = parts[0]
        application = parts[1]
        stage = f"{parts[2]}/{parts[3]}"
        key = '/'.join(parts[4:]) if len(parts) > 4 else None
        return namespace, application, stage, key


    def get_hierachy_paths(self, context, key=None, path_prefix=None, ignore_stage=False, uninherited=False, reverse=False):
        result = []
        if path_prefix.endswith('/'): path_prefix = path_prefix[:-1]
        if uninherited:
            result.append(path_prefix + context.get_path(key))
        else:
            nss = ['default', context.namespace] if not context.namespace == 'default' else ['default']
            apps = ['default', context.application] if not context.application == 'default' else ['default']
            stages = ['default', Stages.parse_name(context.stage)] if not ignore_stage and not Stages.parse_name(context.stage) == 'default' else ['default']
            envs = [0, context.env] if not ignore_stage and not context.env == 0 else [0]

            for ns in nss:
                for app in apps:
                    ### only default app is considered for inheritence when namespace is default to simplify hierachy
                    if ns == 'default' and not app == 'default': continue
                    for stage in stages:
                        for env in envs:
                            ### Numbered envs are not considered for inheritence to simplify hierachy
                            if env > 0 and (stage == 'default' or app == 'default' or ns == 'default'): continue
                            result.append(path_prefix + Context(ns, app, f'{stage}/{env}').get_path(key))

        return list(reversed(result)) if reverse else result


Contexts = ContextService()
