from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers, ArtifactoryProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.contexts import Contexts
from dsocli.aws_s3_utils import *
from dsocli.settings import *
from dsocli.configs import Config


__default_spec = {
    'bucket': 'mybucket',
    'pathPrefix': 'dso/v1/',
}


def get_default_spec():
    return __default_spec.copy()


class AwsS3ArtifactoryProvider(ArtifactoryProvider):

    def __init__(self):
        super().__init__('artifactory/aws/s3/v1')


    def get_bucket_name(self):
        return AppConfigsartifactory_spec('bucket')

    ### adds service name to the artifactory prefix
    def get_path_prefix(self, service):
        storePathPrefix = AppConfigsartifactory_spec('pathPrefix')
        if not storePathPrefix.endswith('/'): storePathPrefix += '/'
        return storePathPrefix + service

    def list(self, service, filter=None):
        Logger.debug(f"Listing artifacts from S3: bucket={self.get_bucket_name()}")
        items = s3_context_list_files(bucket=self.get_bucket_name(), path_prefix=self.get_path_prefix(service), filter=filter)
        result = {'Files': items}
        return result


    def add(self, filepath, key, service):
        Logger.debug(f"Adding artifact '{key}' to S3: bucket={self.get_bucket_name()}")
        response = s3_context_add_file(filepath=filepath, bucket=self.get_bucket_name(), key=key, path_prefix=self.get_path_prefix(service))
        result = {
                # 'RevisionId': str(response['Version']),
                'Key': key,
                'Context': {
                    'Namespace': Config.namespace,
                    'Application': Config.application,
                    'Stage': Config.stage,
                },
            }
        result.update(response)
        return result


    def get(self, key, service, revision=None):
        Logger.debug(f"Getting artifact '{key}' from S3: bucket={self.get_bucket_name()}")
        response = s3_context_get_file(bucket=self.get_bucket_name(), key=key, path_prefix=self.get_path_prefix(service))
        if not response:
            raise DSOException(f"Artifact '{key}' not found in the given context: namespace:{Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        result = {
                # 'RevisionId': str(response['Version']),
                'Key': key,
                'Context': {
                    'Namespace': Config.namespace,
                    'Application': Config.application,
                    'Stage': Config.stage,
                },
            }
        result.update(response)
        return result

        # response = get_ssm_artifact_history(found['Name'])
        # artifact = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        # if revision is None:
        #     ### get the latest revision
        #     result = {
        #             'RevisionId': str(artifact[0]['Version']),
        #             'Date': artifact[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
        #             'Key': key, 
        #             'Scope': found['Scope'],
        #             'Context': found['Context'],
        #             'User': artifact[0]['LastModifiedUser'],
        #             'Path': found['Name'],
        #             'Contents': artifact[0]['Value'],
        #             }
        # else:
        #     ### get specific revision
        #     artifact = [x for x in artifact if str(x['Version']) == revision]
        #     if not artifact:
        #         raise DSOException(f"Revision '{revision}' not found for artifact '{key}' in the given context: namespace:{Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        #     result = {
        #             'RevisionId': str(artifact[0]['Version']),
        #             'Date': artifact[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
        #             'Key': key, 
        #             'Scope': found['Scope'],
        #             'Context': found['Context'],
        #             'Path': found['Name'],
        #             'User': artifact[0]['LastModifiedUser'],
        #             'Contents': artifact[0]['Value'],
        #             }

        return result



    def history(self, key, include_contents=False):
        Logger.debug(f"Locating artifact '{key}' from S3: bucket={self.get_bucket_name()}")
        found = locate_ssm_parameter_in_context_hierachy(key=key, service=self.get_path_prefix())
        if not found:
            raise DSOException(f"Artifact '{key}' not found in the given context: namespace:{Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Storage '{key}' not found in the given context: namespace:{Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        Logger.debug(f"Getting S3 artifact: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        artifact = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if include_contents:
            result = { "Revisions":
                [{
                    'RevisionId': str(artifact['Version']),
                    'Date': artifact['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Context': found['Context'],
                    'User': artifact['LastModifiedUser'],
                    # 'Path': found['Name'],
                    'Contents': artifact[0]['Value'],

                } for artifact in artifact]
            }
        else:
            result = { "Revisions":
                [{
                    'RevisionId': str(artifact['Version']),
                    'Date': artifact['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Context': found['Context'],
                    'User': artifact['LastModifiedUser'],
                    # 'Path': found['Name'],
                } for artifact in artifact]
            }

        return result



    def delete(self, key, service):
        Logger.debug(f"Deleting artifact '{key}' from S3: bucket={self.get_bucket_name()}")
        response = s3_context_delete_file(bucket=self.get_bucket_name(), key=key, path_prefix=self.get_path_prefix(service))
        if not response:
            raise DSOException(f"Artifact '{key}' not found in the given context: namespace:{Config.namespace}, application={Config.application}, stage={Config.short_stage}")
        result = {
                # 'RevisionId': str(response['Version']),
                'Key': key,
                'Context': {
                    'Namespace': Config.namespace,
                    'Application': Config.application,
                    'Stage': Config.stage,
                },
            }
        result.update(response)
        return result



def register():
    Providers.register(AwsS3ArtifactoryProvider())
