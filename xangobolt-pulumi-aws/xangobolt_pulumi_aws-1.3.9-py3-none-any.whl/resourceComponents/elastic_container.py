# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time, pulumi
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output
from pulumi_aws.ecs import task_definition
# from pulumi_aws import cloudwatch, config, ec2, iam

from resources import ecs, s3, lb, ec2, autoscaling, sm
from resourceComponents import load_balancer, secrets_manager, security_group

# from .iam_helpers import assume_role_policy_for_principal
from .subnet_distributor import SubnetDistributor



class ElasticContainerService(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, dns_zone: None, ecs_sg: None, opts:  ResourceOptions = None):
        """
        Constructs an ECS Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Ecs', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [ecs]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # # Create ECS Security Group
        # ecs_sg = [(security_group.SEC_GRP(
        #     props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]['lt_sg']['sg_name'],
        #     props,
        #     vpc_id=vpc_props["vpcid"],
        #     er=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]['lt_sg']["sg_rules"]["egress"],
        #     ir=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]['lt_sg']["sg_rules"]["ingress"],
        #     parent=self, 
        #     provider=opts.providers.get(props.stack+'_prov')))
        # for i in props.ecs
        # ]

        # Create LB Security Group
        lb_sg = [(security_group.SEC_GRP(
            props.ecs[i]['lb_sg']['sg_name'],
            props,
            vpc_id=vpc_props["vpcid"],
            er=props.ecs[i]['lb_sg']["sg_rules"]["egress"],
            ir=props.ecs[i]['lb_sg']["sg_rules"]["ingress"],
            parent=self, 
            provider=opts.providers.get(props.stack+'_prov')))
        for i in props.ecs
        ]

        # Create Auto Scaling Group
        ecs_autoscalinggroup = [autoscaling.AutoScaleingGroup(
            props.ecs[i]["capacity_provider"]["autoscaling"]["asg_name"],
            props,
            lt_id=(ec2.LaunchTemplates(
                props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["lt_name"],
                props,
                sg_ids=ecs_sg,
                vpc_id=vpc_props["vpcid"], 
                snet_ids=vpc_props["subnets"],
                iam_ip_arn=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["instance_profile"],
                image_id=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["image_id"],
                instance_type=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["instance_type"],
                key_name=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["key_pair"],
                user_data=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["user_data"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.ecs
        ]

        # Create ECS Cluster
        ecs_cluster = [ecs.ecs_cluster(
            props.ecs[i]["cluster_name"],
            props,
            cp=(ecs.ecs_capacity_provider(
                props.ecs[i]["capacity_provider"]["cp_name"],
                props, 
                asg_arn=ecs_autoscalinggroup[0].arn,
                parent=self,
                depends_on=ecs_autoscalinggroup,
                provider=opts.providers.get(props.stack+'_prov')).name),
            # cp=ecs_capacity_provider[0].name,
            parent=self,
            depends_on=ecs_autoscalinggroup,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.ecs
        ]

        # # Create Secret for URLs
        # secret = sm.Secret(
        #     'settings'+props.stack,
        #     props,
        #     name=props.sm["url-secrets"]["secret_name"],
        #     parent=self,
        #     depends_on=opts.depends_on,
        #     provider=opts.providers.get(props.stack+'_prov')
        # )


        # Create Service
        es = [ecs.ecs_service(
            props.service_def[i]["service_name"], 
            props,
            td_arn=(ecs.ecs_task_definition(
                props.service_def[i]['taskDefinition']["td_name"], 
                props,
                family=props.service_def[i]['taskDefinition']["family_name"],
                volume=props.service_def[i]['taskDefinition']["volume_name"],
                cd=json.dumps(props.service_def[i]['taskDefinition']["container_def"]["container_definitions"]),
                parent=self,
                depends_on=ecs_cluster,
                provider=opts.providers.get(props.stack+'_prov')).arn),
            cluster_id=ecs_cluster[0],
            vpc_id=vpc_props["vpcid"],
            tg_id=None if props.service_def[i]['targetGroup']["tg_enabled"] == 'false' else 
                (load_balancer.ECS_LB(
                    props.service_def[i]['targetGroup']["tg_name"], 
                    props, 
                    snet_ids=vpc_props["subnets"],
                    vpc_id=vpc_props["vpcid"],
                    sg_ids=lb_sg[0].id,
                    asg_name=ecs_autoscalinggroup[0].name,
                    hcp=props.service_def[i]['targetGroup']["healthcheckpath"],
                    dns_zone=dns_zone,
                    dns_name=props.service_def[i]['targetGroup']["dns_record"],
                    cert=props.service_def[i]['targetGroup']["acm_cert"],
                    lb_ports=props.service_def[i]['targetGroup']["lb_ports"],
                    parent=self,
                    depends_on=ecs_cluster,
                    provider=opts.providers.get(props.stack+'_prov'))
                ),
            cp_name=ecs_cluster[0].capacity_providers[0],
            container=props.service_def[i]['taskDefinition']["container_def"]["container_definitions"][0]["name"],
            count=props.service_def[i]["count"],
            parent=self,
            depends_on=ecs_cluster,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.service_def
        ]


        string = Output.all().apply(lambda args: sm.urlJsonify(
                api=props.sm["url-secrets"]["secret_version"]["api"],
                portal=props.sm["url-secrets"]["secret_version"]["portal"],
                dash=props.sm["url-secrets"]["secret_version"]["dashboard"],
                cp=props.sm["url-secrets"]["secret_version"]["cp"]
            )
        )
        

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'settings-'+props.stack,
            props=props,
            name=props.sm["url-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )

        self.clusterName = ecs_cluster[0].name
        
        # for i in range(len(es)):
        #     self.lbs = es[i].load_balancers

        # self.lbs = es[0].load_balancers