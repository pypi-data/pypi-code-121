from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.route53 as route53
import pulumi_aws_native.route53 as route53_native

def Zone(stem, props, provider=None, parent=None, depends_on=None):
    zone = route53.Zone(
        f'r53z-{stem}',
        name=f'{stem}',
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return zone


def Record(stem, props, zone_id=None, type=None, name=None, lbz_name=None, lbz_id=None, provider=None, parent=None, depends_on=None):
    zone = route53.Record(
        f'r53zr-{stem}',
        zone_id=zone_id,
        name=name,
        type=type,
        aliases=[
            route53.RecordAliasArgs(
            name=lbz_name,
            zone_id=lbz_id,
            evaluate_target_health=True,
        )],
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return zone