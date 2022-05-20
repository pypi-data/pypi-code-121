"""
    Agilicus API

    Agilicus is API-first. Modern software is controlled by other software, is open, is available for you to use the way you want, securely, simply.  A rendered, online viewable and usable version of this specification is available at [api](https://www.agilicus.com/api). You may try the API inline directly in the web page. To do so, first obtain an Authentication Token (the simplest way is to install the Python SDK, and then run `agilicus-cli --issuer https://MYISSUER get-token`). You will need an org-id for most calls (and can obtain from `agilicus-cli --issuer https://MYISSUER list-orgs`). The `MYISSUER` will typically be `auth.MYDOMAIN`, and you will see it as you sign-in to the administrative UI.  This API releases on Bearer-Token authentication. To obtain a valid bearer token you will need to Authenticate to an Issuer with OpenID Connect (a superset of OAUTH2).  Your \"issuer\" will look like https://auth.MYDOMAIN. For example, when you signed-up, if you said \"use my own domain name\" and assigned a CNAME of cloud.example.com, then your issuer would be https://auth.cloud.example.com.  If you selected \"use an Agilicus supplied domain name\", your issuer would look like https://auth.myorg.agilicus.cloud.  For test purposes you can use our [Python SDK](https://pypi.org/project/agilicus/) and run `agilicus-cli --issuer https://auth.MYDOMAIN get-token`.  This API may be used in any language runtime that supports OpenAPI 3.0, or, you may use our [Python SDK](https://pypi.org/project/agilicus/), our [Typescript SDK](https://www.npmjs.com/package/@agilicus/angular), or our [Golang SDK](https://git.agilicus.com/pub/sdk-go).  100% of the activities in our system our API-driven, from our web-admin, through our progressive web applications, to all internals: there is nothing that is not accessible.  For more information, see [developer resources](https://www.agilicus.com/developer).   # noqa: E501

    The version of the OpenAPI document: 2022.05.18
    Contact: dev@agilicus.com
    Generated by: https://openapi-generator.tech
"""


import unittest

import agilicus_api
from agilicus_api.api.connectors_api import ConnectorsApi  # noqa: E501


class TestConnectorsApi(unittest.TestCase):
    """ConnectorsApi unit test stubs"""

    def setUp(self):
        self.api = ConnectorsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_agent_connector(self):
        """Test case for create_agent_connector

        Create an agent connector  # noqa: E501
        """
        pass

    def test_create_agent_csr(self):
        """Test case for create_agent_csr

        Creates a CertSigningReq  # noqa: E501
        """
        pass

    def test_create_agent_stats(self):
        """Test case for create_agent_stats

        Creates an AgentConnectorStats record.  # noqa: E501
        """
        pass

    def test_create_csr(self):
        """Test case for create_csr

        Creates a CertSigningReq  # noqa: E501
        """
        pass

    def test_create_ipsec_connector(self):
        """Test case for create_ipsec_connector

        Create an IPsec connector  # noqa: E501
        """
        pass

    def test_delete_agent_connector(self):
        """Test case for delete_agent_connector

        Delete a agent  # noqa: E501
        """
        pass

    def test_delete_connector(self):
        """Test case for delete_connector

        Delete a connector  # noqa: E501
        """
        pass

    def test_delete_ipsec_connector(self):
        """Test case for delete_ipsec_connector

        Delete an IPsec connector  # noqa: E501
        """
        pass

    def test_get_agent_connector(self):
        """Test case for get_agent_connector

        Get an agent  # noqa: E501
        """
        pass

    def test_get_agent_csr(self):
        """Test case for get_agent_csr

        Update a CertSigningReq  # noqa: E501
        """
        pass

    def test_get_agent_info(self):
        """Test case for get_agent_info

        Get information associated with connector  # noqa: E501
        """
        pass

    def test_get_agent_stats(self):
        """Test case for get_agent_stats

        Get the AgentConnector stats  # noqa: E501
        """
        pass

    def test_get_connector(self):
        """Test case for get_connector

        Get a connector  # noqa: E501
        """
        pass

    def test_get_ipsec_connector(self):
        """Test case for get_ipsec_connector

        Get an IPsec connector  # noqa: E501
        """
        pass

    def test_get_ipsec_connector_info(self):
        """Test case for get_ipsec_connector_info

        Get IPsec connector runtime information  # noqa: E501
        """
        pass

    def test_list_agent_connector(self):
        """Test case for list_agent_connector

        list agent connectors  # noqa: E501
        """
        pass

    def test_list_agent_csr(self):
        """Test case for list_agent_csr

        list agent connector certificate signing requests  # noqa: E501
        """
        pass

    def test_list_connector(self):
        """Test case for list_connector

        List connectors  # noqa: E501
        """
        pass

    def test_list_connector_guid_mapping(self):
        """Test case for list_connector_guid_mapping

        Get all connector guids and a unique name mapping  # noqa: E501
        """
        pass

    def test_list_ipsec_connector(self):
        """Test case for list_ipsec_connector

        list IPsec connectors  # noqa: E501
        """
        pass

    def test_replace_agent_connector(self):
        """Test case for replace_agent_connector

        Update an agent  # noqa: E501
        """
        pass

    def test_replace_agent_connector_local_auth_info(self):
        """Test case for replace_agent_connector_local_auth_info

        Update an agent's local authentication information  # noqa: E501
        """
        pass

    def test_replace_agent_csr(self):
        """Test case for replace_agent_csr

        Update a CertSigningReq  # noqa: E501
        """
        pass

    def test_replace_ipsec_connector(self):
        """Test case for replace_ipsec_connector

        Update an IPsec connector  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
