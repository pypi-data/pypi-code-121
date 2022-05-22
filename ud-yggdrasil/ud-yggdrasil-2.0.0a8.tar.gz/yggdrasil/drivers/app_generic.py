# todo (mt) Enforce some class attributes to be implemented in subclasses
# todo (mt) add decorators for logging on app_web & app_local


class AppGeneric(object):
    """
    Generic application class. Any implementation of an App class should inheritc AppGeneric.
    """
    identifier = None
    name_settings_file = None
    parameters = None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name")
        self.is_installed = kwargs.pop("is_installed")

    @classmethod
    def set_class_constants(cls, *args, **kwargs):
        pass

    def create(self, path_scripts: str, path_venvs: str, path_templates: str, **kwargs):
        raise Exception("Function should be overriden by subclass")

    def remove(self, *args, **kwargs):
        raise Exception("Function should be overriden by subclass")

    @classmethod
    def seed_settings(cls, root):
        raise Exception("Should be implemented by each ")

    @classmethod
    def load_settings(self, root) -> []:
        raise Exception("Should be implemented by each ")

    def __repr__(self):
        mapping_installed = {
            True: "installed",
            False: "not installed",
        }
        return 'app {0} ({1}, {2})'.format(self.name,self.__class__.__name__, mapping_installed[self.is_installed])

    def __str__(self):
        return 'App {0}'.format(self.name)


class ListApps(object):
    def __init__(self):
        self.classes_apps = AppGeneric.__subclasses__()

    def select(self, **kwargs):
        for class_app in self.classes_apps:
            condition_out = True
            for att, val in kwargs.items():
                if getattr(class_app, att) != val:
                    condition_out = False
            if condition_out: return class_app

