#!/usr/bin/env python

import boto3


def get_account_id():
    return boto3.client('sts').get_caller_identity().get('Account')


def get_ssm_parameter_value(ssm_parameter_name):
    ssm = boto3.client('ssm')
    return ssm.get_parameter(Name=ssm_parameter_name,
                             WithDecryption=True)['Parameter']['Value']
