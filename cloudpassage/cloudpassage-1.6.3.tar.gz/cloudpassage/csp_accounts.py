"""CspAccount class"""

import cloudpassage.sanity as sanity
from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class CspAccount(HaloEndpoint):
    """Initializing the CspAccount class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.


    Supported keyword args for filtering CspAccount.list_all():

    """

    object_name = "csp_account"
    objects_name = "csp_accounts"
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

    def activate(self, halo_csp_account_id):
        """This method activates a CSP Account

        Args:
            halo_csp_account_id (str): Internal Halo ID of CSP Account

        Returns:
            True if successful, throws exception on failure

        """

        sanity.validate_object_id(halo_csp_account_id)
        endpoint = "{}/{}".format(self.endpoint(), halo_csp_account_id)
        body = {"monitoring_state": "active"}
        request = HttpHelper(self.session)
        request.put(endpoint, body)
        # Exceptions fire deeper if this fails.  Otherwise, return True.
        return True

    def deactivate(self, halo_csp_account_id):
        """This method deactivates a CSP Account

        Args:
            halo_csp_account_id (str): Internal Halo ID of CSP Account

        Returns:
            True if successful, throws exception on failure

        """

        sanity.validate_object_id(halo_csp_account_id)
        endpoint = "{}/{}".format(self.endpoint(), halo_csp_account_id)
        body = {"monitoring_state": "inactive"}
        request = HttpHelper(self.session)
        request.put(endpoint, body)
        # Exceptions fire deeper if this fails.  Otherwise, return True.
        return True

    def scan(self, halo_csp_account_id):
        """This method initiates a scan of a CSP account
            manually outside of its existing schedule.

        Args:
            halo_csp_account_id (str): Internal Halo ID of CSP Account

        Returns:
            True if successful, throws exception on failure
        """

        sanity.validate_object_id(halo_csp_account_id)
        endpoint = "{}/{}/scan_now".format(self.endpoint(),
                                           halo_csp_account_id)
        body = {}
        request = HttpHelper(self.session)
        response = request.post(endpoint, body)
        return response
