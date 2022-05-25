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
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input

from resources import ec2
from resourceComponents import security_group


class BastionHosts(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, opts:  ResourceOptions = None):
        """
        Constructs an Rediss Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('BastionHost', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags

        # Create Bastion Hosts
        ec2_BASTION = [ec2.Instance(
            props.bh[i]["instance_name"],
            props,
            lt_id=(ec2.LaunchTemplates(
                props.bh[i]["instance_name"],
                props,
                sg_ids=[(security_group.SEC_GRP(
                    props.bh[i]["bh_lt"]["lt_sg"]['sg_name'],
                    props,
                    vpc_id=vpc_props["vpcid"],
                    er=props.bh[i]["bh_lt"]["lt_sg"]["sg_rules"]["egress"],
                    ir=props.bh[i]["bh_lt"]["lt_sg"]["sg_rules"]["ingress"],
                    parent=self, 
                    provider=opts.providers.get(props.stack+'_prov')).id)
                ],
                vpc_id=vpc_props["vpcid"], 
                snet_ids=vpc_props["subnets"],
                iam_ip_arn=props.bh[i]["bh_lt"]["instance_profile"],
                image_id=props.bh[i]["bh_lt"]["image_id"],
                instance_type=props.bh[i]["bh_lt"]["instance_type"],
                key_name=props.bh[i]["bh_lt"]["key_pair"],
                user_data=props.bh[i]["bh_lt"]["user_data"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.bh
        ]

        self.win_bh_sg = ec2_BASTION[0].vpc_security_group_ids[0]
        self.lh_bh_sg = ec2_BASTION[1].vpc_security_group_ids[0]