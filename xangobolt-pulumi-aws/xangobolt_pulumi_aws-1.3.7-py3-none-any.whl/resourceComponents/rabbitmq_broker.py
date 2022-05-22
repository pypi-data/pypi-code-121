# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time
import string
from grpc import server
import pulumi
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output

from resources import mq, ec2, sm, random
from resourceComponents import secrets_manager, security_group


class RabbitMQ(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, opts:  ResourceOptions = None):
        """
        Constructs an Rabbitmq Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Rabbitmq', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [mq, ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create Rabbitmq Cluster Password
        password = random.RandomString(
            name,
            parent=self,
            depends_on=opts.depends_on,
        )

        # Create Rabitmq Cluster
        mq_cluster = [mq.Broker(
            props.mq[i]["broker_name"],
            props,
            username=props.mq[i]["setflow_sm"]["secret_version"]["username"],
            password=password.result,
            secgrp_ids=[(security_group.SEC_GRP(
                props.mq[i]["setflow_sg"]["sg_name"],
                props,
                vpc_id=vpc_props["vpcid"],
                er=props.mq[i]["setflow_sg"]["sg_rules"]["egress"],
                ir=props.mq[i]["setflow_sg"]["sg_rules"]["ingress"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id)
            ],
            snet_ids=vpc_props["subnets"],
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.mq
        ]

        string = Output.all(url=mq_cluster[0].instances[0].console_url, pword=password.result).apply(lambda args: sm.mqJsonify(
                username=props.sm["rabbitmq-secrets"]["secret_version"]["username"],
                password=args['pword'],
                server=args['url'].replace("https://", ""),
                tls=props.sm["rabbitmq-secrets"]["secret_version"]["Ssl"]
            )
        )

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'rabbitmq-'+props.stack,
            props=props,
            name=props.sm["rabbitmq-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )