
from .constants import *
from .providers import ProviderBase, Providers
from .artifacts import Artifactory
from .logger import Logger
from .exceptions import DSOException
from .configs import Config


key_regex_pattern = r"^[a-zA-Z]([./a-zA-Z0-9_-]*[a-zA-Z0-9])?$"

class PackageProvider(ProviderBase):
    def list(self, filter=None):
        raise NotImplementedError()
    def build(self, key):
        raise NotImplementedError()
    def get(self, key, revision=None):
        raise NotImplementedError()
    # def history(self, key):
    #     raise NotImplementedError()
    def delete(self, key):
        raise NotImplementedError()


class PackageService():
    

    service_name = 'package'


    # def validate_key(self, key):
    #     Logger.info(f"Validating package key '{key}'...")
    #     if not key:
    #         raise DSOException(MESSAGES['KeyNull'])
    #     if key == 'dso' or key.startswith('dso.'):
    #         raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
    #     if not re.match(key_regex_pattern, key):
    #         raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, key_regex_pattern))
    #     ### the regex does not check adjacent special chars
    #     if '..' in key:
    #         raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

    #     if '//' in key:
    #         raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '//'))


    @property
    def version_major(self):
        try:
            return int(AppConfigsget(key='version.major', service=self.service_name)['Value'])
        except DSOException:
            init_version_major = 0
            self.version_major = init_version_major
            return init_version_major

    @version_major.setter
    def version_major(self, value):
        AppConfigsset(key='version.major', value=str(value), service=self.service_name)


    @property
    def version_minor(self):
        try:
            return int(AppConfigsget(key='version.minor', service=self.service_name)['Value'])
        except DSOException:
            init_version_minor = 0
            self.version_minor = init_version_minor
            return init_version_minor

    @version_minor.setter
    def version_minor(self, value):
        AppConfigsset(key='version.minor', value=str(value), service=self.service_name)


    @property
    def version_patch(self):
        try:
            return int(AppConfigsget(key='version.patch', service=self.service_name)['Value'])
        except DSOException:
            init_version_patch = 0
            self.version_patch = init_version_patch
            return init_version_patch

    @version_patch.setter
    def version_patch(self, value):
        AppConfigsset(key='version.patch', value=str(value), service=self.service_name)


    @property
    def version_build(self):
        try:
            return int(AppConfigsget(key='version.build', service=self.service_name)['Value'])
        except DSOException:
            init_version_build = 0
            self.version_build = init_version_build
            return init_version_build


    @version_build.setter
    def version_build(self, value):
        AppConfigsset(key='version.build', value=str(value), service=self.service_name)


    def list(self, filter=None):
        provider = Providers.PackageProvider()
        Logger.info(f"Listing packages: namespace={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        response = Artifactory.list(service=self.service_name, filter=filter)
        result = {'Packages': response['Artifacts']}
        return result


    def build(self):
        provider = Providers.PackageProvider()
        Logger.info(f"Building package: namespace={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        artifact = provider.build()
        major = self.version_major
        minor = self.version_minor
        patch = self.version_patch
        build = self.version_build
        artifactKey = f"{major}.{minor}.{patch}.{build}"
        self.version_build = build + 1
        Logger.info(f"Adding package '{artifactKey}' to artifact store...")
        # changed = Logger.decrease_verbosity()
        # try:
        #     response = Artifactory.add(filepath=artifact, key=artifactKey ,service=self.service_name)
        # finally:
        #     if changed: Logger.increase_verbosity()
        response = Artifactory.add(filepath=artifact, key=artifactKey ,service=self.service_name)
        return response


    def get(self, key):
        Logger.info(f"Getting package '{key}': namespace={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        response = Artifactory.get(key=key, service=self.service_name)
        return response


    # def history(self, key):
    #     self.config = config
    #     provider = Providers.PackageProvider()
    #     Logger.info(f"Fetching history of package '{key}': namespace={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
    #     return provider.history(key)


    def delete(self, key):
        Logger.info(f"Deleting package '{key}': namespace={Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        response = Artifactory.delete(key=key, service=self.service_name)
        return response


Packages = PackageService()