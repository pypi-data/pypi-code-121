"""CspFinding class"""

from .halo_endpoint import HaloEndpoint


class CspFinding(HaloEndpoint):
    """Initializing the CspAccount class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.

    """

    object_name = "csp_finding"
    objects_name = "csp_findings"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def pagination_key(self):
        """Return the pagination key for parsing paged results."""
        return self.objects_name

    def object_key(self):
        """Return the object key for parsing detailed results."""
        return self.object_name

    def list_all(self, **kwargs):
        """Lists all CSP Findings.

        Keyword Args:
            csp_rule_id (str or list): The user-readable ID of the rule.
                Example: CIS:1.1
            rule_id (str or list):
                The UUID number of the rule that was applied;
                for example, 280d33b6ef3411e88ad765862e629d59
            csp_resource_type (str or list): The type of cloud resource;
                for example, Policy, Role, User, and so on
            csp_service_type (str or list): The type of cloud service;
                for example, IAM, S3, EC2, and so on
            policy_name (str or list): The name of the policy that was applied;
                for example, CIS-Benchmark
            rule_name (str or list): The name of the rule that was applied;
                for example Ensure MFA is enabled for the "root" account

        Returns:
            list: List of CSP Findings represented as dictionary-type objects
        """
        return super(CspFinding, self).list_all(**kwargs)

    def describe(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def create(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def delete(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def update(self):
        """Not implemented for this object."""
        raise NotImplementedError
