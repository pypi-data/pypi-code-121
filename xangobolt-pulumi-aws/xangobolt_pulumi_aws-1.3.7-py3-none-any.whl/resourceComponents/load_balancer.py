from arpeggio.cleanpeg import NOT, prefix
import pulumi
from pulumi import ComponentResource, ResourceOptions, StackReference, Input, Output
from resources import lb, autoscaling, route53, sm


def ECS_LB(stem, props, snet_ids=None, sg_ids=None, vpc_id=None, asg_name=None, hcp=None, dns_zone=None, dns_name=None, sec_id=None, secret=None, cert=None, lb_ports=None, provider=None, parent=None, depends_on=None):
    ecs_lb = lb.AppLoadBalancer(
        stem,
        props, 
        snet_ids=snet_ids,
        sg_ids=sg_ids,
        parent=parent,
        depends_on=depends_on,
        provider=provider
    )

    # Create Target Group
    ecs_tg = lb.TargetGroup(
        stem, 
        props, 
        vpc_id=vpc_id,
        hcp=hcp,
        parent=parent,
        depends_on=depends_on,
        provider=provider
    )

    # # Create Forward Listener
    # fw_listener = [lb.Listener_SSL(
    #     stem,
    #     props,
    #     lb_arn=ecs_lb.arn,
    #     tg_arn=ecs_tg.arn,
    #     cert_arn=cert,
    #     lb_port= lb_ports[i]["port"],
    #     parent=parent,
    #     count = i,
    #     depends_on=ecs_tg,
    #     provider=provider
    # )
    # for i in range(len(lb_ports))
    # ]

    # Create Forward Listener from port 443 to target group
    web_fw_listener = lb.F_Listener_SSL(
        stem,
        props,
        lb_arn=ecs_lb.arn,
        tg_arn=ecs_tg.arn,
        cert_arn=cert,
        lb_port= 443,
        parent=parent,
        depends_on=ecs_tg,
        provider=provider
    )

    # Create Forward Listener from port 8090 to target group
    web_fw_listener = lb.F_Listener(
        stem,
        props,
        lb_arn=ecs_lb.arn,
        tg_arn=ecs_tg.arn,
        cert_arn=cert,
        lb_port= 8090,
        parent=parent,
        depends_on=ecs_tg,
        provider=provider
    )

    # Create Redirect Listener from port 80 to 443
    r_listener = lb.R_Listener_SSL(
        stem,
        props,
        lb_arn=ecs_lb.arn,
        lb_port=80,
        rport="443",
        parent=parent,
        depends_on=ecs_lb,
        provider=provider
    )

    # Create DNS Record
    dnsrecord = Output.all(dnsname=ecs_lb.dns_name).apply(lambda args: route53.Record(
            dns_name,
            props,
            zone_id=dns_zone,
            type='A',
            name=dns_name, 
            lbz_name='dualstack.'+args['dnsname'], 
            lbz_id=ecs_lb.zone_id,
            parent=parent,
            depends_on=depends_on,
            provider=provider
        )
    )

    pulumi.export('lbName', ecs_lb.dns_name)
    pulumi.export('lbID', ecs_lb.zone_id)
    return ecs_tg

    


