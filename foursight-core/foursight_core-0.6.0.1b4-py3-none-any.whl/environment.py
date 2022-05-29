from .s3_connection import S3Connection
from dcicutils.env_base import EnvManager
from dcicutils.env_utils import get_foursight_bucket, get_foursight_bucket_prefix


class Environment(object):

    def __init__(self, foursight_prefix):

        # This consistency check can go away later, but when it does we can also get
        # rid of the argument that is passed, since it should be possible to look up.
        declared_bucket_prefix = get_foursight_bucket_prefix()
        if not declared_bucket_prefix:
            raise RuntimeError(f"There is no declared foursight bucket prefix."
                               f" It should probably be {foursight_prefix!r}.")
        elif declared_bucket_prefix != foursight_prefix:
            raise RuntimeError(f"The value of foursight_prefix, {foursight_prefix},"
                               f" does not match the declared foursight bucket prefix, {declared_bucket_prefix}.")

        self.prefix = foursight_prefix
        self.s3_connection = S3Connection(self.get_env_bucket_name())

    def get_env_bucket_name(self):
        computed_result = self.prefix + '-envs'

        # Consistency check, but accessing the declared value might be a better way to get this.
        declared_result = EnvManager.global_env_bucket_name()
        if declared_result != computed_result:
            raise RuntimeError(f"get_env_bucket_name computed {computed_result},"
                               f" but the declared result was {declared_result}.")

        return computed_result

    def list_environment_names(self):
        """
        Lists all environments in the foursight-envs s3. Returns a list of names
        """
        computed_result = [key for key in self.s3_connection.list_all_keys() if not key.endswith(".ecosystem")]

        # Consistency check. The declared result would be a more abstract way to compute this.
        declared_result = EnvManager.get_all_environments(self.get_env_bucket_name())
        if declared_result != computed_result:
            raise RuntimeError("list_environment_names has consistency problems.")

        return computed_result

    def list_valid_schedule_environment_names(self):
        """Lists all valid environ names used in schedules including 'all'"""

        # This call requires no changes. -kmp 24-May-2022
        return self.list_environment_names() + ['all']

    def is_valid_environment_name(self, env):
        """check if env is a valid environment name"""

        # This call requires no changes. -kmp 24-May-2022
        if env in self.list_environment_names():
            return True
        else:
            return False

    def get_environment_info_from_s3(self, env_name):

        # This call requires no changes. -kmp 24-May-2022
        return self.s3_connection.get_object(env_name)

    def get_environment_and_bucket_info(self, env_name, stage):
        env_info = self.get_environment_info_from_s3(env_name)
        # check that the keys we need are in the object
        if isinstance(env_info, dict) and {'fourfront', 'es'} <= set(env_info):
            portal_url = env_info['fourfront']
            es_url = env_info['es']

            # Isn't the ff_env required? Does this defaulting ever matter? -kmp 24-May-2022
            defaulted_ff_env = env_info.get('ff_env', ''.join(['fourfront-', env_name]))

            computed_bucket_name = ''.join([self.prefix + '-', stage, '-', env_name])
            declared_bucket_name = get_foursight_bucket(envname=env_name, stage=stage)
            if declared_bucket_name != computed_bucket_name:
                raise RuntimeError(f"For environment {env_name}, the computed bucket name, {computed_bucket_name},"
                                   f" does not match the declared result, {declared_bucket_name}.")

            env_and_bucket_info = {
                'fourfront': portal_url,
                'es': es_url,
                'ff_env': defaulted_ff_env,
                'bucket': computed_bucket_name,
            }
            return env_and_bucket_info
        else:
            raise Exception(f'Malformatted environment info on S3 for key {env_name}: {env_info}')

    def get_selected_environment_names(self, env_name):

        # This is weirdly named. A better name would be expand_environment_names or get_matching_environment_names.
        # But it doesn't need to change. -kmp 24-May-2022
        if env_name == 'all':
            return self.list_environment_names()
        elif self.is_valid_environment_name(env_name):
            return [env_name]
        else:
            raise Exception("not a valid env name")

    def get_environment_and_bucket_info_in_batch(self, stage, env=None, envs=None):
        """
        Generate environment information from the envs bucket in s3.
        Returns a dictionary keyed by environment name with value of a sub-dict
        with the fields needed to initiate a connection.

        :param stage: a chalice stage (generally one of 'dev' or 'prod')
        :param env: allows you to specify a single env to be initialized, or the token 'all'.
        :param envs: allows you to specify multiple envs to be initialized
        """
        if env and envs:
            ValueError("get_environment_and_bucket_info_in_batch accepts either 'env=' or 'envs=' but not both.")

        try:
            env_keys = envs or self.get_selected_environment_names(env or 'all')
        except Exception:
            env_keys = []  # provided env is not in s3, so behave like no envs were requested

        return {
            env_key: self.get_environment_and_bucket_info(env_key, stage)
            for env_key in env_keys
        }
