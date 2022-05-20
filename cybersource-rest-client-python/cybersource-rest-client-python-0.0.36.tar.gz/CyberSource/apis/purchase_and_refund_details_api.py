# coding: utf-8

"""
    CyberSource Merged Spec

    All CyberSource API specs merged together. These are available at https://developer.cybersource.com/api/reference/api-reference.html

    OpenAPI spec version: 0.0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient
import CyberSource.logging.log_factory as LogFactory


class PurchaseAndRefundDetailsApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """
	
    def __init__(self, merchant_config, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client
        self.api_client.set_configuration(merchant_config)
        self.logger = LogFactory.setup_logger(self.__class__.__name__, self.api_client.mconfig.log_config)



    def get_purchase_and_refund_details(self, start_time, end_time, **kwargs):
        """
        Get Purchase and Refund Details
        Download the Purchase and Refund Details report. This report report includes all purchases and refund transactions, as well as all activities related to transactions resulting in an adjustment to the net proceeds. 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_purchase_and_refund_details(start_time, end_time, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param datetime start_time: Valid report Start Time in **ISO 8601 format** Please refer the following link to know more about ISO 8601 format.[Rfc Date Format](https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14)  **Example date format:**   - yyyy-MM-dd'T'HH:mm:ss.SSSZ (e.g. 2018-01-01T00:00:00.000Z)  (required)
        :param datetime end_time: Valid report End Time in **ISO 8601 format** Please refer the following link to know more about ISO 8601 format.[Rfc Date Format](https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14)  **Example date format:**   - yyyy-MM-dd'T'HH:mm:ss.SSSZ (e.g. 2018-01-01T00:00:00.000Z)  (required)
        :param str organization_id: Valid Organization Id
        :param str payment_subtype: Payment Subtypes.   - **ALL**:  All Payment Subtypes   - **VI** :  Visa   - **MC** :  Master Card   - **AX** :  American Express   - **DI** :  Discover   - **DP** :  Pinless Debit 
        :param str view_by: View results by Request Date or Submission Date.   - **requestDate** : Request Date   - **submissionDate**: Submission Date 
        :param str group_name: Valid CyberSource Group Name.User can define groups using CBAPI and Group Management Module in EBC2. Groups are collection of organizationIds
        :param int offset: Offset of the Purchase and Refund Results.
        :param int limit: Results count per page. Range(1-2000)
        :return: ReportingV3PurchaseRefundDetailsGet200Response
                 If the method is called asynchronously,
                 returns the request thread.
        """

        if self.api_client.mconfig.log_config.enable_log:
            self.logger.info("CALL TO METHOD `get_purchase_and_refund_details` STARTED")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.get_purchase_and_refund_details_with_http_info(start_time, end_time, **kwargs)
        else:
            (data) = self.get_purchase_and_refund_details_with_http_info(start_time, end_time, **kwargs)
            return data

    def get_purchase_and_refund_details_with_http_info(self, start_time, end_time, **kwargs):
        """
        Get Purchase and Refund Details
        Download the Purchase and Refund Details report. This report report includes all purchases and refund transactions, as well as all activities related to transactions resulting in an adjustment to the net proceeds. 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_purchase_and_refund_details_with_http_info(start_time, end_time, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param datetime start_time: Valid report Start Time in **ISO 8601 format** Please refer the following link to know more about ISO 8601 format.[Rfc Date Format](https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14)  **Example date format:**   - yyyy-MM-dd'T'HH:mm:ss.SSSZ (e.g. 2018-01-01T00:00:00.000Z)  (required)
        :param datetime end_time: Valid report End Time in **ISO 8601 format** Please refer the following link to know more about ISO 8601 format.[Rfc Date Format](https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14)  **Example date format:**   - yyyy-MM-dd'T'HH:mm:ss.SSSZ (e.g. 2018-01-01T00:00:00.000Z)  (required)
        :param str organization_id: Valid Organization Id
        :param str payment_subtype: Payment Subtypes.   - **ALL**:  All Payment Subtypes   - **VI** :  Visa   - **MC** :  Master Card   - **AX** :  American Express   - **DI** :  Discover   - **DP** :  Pinless Debit 
        :param str view_by: View results by Request Date or Submission Date.   - **requestDate** : Request Date   - **submissionDate**: Submission Date 
        :param str group_name: Valid CyberSource Group Name.User can define groups using CBAPI and Group Management Module in EBC2. Groups are collection of organizationIds
        :param int offset: Offset of the Purchase and Refund Results.
        :param int limit: Results count per page. Range(1-2000)
        :return: ReportingV3PurchaseRefundDetailsGet200Response
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['start_time', 'end_time', 'organization_id', 'payment_subtype', 'view_by', 'group_name', 'offset', 'limit']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_purchase_and_refund_details" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'start_time' is set
        if ('start_time' not in params) or (params['start_time'] is None):
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Missing the required parameter `start_time` when calling `get_purchase_and_refund_details`")
            raise ValueError("Missing the required parameter `start_time` when calling `get_purchase_and_refund_details`")
        # verify the required parameter 'end_time' is set
        if ('end_time' not in params) or (params['end_time'] is None):
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Missing the required parameter `end_time` when calling `get_purchase_and_refund_details`")
            raise ValueError("Missing the required parameter `end_time` when calling `get_purchase_and_refund_details`")

        if 'organization_id' in params and len(params['organization_id']) > 32:
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, length must be less than or equal to `32`")
            raise ValueError("Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, length must be less than or equal to `32`")
        if 'organization_id' in params and len(params['organization_id']) < 1:
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, length must be greater than or equal to `1`")
            raise ValueError("Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, length must be greater than or equal to `1`")
        if 'organization_id' in params and not re.search('[a-zA-Z0-9-_]+', params['organization_id']):
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, must conform to the pattern `/[a-zA-Z0-9-_]+/`")
            raise ValueError("Invalid value for parameter `organization_id` when calling `get_purchase_and_refund_details`, must conform to the pattern `/[a-zA-Z0-9-_]+/`")
        if 'limit' in params and params['limit'] > 2000:
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Invalid value for parameter `limit` when calling `get_purchase_and_refund_details`, must be a value less than or equal to `2000`")
            raise ValueError("Invalid value for parameter `limit` when calling `get_purchase_and_refund_details`, must be a value less than or equal to `2000`")
        if 'limit' in params and params['limit'] < 1:
            if self.api_client.mconfig.log_config.enable_log:
                self.logger.error("InvalidArgumentException : Invalid value for parameter `limit` when calling `get_purchase_and_refund_details`, must be a value greater than or equal to `1`")
            raise ValueError("Invalid value for parameter `limit` when calling `get_purchase_and_refund_details`, must be a value greater than or equal to `1`")

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'start_time' in params:
            query_params.append(('startTime', params['start_time']))
        if 'end_time' in params:
            query_params.append(('endTime', params['end_time']))
        if 'organization_id' in params:
            query_params.append(('organizationId', params['organization_id']))
        if 'payment_subtype' in params:
            query_params.append(('paymentSubtype', params['payment_subtype']))
        if 'view_by' in params:
            query_params.append(('viewBy', params['view_by']))
        if 'group_name' in params:
            query_params.append(('groupName', params['group_name']))
        if 'offset' in params:
            query_params.append(('offset', params['offset']))
        if 'limit' in params:
            query_params.append(('limit', params['limit']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'GET' in ('POST'):
            body_params = '{}'
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/hal+json', 'application/xml', 'text/csv'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json;charset=utf-8'])

        # Authentication setting
        auth_settings = []

        return self.api_client.call_api(f'/reporting/v3/purchase-refund-details', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ReportingV3PurchaseRefundDetailsGet200Response',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
