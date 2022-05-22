# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time
from typing import Mapping, Sequence
import pulumi
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output

from resources import s3, sm
from resourceComponents import secrets_manager


class Bucket(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        """
        Constructs a Bucket.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Bucket', name, {}, opts)

        Resources = [s3]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create S3 Bucket
        s3_bucket = [s3.S3_Bucket(
            props.s3[i]["bucket_name"],
            props,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.s3
        ]


        string = Output.all(bucket=s3_bucket[0].bucket).apply(lambda args: sm.s3Jsonify(
                keyname=props.sm["services-secrets"]["secret_version"]["keyname"],
                bucket=args['bucket'],
                UseBabelFish=props.sm["services-secrets"]["secret_version"]["UseBabelFish"],
                AllowAllQueueNotification=props.sm["services-secrets"]["secret_version"]["AllowAllQueueNotification"]
            )
        )
        

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            's3-'+props.stack,
            props=props,
            name=props.sm["services-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )