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

from resources import route53
from resourceComponents import secrets_manager


class Route53Zone(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, opts:  ResourceOptions = None):
        """
        Constructs a Route53 Zone.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Route53', name, {}, opts)

        Resources = [route53]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create Zone
        zone = [route53.Zone(
            props.dns[i]["zone_name"],
            props,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.dns
        ]

        self.zone_id = zone[0].id