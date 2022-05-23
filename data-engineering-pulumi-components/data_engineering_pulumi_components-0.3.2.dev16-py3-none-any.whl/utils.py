import re
from typing import Optional


def validate_principal(principal: str) -> None:
    """Checks that an AWS principal is valid.

    Parameters
    ----------
    principal : str
        An AWS principal. Can be any of: AWS account and root user, IAM user, federated
        user, IAM role, assumed-role session, anonymous user.

    Raises
    ------
    TypeError
        If the principal is not of type str.
    ValueError
        If the principal is not valid.
    """
    if not isinstance(principal, str):
        raise TypeError("principal must be of type str")

    # Anonymous users (public), specified by "*" only
    if re.match(r"^\*$", principal):
        return

    # An AWS account specified by an account ID, for example, "123456789012"
    if re.match(r"^\d{12}$", principal):
        return

    # An AWS account specified by the root user ARN, for example,
    # "arn:aws:iam::123456789012:root"
    if re.match(r"^arn:aws:iam::\d{12}:root$", principal):
        return

    principal_pattern = r"(?:(?=.{1,64}\/)[\w\+=,\.@-]+\/)*(?=.{1,64}$)[\w\+=,\.@-]+$"

    # An AWS IAM user ARN, for example, "arn:aws:iam::123456789012:user/user-name"
    if re.match(
        r"^arn:aws:iam::\d{12}:user\/" + principal_pattern,
        principal,
    ):
        return

    # An AWS IAM role ARN or federated user ARN, for example,
    # "arn:aws:iam::123456789012:role/role-name"
    if re.match(
        r"^arn:aws:iam::\d{12}:role\/" + principal_pattern,
        principal,
    ):
        return

    # An AWS IAM assumed-role session, for example,
    # "arn:aws:iam::123456789012:assumed-role/role-name/role-session-name"
    if re.match(
        r"^arn:aws:sts::\d{12}:assumed-role\/" + principal_pattern,
        principal,
    ):
        return

    # If the principal doesn't match any of the valid formats
    raise ValueError("principal is invalid")


def is_anonymous_user(principal: str) -> bool:
    """Checks if a principal is an anonymous user.

    Parameters
    ----------
    principal : str
        An AWS principal.

    Returns
    -------
    bool
        If principal is an anonymous user.
    """
    return bool(re.match(r"^\*$", principal))


def extract_application_name_from_stack_name(stack_name):
    """Extract the application name from the stack name

    Parameters
    ----------
    stack_name: str
        Stack name (microservice namespace)
    Returns
    -------
    str
    """
    application_name = stack_name
    stack_name_words = stack_name.split("-")
    if len(stack_name_words) > 1:
        expected_env_names = ("dev", "preprod", "prod", "testing", "research", "test")
        regex = f"^[a-zA-Z0-9-]+-({'|'.join(expected_env_names)})-[a-zA-Z0-9-]+$"
        if stack_name_words[-1] in expected_env_names:
            # Remove env name if stack name ends with the env name
            application_name = "-".join(stack_name_words[:-1])
        elif re.match(regex, application_name):
            # Remove everything after the env name, including the env name
            env = [w for w in stack_name_words if w in expected_env_names]
            application_name = application_name[: application_name.index(env[0]) - 1]

    return application_name


class Tagger:
    def __init__(
        self,
        environment_name: str,
        business_unit: Optional[str] = "Platforms",
        allowed_business_units: Optional[list] = None,
        application: Optional[str] = "Data Engineering",
        owner: Optional[
            str
        ] = "Data Engineering:dataengineering@digital.justice.gov.uk",
        **kwargs,
    ):
        """
        Provides a Tagger resource.

        Parameters
        ----------
        environment_name : str
            The name of the environment in which resources are deployed, for example,
            "alpha", "prod" or "dev".
        business_unit : str, optional
            The business unit of the team that owns the resources. Should be one of
            allowed_business_units.
            By default "Platforms".
        allowed_business_units : list, optional
            A list of allowed business units.
            By default, ["HQ", "HMPPS", "OPG", "LAA", "HMCTS", "CICA", "Platforms"].
        application : str, optional
            The application in which the resources are used.
            By default "Data Engineering".
        owner : str, optional
            The owner of the resources. This should be of the form
            <team-name>:<team-email>.
            By default "Data Engineering:dataengineering@digital.justice.gov.uk".

        """
        if allowed_business_units is None:
            self._allowed_business_units = [
                "HQ",
                "HMPPS",
                "OPG",
                "LAA",
                "HMCTS",
                "CICA",
                "Platforms",
            ]
        else:
            self._allowed_business_units = allowed_business_units

        if not isinstance(environment_name, str):
            raise TypeError("environment_name must be of type str")
        if not isinstance(business_unit, str):
            raise TypeError("business_unit must be of type str")
        if not isinstance(self._allowed_business_units, list):
            raise TypeError("allowed_business_units must be of type list")
        if not isinstance(application, str):
            raise TypeError("application must be of type str")
        if not isinstance(owner, str):
            raise TypeError("owner must be of type str")

        self._check_business_unit(business_unit, self._allowed_business_units)
        if "is_production" in kwargs:
            raise KeyError("is_production is not an allowed argument")

        self._global_tags = {
            "environment_name": environment_name,
            "business_unit": business_unit,
            "allowed_business_units": self._allowed_business_units,
            "application": application,
            "owner": owner,
        }
        self._global_tags.update(kwargs)

    def _check_business_unit(self, business_unit: str, allowed_business_units: list):
        """Checks if business_unit is an allowed value

        Parameters
        ----------
        business_unit : str
            The business unit of the team that owns the resources. This should be one of
            allowed_business_units.
        allowed_business_units : list
            A list of allowed business units.

        Raises
        ------
        ValueError
            If the value of business_unit is not allowed a ValueError will be raised.
        """
        if business_unit not in allowed_business_units:
            raise ValueError(
                f"business_unit must be one of {', '.join(allowed_business_units)}"
            )

    def create_tags(self, name: str, **kwargs) -> dict:
        """
        Creates a dictionary of mandatory and custom tags that can be passed to the tags
        argument of a Pulumi resource.

        Parameters
        ----------
        name : str
            The name of the resource for which the tags will be created. This should be
            the same as the name of the Pulumi resource to which you are adding the
            tags.

        Returns
        -------
        dict
            A dictionary of mandatory and custom tags that can be passed to the tags
            argument of a Pulumi resource.
        """
        if not isinstance(name, str):
            raise TypeError("name must be of type str")

        init_tags = self._global_tags
        init_tags.update(kwargs)
        tags = {}
        for key, value in init_tags.items():
            if key == "business_unit":
                self._check_business_unit(value, init_tags["allowed_business_units"])
            if key in ["is_production"]:
                raise KeyError(f"{key} is not an allowed argument")
            if key != "allowed_business_units":
                tags[key.replace("_", "-").lower()] = str(value)
        tags["is-production"] = str(tags["environment-name"] in ["alpha", "prod"])
        tags["Name"] = name
        return tags


class BucketDetails:
    def __init__(self, bucket_name: str):
        """Lets you use an existing bucket as the destination bucket, for example in
        a MoveObjectFunction. Insert the bucket's name and get a Bucket-like object
        that has name and Arn attributes.
        """
        self.name = bucket_name

    @property
    def arn(self) -> str:
        """Return s3 Arn based on the bucket's name."""
        return f"arn:aws:s3:::{self.name}"
