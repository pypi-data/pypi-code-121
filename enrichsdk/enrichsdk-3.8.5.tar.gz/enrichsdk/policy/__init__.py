import json
import re
import logging

logger = logging.getLogger("app")

__all__ = ["BasePolicyEngine", "BaseResource", "BasePrincipal"]


class BaseResource(object):
    """Resource base class

    This will encapsulate data and matching patterns
    """

    def __init__(self, name, *args, **kwargs):
        if not isinstance(name, str) or len(name) == 0:
            raise Exception("Invalid resource name")

        self.name = name

    def match(self, name):
        return re.match(name, self.name) is not None

    def enforce(self, principal, action, args):
        return {"status": action, "details": args}


class BasePrincipal(object):
    """Principal base class

    This will encapsulate information about the principal
    (who) is asking for access
    """

    def __init__(self, identifiers, roles, attrs, *args, **kwargs):

        if (
            (identifiers is None)
            or (not isinstance(identifiers, list))
            or (len(identifiers) == 0)
        ):
            raise Exception("Invalid identifier specification")

        for i in identifiers:
            if (not isinstance(i, str)) or (len(i) == 0):
                raise Exception(
                    "Invalid identifier specification. Each identifier must be a non-trivial string"
                )

        if (roles is None) or (not isinstance(roles, dict)) or (len(roles) == 0):
            raise Exception("Invalid role specification")

        for r in roles:
            if (
                (not isinstance(r, str))
                or (len(r) == 0)
                or (not isinstance(roles[r], list))
                or (len(roles[r]) == 0)
            ):
                raise Exception(
                    "Invalid role specification Every role should be associated with a list of strings"
                )

        if (attrs is None) or (not isinstance(attrs, dict)) or (len(attrs) == 0):
            raise Exception("Invalid attribute specification. Not a dictionary")

        for a in attrs:
            if (not isinstance(a, str)) or (len(a) == 0):
                raise Exception(
                    "Invalid attribute specification. Every attribute name must be a string"
                )

        self.roles = roles
        self.identifiers = identifiers
        self.attrs = attrs

    def match(self, name):

        # First match the identifiers
        for i in self.identifiers:
            if re.match(name, i) is not None:
                return True

        for r, namelist in self.roles.items():
            for n in namelist:
                role = "Role::{}::{}".format(r, n)
                if re.match(name, role) is not None:
                    return True

        return False

    def get_attr(self, name):
        if not name.startswith("principal::"):
            raise Exception("Invalid attribute")

        if name not in self.attrs:
            raise Exception("Could not find attribute")

        return self.attrs[name]


class BasePolicyEngine(object):
    """Policy base class

    This is still work in progress. The goal is to support

    (a) row-level visibility of data (e.g., some store managers
        seeing only their store's data)
    (b) Possible anonymization and other special functions

    All principals and resources are strings that specify
    patterns. Examples include:

    (a) username::<name> (principal)
    (b) username::* (principal)
    (c) DailySummary::user_profile (resource)


    """

    NAME = "BasePolicy"

    def __init__(self, *args, **kwargs):

        self.spec = None
        self.args = None

    def configure(self, spec):
        """
        Configure an instance of the policy implementor with a
        specification

        Args:
          spec (dict): Specification

        """

        if not isinstance(spec, dict):
            raise Exception("Invalid specification format")

        self.spec = spec
        self.args = spec.get("args", {})

    def validate(self):
        """
        Validate the specification. Raise an exception if
        invalid
        """

        if self.args is None:
            raise Exception("Policy not configured")

        if "policies" not in self.args:
            raise Exception("Missing policy specification")

        policies = self.args["policies"]

        if not isinstance(policies, list):
            raise Exception("Policy specification must be a list")

        if len(policies) == 0:
            raise Exception("Empty list of policies")

        for p in policies:

            # => Is the specification valid?
            if (
                (not isinstance(p, dict))
                or (("principal" not in p) or (p["principal"] in [None, ""]))
                or (("resource" not in p) or (p["resource"] in [None, ""]))
                or (("action" not in p) or (p["action"] in [None, ""]))
            ):
                raise Exception(
                    "Invalid specification. Each policy should be a dictionary with a definition of principal, resource, and actions "
                )

            action = p["action"]
            if action not in ["allow", "deny", "filter"]:
                raise Exception("Invalid action in specification")

            if "args" in p and not isinstance(p["args"], dict):
                raise Exception(
                    "Invalid specification. Action args when specified should be a dict"
                )

            nomatch = p.get("nomatch", "pass")
            if nomatch not in ["allow", "deny", "pass"]:
                raise Exception(
                    "Invalid specification. Nomatch rule must be either allow, deny, or pass. Default is pass"
                )

    def apply(self, principal, resource):
        """
        Apply the policy specification

        Args:
          principal (str): username/other identifier
          resource (dict): resource name

        Returns:
          dict: Output with result of the policy check ('status') and the data

        """

        deny_response = {"status": "deny"}

        if not issubclass(principal.__class__, BasePrincipal):
            raise Exception("Principal should be a subclass of BasePrincipal")

        if not issubclass(resource.__class__, BaseResource):
            raise Exception("resource should be a subclass of BaseResource")

        for i, p in enumerate(self.args["policies"]):

            name = p.get("name", "Policy{}".format(i))
            logger.debug("Matching:", name)
            logger.debug("Principal:", p["principal"], principal.match(p["principal"]))
            logger.debug("Resource:", p["resource"], resource.match(p["resource"]))

            nomatch = p.get("nomatch", "pass")
            args = p.get("args", {})

            if principal.match(p["principal"]) and resource.match(p["resource"]):
                action = p["action"]
                logger.debug("Action:", action)
                if action == "deny":
                    return deny_response
                return resource.enforce(principal, action, args)
            else:
                if nomatch == "pass":
                    continue
                elif nomatch == "allow":
                    return resource.enforce(principal, nomatch, args)
                else:
                    return deny_response

        # No match for any policy
        return {"status": "deny"}


if __name__ == "__main__":
    print(vars())
    subclasses = vars()["BasePolicy"].__subclasses__()
    for cls in subclasses:
        print(cls.NAME)
