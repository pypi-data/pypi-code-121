"""
Type annotations for appflow service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_appflow/type_defs/)

Usage::

    ```python
    from mypy_boto3_appflow.type_defs import AggregationConfigTypeDef

    data: AggregationConfigTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    AggregationTypeType,
    AuthenticationTypeType,
    ConnectionModeType,
    ConnectorTypeType,
    DatadogConnectorOperatorType,
    DataPullModeType,
    DynatraceConnectorOperatorType,
    ExecutionStatusType,
    FileTypeType,
    FlowStatusType,
    GoogleAnalyticsConnectorOperatorType,
    InforNexusConnectorOperatorType,
    MarketoConnectorOperatorType,
    OAuth2CustomPropTypeType,
    OAuth2GrantTypeType,
    OperatorPropertiesKeysType,
    OperatorsType,
    OperatorType,
    PrefixFormatType,
    PrefixTypeType,
    PrivateConnectionProvisioningFailureCauseType,
    PrivateConnectionProvisioningStatusType,
    S3ConnectorOperatorType,
    S3InputFileTypeType,
    SalesforceConnectorOperatorType,
    SAPODataConnectorOperatorType,
    ScheduleFrequencyTypeType,
    ServiceNowConnectorOperatorType,
    SingularConnectorOperatorType,
    SlackConnectorOperatorType,
    TaskTypeType,
    TrendmicroConnectorOperatorType,
    TriggerTypeType,
    VeevaConnectorOperatorType,
    WriteOperationTypeType,
    ZendeskConnectorOperatorType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AggregationConfigTypeDef",
    "AmplitudeConnectorProfileCredentialsTypeDef",
    "AmplitudeSourcePropertiesTypeDef",
    "ApiKeyCredentialsTypeDef",
    "AuthParameterTypeDef",
    "BasicAuthCredentialsTypeDef",
    "ConnectorRuntimeSettingTypeDef",
    "ConnectorDetailTypeDef",
    "DestinationFieldPropertiesTypeDef",
    "SourceFieldPropertiesTypeDef",
    "ConnectorEntityTypeDef",
    "GoogleAnalyticsMetadataTypeDef",
    "HoneycodeMetadataTypeDef",
    "SalesforceMetadataTypeDef",
    "SlackMetadataTypeDef",
    "SnowflakeMetadataTypeDef",
    "ZendeskMetadataTypeDef",
    "ConnectorOAuthRequestTypeDef",
    "ConnectorOperatorTypeDef",
    "DatadogConnectorProfileCredentialsTypeDef",
    "DynatraceConnectorProfileCredentialsTypeDef",
    "InforNexusConnectorProfileCredentialsTypeDef",
    "RedshiftConnectorProfileCredentialsTypeDef",
    "ServiceNowConnectorProfileCredentialsTypeDef",
    "SingularConnectorProfileCredentialsTypeDef",
    "SnowflakeConnectorProfileCredentialsTypeDef",
    "TrendmicroConnectorProfileCredentialsTypeDef",
    "VeevaConnectorProfileCredentialsTypeDef",
    "DatadogConnectorProfilePropertiesTypeDef",
    "DynatraceConnectorProfilePropertiesTypeDef",
    "InforNexusConnectorProfilePropertiesTypeDef",
    "MarketoConnectorProfilePropertiesTypeDef",
    "RedshiftConnectorProfilePropertiesTypeDef",
    "SalesforceConnectorProfilePropertiesTypeDef",
    "ServiceNowConnectorProfilePropertiesTypeDef",
    "SlackConnectorProfilePropertiesTypeDef",
    "SnowflakeConnectorProfilePropertiesTypeDef",
    "VeevaConnectorProfilePropertiesTypeDef",
    "ZendeskConnectorProfilePropertiesTypeDef",
    "PrivateConnectionProvisioningStateTypeDef",
    "LambdaConnectorProvisioningConfigTypeDef",
    "ResponseMetadataTypeDef",
    "CustomAuthCredentialsTypeDef",
    "ErrorHandlingConfigTypeDef",
    "OAuth2PropertiesTypeDef",
    "CustomConnectorSourcePropertiesTypeDef",
    "CustomerProfilesDestinationPropertiesTypeDef",
    "DatadogSourcePropertiesTypeDef",
    "DeleteConnectorProfileRequestRequestTypeDef",
    "DeleteFlowRequestRequestTypeDef",
    "DescribeConnectorEntityRequestRequestTypeDef",
    "DescribeConnectorProfilesRequestRequestTypeDef",
    "DescribeConnectorRequestRequestTypeDef",
    "DescribeConnectorsRequestRequestTypeDef",
    "DescribeFlowExecutionRecordsRequestRequestTypeDef",
    "DescribeFlowRequestRequestTypeDef",
    "ExecutionDetailsTypeDef",
    "DynatraceSourcePropertiesTypeDef",
    "ErrorInfoTypeDef",
    "RangeTypeDef",
    "GoogleAnalyticsSourcePropertiesTypeDef",
    "IncrementalPullConfigTypeDef",
    "InforNexusSourcePropertiesTypeDef",
    "ListConnectorEntitiesRequestRequestTypeDef",
    "ListConnectorsRequestRequestTypeDef",
    "ListFlowsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "MarketoSourcePropertiesTypeDef",
    "OAuth2CustomParameterTypeDef",
    "OAuthPropertiesTypeDef",
    "PrefixConfigTypeDef",
    "S3InputFormatConfigTypeDef",
    "SuccessResponseHandlingConfigTypeDef",
    "SAPODataSourcePropertiesTypeDef",
    "SalesforceSourcePropertiesTypeDef",
    "ScheduledTriggerPropertiesTypeDef",
    "ServiceNowSourcePropertiesTypeDef",
    "SingularSourcePropertiesTypeDef",
    "SlackSourcePropertiesTypeDef",
    "TrendmicroSourcePropertiesTypeDef",
    "VeevaSourcePropertiesTypeDef",
    "ZendeskSourcePropertiesTypeDef",
    "StartFlowRequestRequestTypeDef",
    "StopFlowRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UnregisterConnectorRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "CustomAuthConfigTypeDef",
    "ConnectorMetadataTypeDef",
    "GoogleAnalyticsConnectorProfileCredentialsTypeDef",
    "HoneycodeConnectorProfileCredentialsTypeDef",
    "MarketoConnectorProfileCredentialsTypeDef",
    "OAuth2CredentialsTypeDef",
    "OAuthCredentialsTypeDef",
    "SalesforceConnectorProfileCredentialsTypeDef",
    "SlackConnectorProfileCredentialsTypeDef",
    "ZendeskConnectorProfileCredentialsTypeDef",
    "TaskTypeDef",
    "ConnectorProvisioningConfigTypeDef",
    "CreateConnectorProfileResponseTypeDef",
    "CreateFlowResponseTypeDef",
    "ListConnectorEntitiesResponseTypeDef",
    "ListConnectorsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "RegisterConnectorResponseTypeDef",
    "StartFlowResponseTypeDef",
    "StopFlowResponseTypeDef",
    "UpdateConnectorProfileResponseTypeDef",
    "UpdateFlowResponseTypeDef",
    "CustomConnectorDestinationPropertiesTypeDef",
    "EventBridgeDestinationPropertiesTypeDef",
    "HoneycodeDestinationPropertiesTypeDef",
    "MarketoDestinationPropertiesTypeDef",
    "RedshiftDestinationPropertiesTypeDef",
    "SalesforceDestinationPropertiesTypeDef",
    "SnowflakeDestinationPropertiesTypeDef",
    "ZendeskDestinationPropertiesTypeDef",
    "CustomConnectorProfilePropertiesTypeDef",
    "FlowDefinitionTypeDef",
    "ExecutionResultTypeDef",
    "FieldTypeDetailsTypeDef",
    "OAuth2DefaultsTypeDef",
    "SAPODataConnectorProfilePropertiesTypeDef",
    "S3OutputFormatConfigTypeDef",
    "UpsolverS3OutputFormatConfigTypeDef",
    "S3SourcePropertiesTypeDef",
    "SAPODataDestinationPropertiesTypeDef",
    "TriggerPropertiesTypeDef",
    "CustomConnectorProfileCredentialsTypeDef",
    "SAPODataConnectorProfileCredentialsTypeDef",
    "RegisterConnectorRequestRequestTypeDef",
    "ListFlowsResponseTypeDef",
    "ExecutionRecordTypeDef",
    "SupportedFieldTypeDetailsTypeDef",
    "AuthenticationConfigTypeDef",
    "ConnectorProfilePropertiesTypeDef",
    "S3DestinationPropertiesTypeDef",
    "UpsolverDestinationPropertiesTypeDef",
    "SourceConnectorPropertiesTypeDef",
    "TriggerConfigTypeDef",
    "ConnectorProfileCredentialsTypeDef",
    "DescribeFlowExecutionRecordsResponseTypeDef",
    "ConnectorEntityFieldTypeDef",
    "ConnectorConfigurationTypeDef",
    "ConnectorProfileTypeDef",
    "DestinationConnectorPropertiesTypeDef",
    "SourceFlowConfigTypeDef",
    "ConnectorProfileConfigTypeDef",
    "DescribeConnectorEntityResponseTypeDef",
    "DescribeConnectorResponseTypeDef",
    "DescribeConnectorsResponseTypeDef",
    "DescribeConnectorProfilesResponseTypeDef",
    "DestinationFlowConfigTypeDef",
    "CreateConnectorProfileRequestRequestTypeDef",
    "UpdateConnectorProfileRequestRequestTypeDef",
    "CreateFlowRequestRequestTypeDef",
    "DescribeFlowResponseTypeDef",
    "UpdateFlowRequestRequestTypeDef",
)

AggregationConfigTypeDef = TypedDict(
    "AggregationConfigTypeDef",
    {
        "aggregationType": AggregationTypeType,
    },
    total=False,
)

AmplitudeConnectorProfileCredentialsTypeDef = TypedDict(
    "AmplitudeConnectorProfileCredentialsTypeDef",
    {
        "apiKey": str,
        "secretKey": str,
    },
)

AmplitudeSourcePropertiesTypeDef = TypedDict(
    "AmplitudeSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

_RequiredApiKeyCredentialsTypeDef = TypedDict(
    "_RequiredApiKeyCredentialsTypeDef",
    {
        "apiKey": str,
    },
)
_OptionalApiKeyCredentialsTypeDef = TypedDict(
    "_OptionalApiKeyCredentialsTypeDef",
    {
        "apiSecretKey": str,
    },
    total=False,
)


class ApiKeyCredentialsTypeDef(
    _RequiredApiKeyCredentialsTypeDef, _OptionalApiKeyCredentialsTypeDef
):
    pass


AuthParameterTypeDef = TypedDict(
    "AuthParameterTypeDef",
    {
        "key": str,
        "isRequired": bool,
        "label": str,
        "description": str,
        "isSensitiveField": bool,
        "connectorSuppliedValues": List[str],
    },
    total=False,
)

BasicAuthCredentialsTypeDef = TypedDict(
    "BasicAuthCredentialsTypeDef",
    {
        "username": str,
        "password": str,
    },
)

ConnectorRuntimeSettingTypeDef = TypedDict(
    "ConnectorRuntimeSettingTypeDef",
    {
        "key": str,
        "dataType": str,
        "isRequired": bool,
        "label": str,
        "description": str,
        "scope": str,
        "connectorSuppliedValueOptions": List[str],
    },
    total=False,
)

ConnectorDetailTypeDef = TypedDict(
    "ConnectorDetailTypeDef",
    {
        "connectorDescription": str,
        "connectorName": str,
        "connectorOwner": str,
        "connectorVersion": str,
        "applicationType": str,
        "connectorType": ConnectorTypeType,
        "connectorLabel": str,
        "registeredAt": datetime,
        "registeredBy": str,
        "connectorProvisioningType": Literal["LAMBDA"],
        "connectorModes": List[str],
    },
    total=False,
)

DestinationFieldPropertiesTypeDef = TypedDict(
    "DestinationFieldPropertiesTypeDef",
    {
        "isCreatable": bool,
        "isNullable": bool,
        "isUpsertable": bool,
        "isUpdatable": bool,
        "isDefaultedOnCreate": bool,
        "supportedWriteOperations": List[WriteOperationTypeType],
    },
    total=False,
)

SourceFieldPropertiesTypeDef = TypedDict(
    "SourceFieldPropertiesTypeDef",
    {
        "isRetrievable": bool,
        "isQueryable": bool,
        "isTimestampFieldForIncrementalQueries": bool,
    },
    total=False,
)

_RequiredConnectorEntityTypeDef = TypedDict(
    "_RequiredConnectorEntityTypeDef",
    {
        "name": str,
    },
)
_OptionalConnectorEntityTypeDef = TypedDict(
    "_OptionalConnectorEntityTypeDef",
    {
        "label": str,
        "hasNestedEntities": bool,
    },
    total=False,
)


class ConnectorEntityTypeDef(_RequiredConnectorEntityTypeDef, _OptionalConnectorEntityTypeDef):
    pass


GoogleAnalyticsMetadataTypeDef = TypedDict(
    "GoogleAnalyticsMetadataTypeDef",
    {
        "oAuthScopes": List[str],
    },
    total=False,
)

HoneycodeMetadataTypeDef = TypedDict(
    "HoneycodeMetadataTypeDef",
    {
        "oAuthScopes": List[str],
    },
    total=False,
)

SalesforceMetadataTypeDef = TypedDict(
    "SalesforceMetadataTypeDef",
    {
        "oAuthScopes": List[str],
    },
    total=False,
)

SlackMetadataTypeDef = TypedDict(
    "SlackMetadataTypeDef",
    {
        "oAuthScopes": List[str],
    },
    total=False,
)

SnowflakeMetadataTypeDef = TypedDict(
    "SnowflakeMetadataTypeDef",
    {
        "supportedRegions": List[str],
    },
    total=False,
)

ZendeskMetadataTypeDef = TypedDict(
    "ZendeskMetadataTypeDef",
    {
        "oAuthScopes": List[str],
    },
    total=False,
)

ConnectorOAuthRequestTypeDef = TypedDict(
    "ConnectorOAuthRequestTypeDef",
    {
        "authCode": str,
        "redirectUri": str,
    },
    total=False,
)

ConnectorOperatorTypeDef = TypedDict(
    "ConnectorOperatorTypeDef",
    {
        "Amplitude": Literal["BETWEEN"],
        "Datadog": DatadogConnectorOperatorType,
        "Dynatrace": DynatraceConnectorOperatorType,
        "GoogleAnalytics": GoogleAnalyticsConnectorOperatorType,
        "InforNexus": InforNexusConnectorOperatorType,
        "Marketo": MarketoConnectorOperatorType,
        "S3": S3ConnectorOperatorType,
        "Salesforce": SalesforceConnectorOperatorType,
        "ServiceNow": ServiceNowConnectorOperatorType,
        "Singular": SingularConnectorOperatorType,
        "Slack": SlackConnectorOperatorType,
        "Trendmicro": TrendmicroConnectorOperatorType,
        "Veeva": VeevaConnectorOperatorType,
        "Zendesk": ZendeskConnectorOperatorType,
        "SAPOData": SAPODataConnectorOperatorType,
        "CustomConnector": OperatorType,
    },
    total=False,
)

DatadogConnectorProfileCredentialsTypeDef = TypedDict(
    "DatadogConnectorProfileCredentialsTypeDef",
    {
        "apiKey": str,
        "applicationKey": str,
    },
)

DynatraceConnectorProfileCredentialsTypeDef = TypedDict(
    "DynatraceConnectorProfileCredentialsTypeDef",
    {
        "apiToken": str,
    },
)

InforNexusConnectorProfileCredentialsTypeDef = TypedDict(
    "InforNexusConnectorProfileCredentialsTypeDef",
    {
        "accessKeyId": str,
        "userId": str,
        "secretAccessKey": str,
        "datakey": str,
    },
)

RedshiftConnectorProfileCredentialsTypeDef = TypedDict(
    "RedshiftConnectorProfileCredentialsTypeDef",
    {
        "username": str,
        "password": str,
    },
)

ServiceNowConnectorProfileCredentialsTypeDef = TypedDict(
    "ServiceNowConnectorProfileCredentialsTypeDef",
    {
        "username": str,
        "password": str,
    },
)

SingularConnectorProfileCredentialsTypeDef = TypedDict(
    "SingularConnectorProfileCredentialsTypeDef",
    {
        "apiKey": str,
    },
)

SnowflakeConnectorProfileCredentialsTypeDef = TypedDict(
    "SnowflakeConnectorProfileCredentialsTypeDef",
    {
        "username": str,
        "password": str,
    },
)

TrendmicroConnectorProfileCredentialsTypeDef = TypedDict(
    "TrendmicroConnectorProfileCredentialsTypeDef",
    {
        "apiSecretKey": str,
    },
)

VeevaConnectorProfileCredentialsTypeDef = TypedDict(
    "VeevaConnectorProfileCredentialsTypeDef",
    {
        "username": str,
        "password": str,
    },
)

DatadogConnectorProfilePropertiesTypeDef = TypedDict(
    "DatadogConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

DynatraceConnectorProfilePropertiesTypeDef = TypedDict(
    "DynatraceConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

InforNexusConnectorProfilePropertiesTypeDef = TypedDict(
    "InforNexusConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

MarketoConnectorProfilePropertiesTypeDef = TypedDict(
    "MarketoConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

_RequiredRedshiftConnectorProfilePropertiesTypeDef = TypedDict(
    "_RequiredRedshiftConnectorProfilePropertiesTypeDef",
    {
        "databaseUrl": str,
        "bucketName": str,
        "roleArn": str,
    },
)
_OptionalRedshiftConnectorProfilePropertiesTypeDef = TypedDict(
    "_OptionalRedshiftConnectorProfilePropertiesTypeDef",
    {
        "bucketPrefix": str,
    },
    total=False,
)


class RedshiftConnectorProfilePropertiesTypeDef(
    _RequiredRedshiftConnectorProfilePropertiesTypeDef,
    _OptionalRedshiftConnectorProfilePropertiesTypeDef,
):
    pass


SalesforceConnectorProfilePropertiesTypeDef = TypedDict(
    "SalesforceConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
        "isSandboxEnvironment": bool,
    },
    total=False,
)

ServiceNowConnectorProfilePropertiesTypeDef = TypedDict(
    "ServiceNowConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

SlackConnectorProfilePropertiesTypeDef = TypedDict(
    "SlackConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

_RequiredSnowflakeConnectorProfilePropertiesTypeDef = TypedDict(
    "_RequiredSnowflakeConnectorProfilePropertiesTypeDef",
    {
        "warehouse": str,
        "stage": str,
        "bucketName": str,
    },
)
_OptionalSnowflakeConnectorProfilePropertiesTypeDef = TypedDict(
    "_OptionalSnowflakeConnectorProfilePropertiesTypeDef",
    {
        "bucketPrefix": str,
        "privateLinkServiceName": str,
        "accountName": str,
        "region": str,
    },
    total=False,
)


class SnowflakeConnectorProfilePropertiesTypeDef(
    _RequiredSnowflakeConnectorProfilePropertiesTypeDef,
    _OptionalSnowflakeConnectorProfilePropertiesTypeDef,
):
    pass


VeevaConnectorProfilePropertiesTypeDef = TypedDict(
    "VeevaConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

ZendeskConnectorProfilePropertiesTypeDef = TypedDict(
    "ZendeskConnectorProfilePropertiesTypeDef",
    {
        "instanceUrl": str,
    },
)

PrivateConnectionProvisioningStateTypeDef = TypedDict(
    "PrivateConnectionProvisioningStateTypeDef",
    {
        "status": PrivateConnectionProvisioningStatusType,
        "failureMessage": str,
        "failureCause": PrivateConnectionProvisioningFailureCauseType,
    },
    total=False,
)

LambdaConnectorProvisioningConfigTypeDef = TypedDict(
    "LambdaConnectorProvisioningConfigTypeDef",
    {
        "lambdaArn": str,
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

_RequiredCustomAuthCredentialsTypeDef = TypedDict(
    "_RequiredCustomAuthCredentialsTypeDef",
    {
        "customAuthenticationType": str,
    },
)
_OptionalCustomAuthCredentialsTypeDef = TypedDict(
    "_OptionalCustomAuthCredentialsTypeDef",
    {
        "credentialsMap": Mapping[str, str],
    },
    total=False,
)


class CustomAuthCredentialsTypeDef(
    _RequiredCustomAuthCredentialsTypeDef, _OptionalCustomAuthCredentialsTypeDef
):
    pass


ErrorHandlingConfigTypeDef = TypedDict(
    "ErrorHandlingConfigTypeDef",
    {
        "failOnFirstDestinationError": bool,
        "bucketPrefix": str,
        "bucketName": str,
    },
    total=False,
)

_RequiredOAuth2PropertiesTypeDef = TypedDict(
    "_RequiredOAuth2PropertiesTypeDef",
    {
        "tokenUrl": str,
        "oAuth2GrantType": OAuth2GrantTypeType,
    },
)
_OptionalOAuth2PropertiesTypeDef = TypedDict(
    "_OptionalOAuth2PropertiesTypeDef",
    {
        "tokenUrlCustomProperties": Mapping[str, str],
    },
    total=False,
)


class OAuth2PropertiesTypeDef(_RequiredOAuth2PropertiesTypeDef, _OptionalOAuth2PropertiesTypeDef):
    pass


_RequiredCustomConnectorSourcePropertiesTypeDef = TypedDict(
    "_RequiredCustomConnectorSourcePropertiesTypeDef",
    {
        "entityName": str,
    },
)
_OptionalCustomConnectorSourcePropertiesTypeDef = TypedDict(
    "_OptionalCustomConnectorSourcePropertiesTypeDef",
    {
        "customProperties": Mapping[str, str],
    },
    total=False,
)


class CustomConnectorSourcePropertiesTypeDef(
    _RequiredCustomConnectorSourcePropertiesTypeDef, _OptionalCustomConnectorSourcePropertiesTypeDef
):
    pass


_RequiredCustomerProfilesDestinationPropertiesTypeDef = TypedDict(
    "_RequiredCustomerProfilesDestinationPropertiesTypeDef",
    {
        "domainName": str,
    },
)
_OptionalCustomerProfilesDestinationPropertiesTypeDef = TypedDict(
    "_OptionalCustomerProfilesDestinationPropertiesTypeDef",
    {
        "objectTypeName": str,
    },
    total=False,
)


class CustomerProfilesDestinationPropertiesTypeDef(
    _RequiredCustomerProfilesDestinationPropertiesTypeDef,
    _OptionalCustomerProfilesDestinationPropertiesTypeDef,
):
    pass


DatadogSourcePropertiesTypeDef = TypedDict(
    "DatadogSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

_RequiredDeleteConnectorProfileRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteConnectorProfileRequestRequestTypeDef",
    {
        "connectorProfileName": str,
    },
)
_OptionalDeleteConnectorProfileRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteConnectorProfileRequestRequestTypeDef",
    {
        "forceDelete": bool,
    },
    total=False,
)


class DeleteConnectorProfileRequestRequestTypeDef(
    _RequiredDeleteConnectorProfileRequestRequestTypeDef,
    _OptionalDeleteConnectorProfileRequestRequestTypeDef,
):
    pass


_RequiredDeleteFlowRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteFlowRequestRequestTypeDef",
    {
        "flowName": str,
    },
)
_OptionalDeleteFlowRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteFlowRequestRequestTypeDef",
    {
        "forceDelete": bool,
    },
    total=False,
)


class DeleteFlowRequestRequestTypeDef(
    _RequiredDeleteFlowRequestRequestTypeDef, _OptionalDeleteFlowRequestRequestTypeDef
):
    pass


_RequiredDescribeConnectorEntityRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeConnectorEntityRequestRequestTypeDef",
    {
        "connectorEntityName": str,
    },
)
_OptionalDescribeConnectorEntityRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeConnectorEntityRequestRequestTypeDef",
    {
        "connectorType": ConnectorTypeType,
        "connectorProfileName": str,
        "apiVersion": str,
    },
    total=False,
)


class DescribeConnectorEntityRequestRequestTypeDef(
    _RequiredDescribeConnectorEntityRequestRequestTypeDef,
    _OptionalDescribeConnectorEntityRequestRequestTypeDef,
):
    pass


DescribeConnectorProfilesRequestRequestTypeDef = TypedDict(
    "DescribeConnectorProfilesRequestRequestTypeDef",
    {
        "connectorProfileNames": Sequence[str],
        "connectorType": ConnectorTypeType,
        "connectorLabel": str,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

_RequiredDescribeConnectorRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeConnectorRequestRequestTypeDef",
    {
        "connectorType": ConnectorTypeType,
    },
)
_OptionalDescribeConnectorRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeConnectorRequestRequestTypeDef",
    {
        "connectorLabel": str,
    },
    total=False,
)


class DescribeConnectorRequestRequestTypeDef(
    _RequiredDescribeConnectorRequestRequestTypeDef, _OptionalDescribeConnectorRequestRequestTypeDef
):
    pass


DescribeConnectorsRequestRequestTypeDef = TypedDict(
    "DescribeConnectorsRequestRequestTypeDef",
    {
        "connectorTypes": Sequence[ConnectorTypeType],
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

_RequiredDescribeFlowExecutionRecordsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeFlowExecutionRecordsRequestRequestTypeDef",
    {
        "flowName": str,
    },
)
_OptionalDescribeFlowExecutionRecordsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeFlowExecutionRecordsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)


class DescribeFlowExecutionRecordsRequestRequestTypeDef(
    _RequiredDescribeFlowExecutionRecordsRequestRequestTypeDef,
    _OptionalDescribeFlowExecutionRecordsRequestRequestTypeDef,
):
    pass


DescribeFlowRequestRequestTypeDef = TypedDict(
    "DescribeFlowRequestRequestTypeDef",
    {
        "flowName": str,
    },
)

ExecutionDetailsTypeDef = TypedDict(
    "ExecutionDetailsTypeDef",
    {
        "mostRecentExecutionMessage": str,
        "mostRecentExecutionTime": datetime,
        "mostRecentExecutionStatus": ExecutionStatusType,
    },
    total=False,
)

DynatraceSourcePropertiesTypeDef = TypedDict(
    "DynatraceSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

ErrorInfoTypeDef = TypedDict(
    "ErrorInfoTypeDef",
    {
        "putFailuresCount": int,
        "executionMessage": str,
    },
    total=False,
)

RangeTypeDef = TypedDict(
    "RangeTypeDef",
    {
        "maximum": float,
        "minimum": float,
    },
    total=False,
)

GoogleAnalyticsSourcePropertiesTypeDef = TypedDict(
    "GoogleAnalyticsSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

IncrementalPullConfigTypeDef = TypedDict(
    "IncrementalPullConfigTypeDef",
    {
        "datetimeTypeFieldName": str,
    },
    total=False,
)

InforNexusSourcePropertiesTypeDef = TypedDict(
    "InforNexusSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

ListConnectorEntitiesRequestRequestTypeDef = TypedDict(
    "ListConnectorEntitiesRequestRequestTypeDef",
    {
        "connectorProfileName": str,
        "connectorType": ConnectorTypeType,
        "entitiesPath": str,
        "apiVersion": str,
    },
    total=False,
)

ListConnectorsRequestRequestTypeDef = TypedDict(
    "ListConnectorsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListFlowsRequestRequestTypeDef = TypedDict(
    "ListFlowsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

MarketoSourcePropertiesTypeDef = TypedDict(
    "MarketoSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

OAuth2CustomParameterTypeDef = TypedDict(
    "OAuth2CustomParameterTypeDef",
    {
        "key": str,
        "isRequired": bool,
        "label": str,
        "description": str,
        "isSensitiveField": bool,
        "connectorSuppliedValues": List[str],
        "type": OAuth2CustomPropTypeType,
    },
    total=False,
)

OAuthPropertiesTypeDef = TypedDict(
    "OAuthPropertiesTypeDef",
    {
        "tokenUrl": str,
        "authCodeUrl": str,
        "oAuthScopes": Sequence[str],
    },
)

PrefixConfigTypeDef = TypedDict(
    "PrefixConfigTypeDef",
    {
        "prefixType": PrefixTypeType,
        "prefixFormat": PrefixFormatType,
    },
    total=False,
)

S3InputFormatConfigTypeDef = TypedDict(
    "S3InputFormatConfigTypeDef",
    {
        "s3InputFileType": S3InputFileTypeType,
    },
    total=False,
)

SuccessResponseHandlingConfigTypeDef = TypedDict(
    "SuccessResponseHandlingConfigTypeDef",
    {
        "bucketPrefix": str,
        "bucketName": str,
    },
    total=False,
)

SAPODataSourcePropertiesTypeDef = TypedDict(
    "SAPODataSourcePropertiesTypeDef",
    {
        "objectPath": str,
    },
    total=False,
)

_RequiredSalesforceSourcePropertiesTypeDef = TypedDict(
    "_RequiredSalesforceSourcePropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalSalesforceSourcePropertiesTypeDef = TypedDict(
    "_OptionalSalesforceSourcePropertiesTypeDef",
    {
        "enableDynamicFieldUpdate": bool,
        "includeDeletedRecords": bool,
    },
    total=False,
)


class SalesforceSourcePropertiesTypeDef(
    _RequiredSalesforceSourcePropertiesTypeDef, _OptionalSalesforceSourcePropertiesTypeDef
):
    pass


_RequiredScheduledTriggerPropertiesTypeDef = TypedDict(
    "_RequiredScheduledTriggerPropertiesTypeDef",
    {
        "scheduleExpression": str,
    },
)
_OptionalScheduledTriggerPropertiesTypeDef = TypedDict(
    "_OptionalScheduledTriggerPropertiesTypeDef",
    {
        "dataPullMode": DataPullModeType,
        "scheduleStartTime": Union[datetime, str],
        "scheduleEndTime": Union[datetime, str],
        "timezone": str,
        "scheduleOffset": int,
        "firstExecutionFrom": Union[datetime, str],
        "flowErrorDeactivationThreshold": int,
    },
    total=False,
)


class ScheduledTriggerPropertiesTypeDef(
    _RequiredScheduledTriggerPropertiesTypeDef, _OptionalScheduledTriggerPropertiesTypeDef
):
    pass


ServiceNowSourcePropertiesTypeDef = TypedDict(
    "ServiceNowSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

SingularSourcePropertiesTypeDef = TypedDict(
    "SingularSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

SlackSourcePropertiesTypeDef = TypedDict(
    "SlackSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

TrendmicroSourcePropertiesTypeDef = TypedDict(
    "TrendmicroSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

_RequiredVeevaSourcePropertiesTypeDef = TypedDict(
    "_RequiredVeevaSourcePropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalVeevaSourcePropertiesTypeDef = TypedDict(
    "_OptionalVeevaSourcePropertiesTypeDef",
    {
        "documentType": str,
        "includeSourceFiles": bool,
        "includeRenditions": bool,
        "includeAllVersions": bool,
    },
    total=False,
)


class VeevaSourcePropertiesTypeDef(
    _RequiredVeevaSourcePropertiesTypeDef, _OptionalVeevaSourcePropertiesTypeDef
):
    pass


ZendeskSourcePropertiesTypeDef = TypedDict(
    "ZendeskSourcePropertiesTypeDef",
    {
        "object": str,
    },
)

StartFlowRequestRequestTypeDef = TypedDict(
    "StartFlowRequestRequestTypeDef",
    {
        "flowName": str,
    },
)

StopFlowRequestRequestTypeDef = TypedDict(
    "StopFlowRequestRequestTypeDef",
    {
        "flowName": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

_RequiredUnregisterConnectorRequestRequestTypeDef = TypedDict(
    "_RequiredUnregisterConnectorRequestRequestTypeDef",
    {
        "connectorLabel": str,
    },
)
_OptionalUnregisterConnectorRequestRequestTypeDef = TypedDict(
    "_OptionalUnregisterConnectorRequestRequestTypeDef",
    {
        "forceDelete": bool,
    },
    total=False,
)


class UnregisterConnectorRequestRequestTypeDef(
    _RequiredUnregisterConnectorRequestRequestTypeDef,
    _OptionalUnregisterConnectorRequestRequestTypeDef,
):
    pass


UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

CustomAuthConfigTypeDef = TypedDict(
    "CustomAuthConfigTypeDef",
    {
        "customAuthenticationType": str,
        "authParameters": List[AuthParameterTypeDef],
    },
    total=False,
)

ConnectorMetadataTypeDef = TypedDict(
    "ConnectorMetadataTypeDef",
    {
        "Amplitude": Dict[str, Any],
        "Datadog": Dict[str, Any],
        "Dynatrace": Dict[str, Any],
        "GoogleAnalytics": GoogleAnalyticsMetadataTypeDef,
        "InforNexus": Dict[str, Any],
        "Marketo": Dict[str, Any],
        "Redshift": Dict[str, Any],
        "S3": Dict[str, Any],
        "Salesforce": SalesforceMetadataTypeDef,
        "ServiceNow": Dict[str, Any],
        "Singular": Dict[str, Any],
        "Slack": SlackMetadataTypeDef,
        "Snowflake": SnowflakeMetadataTypeDef,
        "Trendmicro": Dict[str, Any],
        "Veeva": Dict[str, Any],
        "Zendesk": ZendeskMetadataTypeDef,
        "EventBridge": Dict[str, Any],
        "Upsolver": Dict[str, Any],
        "CustomerProfiles": Dict[str, Any],
        "Honeycode": HoneycodeMetadataTypeDef,
        "SAPOData": Dict[str, Any],
    },
    total=False,
)

_RequiredGoogleAnalyticsConnectorProfileCredentialsTypeDef = TypedDict(
    "_RequiredGoogleAnalyticsConnectorProfileCredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
    },
)
_OptionalGoogleAnalyticsConnectorProfileCredentialsTypeDef = TypedDict(
    "_OptionalGoogleAnalyticsConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "refreshToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)


class GoogleAnalyticsConnectorProfileCredentialsTypeDef(
    _RequiredGoogleAnalyticsConnectorProfileCredentialsTypeDef,
    _OptionalGoogleAnalyticsConnectorProfileCredentialsTypeDef,
):
    pass


HoneycodeConnectorProfileCredentialsTypeDef = TypedDict(
    "HoneycodeConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "refreshToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)

_RequiredMarketoConnectorProfileCredentialsTypeDef = TypedDict(
    "_RequiredMarketoConnectorProfileCredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
    },
)
_OptionalMarketoConnectorProfileCredentialsTypeDef = TypedDict(
    "_OptionalMarketoConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)


class MarketoConnectorProfileCredentialsTypeDef(
    _RequiredMarketoConnectorProfileCredentialsTypeDef,
    _OptionalMarketoConnectorProfileCredentialsTypeDef,
):
    pass


OAuth2CredentialsTypeDef = TypedDict(
    "OAuth2CredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
        "accessToken": str,
        "refreshToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)

_RequiredOAuthCredentialsTypeDef = TypedDict(
    "_RequiredOAuthCredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
    },
)
_OptionalOAuthCredentialsTypeDef = TypedDict(
    "_OptionalOAuthCredentialsTypeDef",
    {
        "accessToken": str,
        "refreshToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)


class OAuthCredentialsTypeDef(_RequiredOAuthCredentialsTypeDef, _OptionalOAuthCredentialsTypeDef):
    pass


SalesforceConnectorProfileCredentialsTypeDef = TypedDict(
    "SalesforceConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "refreshToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
        "clientCredentialsArn": str,
    },
    total=False,
)

_RequiredSlackConnectorProfileCredentialsTypeDef = TypedDict(
    "_RequiredSlackConnectorProfileCredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
    },
)
_OptionalSlackConnectorProfileCredentialsTypeDef = TypedDict(
    "_OptionalSlackConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)


class SlackConnectorProfileCredentialsTypeDef(
    _RequiredSlackConnectorProfileCredentialsTypeDef,
    _OptionalSlackConnectorProfileCredentialsTypeDef,
):
    pass


_RequiredZendeskConnectorProfileCredentialsTypeDef = TypedDict(
    "_RequiredZendeskConnectorProfileCredentialsTypeDef",
    {
        "clientId": str,
        "clientSecret": str,
    },
)
_OptionalZendeskConnectorProfileCredentialsTypeDef = TypedDict(
    "_OptionalZendeskConnectorProfileCredentialsTypeDef",
    {
        "accessToken": str,
        "oAuthRequest": ConnectorOAuthRequestTypeDef,
    },
    total=False,
)


class ZendeskConnectorProfileCredentialsTypeDef(
    _RequiredZendeskConnectorProfileCredentialsTypeDef,
    _OptionalZendeskConnectorProfileCredentialsTypeDef,
):
    pass


_RequiredTaskTypeDef = TypedDict(
    "_RequiredTaskTypeDef",
    {
        "sourceFields": Sequence[str],
        "taskType": TaskTypeType,
    },
)
_OptionalTaskTypeDef = TypedDict(
    "_OptionalTaskTypeDef",
    {
        "connectorOperator": ConnectorOperatorTypeDef,
        "destinationField": str,
        "taskProperties": Mapping[OperatorPropertiesKeysType, str],
    },
    total=False,
)


class TaskTypeDef(_RequiredTaskTypeDef, _OptionalTaskTypeDef):
    pass


ConnectorProvisioningConfigTypeDef = TypedDict(
    "ConnectorProvisioningConfigTypeDef",
    {
        "lambda": LambdaConnectorProvisioningConfigTypeDef,
    },
    total=False,
)

CreateConnectorProfileResponseTypeDef = TypedDict(
    "CreateConnectorProfileResponseTypeDef",
    {
        "connectorProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFlowResponseTypeDef = TypedDict(
    "CreateFlowResponseTypeDef",
    {
        "flowArn": str,
        "flowStatus": FlowStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListConnectorEntitiesResponseTypeDef = TypedDict(
    "ListConnectorEntitiesResponseTypeDef",
    {
        "connectorEntityMap": Dict[str, List[ConnectorEntityTypeDef]],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListConnectorsResponseTypeDef = TypedDict(
    "ListConnectorsResponseTypeDef",
    {
        "connectors": List[ConnectorDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterConnectorResponseTypeDef = TypedDict(
    "RegisterConnectorResponseTypeDef",
    {
        "connectorArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartFlowResponseTypeDef = TypedDict(
    "StartFlowResponseTypeDef",
    {
        "flowArn": str,
        "flowStatus": FlowStatusType,
        "executionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopFlowResponseTypeDef = TypedDict(
    "StopFlowResponseTypeDef",
    {
        "flowArn": str,
        "flowStatus": FlowStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateConnectorProfileResponseTypeDef = TypedDict(
    "UpdateConnectorProfileResponseTypeDef",
    {
        "connectorProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateFlowResponseTypeDef = TypedDict(
    "UpdateFlowResponseTypeDef",
    {
        "flowStatus": FlowStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCustomConnectorDestinationPropertiesTypeDef = TypedDict(
    "_RequiredCustomConnectorDestinationPropertiesTypeDef",
    {
        "entityName": str,
    },
)
_OptionalCustomConnectorDestinationPropertiesTypeDef = TypedDict(
    "_OptionalCustomConnectorDestinationPropertiesTypeDef",
    {
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
        "writeOperationType": WriteOperationTypeType,
        "idFieldNames": Sequence[str],
        "customProperties": Mapping[str, str],
    },
    total=False,
)


class CustomConnectorDestinationPropertiesTypeDef(
    _RequiredCustomConnectorDestinationPropertiesTypeDef,
    _OptionalCustomConnectorDestinationPropertiesTypeDef,
):
    pass


_RequiredEventBridgeDestinationPropertiesTypeDef = TypedDict(
    "_RequiredEventBridgeDestinationPropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalEventBridgeDestinationPropertiesTypeDef = TypedDict(
    "_OptionalEventBridgeDestinationPropertiesTypeDef",
    {
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
    },
    total=False,
)


class EventBridgeDestinationPropertiesTypeDef(
    _RequiredEventBridgeDestinationPropertiesTypeDef,
    _OptionalEventBridgeDestinationPropertiesTypeDef,
):
    pass


_RequiredHoneycodeDestinationPropertiesTypeDef = TypedDict(
    "_RequiredHoneycodeDestinationPropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalHoneycodeDestinationPropertiesTypeDef = TypedDict(
    "_OptionalHoneycodeDestinationPropertiesTypeDef",
    {
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
    },
    total=False,
)


class HoneycodeDestinationPropertiesTypeDef(
    _RequiredHoneycodeDestinationPropertiesTypeDef, _OptionalHoneycodeDestinationPropertiesTypeDef
):
    pass


_RequiredMarketoDestinationPropertiesTypeDef = TypedDict(
    "_RequiredMarketoDestinationPropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalMarketoDestinationPropertiesTypeDef = TypedDict(
    "_OptionalMarketoDestinationPropertiesTypeDef",
    {
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
    },
    total=False,
)


class MarketoDestinationPropertiesTypeDef(
    _RequiredMarketoDestinationPropertiesTypeDef, _OptionalMarketoDestinationPropertiesTypeDef
):
    pass


_RequiredRedshiftDestinationPropertiesTypeDef = TypedDict(
    "_RequiredRedshiftDestinationPropertiesTypeDef",
    {
        "object": str,
        "intermediateBucketName": str,
    },
)
_OptionalRedshiftDestinationPropertiesTypeDef = TypedDict(
    "_OptionalRedshiftDestinationPropertiesTypeDef",
    {
        "bucketPrefix": str,
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
    },
    total=False,
)


class RedshiftDestinationPropertiesTypeDef(
    _RequiredRedshiftDestinationPropertiesTypeDef, _OptionalRedshiftDestinationPropertiesTypeDef
):
    pass


_RequiredSalesforceDestinationPropertiesTypeDef = TypedDict(
    "_RequiredSalesforceDestinationPropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalSalesforceDestinationPropertiesTypeDef = TypedDict(
    "_OptionalSalesforceDestinationPropertiesTypeDef",
    {
        "idFieldNames": Sequence[str],
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
        "writeOperationType": WriteOperationTypeType,
    },
    total=False,
)


class SalesforceDestinationPropertiesTypeDef(
    _RequiredSalesforceDestinationPropertiesTypeDef, _OptionalSalesforceDestinationPropertiesTypeDef
):
    pass


_RequiredSnowflakeDestinationPropertiesTypeDef = TypedDict(
    "_RequiredSnowflakeDestinationPropertiesTypeDef",
    {
        "object": str,
        "intermediateBucketName": str,
    },
)
_OptionalSnowflakeDestinationPropertiesTypeDef = TypedDict(
    "_OptionalSnowflakeDestinationPropertiesTypeDef",
    {
        "bucketPrefix": str,
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
    },
    total=False,
)


class SnowflakeDestinationPropertiesTypeDef(
    _RequiredSnowflakeDestinationPropertiesTypeDef, _OptionalSnowflakeDestinationPropertiesTypeDef
):
    pass


_RequiredZendeskDestinationPropertiesTypeDef = TypedDict(
    "_RequiredZendeskDestinationPropertiesTypeDef",
    {
        "object": str,
    },
)
_OptionalZendeskDestinationPropertiesTypeDef = TypedDict(
    "_OptionalZendeskDestinationPropertiesTypeDef",
    {
        "idFieldNames": Sequence[str],
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
        "writeOperationType": WriteOperationTypeType,
    },
    total=False,
)


class ZendeskDestinationPropertiesTypeDef(
    _RequiredZendeskDestinationPropertiesTypeDef, _OptionalZendeskDestinationPropertiesTypeDef
):
    pass


CustomConnectorProfilePropertiesTypeDef = TypedDict(
    "CustomConnectorProfilePropertiesTypeDef",
    {
        "profileProperties": Mapping[str, str],
        "oAuth2Properties": OAuth2PropertiesTypeDef,
    },
    total=False,
)

FlowDefinitionTypeDef = TypedDict(
    "FlowDefinitionTypeDef",
    {
        "flowArn": str,
        "description": str,
        "flowName": str,
        "flowStatus": FlowStatusType,
        "sourceConnectorType": ConnectorTypeType,
        "sourceConnectorLabel": str,
        "destinationConnectorType": ConnectorTypeType,
        "destinationConnectorLabel": str,
        "triggerType": TriggerTypeType,
        "createdAt": datetime,
        "lastUpdatedAt": datetime,
        "createdBy": str,
        "lastUpdatedBy": str,
        "tags": Dict[str, str],
        "lastRunExecutionDetails": ExecutionDetailsTypeDef,
    },
    total=False,
)

ExecutionResultTypeDef = TypedDict(
    "ExecutionResultTypeDef",
    {
        "errorInfo": ErrorInfoTypeDef,
        "bytesProcessed": int,
        "bytesWritten": int,
        "recordsProcessed": int,
    },
    total=False,
)

_RequiredFieldTypeDetailsTypeDef = TypedDict(
    "_RequiredFieldTypeDetailsTypeDef",
    {
        "fieldType": str,
        "filterOperators": List[OperatorType],
    },
)
_OptionalFieldTypeDetailsTypeDef = TypedDict(
    "_OptionalFieldTypeDetailsTypeDef",
    {
        "supportedValues": List[str],
        "valueRegexPattern": str,
        "supportedDateFormat": str,
        "fieldValueRange": RangeTypeDef,
        "fieldLengthRange": RangeTypeDef,
    },
    total=False,
)


class FieldTypeDetailsTypeDef(_RequiredFieldTypeDetailsTypeDef, _OptionalFieldTypeDetailsTypeDef):
    pass


OAuth2DefaultsTypeDef = TypedDict(
    "OAuth2DefaultsTypeDef",
    {
        "oauthScopes": List[str],
        "tokenUrls": List[str],
        "authCodeUrls": List[str],
        "oauth2GrantTypesSupported": List[OAuth2GrantTypeType],
        "oauth2CustomProperties": List[OAuth2CustomParameterTypeDef],
    },
    total=False,
)

_RequiredSAPODataConnectorProfilePropertiesTypeDef = TypedDict(
    "_RequiredSAPODataConnectorProfilePropertiesTypeDef",
    {
        "applicationHostUrl": str,
        "applicationServicePath": str,
        "portNumber": int,
        "clientNumber": str,
    },
)
_OptionalSAPODataConnectorProfilePropertiesTypeDef = TypedDict(
    "_OptionalSAPODataConnectorProfilePropertiesTypeDef",
    {
        "logonLanguage": str,
        "privateLinkServiceName": str,
        "oAuthProperties": OAuthPropertiesTypeDef,
    },
    total=False,
)


class SAPODataConnectorProfilePropertiesTypeDef(
    _RequiredSAPODataConnectorProfilePropertiesTypeDef,
    _OptionalSAPODataConnectorProfilePropertiesTypeDef,
):
    pass


S3OutputFormatConfigTypeDef = TypedDict(
    "S3OutputFormatConfigTypeDef",
    {
        "fileType": FileTypeType,
        "prefixConfig": PrefixConfigTypeDef,
        "aggregationConfig": AggregationConfigTypeDef,
        "preserveSourceDataTyping": bool,
    },
    total=False,
)

_RequiredUpsolverS3OutputFormatConfigTypeDef = TypedDict(
    "_RequiredUpsolverS3OutputFormatConfigTypeDef",
    {
        "prefixConfig": PrefixConfigTypeDef,
    },
)
_OptionalUpsolverS3OutputFormatConfigTypeDef = TypedDict(
    "_OptionalUpsolverS3OutputFormatConfigTypeDef",
    {
        "fileType": FileTypeType,
        "aggregationConfig": AggregationConfigTypeDef,
    },
    total=False,
)


class UpsolverS3OutputFormatConfigTypeDef(
    _RequiredUpsolverS3OutputFormatConfigTypeDef, _OptionalUpsolverS3OutputFormatConfigTypeDef
):
    pass


_RequiredS3SourcePropertiesTypeDef = TypedDict(
    "_RequiredS3SourcePropertiesTypeDef",
    {
        "bucketName": str,
    },
)
_OptionalS3SourcePropertiesTypeDef = TypedDict(
    "_OptionalS3SourcePropertiesTypeDef",
    {
        "bucketPrefix": str,
        "s3InputFormatConfig": S3InputFormatConfigTypeDef,
    },
    total=False,
)


class S3SourcePropertiesTypeDef(
    _RequiredS3SourcePropertiesTypeDef, _OptionalS3SourcePropertiesTypeDef
):
    pass


_RequiredSAPODataDestinationPropertiesTypeDef = TypedDict(
    "_RequiredSAPODataDestinationPropertiesTypeDef",
    {
        "objectPath": str,
    },
)
_OptionalSAPODataDestinationPropertiesTypeDef = TypedDict(
    "_OptionalSAPODataDestinationPropertiesTypeDef",
    {
        "successResponseHandlingConfig": SuccessResponseHandlingConfigTypeDef,
        "idFieldNames": Sequence[str],
        "errorHandlingConfig": ErrorHandlingConfigTypeDef,
        "writeOperationType": WriteOperationTypeType,
    },
    total=False,
)


class SAPODataDestinationPropertiesTypeDef(
    _RequiredSAPODataDestinationPropertiesTypeDef, _OptionalSAPODataDestinationPropertiesTypeDef
):
    pass


TriggerPropertiesTypeDef = TypedDict(
    "TriggerPropertiesTypeDef",
    {
        "Scheduled": ScheduledTriggerPropertiesTypeDef,
    },
    total=False,
)

_RequiredCustomConnectorProfileCredentialsTypeDef = TypedDict(
    "_RequiredCustomConnectorProfileCredentialsTypeDef",
    {
        "authenticationType": AuthenticationTypeType,
    },
)
_OptionalCustomConnectorProfileCredentialsTypeDef = TypedDict(
    "_OptionalCustomConnectorProfileCredentialsTypeDef",
    {
        "basic": BasicAuthCredentialsTypeDef,
        "oauth2": OAuth2CredentialsTypeDef,
        "apiKey": ApiKeyCredentialsTypeDef,
        "custom": CustomAuthCredentialsTypeDef,
    },
    total=False,
)


class CustomConnectorProfileCredentialsTypeDef(
    _RequiredCustomConnectorProfileCredentialsTypeDef,
    _OptionalCustomConnectorProfileCredentialsTypeDef,
):
    pass


SAPODataConnectorProfileCredentialsTypeDef = TypedDict(
    "SAPODataConnectorProfileCredentialsTypeDef",
    {
        "basicAuthCredentials": BasicAuthCredentialsTypeDef,
        "oAuthCredentials": OAuthCredentialsTypeDef,
    },
    total=False,
)

RegisterConnectorRequestRequestTypeDef = TypedDict(
    "RegisterConnectorRequestRequestTypeDef",
    {
        "connectorLabel": str,
        "description": str,
        "connectorProvisioningType": Literal["LAMBDA"],
        "connectorProvisioningConfig": ConnectorProvisioningConfigTypeDef,
    },
    total=False,
)

ListFlowsResponseTypeDef = TypedDict(
    "ListFlowsResponseTypeDef",
    {
        "flows": List[FlowDefinitionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExecutionRecordTypeDef = TypedDict(
    "ExecutionRecordTypeDef",
    {
        "executionId": str,
        "executionStatus": ExecutionStatusType,
        "executionResult": ExecutionResultTypeDef,
        "startedAt": datetime,
        "lastUpdatedAt": datetime,
        "dataPullStartTime": datetime,
        "dataPullEndTime": datetime,
    },
    total=False,
)

SupportedFieldTypeDetailsTypeDef = TypedDict(
    "SupportedFieldTypeDetailsTypeDef",
    {
        "v1": FieldTypeDetailsTypeDef,
    },
)

AuthenticationConfigTypeDef = TypedDict(
    "AuthenticationConfigTypeDef",
    {
        "isBasicAuthSupported": bool,
        "isApiKeyAuthSupported": bool,
        "isOAuth2Supported": bool,
        "isCustomAuthSupported": bool,
        "oAuth2Defaults": OAuth2DefaultsTypeDef,
        "customAuthConfigs": List[CustomAuthConfigTypeDef],
    },
    total=False,
)

ConnectorProfilePropertiesTypeDef = TypedDict(
    "ConnectorProfilePropertiesTypeDef",
    {
        "Amplitude": Mapping[str, Any],
        "Datadog": DatadogConnectorProfilePropertiesTypeDef,
        "Dynatrace": DynatraceConnectorProfilePropertiesTypeDef,
        "GoogleAnalytics": Mapping[str, Any],
        "Honeycode": Mapping[str, Any],
        "InforNexus": InforNexusConnectorProfilePropertiesTypeDef,
        "Marketo": MarketoConnectorProfilePropertiesTypeDef,
        "Redshift": RedshiftConnectorProfilePropertiesTypeDef,
        "Salesforce": SalesforceConnectorProfilePropertiesTypeDef,
        "ServiceNow": ServiceNowConnectorProfilePropertiesTypeDef,
        "Singular": Mapping[str, Any],
        "Slack": SlackConnectorProfilePropertiesTypeDef,
        "Snowflake": SnowflakeConnectorProfilePropertiesTypeDef,
        "Trendmicro": Mapping[str, Any],
        "Veeva": VeevaConnectorProfilePropertiesTypeDef,
        "Zendesk": ZendeskConnectorProfilePropertiesTypeDef,
        "SAPOData": SAPODataConnectorProfilePropertiesTypeDef,
        "CustomConnector": CustomConnectorProfilePropertiesTypeDef,
    },
    total=False,
)

_RequiredS3DestinationPropertiesTypeDef = TypedDict(
    "_RequiredS3DestinationPropertiesTypeDef",
    {
        "bucketName": str,
    },
)
_OptionalS3DestinationPropertiesTypeDef = TypedDict(
    "_OptionalS3DestinationPropertiesTypeDef",
    {
        "bucketPrefix": str,
        "s3OutputFormatConfig": S3OutputFormatConfigTypeDef,
    },
    total=False,
)


class S3DestinationPropertiesTypeDef(
    _RequiredS3DestinationPropertiesTypeDef, _OptionalS3DestinationPropertiesTypeDef
):
    pass


_RequiredUpsolverDestinationPropertiesTypeDef = TypedDict(
    "_RequiredUpsolverDestinationPropertiesTypeDef",
    {
        "bucketName": str,
        "s3OutputFormatConfig": UpsolverS3OutputFormatConfigTypeDef,
    },
)
_OptionalUpsolverDestinationPropertiesTypeDef = TypedDict(
    "_OptionalUpsolverDestinationPropertiesTypeDef",
    {
        "bucketPrefix": str,
    },
    total=False,
)


class UpsolverDestinationPropertiesTypeDef(
    _RequiredUpsolverDestinationPropertiesTypeDef, _OptionalUpsolverDestinationPropertiesTypeDef
):
    pass


SourceConnectorPropertiesTypeDef = TypedDict(
    "SourceConnectorPropertiesTypeDef",
    {
        "Amplitude": AmplitudeSourcePropertiesTypeDef,
        "Datadog": DatadogSourcePropertiesTypeDef,
        "Dynatrace": DynatraceSourcePropertiesTypeDef,
        "GoogleAnalytics": GoogleAnalyticsSourcePropertiesTypeDef,
        "InforNexus": InforNexusSourcePropertiesTypeDef,
        "Marketo": MarketoSourcePropertiesTypeDef,
        "S3": S3SourcePropertiesTypeDef,
        "Salesforce": SalesforceSourcePropertiesTypeDef,
        "ServiceNow": ServiceNowSourcePropertiesTypeDef,
        "Singular": SingularSourcePropertiesTypeDef,
        "Slack": SlackSourcePropertiesTypeDef,
        "Trendmicro": TrendmicroSourcePropertiesTypeDef,
        "Veeva": VeevaSourcePropertiesTypeDef,
        "Zendesk": ZendeskSourcePropertiesTypeDef,
        "SAPOData": SAPODataSourcePropertiesTypeDef,
        "CustomConnector": CustomConnectorSourcePropertiesTypeDef,
    },
    total=False,
)

_RequiredTriggerConfigTypeDef = TypedDict(
    "_RequiredTriggerConfigTypeDef",
    {
        "triggerType": TriggerTypeType,
    },
)
_OptionalTriggerConfigTypeDef = TypedDict(
    "_OptionalTriggerConfigTypeDef",
    {
        "triggerProperties": TriggerPropertiesTypeDef,
    },
    total=False,
)


class TriggerConfigTypeDef(_RequiredTriggerConfigTypeDef, _OptionalTriggerConfigTypeDef):
    pass


ConnectorProfileCredentialsTypeDef = TypedDict(
    "ConnectorProfileCredentialsTypeDef",
    {
        "Amplitude": AmplitudeConnectorProfileCredentialsTypeDef,
        "Datadog": DatadogConnectorProfileCredentialsTypeDef,
        "Dynatrace": DynatraceConnectorProfileCredentialsTypeDef,
        "GoogleAnalytics": GoogleAnalyticsConnectorProfileCredentialsTypeDef,
        "Honeycode": HoneycodeConnectorProfileCredentialsTypeDef,
        "InforNexus": InforNexusConnectorProfileCredentialsTypeDef,
        "Marketo": MarketoConnectorProfileCredentialsTypeDef,
        "Redshift": RedshiftConnectorProfileCredentialsTypeDef,
        "Salesforce": SalesforceConnectorProfileCredentialsTypeDef,
        "ServiceNow": ServiceNowConnectorProfileCredentialsTypeDef,
        "Singular": SingularConnectorProfileCredentialsTypeDef,
        "Slack": SlackConnectorProfileCredentialsTypeDef,
        "Snowflake": SnowflakeConnectorProfileCredentialsTypeDef,
        "Trendmicro": TrendmicroConnectorProfileCredentialsTypeDef,
        "Veeva": VeevaConnectorProfileCredentialsTypeDef,
        "Zendesk": ZendeskConnectorProfileCredentialsTypeDef,
        "SAPOData": SAPODataConnectorProfileCredentialsTypeDef,
        "CustomConnector": CustomConnectorProfileCredentialsTypeDef,
    },
    total=False,
)

DescribeFlowExecutionRecordsResponseTypeDef = TypedDict(
    "DescribeFlowExecutionRecordsResponseTypeDef",
    {
        "flowExecutions": List[ExecutionRecordTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredConnectorEntityFieldTypeDef = TypedDict(
    "_RequiredConnectorEntityFieldTypeDef",
    {
        "identifier": str,
    },
)
_OptionalConnectorEntityFieldTypeDef = TypedDict(
    "_OptionalConnectorEntityFieldTypeDef",
    {
        "parentIdentifier": str,
        "label": str,
        "isPrimaryKey": bool,
        "defaultValue": str,
        "isDeprecated": bool,
        "supportedFieldTypeDetails": SupportedFieldTypeDetailsTypeDef,
        "description": str,
        "sourceProperties": SourceFieldPropertiesTypeDef,
        "destinationProperties": DestinationFieldPropertiesTypeDef,
        "customProperties": Dict[str, str],
    },
    total=False,
)


class ConnectorEntityFieldTypeDef(
    _RequiredConnectorEntityFieldTypeDef, _OptionalConnectorEntityFieldTypeDef
):
    pass


ConnectorConfigurationTypeDef = TypedDict(
    "ConnectorConfigurationTypeDef",
    {
        "canUseAsSource": bool,
        "canUseAsDestination": bool,
        "supportedDestinationConnectors": List[ConnectorTypeType],
        "supportedSchedulingFrequencies": List[ScheduleFrequencyTypeType],
        "isPrivateLinkEnabled": bool,
        "isPrivateLinkEndpointUrlRequired": bool,
        "supportedTriggerTypes": List[TriggerTypeType],
        "connectorMetadata": ConnectorMetadataTypeDef,
        "connectorType": ConnectorTypeType,
        "connectorLabel": str,
        "connectorDescription": str,
        "connectorOwner": str,
        "connectorName": str,
        "connectorVersion": str,
        "connectorArn": str,
        "connectorModes": List[str],
        "authenticationConfig": AuthenticationConfigTypeDef,
        "connectorRuntimeSettings": List[ConnectorRuntimeSettingTypeDef],
        "supportedApiVersions": List[str],
        "supportedOperators": List[OperatorsType],
        "supportedWriteOperations": List[WriteOperationTypeType],
        "connectorProvisioningType": Literal["LAMBDA"],
        "connectorProvisioningConfig": ConnectorProvisioningConfigTypeDef,
        "logoURL": str,
        "registeredAt": datetime,
        "registeredBy": str,
    },
    total=False,
)

ConnectorProfileTypeDef = TypedDict(
    "ConnectorProfileTypeDef",
    {
        "connectorProfileArn": str,
        "connectorProfileName": str,
        "connectorType": ConnectorTypeType,
        "connectorLabel": str,
        "connectionMode": ConnectionModeType,
        "credentialsArn": str,
        "connectorProfileProperties": ConnectorProfilePropertiesTypeDef,
        "createdAt": datetime,
        "lastUpdatedAt": datetime,
        "privateConnectionProvisioningState": PrivateConnectionProvisioningStateTypeDef,
    },
    total=False,
)

DestinationConnectorPropertiesTypeDef = TypedDict(
    "DestinationConnectorPropertiesTypeDef",
    {
        "Redshift": RedshiftDestinationPropertiesTypeDef,
        "S3": S3DestinationPropertiesTypeDef,
        "Salesforce": SalesforceDestinationPropertiesTypeDef,
        "Snowflake": SnowflakeDestinationPropertiesTypeDef,
        "EventBridge": EventBridgeDestinationPropertiesTypeDef,
        "LookoutMetrics": Mapping[str, Any],
        "Upsolver": UpsolverDestinationPropertiesTypeDef,
        "Honeycode": HoneycodeDestinationPropertiesTypeDef,
        "CustomerProfiles": CustomerProfilesDestinationPropertiesTypeDef,
        "Zendesk": ZendeskDestinationPropertiesTypeDef,
        "Marketo": MarketoDestinationPropertiesTypeDef,
        "CustomConnector": CustomConnectorDestinationPropertiesTypeDef,
        "SAPOData": SAPODataDestinationPropertiesTypeDef,
    },
    total=False,
)

_RequiredSourceFlowConfigTypeDef = TypedDict(
    "_RequiredSourceFlowConfigTypeDef",
    {
        "connectorType": ConnectorTypeType,
        "sourceConnectorProperties": SourceConnectorPropertiesTypeDef,
    },
)
_OptionalSourceFlowConfigTypeDef = TypedDict(
    "_OptionalSourceFlowConfigTypeDef",
    {
        "apiVersion": str,
        "connectorProfileName": str,
        "incrementalPullConfig": IncrementalPullConfigTypeDef,
    },
    total=False,
)


class SourceFlowConfigTypeDef(_RequiredSourceFlowConfigTypeDef, _OptionalSourceFlowConfigTypeDef):
    pass


ConnectorProfileConfigTypeDef = TypedDict(
    "ConnectorProfileConfigTypeDef",
    {
        "connectorProfileProperties": ConnectorProfilePropertiesTypeDef,
        "connectorProfileCredentials": ConnectorProfileCredentialsTypeDef,
    },
)

DescribeConnectorEntityResponseTypeDef = TypedDict(
    "DescribeConnectorEntityResponseTypeDef",
    {
        "connectorEntityFields": List[ConnectorEntityFieldTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeConnectorResponseTypeDef = TypedDict(
    "DescribeConnectorResponseTypeDef",
    {
        "connectorConfiguration": ConnectorConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeConnectorsResponseTypeDef = TypedDict(
    "DescribeConnectorsResponseTypeDef",
    {
        "connectorConfigurations": Dict[ConnectorTypeType, ConnectorConfigurationTypeDef],
        "connectors": List[ConnectorDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeConnectorProfilesResponseTypeDef = TypedDict(
    "DescribeConnectorProfilesResponseTypeDef",
    {
        "connectorProfileDetails": List[ConnectorProfileTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredDestinationFlowConfigTypeDef = TypedDict(
    "_RequiredDestinationFlowConfigTypeDef",
    {
        "connectorType": ConnectorTypeType,
        "destinationConnectorProperties": DestinationConnectorPropertiesTypeDef,
    },
)
_OptionalDestinationFlowConfigTypeDef = TypedDict(
    "_OptionalDestinationFlowConfigTypeDef",
    {
        "apiVersion": str,
        "connectorProfileName": str,
    },
    total=False,
)


class DestinationFlowConfigTypeDef(
    _RequiredDestinationFlowConfigTypeDef, _OptionalDestinationFlowConfigTypeDef
):
    pass


_RequiredCreateConnectorProfileRequestRequestTypeDef = TypedDict(
    "_RequiredCreateConnectorProfileRequestRequestTypeDef",
    {
        "connectorProfileName": str,
        "connectorType": ConnectorTypeType,
        "connectionMode": ConnectionModeType,
        "connectorProfileConfig": ConnectorProfileConfigTypeDef,
    },
)
_OptionalCreateConnectorProfileRequestRequestTypeDef = TypedDict(
    "_OptionalCreateConnectorProfileRequestRequestTypeDef",
    {
        "kmsArn": str,
        "connectorLabel": str,
    },
    total=False,
)


class CreateConnectorProfileRequestRequestTypeDef(
    _RequiredCreateConnectorProfileRequestRequestTypeDef,
    _OptionalCreateConnectorProfileRequestRequestTypeDef,
):
    pass


UpdateConnectorProfileRequestRequestTypeDef = TypedDict(
    "UpdateConnectorProfileRequestRequestTypeDef",
    {
        "connectorProfileName": str,
        "connectionMode": ConnectionModeType,
        "connectorProfileConfig": ConnectorProfileConfigTypeDef,
    },
)

_RequiredCreateFlowRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFlowRequestRequestTypeDef",
    {
        "flowName": str,
        "triggerConfig": TriggerConfigTypeDef,
        "sourceFlowConfig": SourceFlowConfigTypeDef,
        "destinationFlowConfigList": Sequence[DestinationFlowConfigTypeDef],
        "tasks": Sequence[TaskTypeDef],
    },
)
_OptionalCreateFlowRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFlowRequestRequestTypeDef",
    {
        "description": str,
        "kmsArn": str,
        "tags": Mapping[str, str],
    },
    total=False,
)


class CreateFlowRequestRequestTypeDef(
    _RequiredCreateFlowRequestRequestTypeDef, _OptionalCreateFlowRequestRequestTypeDef
):
    pass


DescribeFlowResponseTypeDef = TypedDict(
    "DescribeFlowResponseTypeDef",
    {
        "flowArn": str,
        "description": str,
        "flowName": str,
        "kmsArn": str,
        "flowStatus": FlowStatusType,
        "flowStatusMessage": str,
        "sourceFlowConfig": SourceFlowConfigTypeDef,
        "destinationFlowConfigList": List[DestinationFlowConfigTypeDef],
        "lastRunExecutionDetails": ExecutionDetailsTypeDef,
        "triggerConfig": TriggerConfigTypeDef,
        "tasks": List[TaskTypeDef],
        "createdAt": datetime,
        "lastUpdatedAt": datetime,
        "createdBy": str,
        "lastUpdatedBy": str,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredUpdateFlowRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateFlowRequestRequestTypeDef",
    {
        "flowName": str,
        "triggerConfig": TriggerConfigTypeDef,
        "sourceFlowConfig": SourceFlowConfigTypeDef,
        "destinationFlowConfigList": Sequence[DestinationFlowConfigTypeDef],
        "tasks": Sequence[TaskTypeDef],
    },
)
_OptionalUpdateFlowRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateFlowRequestRequestTypeDef",
    {
        "description": str,
    },
    total=False,
)


class UpdateFlowRequestRequestTypeDef(
    _RequiredUpdateFlowRequestRequestTypeDef, _OptionalUpdateFlowRequestRequestTypeDef
):
    pass
