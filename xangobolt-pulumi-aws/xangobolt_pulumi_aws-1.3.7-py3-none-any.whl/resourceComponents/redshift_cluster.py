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

from resources import redshift, ec2, sm, random
from resourceComponents import secrets_manager, security_group


class Redshift(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, redshift_sg: None, opts:  ResourceOptions = None):
        """
        Constructs an Redshift Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Redshift', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [redshift, ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create Redshift Cluster Password
        password = random.RandomString(
            name,
            parent=self,
            depends_on=opts.depends_on,
        )

        # Create RDS Instance
        redshift_cluster = [redshift.Cluster(
            props.redshift[i]["cluster_name"],
            props,
            db_name=props.redshift[i]["database_name"],
            username=props.redshift[i]["setflow_sm"]["secret_version"]["username"],
            password=password.result,
            secgrp_ids=redshift_sg,
            snetgrp_name=(redshift.SubnetGroup(
                props.redshift[i]["snetgrp_name"],
                props,
                snet_ids=vpc_props["subnets"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.redshift
        ]


        string = Output.all(host=redshift_cluster[0].dns_name, pword=password.result).apply(lambda args: sm.redshiftJsonify(
                username=props.sm["redshift-secrets"]["secret_version"]["username"],
                password=args['pword'],
                engine=props.sm["redshift-secrets"]["secret_version"]["engine"],
                host=args['host'],
                port=props.sm["redshift-secrets"]["secret_version"]["port"],
                db_id=props.sm["redshift-secrets"]["secret_version"]["dbInstanceIdentifier"],
                db=props.sm["redshift-secrets"]["secret_version"]["database"],
            )
        )
        

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'redshift-'+props.stack,
            props=props,
            name=props.sm["redshift-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )