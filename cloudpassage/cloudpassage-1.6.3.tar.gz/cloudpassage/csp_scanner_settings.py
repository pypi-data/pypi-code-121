"""CspSetting class"""

from .halo_endpoint import HaloEndpoint
from .http_helper import HttpHelper
from .utility import Utility as utility


class CspSetting(HaloEndpoint):
    """Initializing the CspSetting class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.

    """

    object_name = "csp_scanner_setting"
    objects_name = "csp_scanner_settings"
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

    def view(self):
        """View current CSP scanner settings

        Returns:
            dict: Dictionary of current CSP scan settings

        """
        request = HttpHelper(self.session)
        return request.get(self.endpoint())

    def update(self, object_body):
        """Update CSP scanner settings

        Args:
            object_body (dict): Dictionary of new settings
            (https://api-doc.cloudpassage.com/help#csp-update-scan-settings)

        Returns:
            None if successful, raises exception if not

        """
        request = HttpHelper(self.session)
        request_body = utility.policy_to_dict(object_body)
        request.put(self.endpoint(), request_body)
        return None

    def create(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def delete(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def describe(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def list_all(self):
        """Not implemented for this object."""
        raise NotImplementedError
