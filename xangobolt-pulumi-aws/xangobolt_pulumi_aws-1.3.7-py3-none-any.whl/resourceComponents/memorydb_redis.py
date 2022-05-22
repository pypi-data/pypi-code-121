# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
from email.headerregistry import Address
import json, time
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output

from resources import memorydb, ec2, sm, random
from resourceComponents import secrets_manager, security_group


class MemoryDB4Redis(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, redis_sg: None, opts:  ResourceOptions = None):
        """
        Constructs an Rediss Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('MemoryDB', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [memorydb, ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create Memorydb Cluster Password
        password = random.RandomString(
            name,
            parent=self,
            depends_on=opts.depends_on,
        )


        # Create Redis Cluster
        redis_cluster = [memorydb.Cluster(
            props.mdb[i]["cluster_name"],
            props,
            acl_name=(memorydb.Acl(
                props.mdb[i]["acl_name"],
                props,
                usernames=[(memorydb.User(
                    props.mdb[i]["setflow_sm"]["secret_version"]["username"],
                    props,
                    username=props.mdb[i]["setflow_sm"]["secret_version"]["username"],
                    passwords=[password.result],
                    accessstring=props.mdb[i]["setflow_sm"]["secret_version"]["access_string"],
                    parent=self, 
                    provider=opts.providers.get(props.stack+'_prov')))
                ],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov'))
            .id),
            secgrp_ids=[redis_sg],
            snetgrp_name=(memorydb.SubnetGroup(
                props.mdb[i]["snetgrp_name"],
                props,
                snet_ids=vpc_props["subnets"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.mdb
        ]

        string = Output.all(address=redis_cluster[0].cluster_endpoints[0].address, pword=password.result).apply(lambda args: sm.redisJsonify(
            username=props.sm["redis-secrets"]["secret_version"]["username"],
            password=args['pword'],
            server=args['address'],
            port=props.sm["redis-secrets"]["secret_version"]["port"]
            )
        )
        
        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'redis-'+props.stack,
            props=props,
            name=props.sm["redis-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )

        