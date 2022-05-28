
import os
from .constants import *
from .providers import Providers, ProviderBase
from .logger import Logger
from .configs import Config



class ArtifactoryService():

    def list(self, service, filter=None):
        provider = Providers.ArtifactoryProvider()
        Logger.info(f"Listing artifacts: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        response = provider.list(filter=filter, service=service)
        result = {
            'Artifacts': response['Files']
        }
        return result

    def add(self, filepath, service, key=None):
        if not key: key = os.path.basename(filepath)
        # self.validate_key(key)
        provider = Providers.ArtifactoryProvider()
        Logger.info(f"Adding artifact '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.add(filepath=filepath, key=key, service=service)


    def get(self, key, service):
        provider = Providers.ArtifactoryProvider()
        Logger.info(f"Getting artifact '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.get(key=key, service=service)


    # def history(self, key):
    #     self.AppConfig = AppConfig
    #     provider = Providers.ArtifactoryProvider()
    #     Logger.info(f"Fetching history of artifact '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
    #     return provider.history(key)


    def delete(self, key, service):
        provider = Providers.ArtifactoryProvider()
        Logger.info(f"Deleting artifact '{key}': namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return provider.delete(key=key, service=service)



Artifactory = ArtifactoryService()
