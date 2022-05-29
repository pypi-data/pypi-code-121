"""
Generate gitignored .chalice/config.json for deploy and then run deploy.
Takes on parameter for now: stage (either "dev" or "prod")
"""
import os
import sys
import argparse
import json
import subprocess

from dcicutils.misc_utils import as_seconds


class Deploy(object):

    DEFAULT_LAMBDA_TIMEOUT = as_seconds(minutes=15)

    CONFIG_BASE = {
      "stages": {
        "dev": {
          "api_gateway_stage": "api",
          "autogen_policy": False,
          "lambda_memory_size": 512,
          "lambda_timeout": DEFAULT_LAMBDA_TIMEOUT,  # 15 mins in seconds
          "environment_variables": {
              "chalice_stage": "dev"
          }
        },
        "prod": {
          "api_gateway_stage": "api",
          "autogen_policy": False,
          "lambda_memory_size": 512,
          "lambda_timeout": DEFAULT_LAMBDA_TIMEOUT,  # 15 mins in seconds
          "environment_variables": {
              "chalice_stage": "prod"
          }
        }
      },
      "version": "2.0",
      "app_name": "foursight-cgap",
      "layers": [
          "arn:aws:lambda:us-east-1:553035198032:layer:git:11"  # required for Deployment Checks - Will 5/20/2020
      ]
    }

    config_dir = os.path.dirname(__file__)

    @classmethod
    def get_config_filepath(cls):
        return os.path.join(cls.config_dir, '.chalice/config.json')

    @classmethod
    def build_config(cls, stage, trial_creds=None, trial_global_env_bucket=False, global_env_bucket=None,
                     security_group_ids=None, subnet_ids=None, check_runner=None, rds_name=None,
                     lambda_timeout=DEFAULT_LAMBDA_TIMEOUT):
        """ Builds the chalice config json file. See: https://aws.github.io/chalice/topics/configfile"""
        if trial_creds:
            # key to decrypt access key
            s3_enc_secret = trial_creds['S3_ENCRYPT_KEY']
            client_id = trial_creds['CLIENT_ID']
            client_secret = trial_creds['CLIENT_SECRET']
            dev_secret = None
            es_host = trial_creds['ES_HOST']
            env_name = trial_creds['ENV_NAME']
            rds_name = trial_creds['RDS_NAME']
            s3_key_id = trial_creds.get('S3_ENCRYPT_KEY_ID')
            if not (s3_enc_secret and client_id and client_secret and es_host and rds_name):
                print(''.join(['ERROR. You are missing one more more environment',
                               'variables needed to deploy the Foursight trial. Need:\n',
                               'S3_ENCRYPT_KEY, CLIENT_ID, CLIENT_SECRET, ES_HOST, RDS_NAME in trial_creds dict.'])
                      )
                sys.exit()
        else:
            s3_enc_secret = os.environ.get("S3_ENCRYPT_KEY")
            client_id = os.environ.get("CLIENT_ID")
            client_secret = os.environ.get("CLIENT_SECRET")
            dev_secret = os.environ.get("DEV_SECRET")
            es_host = None  # not previously passed to config
            env_name = None
            s3_key_id = None  # not supported in legacy
            if not (s3_enc_secret and client_id and client_secret and dev_secret):
                print(''.join(['ERROR. You are missing one more more environment ',
                               'variables needed to deploy Foursight.\n',
                               'Need: S3_ENCRYPT_KEY, CLIENT_ID, CLIENT_SECRET, DEV_SECRET.'])
                      )
                sys.exit()
        for curr_stage_name in ['dev', 'prod']:
            curr_stage = cls.CONFIG_BASE['stages'][curr_stage_name]
            curr_stage_environ = curr_stage['environment_variables']

            curr_stage_environ['S3_ENCRYPT_KEY'] = s3_enc_secret
            curr_stage_environ['CLIENT_ID'] = client_id
            curr_stage_environ['CLIENT_SECRET'] = client_secret
            if rds_name:
                curr_stage_environ['RDS_NAME'] = rds_name
            if dev_secret:  # still pass in main account, ignored in alpha infra - Will Aug 24 2021
                curr_stage_environ['DEV_SECRET'] = dev_secret
            if env_name:
                curr_stage_environ['ENV_NAME'] = env_name
            if es_host:
                curr_stage_environ['ES_HOST'] = es_host
            if s3_key_id:
                curr_stage_environ['S3_ENCRYPT_KEY_ID'] = s3_key_id
            if trial_global_env_bucket:
                # in the trial account setup, use a shorter timeout
                curr_stage['lambda_timeout'] = lambda_timeout
                if not global_env_bucket:
                    global_bucket_env_from_environ = os.environ.get('GLOBAL_BUCKET_ENV')
                    global_env_bucket_from_environ = os.environ.get('GLOBAL_ENV_BUCKET')
                    if (global_bucket_env_from_environ
                            and global_env_bucket_from_environ
                            and global_bucket_env_from_environ != global_env_bucket_from_environ):
                        print('ERROR. GLOBAL_BUCKET_ENV and GLOBAL_ENV_BUCKET are both set, but inconsistently.')
                        sys.exit()
                    global_env_bucket = global_bucket_env_from_environ or global_env_bucket_from_environ
                if global_env_bucket:
                    curr_stage_environ['GLOBAL_BUCKET_ENV'] = global_env_bucket  # legacy compatibility
                    curr_stage_environ['GLOBAL_ENV_BUCKET'] = global_env_bucket
                else:
                    print('ERROR. GLOBAL_ENV_BUCKET must be set or global_env_bucket= must be passed'
                          ' when building the trial config.')
                    sys.exit()
            if security_group_ids:
                curr_stage['security_group_ids'] = security_group_ids
            if subnet_ids:
                curr_stage['subnet_ids'] = subnet_ids
            if check_runner:
                curr_stage_environ['CHECK_RUNNER'] = check_runner

        filename = cls.get_config_filepath()
        print(''.join(['Writing: ', filename]))
        with open(filename, 'w') as config_file:
            config_file.write(json.dumps(cls.CONFIG_BASE))
        # export poetry into requirements
        subprocess.check_call(
            ['poetry', 'export', '-f', 'requirements.txt', '--without-hashes', '-o', 'requirements.txt'])

    @classmethod
    def build_config_and_deploy(cls, stage):
        cls.build_config(stage)
        # actually deploy
        subprocess.call(['chalice', 'deploy', '--stage', stage])

    @classmethod
    def build_config_and_package(cls, args, trial_creds=None, global_env_bucket=None,
                                 security_ids=None, subnet_ids=None, check_runner=None,
                                 lambda_timeout=DEFAULT_LAMBDA_TIMEOUT, rds_name=None,
                                 # These next args are preferred over passing 'args'.
                                 merge_template=None, output_file=None, stage=None, trial=None,
                                 ):
        """ Builds a config with a special case for the trial account. For the trial account, expects a dictionary of
            environment variables, a list of security group ids, and a list of subnet ids. Finally, packages as a
            Cloudformation template."""

        # For compatibility during transition, we allow these argument to be passed in lieu of args.
        if merge_template is None:
            merge_template = args.merge_template
        if output_file is None:
            output_file = args.output_file
        if stage is None:
            stage = args.stage
        if trial is None:
            trial = args.trial

        if trial:
            if trial_creds and security_ids and subnet_ids and check_runner:
                cls.build_config(stage, trial_creds=trial_creds, trial_global_env_bucket=True,
                                 global_env_bucket=global_env_bucket, lambda_timeout=lambda_timeout,
                                 security_group_ids=security_ids, subnet_ids=subnet_ids, check_runner=check_runner,
                                 rds_name=rds_name)
            else:
                raise Exception('Build config requires trial_creds, sg id, and subnet ids to run in trial account')
        else:
            cls.build_config(stage=stage)
        # actually package cloudformation templates
        # add --single-file ?
        flags = ['--stage', stage, '--pkg-format', 'cloudformation', '--template-format', 'yaml']
        if merge_template:
            flags.extend(['--merge-template', merge_template])
        subprocess.call(['chalice', 'package', *flags, output_file])


def main():
    parser = argparse.ArgumentParser('chalice_deploy')
    parser.add_argument(
        "stage",
        type=str,
        choices=['dev', 'prod'],
        help="chalice deployment stage. Must be one of 'prod' or 'dev'")
    args = parser.parse_args()
    Deploy.build_config_and_deploy(stage=args.stage)


if __name__ == '__main__':
    main()
