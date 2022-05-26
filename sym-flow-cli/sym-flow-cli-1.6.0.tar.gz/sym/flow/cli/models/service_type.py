from enum import Enum
from typing import Callable, List, NamedTuple, Optional


class ServiceTypeMeta(NamedTuple):
    type_name: str
    matcher: str
    external_id_name: str
    validator: Optional[Callable[[str], bool]] = None
    help_str: Optional[str] = None


class ServiceType(ServiceTypeMeta, Enum):
    """All Service Types recognized by the Sym API"""

    @classmethod
    def public(cls) -> List["ServiceType"]:
        """Returns all ServiceTypes that can be edited by external users"""
        private_services = [cls.SYM, cls.AUTH0]
        return [s for s in cls if s not in private_services]

    @classmethod
    def all_public_names(cls) -> List[str]:
        """Returns all service types names that can be edited by external users"""
        return [str(s) for s in cls.public()]

    @classmethod
    def all_names(cls) -> List[str]:
        """Returns all service type names"""
        return [str(s) for s in ServiceType]

    @classmethod
    def get(cls, name) -> Optional["ServiceType"]:
        # Names in the enum member map are all uppercase
        if name.upper() in cls._member_map_:
            return ServiceType[name.upper()]
        else:
            return None

    def __str__(self):
        return self.value.type_name

    SYM = ServiceTypeMeta("sym", matcher="email", external_id_name="Org Slug")
    SLACK = ServiceTypeMeta(
        "slack",
        matcher="user_id",
        external_id_name="Workspace ID",
        validator=lambda id: id.startswith("T") and id.isupper(),
        help_str="Must start with 'T' and be all upper case",
    )
    AWS_SSO = ServiceTypeMeta(
        "aws_sso",
        matcher="principal_uuid",
        external_id_name="Instance ARN",
        validator=lambda arn: arn.startswith("arn:aws:sso:::instance/"),
        help_str="Must start with 'arn:aws:sso:::instance/'",
    )
    PAGERDUTY = ServiceTypeMeta(
        "pagerduty", matcher="user_id", external_id_name="PagerDuty Subdomain"
    )
    AWS_IAM = ServiceTypeMeta(
        "aws_iam",
        matcher="user_arn",
        external_id_name="Account #",
        validator=lambda acct_num: acct_num.isdigit() and len(acct_num) == 12,
        help_str="Must be a 12 digit account number",
    )
    APTIBLE = ServiceTypeMeta(
        "aptible", matcher="user_id", external_id_name="Organization ID"
    )
    GOOGLE = ServiceTypeMeta("google", matcher="email", external_id_name="Email Domain")
    AUTH0 = ServiceTypeMeta("auth0", matcher="idp_id", external_id_name="External ID")
    OKTA = ServiceTypeMeta("okta", matcher="user_id", external_id_name="Okta Domain")
    GITHUB = ServiceTypeMeta(
        "github", matcher="user_id", external_id_name="Github Organization Name"
    )
    CUSTOM = ServiceTypeMeta(
        "custom", matcher="user_id", external_id_name="Custom Service External ID"
    )


# Services managed by Sym, not customers
MANAGED_SERVICES = [ServiceType.SYM.type_name, ServiceType.AUTH0.type_name]
