"""
Type annotations for cloudformation service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/type_defs/)

Usage::

    ```python
    from mypy_boto3_cloudformation.type_defs import AccountGateResultTypeDef

    data: AccountGateResultTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AccountGateStatusType,
    CallAsType,
    CapabilityType,
    CategoryType,
    ChangeActionType,
    ChangeSetHooksStatusType,
    ChangeSetStatusType,
    ChangeSetTypeType,
    ChangeSourceType,
    DeprecatedStatusType,
    DifferenceTypeType,
    EvaluationTypeType,
    ExecutionStatusType,
    HandlerErrorCodeType,
    HookFailureModeType,
    HookStatusType,
    IdentityProviderType,
    OnFailureType,
    OperationStatusType,
    PermissionModelsType,
    ProvisioningTypeType,
    PublisherStatusType,
    RegionConcurrencyTypeType,
    RegistrationStatusType,
    RegistryTypeType,
    ReplacementType,
    RequiresRecreationType,
    ResourceAttributeType,
    ResourceSignalStatusType,
    ResourceStatusType,
    StackDriftDetectionStatusType,
    StackDriftStatusType,
    StackInstanceDetailedStatusType,
    StackInstanceStatusType,
    StackResourceDriftStatusType,
    StackSetDriftDetectionStatusType,
    StackSetDriftStatusType,
    StackSetOperationActionType,
    StackSetOperationResultStatusType,
    StackSetOperationStatusType,
    StackSetStatusType,
    StackStatusType,
    TemplateStageType,
    ThirdPartyTypeType,
    TypeTestsStatusType,
    VersionBumpType,
    VisibilityType,
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
    "AccountGateResultTypeDef",
    "AccountLimitTypeDef",
    "LoggingConfigTypeDef",
    "ResponseMetadataTypeDef",
    "AutoDeploymentTypeDef",
    "TypeConfigurationIdentifierTypeDef",
    "TypeConfigurationDetailsTypeDef",
    "CancelUpdateStackInputRequestTypeDef",
    "CancelUpdateStackInputStackCancelUpdateTypeDef",
    "ChangeSetHookResourceTargetDetailsTypeDef",
    "ChangeSetSummaryTypeDef",
    "ContinueUpdateRollbackInputRequestTypeDef",
    "ParameterTypeDef",
    "ResourceToImportTypeDef",
    "TagTypeDef",
    "DeploymentTargetsTypeDef",
    "StackSetOperationPreferencesTypeDef",
    "ManagedExecutionTypeDef",
    "DeactivateTypeInputRequestTypeDef",
    "DeleteChangeSetInputRequestTypeDef",
    "DeleteStackInputRequestTypeDef",
    "DeleteStackInputStackDeleteTypeDef",
    "DeleteStackSetInputRequestTypeDef",
    "DeregisterTypeInputRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeAccountLimitsInputRequestTypeDef",
    "DescribeChangeSetHooksInputRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeChangeSetInputRequestTypeDef",
    "DescribePublisherInputRequestTypeDef",
    "DescribeStackDriftDetectionStatusInputRequestTypeDef",
    "DescribeStackEventsInputRequestTypeDef",
    "StackEventTypeDef",
    "DescribeStackInstanceInputRequestTypeDef",
    "DescribeStackResourceDriftsInputRequestTypeDef",
    "DescribeStackResourceInputRequestTypeDef",
    "DescribeStackResourcesInputRequestTypeDef",
    "DescribeStackSetInputRequestTypeDef",
    "DescribeStackSetOperationInputRequestTypeDef",
    "DescribeStacksInputRequestTypeDef",
    "DescribeTypeInputRequestTypeDef",
    "RequiredActivatedTypeTypeDef",
    "DescribeTypeRegistrationInputRequestTypeDef",
    "DetectStackDriftInputRequestTypeDef",
    "DetectStackResourceDriftInputRequestTypeDef",
    "ExecuteChangeSetInputRequestTypeDef",
    "ExportTypeDef",
    "GetStackPolicyInputRequestTypeDef",
    "GetTemplateInputRequestTypeDef",
    "GetTemplateSummaryInputRequestTypeDef",
    "ResourceIdentifierSummaryTypeDef",
    "ListChangeSetsInputRequestTypeDef",
    "ListExportsInputRequestTypeDef",
    "ListImportsInputRequestTypeDef",
    "StackInstanceFilterTypeDef",
    "ListStackResourcesInputRequestTypeDef",
    "ListStackSetOperationResultsInputRequestTypeDef",
    "ListStackSetOperationsInputRequestTypeDef",
    "StackSetOperationSummaryTypeDef",
    "ListStackSetsInputRequestTypeDef",
    "ListStacksInputRequestTypeDef",
    "ListTypeRegistrationsInputRequestTypeDef",
    "ListTypeVersionsInputRequestTypeDef",
    "TypeVersionSummaryTypeDef",
    "TypeFiltersTypeDef",
    "TypeSummaryTypeDef",
    "ModuleInfoTypeDef",
    "OutputTypeDef",
    "ParameterConstraintsTypeDef",
    "PhysicalResourceIdContextKeyValuePairTypeDef",
    "PropertyDifferenceTypeDef",
    "PublishTypeInputRequestTypeDef",
    "RecordHandlerProgressInputRequestTypeDef",
    "RegisterPublisherInputRequestTypeDef",
    "ResourceTargetDefinitionTypeDef",
    "RollbackTriggerTypeDef",
    "RollbackStackInputRequestTypeDef",
    "ServiceResourceEventRequestTypeDef",
    "ServiceResourceStackRequestTypeDef",
    "ServiceResourceStackResourceRequestTypeDef",
    "ServiceResourceStackResourceSummaryRequestTypeDef",
    "SetStackPolicyInputRequestTypeDef",
    "SetTypeConfigurationInputRequestTypeDef",
    "SetTypeDefaultVersionInputRequestTypeDef",
    "SignalResourceInputRequestTypeDef",
    "StackDriftInformationSummaryTypeDef",
    "StackDriftInformationTypeDef",
    "StackInstanceComprehensiveStatusTypeDef",
    "StackResourceDriftInformationTypeDef",
    "StackResourceDriftInformationSummaryTypeDef",
    "StackResourceRequestTypeDef",
    "StackSetDriftDetectionDetailsTypeDef",
    "StopStackSetOperationInputRequestTypeDef",
    "TemplateParameterTypeDef",
    "TestTypeInputRequestTypeDef",
    "UpdateTerminationProtectionInputRequestTypeDef",
    "ValidateTemplateInputRequestTypeDef",
    "StackSetOperationResultSummaryTypeDef",
    "ActivateTypeInputRequestTypeDef",
    "RegisterTypeInputRequestTypeDef",
    "ActivateTypeOutputTypeDef",
    "CreateChangeSetOutputTypeDef",
    "CreateStackInstancesOutputTypeDef",
    "CreateStackOutputTypeDef",
    "CreateStackSetOutputTypeDef",
    "DeleteStackInstancesOutputTypeDef",
    "DescribeAccountLimitsOutputTypeDef",
    "DescribePublisherOutputTypeDef",
    "DescribeStackDriftDetectionStatusOutputTypeDef",
    "DescribeTypeRegistrationOutputTypeDef",
    "DetectStackDriftOutputTypeDef",
    "DetectStackSetDriftOutputTypeDef",
    "EstimateTemplateCostOutputTypeDef",
    "GetStackPolicyOutputTypeDef",
    "GetTemplateOutputTypeDef",
    "ImportStacksToStackSetOutputTypeDef",
    "ListImportsOutputTypeDef",
    "ListTypeRegistrationsOutputTypeDef",
    "ModuleInfoResponseMetadataTypeDef",
    "PublishTypeOutputTypeDef",
    "RegisterPublisherOutputTypeDef",
    "RegisterTypeOutputTypeDef",
    "RollbackStackOutputTypeDef",
    "SetTypeConfigurationOutputTypeDef",
    "StackDriftInformationResponseMetadataTypeDef",
    "StackResourceDriftInformationResponseMetadataTypeDef",
    "StackResourceDriftInformationSummaryResponseMetadataTypeDef",
    "TestTypeOutputTypeDef",
    "UpdateStackInstancesOutputTypeDef",
    "UpdateStackOutputTypeDef",
    "UpdateStackSetOutputTypeDef",
    "UpdateTerminationProtectionOutputTypeDef",
    "BatchDescribeTypeConfigurationsErrorTypeDef",
    "BatchDescribeTypeConfigurationsInputRequestTypeDef",
    "ChangeSetHookTargetDetailsTypeDef",
    "ListChangeSetsOutputTypeDef",
    "EstimateTemplateCostInputRequestTypeDef",
    "CreateStackInstancesInputRequestTypeDef",
    "DeleteStackInstancesInputRequestTypeDef",
    "DetectStackSetDriftInputRequestTypeDef",
    "ImportStacksToStackSetInputRequestTypeDef",
    "UpdateStackInstancesInputRequestTypeDef",
    "CreateStackSetInputRequestTypeDef",
    "StackSetSummaryTypeDef",
    "UpdateStackSetInputRequestTypeDef",
    "DescribeAccountLimitsInputDescribeAccountLimitsPaginateTypeDef",
    "DescribeChangeSetInputDescribeChangeSetPaginateTypeDef",
    "DescribeStackEventsInputDescribeStackEventsPaginateTypeDef",
    "DescribeStacksInputDescribeStacksPaginateTypeDef",
    "ListChangeSetsInputListChangeSetsPaginateTypeDef",
    "ListExportsInputListExportsPaginateTypeDef",
    "ListImportsInputListImportsPaginateTypeDef",
    "ListStackResourcesInputListStackResourcesPaginateTypeDef",
    "ListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef",
    "ListStackSetOperationsInputListStackSetOperationsPaginateTypeDef",
    "ListStackSetsInputListStackSetsPaginateTypeDef",
    "ListStacksInputListStacksPaginateTypeDef",
    "DescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef",
    "DescribeStacksInputStackCreateCompleteWaitTypeDef",
    "DescribeStacksInputStackDeleteCompleteWaitTypeDef",
    "DescribeStacksInputStackExistsWaitTypeDef",
    "DescribeStacksInputStackImportCompleteWaitTypeDef",
    "DescribeStacksInputStackRollbackCompleteWaitTypeDef",
    "DescribeStacksInputStackUpdateCompleteWaitTypeDef",
    "DescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef",
    "DescribeStackEventsOutputTypeDef",
    "DescribeTypeOutputTypeDef",
    "ListExportsOutputTypeDef",
    "ListStackInstancesInputListStackInstancesPaginateTypeDef",
    "ListStackInstancesInputRequestTypeDef",
    "ListStackSetOperationsOutputTypeDef",
    "ListTypeVersionsOutputTypeDef",
    "ListTypesInputListTypesPaginateTypeDef",
    "ListTypesInputRequestTypeDef",
    "ListTypesOutputTypeDef",
    "ParameterDeclarationTypeDef",
    "StackResourceDriftTypeDef",
    "ResourceChangeDetailTypeDef",
    "RollbackConfigurationResponseMetadataTypeDef",
    "RollbackConfigurationTypeDef",
    "StackSummaryTypeDef",
    "StackInstanceSummaryTypeDef",
    "StackInstanceTypeDef",
    "StackResourceDetailTypeDef",
    "StackResourceTypeDef",
    "StackResourceSummaryTypeDef",
    "StackSetOperationTypeDef",
    "StackSetTypeDef",
    "ValidateTemplateOutputTypeDef",
    "ListStackSetOperationResultsOutputTypeDef",
    "BatchDescribeTypeConfigurationsOutputTypeDef",
    "ChangeSetHookTypeDef",
    "ListStackSetsOutputTypeDef",
    "GetTemplateSummaryOutputTypeDef",
    "DescribeStackResourceDriftsOutputTypeDef",
    "DetectStackResourceDriftOutputTypeDef",
    "ResourceChangeTypeDef",
    "CreateChangeSetInputRequestTypeDef",
    "CreateStackInputRequestTypeDef",
    "CreateStackInputServiceResourceCreateStackTypeDef",
    "StackTypeDef",
    "UpdateStackInputRequestTypeDef",
    "UpdateStackInputStackUpdateTypeDef",
    "ListStacksOutputTypeDef",
    "ListStackInstancesOutputTypeDef",
    "DescribeStackInstanceOutputTypeDef",
    "DescribeStackResourceOutputTypeDef",
    "DescribeStackResourcesOutputTypeDef",
    "ListStackResourcesOutputTypeDef",
    "DescribeStackSetOperationOutputTypeDef",
    "DescribeStackSetOutputTypeDef",
    "DescribeChangeSetHooksOutputTypeDef",
    "ChangeTypeDef",
    "DescribeStacksOutputTypeDef",
    "DescribeChangeSetOutputTypeDef",
)

AccountGateResultTypeDef = TypedDict(
    "AccountGateResultTypeDef",
    {
        "Status": AccountGateStatusType,
        "StatusReason": str,
    },
    total=False,
)

AccountLimitTypeDef = TypedDict(
    "AccountLimitTypeDef",
    {
        "Name": str,
        "Value": int,
    },
    total=False,
)

LoggingConfigTypeDef = TypedDict(
    "LoggingConfigTypeDef",
    {
        "LogRoleArn": str,
        "LogGroupName": str,
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

AutoDeploymentTypeDef = TypedDict(
    "AutoDeploymentTypeDef",
    {
        "Enabled": bool,
        "RetainStacksOnAccountRemoval": bool,
    },
    total=False,
)

TypeConfigurationIdentifierTypeDef = TypedDict(
    "TypeConfigurationIdentifierTypeDef",
    {
        "TypeArn": str,
        "TypeConfigurationAlias": str,
        "TypeConfigurationArn": str,
        "Type": ThirdPartyTypeType,
        "TypeName": str,
    },
    total=False,
)

TypeConfigurationDetailsTypeDef = TypedDict(
    "TypeConfigurationDetailsTypeDef",
    {
        "Arn": str,
        "Alias": str,
        "Configuration": str,
        "LastUpdated": datetime,
        "TypeArn": str,
        "TypeName": str,
        "IsDefaultConfiguration": bool,
    },
    total=False,
)

_RequiredCancelUpdateStackInputRequestTypeDef = TypedDict(
    "_RequiredCancelUpdateStackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalCancelUpdateStackInputRequestTypeDef = TypedDict(
    "_OptionalCancelUpdateStackInputRequestTypeDef",
    {
        "ClientRequestToken": str,
    },
    total=False,
)


class CancelUpdateStackInputRequestTypeDef(
    _RequiredCancelUpdateStackInputRequestTypeDef, _OptionalCancelUpdateStackInputRequestTypeDef
):
    pass


CancelUpdateStackInputStackCancelUpdateTypeDef = TypedDict(
    "CancelUpdateStackInputStackCancelUpdateTypeDef",
    {
        "ClientRequestToken": str,
    },
    total=False,
)

ChangeSetHookResourceTargetDetailsTypeDef = TypedDict(
    "ChangeSetHookResourceTargetDetailsTypeDef",
    {
        "LogicalResourceId": str,
        "ResourceType": str,
        "ResourceAction": ChangeActionType,
    },
    total=False,
)

ChangeSetSummaryTypeDef = TypedDict(
    "ChangeSetSummaryTypeDef",
    {
        "StackId": str,
        "StackName": str,
        "ChangeSetId": str,
        "ChangeSetName": str,
        "ExecutionStatus": ExecutionStatusType,
        "Status": ChangeSetStatusType,
        "StatusReason": str,
        "CreationTime": datetime,
        "Description": str,
        "IncludeNestedStacks": bool,
        "ParentChangeSetId": str,
        "RootChangeSetId": str,
    },
    total=False,
)

_RequiredContinueUpdateRollbackInputRequestTypeDef = TypedDict(
    "_RequiredContinueUpdateRollbackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalContinueUpdateRollbackInputRequestTypeDef = TypedDict(
    "_OptionalContinueUpdateRollbackInputRequestTypeDef",
    {
        "RoleARN": str,
        "ResourcesToSkip": Sequence[str],
        "ClientRequestToken": str,
    },
    total=False,
)


class ContinueUpdateRollbackInputRequestTypeDef(
    _RequiredContinueUpdateRollbackInputRequestTypeDef,
    _OptionalContinueUpdateRollbackInputRequestTypeDef,
):
    pass


ParameterTypeDef = TypedDict(
    "ParameterTypeDef",
    {
        "ParameterKey": str,
        "ParameterValue": str,
        "UsePreviousValue": bool,
        "ResolvedValue": str,
    },
    total=False,
)

ResourceToImportTypeDef = TypedDict(
    "ResourceToImportTypeDef",
    {
        "ResourceType": str,
        "LogicalResourceId": str,
        "ResourceIdentifier": Mapping[str, str],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

DeploymentTargetsTypeDef = TypedDict(
    "DeploymentTargetsTypeDef",
    {
        "Accounts": Sequence[str],
        "AccountsUrl": str,
        "OrganizationalUnitIds": Sequence[str],
    },
    total=False,
)

StackSetOperationPreferencesTypeDef = TypedDict(
    "StackSetOperationPreferencesTypeDef",
    {
        "RegionConcurrencyType": RegionConcurrencyTypeType,
        "RegionOrder": Sequence[str],
        "FailureToleranceCount": int,
        "FailureTolerancePercentage": int,
        "MaxConcurrentCount": int,
        "MaxConcurrentPercentage": int,
    },
    total=False,
)

ManagedExecutionTypeDef = TypedDict(
    "ManagedExecutionTypeDef",
    {
        "Active": bool,
    },
    total=False,
)

DeactivateTypeInputRequestTypeDef = TypedDict(
    "DeactivateTypeInputRequestTypeDef",
    {
        "TypeName": str,
        "Type": ThirdPartyTypeType,
        "Arn": str,
    },
    total=False,
)

_RequiredDeleteChangeSetInputRequestTypeDef = TypedDict(
    "_RequiredDeleteChangeSetInputRequestTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalDeleteChangeSetInputRequestTypeDef = TypedDict(
    "_OptionalDeleteChangeSetInputRequestTypeDef",
    {
        "StackName": str,
    },
    total=False,
)


class DeleteChangeSetInputRequestTypeDef(
    _RequiredDeleteChangeSetInputRequestTypeDef, _OptionalDeleteChangeSetInputRequestTypeDef
):
    pass


_RequiredDeleteStackInputRequestTypeDef = TypedDict(
    "_RequiredDeleteStackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalDeleteStackInputRequestTypeDef = TypedDict(
    "_OptionalDeleteStackInputRequestTypeDef",
    {
        "RetainResources": Sequence[str],
        "RoleARN": str,
        "ClientRequestToken": str,
    },
    total=False,
)


class DeleteStackInputRequestTypeDef(
    _RequiredDeleteStackInputRequestTypeDef, _OptionalDeleteStackInputRequestTypeDef
):
    pass


DeleteStackInputStackDeleteTypeDef = TypedDict(
    "DeleteStackInputStackDeleteTypeDef",
    {
        "RetainResources": Sequence[str],
        "RoleARN": str,
        "ClientRequestToken": str,
    },
    total=False,
)

_RequiredDeleteStackSetInputRequestTypeDef = TypedDict(
    "_RequiredDeleteStackSetInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalDeleteStackSetInputRequestTypeDef = TypedDict(
    "_OptionalDeleteStackSetInputRequestTypeDef",
    {
        "CallAs": CallAsType,
    },
    total=False,
)


class DeleteStackSetInputRequestTypeDef(
    _RequiredDeleteStackSetInputRequestTypeDef, _OptionalDeleteStackSetInputRequestTypeDef
):
    pass


DeregisterTypeInputRequestTypeDef = TypedDict(
    "DeregisterTypeInputRequestTypeDef",
    {
        "Arn": str,
        "Type": RegistryTypeType,
        "TypeName": str,
        "VersionId": str,
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

DescribeAccountLimitsInputRequestTypeDef = TypedDict(
    "DescribeAccountLimitsInputRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)

_RequiredDescribeChangeSetHooksInputRequestTypeDef = TypedDict(
    "_RequiredDescribeChangeSetHooksInputRequestTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalDescribeChangeSetHooksInputRequestTypeDef = TypedDict(
    "_OptionalDescribeChangeSetHooksInputRequestTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "LogicalResourceId": str,
    },
    total=False,
)


class DescribeChangeSetHooksInputRequestTypeDef(
    _RequiredDescribeChangeSetHooksInputRequestTypeDef,
    _OptionalDescribeChangeSetHooksInputRequestTypeDef,
):
    pass


WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
)

_RequiredDescribeChangeSetInputRequestTypeDef = TypedDict(
    "_RequiredDescribeChangeSetInputRequestTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalDescribeChangeSetInputRequestTypeDef = TypedDict(
    "_OptionalDescribeChangeSetInputRequestTypeDef",
    {
        "StackName": str,
        "NextToken": str,
    },
    total=False,
)


class DescribeChangeSetInputRequestTypeDef(
    _RequiredDescribeChangeSetInputRequestTypeDef, _OptionalDescribeChangeSetInputRequestTypeDef
):
    pass


DescribePublisherInputRequestTypeDef = TypedDict(
    "DescribePublisherInputRequestTypeDef",
    {
        "PublisherId": str,
    },
    total=False,
)

DescribeStackDriftDetectionStatusInputRequestTypeDef = TypedDict(
    "DescribeStackDriftDetectionStatusInputRequestTypeDef",
    {
        "StackDriftDetectionId": str,
    },
)

DescribeStackEventsInputRequestTypeDef = TypedDict(
    "DescribeStackEventsInputRequestTypeDef",
    {
        "StackName": str,
        "NextToken": str,
    },
    total=False,
)

_RequiredStackEventTypeDef = TypedDict(
    "_RequiredStackEventTypeDef",
    {
        "StackId": str,
        "EventId": str,
        "StackName": str,
        "Timestamp": datetime,
    },
)
_OptionalStackEventTypeDef = TypedDict(
    "_OptionalStackEventTypeDef",
    {
        "LogicalResourceId": str,
        "PhysicalResourceId": str,
        "ResourceType": str,
        "ResourceStatus": ResourceStatusType,
        "ResourceStatusReason": str,
        "ResourceProperties": str,
        "ClientRequestToken": str,
        "HookType": str,
        "HookStatus": HookStatusType,
        "HookStatusReason": str,
        "HookInvocationPoint": Literal["PRE_PROVISION"],
        "HookFailureMode": HookFailureModeType,
    },
    total=False,
)


class StackEventTypeDef(_RequiredStackEventTypeDef, _OptionalStackEventTypeDef):
    pass


_RequiredDescribeStackInstanceInputRequestTypeDef = TypedDict(
    "_RequiredDescribeStackInstanceInputRequestTypeDef",
    {
        "StackSetName": str,
        "StackInstanceAccount": str,
        "StackInstanceRegion": str,
    },
)
_OptionalDescribeStackInstanceInputRequestTypeDef = TypedDict(
    "_OptionalDescribeStackInstanceInputRequestTypeDef",
    {
        "CallAs": CallAsType,
    },
    total=False,
)


class DescribeStackInstanceInputRequestTypeDef(
    _RequiredDescribeStackInstanceInputRequestTypeDef,
    _OptionalDescribeStackInstanceInputRequestTypeDef,
):
    pass


_RequiredDescribeStackResourceDriftsInputRequestTypeDef = TypedDict(
    "_RequiredDescribeStackResourceDriftsInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalDescribeStackResourceDriftsInputRequestTypeDef = TypedDict(
    "_OptionalDescribeStackResourceDriftsInputRequestTypeDef",
    {
        "StackResourceDriftStatusFilters": Sequence[StackResourceDriftStatusType],
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class DescribeStackResourceDriftsInputRequestTypeDef(
    _RequiredDescribeStackResourceDriftsInputRequestTypeDef,
    _OptionalDescribeStackResourceDriftsInputRequestTypeDef,
):
    pass


DescribeStackResourceInputRequestTypeDef = TypedDict(
    "DescribeStackResourceInputRequestTypeDef",
    {
        "StackName": str,
        "LogicalResourceId": str,
    },
)

DescribeStackResourcesInputRequestTypeDef = TypedDict(
    "DescribeStackResourcesInputRequestTypeDef",
    {
        "StackName": str,
        "LogicalResourceId": str,
        "PhysicalResourceId": str,
    },
    total=False,
)

_RequiredDescribeStackSetInputRequestTypeDef = TypedDict(
    "_RequiredDescribeStackSetInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalDescribeStackSetInputRequestTypeDef = TypedDict(
    "_OptionalDescribeStackSetInputRequestTypeDef",
    {
        "CallAs": CallAsType,
    },
    total=False,
)


class DescribeStackSetInputRequestTypeDef(
    _RequiredDescribeStackSetInputRequestTypeDef, _OptionalDescribeStackSetInputRequestTypeDef
):
    pass


_RequiredDescribeStackSetOperationInputRequestTypeDef = TypedDict(
    "_RequiredDescribeStackSetOperationInputRequestTypeDef",
    {
        "StackSetName": str,
        "OperationId": str,
    },
)
_OptionalDescribeStackSetOperationInputRequestTypeDef = TypedDict(
    "_OptionalDescribeStackSetOperationInputRequestTypeDef",
    {
        "CallAs": CallAsType,
    },
    total=False,
)


class DescribeStackSetOperationInputRequestTypeDef(
    _RequiredDescribeStackSetOperationInputRequestTypeDef,
    _OptionalDescribeStackSetOperationInputRequestTypeDef,
):
    pass


DescribeStacksInputRequestTypeDef = TypedDict(
    "DescribeStacksInputRequestTypeDef",
    {
        "StackName": str,
        "NextToken": str,
    },
    total=False,
)

DescribeTypeInputRequestTypeDef = TypedDict(
    "DescribeTypeInputRequestTypeDef",
    {
        "Type": RegistryTypeType,
        "TypeName": str,
        "Arn": str,
        "VersionId": str,
        "PublisherId": str,
        "PublicVersionNumber": str,
    },
    total=False,
)

RequiredActivatedTypeTypeDef = TypedDict(
    "RequiredActivatedTypeTypeDef",
    {
        "TypeNameAlias": str,
        "OriginalTypeName": str,
        "PublisherId": str,
        "SupportedMajorVersions": List[int],
    },
    total=False,
)

DescribeTypeRegistrationInputRequestTypeDef = TypedDict(
    "DescribeTypeRegistrationInputRequestTypeDef",
    {
        "RegistrationToken": str,
    },
)

_RequiredDetectStackDriftInputRequestTypeDef = TypedDict(
    "_RequiredDetectStackDriftInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalDetectStackDriftInputRequestTypeDef = TypedDict(
    "_OptionalDetectStackDriftInputRequestTypeDef",
    {
        "LogicalResourceIds": Sequence[str],
    },
    total=False,
)


class DetectStackDriftInputRequestTypeDef(
    _RequiredDetectStackDriftInputRequestTypeDef, _OptionalDetectStackDriftInputRequestTypeDef
):
    pass


DetectStackResourceDriftInputRequestTypeDef = TypedDict(
    "DetectStackResourceDriftInputRequestTypeDef",
    {
        "StackName": str,
        "LogicalResourceId": str,
    },
)

_RequiredExecuteChangeSetInputRequestTypeDef = TypedDict(
    "_RequiredExecuteChangeSetInputRequestTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalExecuteChangeSetInputRequestTypeDef = TypedDict(
    "_OptionalExecuteChangeSetInputRequestTypeDef",
    {
        "StackName": str,
        "ClientRequestToken": str,
        "DisableRollback": bool,
    },
    total=False,
)


class ExecuteChangeSetInputRequestTypeDef(
    _RequiredExecuteChangeSetInputRequestTypeDef, _OptionalExecuteChangeSetInputRequestTypeDef
):
    pass


ExportTypeDef = TypedDict(
    "ExportTypeDef",
    {
        "ExportingStackId": str,
        "Name": str,
        "Value": str,
    },
    total=False,
)

GetStackPolicyInputRequestTypeDef = TypedDict(
    "GetStackPolicyInputRequestTypeDef",
    {
        "StackName": str,
    },
)

GetTemplateInputRequestTypeDef = TypedDict(
    "GetTemplateInputRequestTypeDef",
    {
        "StackName": str,
        "ChangeSetName": str,
        "TemplateStage": TemplateStageType,
    },
    total=False,
)

GetTemplateSummaryInputRequestTypeDef = TypedDict(
    "GetTemplateSummaryInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "StackName": str,
        "StackSetName": str,
        "CallAs": CallAsType,
    },
    total=False,
)

ResourceIdentifierSummaryTypeDef = TypedDict(
    "ResourceIdentifierSummaryTypeDef",
    {
        "ResourceType": str,
        "LogicalResourceIds": List[str],
        "ResourceIdentifiers": List[str],
    },
    total=False,
)

_RequiredListChangeSetsInputRequestTypeDef = TypedDict(
    "_RequiredListChangeSetsInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalListChangeSetsInputRequestTypeDef = TypedDict(
    "_OptionalListChangeSetsInputRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)


class ListChangeSetsInputRequestTypeDef(
    _RequiredListChangeSetsInputRequestTypeDef, _OptionalListChangeSetsInputRequestTypeDef
):
    pass


ListExportsInputRequestTypeDef = TypedDict(
    "ListExportsInputRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)

_RequiredListImportsInputRequestTypeDef = TypedDict(
    "_RequiredListImportsInputRequestTypeDef",
    {
        "ExportName": str,
    },
)
_OptionalListImportsInputRequestTypeDef = TypedDict(
    "_OptionalListImportsInputRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)


class ListImportsInputRequestTypeDef(
    _RequiredListImportsInputRequestTypeDef, _OptionalListImportsInputRequestTypeDef
):
    pass


StackInstanceFilterTypeDef = TypedDict(
    "StackInstanceFilterTypeDef",
    {
        "Name": Literal["DETAILED_STATUS"],
        "Values": str,
    },
    total=False,
)

_RequiredListStackResourcesInputRequestTypeDef = TypedDict(
    "_RequiredListStackResourcesInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalListStackResourcesInputRequestTypeDef = TypedDict(
    "_OptionalListStackResourcesInputRequestTypeDef",
    {
        "NextToken": str,
    },
    total=False,
)


class ListStackResourcesInputRequestTypeDef(
    _RequiredListStackResourcesInputRequestTypeDef, _OptionalListStackResourcesInputRequestTypeDef
):
    pass


_RequiredListStackSetOperationResultsInputRequestTypeDef = TypedDict(
    "_RequiredListStackSetOperationResultsInputRequestTypeDef",
    {
        "StackSetName": str,
        "OperationId": str,
    },
)
_OptionalListStackSetOperationResultsInputRequestTypeDef = TypedDict(
    "_OptionalListStackSetOperationResultsInputRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "CallAs": CallAsType,
    },
    total=False,
)


class ListStackSetOperationResultsInputRequestTypeDef(
    _RequiredListStackSetOperationResultsInputRequestTypeDef,
    _OptionalListStackSetOperationResultsInputRequestTypeDef,
):
    pass


_RequiredListStackSetOperationsInputRequestTypeDef = TypedDict(
    "_RequiredListStackSetOperationsInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalListStackSetOperationsInputRequestTypeDef = TypedDict(
    "_OptionalListStackSetOperationsInputRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "CallAs": CallAsType,
    },
    total=False,
)


class ListStackSetOperationsInputRequestTypeDef(
    _RequiredListStackSetOperationsInputRequestTypeDef,
    _OptionalListStackSetOperationsInputRequestTypeDef,
):
    pass


StackSetOperationSummaryTypeDef = TypedDict(
    "StackSetOperationSummaryTypeDef",
    {
        "OperationId": str,
        "Action": StackSetOperationActionType,
        "Status": StackSetOperationStatusType,
        "CreationTimestamp": datetime,
        "EndTimestamp": datetime,
        "StatusReason": str,
    },
    total=False,
)

ListStackSetsInputRequestTypeDef = TypedDict(
    "ListStackSetsInputRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "Status": StackSetStatusType,
        "CallAs": CallAsType,
    },
    total=False,
)

ListStacksInputRequestTypeDef = TypedDict(
    "ListStacksInputRequestTypeDef",
    {
        "NextToken": str,
        "StackStatusFilter": Sequence[StackStatusType],
    },
    total=False,
)

ListTypeRegistrationsInputRequestTypeDef = TypedDict(
    "ListTypeRegistrationsInputRequestTypeDef",
    {
        "Type": RegistryTypeType,
        "TypeName": str,
        "TypeArn": str,
        "RegistrationStatusFilter": RegistrationStatusType,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListTypeVersionsInputRequestTypeDef = TypedDict(
    "ListTypeVersionsInputRequestTypeDef",
    {
        "Type": RegistryTypeType,
        "TypeName": str,
        "Arn": str,
        "MaxResults": int,
        "NextToken": str,
        "DeprecatedStatus": DeprecatedStatusType,
        "PublisherId": str,
    },
    total=False,
)

TypeVersionSummaryTypeDef = TypedDict(
    "TypeVersionSummaryTypeDef",
    {
        "Type": RegistryTypeType,
        "TypeName": str,
        "VersionId": str,
        "IsDefaultVersion": bool,
        "Arn": str,
        "TimeCreated": datetime,
        "Description": str,
        "PublicVersionNumber": str,
    },
    total=False,
)

TypeFiltersTypeDef = TypedDict(
    "TypeFiltersTypeDef",
    {
        "Category": CategoryType,
        "PublisherId": str,
        "TypeNamePrefix": str,
    },
    total=False,
)

TypeSummaryTypeDef = TypedDict(
    "TypeSummaryTypeDef",
    {
        "Type": RegistryTypeType,
        "TypeName": str,
        "DefaultVersionId": str,
        "TypeArn": str,
        "LastUpdated": datetime,
        "Description": str,
        "PublisherId": str,
        "OriginalTypeName": str,
        "PublicVersionNumber": str,
        "LatestPublicVersion": str,
        "PublisherIdentity": IdentityProviderType,
        "PublisherName": str,
        "IsActivated": bool,
    },
    total=False,
)

ModuleInfoTypeDef = TypedDict(
    "ModuleInfoTypeDef",
    {
        "TypeHierarchy": str,
        "LogicalIdHierarchy": str,
    },
    total=False,
)

OutputTypeDef = TypedDict(
    "OutputTypeDef",
    {
        "OutputKey": str,
        "OutputValue": str,
        "Description": str,
        "ExportName": str,
    },
    total=False,
)

ParameterConstraintsTypeDef = TypedDict(
    "ParameterConstraintsTypeDef",
    {
        "AllowedValues": List[str],
    },
    total=False,
)

PhysicalResourceIdContextKeyValuePairTypeDef = TypedDict(
    "PhysicalResourceIdContextKeyValuePairTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

PropertyDifferenceTypeDef = TypedDict(
    "PropertyDifferenceTypeDef",
    {
        "PropertyPath": str,
        "ExpectedValue": str,
        "ActualValue": str,
        "DifferenceType": DifferenceTypeType,
    },
)

PublishTypeInputRequestTypeDef = TypedDict(
    "PublishTypeInputRequestTypeDef",
    {
        "Type": ThirdPartyTypeType,
        "Arn": str,
        "TypeName": str,
        "PublicVersionNumber": str,
    },
    total=False,
)

_RequiredRecordHandlerProgressInputRequestTypeDef = TypedDict(
    "_RequiredRecordHandlerProgressInputRequestTypeDef",
    {
        "BearerToken": str,
        "OperationStatus": OperationStatusType,
    },
)
_OptionalRecordHandlerProgressInputRequestTypeDef = TypedDict(
    "_OptionalRecordHandlerProgressInputRequestTypeDef",
    {
        "CurrentOperationStatus": OperationStatusType,
        "StatusMessage": str,
        "ErrorCode": HandlerErrorCodeType,
        "ResourceModel": str,
        "ClientRequestToken": str,
    },
    total=False,
)


class RecordHandlerProgressInputRequestTypeDef(
    _RequiredRecordHandlerProgressInputRequestTypeDef,
    _OptionalRecordHandlerProgressInputRequestTypeDef,
):
    pass


RegisterPublisherInputRequestTypeDef = TypedDict(
    "RegisterPublisherInputRequestTypeDef",
    {
        "AcceptTermsAndConditions": bool,
        "ConnectionArn": str,
    },
    total=False,
)

ResourceTargetDefinitionTypeDef = TypedDict(
    "ResourceTargetDefinitionTypeDef",
    {
        "Attribute": ResourceAttributeType,
        "Name": str,
        "RequiresRecreation": RequiresRecreationType,
    },
    total=False,
)

RollbackTriggerTypeDef = TypedDict(
    "RollbackTriggerTypeDef",
    {
        "Arn": str,
        "Type": str,
    },
)

_RequiredRollbackStackInputRequestTypeDef = TypedDict(
    "_RequiredRollbackStackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalRollbackStackInputRequestTypeDef = TypedDict(
    "_OptionalRollbackStackInputRequestTypeDef",
    {
        "RoleARN": str,
        "ClientRequestToken": str,
    },
    total=False,
)


class RollbackStackInputRequestTypeDef(
    _RequiredRollbackStackInputRequestTypeDef, _OptionalRollbackStackInputRequestTypeDef
):
    pass


ServiceResourceEventRequestTypeDef = TypedDict(
    "ServiceResourceEventRequestTypeDef",
    {
        "id": str,
    },
)

ServiceResourceStackRequestTypeDef = TypedDict(
    "ServiceResourceStackRequestTypeDef",
    {
        "name": str,
    },
)

ServiceResourceStackResourceRequestTypeDef = TypedDict(
    "ServiceResourceStackResourceRequestTypeDef",
    {
        "stack_name": str,
        "logical_id": str,
    },
)

ServiceResourceStackResourceSummaryRequestTypeDef = TypedDict(
    "ServiceResourceStackResourceSummaryRequestTypeDef",
    {
        "stack_name": str,
        "logical_id": str,
    },
)

_RequiredSetStackPolicyInputRequestTypeDef = TypedDict(
    "_RequiredSetStackPolicyInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalSetStackPolicyInputRequestTypeDef = TypedDict(
    "_OptionalSetStackPolicyInputRequestTypeDef",
    {
        "StackPolicyBody": str,
        "StackPolicyURL": str,
    },
    total=False,
)


class SetStackPolicyInputRequestTypeDef(
    _RequiredSetStackPolicyInputRequestTypeDef, _OptionalSetStackPolicyInputRequestTypeDef
):
    pass


_RequiredSetTypeConfigurationInputRequestTypeDef = TypedDict(
    "_RequiredSetTypeConfigurationInputRequestTypeDef",
    {
        "Configuration": str,
    },
)
_OptionalSetTypeConfigurationInputRequestTypeDef = TypedDict(
    "_OptionalSetTypeConfigurationInputRequestTypeDef",
    {
        "TypeArn": str,
        "ConfigurationAlias": str,
        "TypeName": str,
        "Type": ThirdPartyTypeType,
    },
    total=False,
)


class SetTypeConfigurationInputRequestTypeDef(
    _RequiredSetTypeConfigurationInputRequestTypeDef,
    _OptionalSetTypeConfigurationInputRequestTypeDef,
):
    pass


SetTypeDefaultVersionInputRequestTypeDef = TypedDict(
    "SetTypeDefaultVersionInputRequestTypeDef",
    {
        "Arn": str,
        "Type": RegistryTypeType,
        "TypeName": str,
        "VersionId": str,
    },
    total=False,
)

SignalResourceInputRequestTypeDef = TypedDict(
    "SignalResourceInputRequestTypeDef",
    {
        "StackName": str,
        "LogicalResourceId": str,
        "UniqueId": str,
        "Status": ResourceSignalStatusType,
    },
)

_RequiredStackDriftInformationSummaryTypeDef = TypedDict(
    "_RequiredStackDriftInformationSummaryTypeDef",
    {
        "StackDriftStatus": StackDriftStatusType,
    },
)
_OptionalStackDriftInformationSummaryTypeDef = TypedDict(
    "_OptionalStackDriftInformationSummaryTypeDef",
    {
        "LastCheckTimestamp": datetime,
    },
    total=False,
)


class StackDriftInformationSummaryTypeDef(
    _RequiredStackDriftInformationSummaryTypeDef, _OptionalStackDriftInformationSummaryTypeDef
):
    pass


_RequiredStackDriftInformationTypeDef = TypedDict(
    "_RequiredStackDriftInformationTypeDef",
    {
        "StackDriftStatus": StackDriftStatusType,
    },
)
_OptionalStackDriftInformationTypeDef = TypedDict(
    "_OptionalStackDriftInformationTypeDef",
    {
        "LastCheckTimestamp": datetime,
    },
    total=False,
)


class StackDriftInformationTypeDef(
    _RequiredStackDriftInformationTypeDef, _OptionalStackDriftInformationTypeDef
):
    pass


StackInstanceComprehensiveStatusTypeDef = TypedDict(
    "StackInstanceComprehensiveStatusTypeDef",
    {
        "DetailedStatus": StackInstanceDetailedStatusType,
    },
    total=False,
)

_RequiredStackResourceDriftInformationTypeDef = TypedDict(
    "_RequiredStackResourceDriftInformationTypeDef",
    {
        "StackResourceDriftStatus": StackResourceDriftStatusType,
    },
)
_OptionalStackResourceDriftInformationTypeDef = TypedDict(
    "_OptionalStackResourceDriftInformationTypeDef",
    {
        "LastCheckTimestamp": datetime,
    },
    total=False,
)


class StackResourceDriftInformationTypeDef(
    _RequiredStackResourceDriftInformationTypeDef, _OptionalStackResourceDriftInformationTypeDef
):
    pass


_RequiredStackResourceDriftInformationSummaryTypeDef = TypedDict(
    "_RequiredStackResourceDriftInformationSummaryTypeDef",
    {
        "StackResourceDriftStatus": StackResourceDriftStatusType,
    },
)
_OptionalStackResourceDriftInformationSummaryTypeDef = TypedDict(
    "_OptionalStackResourceDriftInformationSummaryTypeDef",
    {
        "LastCheckTimestamp": datetime,
    },
    total=False,
)


class StackResourceDriftInformationSummaryTypeDef(
    _RequiredStackResourceDriftInformationSummaryTypeDef,
    _OptionalStackResourceDriftInformationSummaryTypeDef,
):
    pass


StackResourceRequestTypeDef = TypedDict(
    "StackResourceRequestTypeDef",
    {
        "logical_id": str,
    },
)

StackSetDriftDetectionDetailsTypeDef = TypedDict(
    "StackSetDriftDetectionDetailsTypeDef",
    {
        "DriftStatus": StackSetDriftStatusType,
        "DriftDetectionStatus": StackSetDriftDetectionStatusType,
        "LastDriftCheckTimestamp": datetime,
        "TotalStackInstancesCount": int,
        "DriftedStackInstancesCount": int,
        "InSyncStackInstancesCount": int,
        "InProgressStackInstancesCount": int,
        "FailedStackInstancesCount": int,
    },
    total=False,
)

_RequiredStopStackSetOperationInputRequestTypeDef = TypedDict(
    "_RequiredStopStackSetOperationInputRequestTypeDef",
    {
        "StackSetName": str,
        "OperationId": str,
    },
)
_OptionalStopStackSetOperationInputRequestTypeDef = TypedDict(
    "_OptionalStopStackSetOperationInputRequestTypeDef",
    {
        "CallAs": CallAsType,
    },
    total=False,
)


class StopStackSetOperationInputRequestTypeDef(
    _RequiredStopStackSetOperationInputRequestTypeDef,
    _OptionalStopStackSetOperationInputRequestTypeDef,
):
    pass


TemplateParameterTypeDef = TypedDict(
    "TemplateParameterTypeDef",
    {
        "ParameterKey": str,
        "DefaultValue": str,
        "NoEcho": bool,
        "Description": str,
    },
    total=False,
)

TestTypeInputRequestTypeDef = TypedDict(
    "TestTypeInputRequestTypeDef",
    {
        "Arn": str,
        "Type": ThirdPartyTypeType,
        "TypeName": str,
        "VersionId": str,
        "LogDeliveryBucket": str,
    },
    total=False,
)

UpdateTerminationProtectionInputRequestTypeDef = TypedDict(
    "UpdateTerminationProtectionInputRequestTypeDef",
    {
        "EnableTerminationProtection": bool,
        "StackName": str,
    },
)

ValidateTemplateInputRequestTypeDef = TypedDict(
    "ValidateTemplateInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
    },
    total=False,
)

StackSetOperationResultSummaryTypeDef = TypedDict(
    "StackSetOperationResultSummaryTypeDef",
    {
        "Account": str,
        "Region": str,
        "Status": StackSetOperationResultStatusType,
        "StatusReason": str,
        "AccountGateResult": AccountGateResultTypeDef,
        "OrganizationalUnitId": str,
    },
    total=False,
)

ActivateTypeInputRequestTypeDef = TypedDict(
    "ActivateTypeInputRequestTypeDef",
    {
        "Type": ThirdPartyTypeType,
        "PublicTypeArn": str,
        "PublisherId": str,
        "TypeName": str,
        "TypeNameAlias": str,
        "AutoUpdate": bool,
        "LoggingConfig": LoggingConfigTypeDef,
        "ExecutionRoleArn": str,
        "VersionBump": VersionBumpType,
        "MajorVersion": int,
    },
    total=False,
)

_RequiredRegisterTypeInputRequestTypeDef = TypedDict(
    "_RequiredRegisterTypeInputRequestTypeDef",
    {
        "TypeName": str,
        "SchemaHandlerPackage": str,
    },
)
_OptionalRegisterTypeInputRequestTypeDef = TypedDict(
    "_OptionalRegisterTypeInputRequestTypeDef",
    {
        "Type": RegistryTypeType,
        "LoggingConfig": LoggingConfigTypeDef,
        "ExecutionRoleArn": str,
        "ClientRequestToken": str,
    },
    total=False,
)


class RegisterTypeInputRequestTypeDef(
    _RequiredRegisterTypeInputRequestTypeDef, _OptionalRegisterTypeInputRequestTypeDef
):
    pass


ActivateTypeOutputTypeDef = TypedDict(
    "ActivateTypeOutputTypeDef",
    {
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateChangeSetOutputTypeDef = TypedDict(
    "CreateChangeSetOutputTypeDef",
    {
        "Id": str,
        "StackId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStackInstancesOutputTypeDef = TypedDict(
    "CreateStackInstancesOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStackOutputTypeDef = TypedDict(
    "CreateStackOutputTypeDef",
    {
        "StackId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStackSetOutputTypeDef = TypedDict(
    "CreateStackSetOutputTypeDef",
    {
        "StackSetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteStackInstancesOutputTypeDef = TypedDict(
    "DeleteStackInstancesOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAccountLimitsOutputTypeDef = TypedDict(
    "DescribeAccountLimitsOutputTypeDef",
    {
        "AccountLimits": List[AccountLimitTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePublisherOutputTypeDef = TypedDict(
    "DescribePublisherOutputTypeDef",
    {
        "PublisherId": str,
        "PublisherStatus": PublisherStatusType,
        "IdentityProvider": IdentityProviderType,
        "PublisherProfile": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackDriftDetectionStatusOutputTypeDef = TypedDict(
    "DescribeStackDriftDetectionStatusOutputTypeDef",
    {
        "StackId": str,
        "StackDriftDetectionId": str,
        "StackDriftStatus": StackDriftStatusType,
        "DetectionStatus": StackDriftDetectionStatusType,
        "DetectionStatusReason": str,
        "DriftedStackResourceCount": int,
        "Timestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTypeRegistrationOutputTypeDef = TypedDict(
    "DescribeTypeRegistrationOutputTypeDef",
    {
        "ProgressStatus": RegistrationStatusType,
        "Description": str,
        "TypeArn": str,
        "TypeVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectStackDriftOutputTypeDef = TypedDict(
    "DetectStackDriftOutputTypeDef",
    {
        "StackDriftDetectionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectStackSetDriftOutputTypeDef = TypedDict(
    "DetectStackSetDriftOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EstimateTemplateCostOutputTypeDef = TypedDict(
    "EstimateTemplateCostOutputTypeDef",
    {
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetStackPolicyOutputTypeDef = TypedDict(
    "GetStackPolicyOutputTypeDef",
    {
        "StackPolicyBody": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTemplateOutputTypeDef = TypedDict(
    "GetTemplateOutputTypeDef",
    {
        "TemplateBody": str,
        "StagesAvailable": List[TemplateStageType],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportStacksToStackSetOutputTypeDef = TypedDict(
    "ImportStacksToStackSetOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListImportsOutputTypeDef = TypedDict(
    "ListImportsOutputTypeDef",
    {
        "Imports": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTypeRegistrationsOutputTypeDef = TypedDict(
    "ListTypeRegistrationsOutputTypeDef",
    {
        "RegistrationTokenList": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModuleInfoResponseMetadataTypeDef = TypedDict(
    "ModuleInfoResponseMetadataTypeDef",
    {
        "TypeHierarchy": str,
        "LogicalIdHierarchy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PublishTypeOutputTypeDef = TypedDict(
    "PublishTypeOutputTypeDef",
    {
        "PublicTypeArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterPublisherOutputTypeDef = TypedDict(
    "RegisterPublisherOutputTypeDef",
    {
        "PublisherId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RegisterTypeOutputTypeDef = TypedDict(
    "RegisterTypeOutputTypeDef",
    {
        "RegistrationToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RollbackStackOutputTypeDef = TypedDict(
    "RollbackStackOutputTypeDef",
    {
        "StackId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SetTypeConfigurationOutputTypeDef = TypedDict(
    "SetTypeConfigurationOutputTypeDef",
    {
        "ConfigurationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StackDriftInformationResponseMetadataTypeDef = TypedDict(
    "StackDriftInformationResponseMetadataTypeDef",
    {
        "StackDriftStatus": StackDriftStatusType,
        "LastCheckTimestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StackResourceDriftInformationResponseMetadataTypeDef = TypedDict(
    "StackResourceDriftInformationResponseMetadataTypeDef",
    {
        "StackResourceDriftStatus": StackResourceDriftStatusType,
        "LastCheckTimestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StackResourceDriftInformationSummaryResponseMetadataTypeDef = TypedDict(
    "StackResourceDriftInformationSummaryResponseMetadataTypeDef",
    {
        "StackResourceDriftStatus": StackResourceDriftStatusType,
        "LastCheckTimestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TestTypeOutputTypeDef = TypedDict(
    "TestTypeOutputTypeDef",
    {
        "TypeVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateStackInstancesOutputTypeDef = TypedDict(
    "UpdateStackInstancesOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateStackOutputTypeDef = TypedDict(
    "UpdateStackOutputTypeDef",
    {
        "StackId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateStackSetOutputTypeDef = TypedDict(
    "UpdateStackSetOutputTypeDef",
    {
        "OperationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTerminationProtectionOutputTypeDef = TypedDict(
    "UpdateTerminationProtectionOutputTypeDef",
    {
        "StackId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDescribeTypeConfigurationsErrorTypeDef = TypedDict(
    "BatchDescribeTypeConfigurationsErrorTypeDef",
    {
        "ErrorCode": str,
        "ErrorMessage": str,
        "TypeConfigurationIdentifier": TypeConfigurationIdentifierTypeDef,
    },
    total=False,
)

BatchDescribeTypeConfigurationsInputRequestTypeDef = TypedDict(
    "BatchDescribeTypeConfigurationsInputRequestTypeDef",
    {
        "TypeConfigurationIdentifiers": Sequence[TypeConfigurationIdentifierTypeDef],
    },
)

ChangeSetHookTargetDetailsTypeDef = TypedDict(
    "ChangeSetHookTargetDetailsTypeDef",
    {
        "TargetType": Literal["RESOURCE"],
        "ResourceTargetDetails": ChangeSetHookResourceTargetDetailsTypeDef,
    },
    total=False,
)

ListChangeSetsOutputTypeDef = TypedDict(
    "ListChangeSetsOutputTypeDef",
    {
        "Summaries": List[ChangeSetSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EstimateTemplateCostInputRequestTypeDef = TypedDict(
    "EstimateTemplateCostInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "Parameters": Sequence[ParameterTypeDef],
    },
    total=False,
)

_RequiredCreateStackInstancesInputRequestTypeDef = TypedDict(
    "_RequiredCreateStackInstancesInputRequestTypeDef",
    {
        "StackSetName": str,
        "Regions": Sequence[str],
    },
)
_OptionalCreateStackInstancesInputRequestTypeDef = TypedDict(
    "_OptionalCreateStackInstancesInputRequestTypeDef",
    {
        "Accounts": Sequence[str],
        "DeploymentTargets": DeploymentTargetsTypeDef,
        "ParameterOverrides": Sequence[ParameterTypeDef],
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "OperationId": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class CreateStackInstancesInputRequestTypeDef(
    _RequiredCreateStackInstancesInputRequestTypeDef,
    _OptionalCreateStackInstancesInputRequestTypeDef,
):
    pass


_RequiredDeleteStackInstancesInputRequestTypeDef = TypedDict(
    "_RequiredDeleteStackInstancesInputRequestTypeDef",
    {
        "StackSetName": str,
        "Regions": Sequence[str],
        "RetainStacks": bool,
    },
)
_OptionalDeleteStackInstancesInputRequestTypeDef = TypedDict(
    "_OptionalDeleteStackInstancesInputRequestTypeDef",
    {
        "Accounts": Sequence[str],
        "DeploymentTargets": DeploymentTargetsTypeDef,
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "OperationId": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class DeleteStackInstancesInputRequestTypeDef(
    _RequiredDeleteStackInstancesInputRequestTypeDef,
    _OptionalDeleteStackInstancesInputRequestTypeDef,
):
    pass


_RequiredDetectStackSetDriftInputRequestTypeDef = TypedDict(
    "_RequiredDetectStackSetDriftInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalDetectStackSetDriftInputRequestTypeDef = TypedDict(
    "_OptionalDetectStackSetDriftInputRequestTypeDef",
    {
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "OperationId": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class DetectStackSetDriftInputRequestTypeDef(
    _RequiredDetectStackSetDriftInputRequestTypeDef, _OptionalDetectStackSetDriftInputRequestTypeDef
):
    pass


_RequiredImportStacksToStackSetInputRequestTypeDef = TypedDict(
    "_RequiredImportStacksToStackSetInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalImportStacksToStackSetInputRequestTypeDef = TypedDict(
    "_OptionalImportStacksToStackSetInputRequestTypeDef",
    {
        "StackIds": Sequence[str],
        "StackIdsUrl": str,
        "OrganizationalUnitIds": Sequence[str],
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "OperationId": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class ImportStacksToStackSetInputRequestTypeDef(
    _RequiredImportStacksToStackSetInputRequestTypeDef,
    _OptionalImportStacksToStackSetInputRequestTypeDef,
):
    pass


_RequiredUpdateStackInstancesInputRequestTypeDef = TypedDict(
    "_RequiredUpdateStackInstancesInputRequestTypeDef",
    {
        "StackSetName": str,
        "Regions": Sequence[str],
    },
)
_OptionalUpdateStackInstancesInputRequestTypeDef = TypedDict(
    "_OptionalUpdateStackInstancesInputRequestTypeDef",
    {
        "Accounts": Sequence[str],
        "DeploymentTargets": DeploymentTargetsTypeDef,
        "ParameterOverrides": Sequence[ParameterTypeDef],
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "OperationId": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class UpdateStackInstancesInputRequestTypeDef(
    _RequiredUpdateStackInstancesInputRequestTypeDef,
    _OptionalUpdateStackInstancesInputRequestTypeDef,
):
    pass


_RequiredCreateStackSetInputRequestTypeDef = TypedDict(
    "_RequiredCreateStackSetInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalCreateStackSetInputRequestTypeDef = TypedDict(
    "_OptionalCreateStackSetInputRequestTypeDef",
    {
        "Description": str,
        "TemplateBody": str,
        "TemplateURL": str,
        "StackId": str,
        "Parameters": Sequence[ParameterTypeDef],
        "Capabilities": Sequence[CapabilityType],
        "Tags": Sequence[TagTypeDef],
        "AdministrationRoleARN": str,
        "ExecutionRoleName": str,
        "PermissionModel": PermissionModelsType,
        "AutoDeployment": AutoDeploymentTypeDef,
        "CallAs": CallAsType,
        "ClientRequestToken": str,
        "ManagedExecution": ManagedExecutionTypeDef,
    },
    total=False,
)


class CreateStackSetInputRequestTypeDef(
    _RequiredCreateStackSetInputRequestTypeDef, _OptionalCreateStackSetInputRequestTypeDef
):
    pass


StackSetSummaryTypeDef = TypedDict(
    "StackSetSummaryTypeDef",
    {
        "StackSetName": str,
        "StackSetId": str,
        "Description": str,
        "Status": StackSetStatusType,
        "AutoDeployment": AutoDeploymentTypeDef,
        "PermissionModel": PermissionModelsType,
        "DriftStatus": StackDriftStatusType,
        "LastDriftCheckTimestamp": datetime,
        "ManagedExecution": ManagedExecutionTypeDef,
    },
    total=False,
)

_RequiredUpdateStackSetInputRequestTypeDef = TypedDict(
    "_RequiredUpdateStackSetInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalUpdateStackSetInputRequestTypeDef = TypedDict(
    "_OptionalUpdateStackSetInputRequestTypeDef",
    {
        "Description": str,
        "TemplateBody": str,
        "TemplateURL": str,
        "UsePreviousTemplate": bool,
        "Parameters": Sequence[ParameterTypeDef],
        "Capabilities": Sequence[CapabilityType],
        "Tags": Sequence[TagTypeDef],
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "AdministrationRoleARN": str,
        "ExecutionRoleName": str,
        "DeploymentTargets": DeploymentTargetsTypeDef,
        "PermissionModel": PermissionModelsType,
        "AutoDeployment": AutoDeploymentTypeDef,
        "OperationId": str,
        "Accounts": Sequence[str],
        "Regions": Sequence[str],
        "CallAs": CallAsType,
        "ManagedExecution": ManagedExecutionTypeDef,
    },
    total=False,
)


class UpdateStackSetInputRequestTypeDef(
    _RequiredUpdateStackSetInputRequestTypeDef, _OptionalUpdateStackSetInputRequestTypeDef
):
    pass


DescribeAccountLimitsInputDescribeAccountLimitsPaginateTypeDef = TypedDict(
    "DescribeAccountLimitsInputDescribeAccountLimitsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeChangeSetInputDescribeChangeSetPaginateTypeDef = TypedDict(
    "_RequiredDescribeChangeSetInputDescribeChangeSetPaginateTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalDescribeChangeSetInputDescribeChangeSetPaginateTypeDef = TypedDict(
    "_OptionalDescribeChangeSetInputDescribeChangeSetPaginateTypeDef",
    {
        "StackName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeChangeSetInputDescribeChangeSetPaginateTypeDef(
    _RequiredDescribeChangeSetInputDescribeChangeSetPaginateTypeDef,
    _OptionalDescribeChangeSetInputDescribeChangeSetPaginateTypeDef,
):
    pass


DescribeStackEventsInputDescribeStackEventsPaginateTypeDef = TypedDict(
    "DescribeStackEventsInputDescribeStackEventsPaginateTypeDef",
    {
        "StackName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputDescribeStacksPaginateTypeDef = TypedDict(
    "DescribeStacksInputDescribeStacksPaginateTypeDef",
    {
        "StackName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListChangeSetsInputListChangeSetsPaginateTypeDef = TypedDict(
    "_RequiredListChangeSetsInputListChangeSetsPaginateTypeDef",
    {
        "StackName": str,
    },
)
_OptionalListChangeSetsInputListChangeSetsPaginateTypeDef = TypedDict(
    "_OptionalListChangeSetsInputListChangeSetsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListChangeSetsInputListChangeSetsPaginateTypeDef(
    _RequiredListChangeSetsInputListChangeSetsPaginateTypeDef,
    _OptionalListChangeSetsInputListChangeSetsPaginateTypeDef,
):
    pass


ListExportsInputListExportsPaginateTypeDef = TypedDict(
    "ListExportsInputListExportsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredListImportsInputListImportsPaginateTypeDef = TypedDict(
    "_RequiredListImportsInputListImportsPaginateTypeDef",
    {
        "ExportName": str,
    },
)
_OptionalListImportsInputListImportsPaginateTypeDef = TypedDict(
    "_OptionalListImportsInputListImportsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListImportsInputListImportsPaginateTypeDef(
    _RequiredListImportsInputListImportsPaginateTypeDef,
    _OptionalListImportsInputListImportsPaginateTypeDef,
):
    pass


_RequiredListStackResourcesInputListStackResourcesPaginateTypeDef = TypedDict(
    "_RequiredListStackResourcesInputListStackResourcesPaginateTypeDef",
    {
        "StackName": str,
    },
)
_OptionalListStackResourcesInputListStackResourcesPaginateTypeDef = TypedDict(
    "_OptionalListStackResourcesInputListStackResourcesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListStackResourcesInputListStackResourcesPaginateTypeDef(
    _RequiredListStackResourcesInputListStackResourcesPaginateTypeDef,
    _OptionalListStackResourcesInputListStackResourcesPaginateTypeDef,
):
    pass


_RequiredListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef = TypedDict(
    "_RequiredListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef",
    {
        "StackSetName": str,
        "OperationId": str,
    },
)
_OptionalListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef = TypedDict(
    "_OptionalListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef",
    {
        "CallAs": CallAsType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef(
    _RequiredListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef,
    _OptionalListStackSetOperationResultsInputListStackSetOperationResultsPaginateTypeDef,
):
    pass


_RequiredListStackSetOperationsInputListStackSetOperationsPaginateTypeDef = TypedDict(
    "_RequiredListStackSetOperationsInputListStackSetOperationsPaginateTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalListStackSetOperationsInputListStackSetOperationsPaginateTypeDef = TypedDict(
    "_OptionalListStackSetOperationsInputListStackSetOperationsPaginateTypeDef",
    {
        "CallAs": CallAsType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListStackSetOperationsInputListStackSetOperationsPaginateTypeDef(
    _RequiredListStackSetOperationsInputListStackSetOperationsPaginateTypeDef,
    _OptionalListStackSetOperationsInputListStackSetOperationsPaginateTypeDef,
):
    pass


ListStackSetsInputListStackSetsPaginateTypeDef = TypedDict(
    "ListStackSetsInputListStackSetsPaginateTypeDef",
    {
        "Status": StackSetStatusType,
        "CallAs": CallAsType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListStacksInputListStacksPaginateTypeDef = TypedDict(
    "ListStacksInputListStacksPaginateTypeDef",
    {
        "StackStatusFilter": Sequence[StackStatusType],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef = TypedDict(
    "_RequiredDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef",
    {
        "ChangeSetName": str,
    },
)
_OptionalDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef = TypedDict(
    "_OptionalDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)


class DescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef(
    _RequiredDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef,
    _OptionalDescribeChangeSetInputChangeSetCreateCompleteWaitTypeDef,
):
    pass


DescribeStacksInputStackCreateCompleteWaitTypeDef = TypedDict(
    "DescribeStacksInputStackCreateCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputStackDeleteCompleteWaitTypeDef = TypedDict(
    "DescribeStacksInputStackDeleteCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputStackExistsWaitTypeDef = TypedDict(
    "DescribeStacksInputStackExistsWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputStackImportCompleteWaitTypeDef = TypedDict(
    "DescribeStacksInputStackImportCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputStackRollbackCompleteWaitTypeDef = TypedDict(
    "DescribeStacksInputStackRollbackCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

DescribeStacksInputStackUpdateCompleteWaitTypeDef = TypedDict(
    "DescribeStacksInputStackUpdateCompleteWaitTypeDef",
    {
        "StackName": str,
        "NextToken": str,
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef = TypedDict(
    "_RequiredDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef",
    {
        "RegistrationToken": str,
    },
)
_OptionalDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef = TypedDict(
    "_OptionalDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef",
    {
        "WaiterConfig": WaiterConfigTypeDef,
    },
    total=False,
)


class DescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef(
    _RequiredDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef,
    _OptionalDescribeTypeRegistrationInputTypeRegistrationCompleteWaitTypeDef,
):
    pass


DescribeStackEventsOutputTypeDef = TypedDict(
    "DescribeStackEventsOutputTypeDef",
    {
        "StackEvents": List[StackEventTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTypeOutputTypeDef = TypedDict(
    "DescribeTypeOutputTypeDef",
    {
        "Arn": str,
        "Type": RegistryTypeType,
        "TypeName": str,
        "DefaultVersionId": str,
        "IsDefaultVersion": bool,
        "TypeTestsStatus": TypeTestsStatusType,
        "TypeTestsStatusDescription": str,
        "Description": str,
        "Schema": str,
        "ProvisioningType": ProvisioningTypeType,
        "DeprecatedStatus": DeprecatedStatusType,
        "LoggingConfig": LoggingConfigTypeDef,
        "RequiredActivatedTypes": List[RequiredActivatedTypeTypeDef],
        "ExecutionRoleArn": str,
        "Visibility": VisibilityType,
        "SourceUrl": str,
        "DocumentationUrl": str,
        "LastUpdated": datetime,
        "TimeCreated": datetime,
        "ConfigurationSchema": str,
        "PublisherId": str,
        "OriginalTypeName": str,
        "OriginalTypeArn": str,
        "PublicVersionNumber": str,
        "LatestPublicVersion": str,
        "IsActivated": bool,
        "AutoUpdate": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListExportsOutputTypeDef = TypedDict(
    "ListExportsOutputTypeDef",
    {
        "Exports": List[ExportTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredListStackInstancesInputListStackInstancesPaginateTypeDef = TypedDict(
    "_RequiredListStackInstancesInputListStackInstancesPaginateTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalListStackInstancesInputListStackInstancesPaginateTypeDef = TypedDict(
    "_OptionalListStackInstancesInputListStackInstancesPaginateTypeDef",
    {
        "Filters": Sequence[StackInstanceFilterTypeDef],
        "StackInstanceAccount": str,
        "StackInstanceRegion": str,
        "CallAs": CallAsType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class ListStackInstancesInputListStackInstancesPaginateTypeDef(
    _RequiredListStackInstancesInputListStackInstancesPaginateTypeDef,
    _OptionalListStackInstancesInputListStackInstancesPaginateTypeDef,
):
    pass


_RequiredListStackInstancesInputRequestTypeDef = TypedDict(
    "_RequiredListStackInstancesInputRequestTypeDef",
    {
        "StackSetName": str,
    },
)
_OptionalListStackInstancesInputRequestTypeDef = TypedDict(
    "_OptionalListStackInstancesInputRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "Filters": Sequence[StackInstanceFilterTypeDef],
        "StackInstanceAccount": str,
        "StackInstanceRegion": str,
        "CallAs": CallAsType,
    },
    total=False,
)


class ListStackInstancesInputRequestTypeDef(
    _RequiredListStackInstancesInputRequestTypeDef, _OptionalListStackInstancesInputRequestTypeDef
):
    pass


ListStackSetOperationsOutputTypeDef = TypedDict(
    "ListStackSetOperationsOutputTypeDef",
    {
        "Summaries": List[StackSetOperationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTypeVersionsOutputTypeDef = TypedDict(
    "ListTypeVersionsOutputTypeDef",
    {
        "TypeVersionSummaries": List[TypeVersionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTypesInputListTypesPaginateTypeDef = TypedDict(
    "ListTypesInputListTypesPaginateTypeDef",
    {
        "Visibility": VisibilityType,
        "ProvisioningType": ProvisioningTypeType,
        "DeprecatedStatus": DeprecatedStatusType,
        "Type": RegistryTypeType,
        "Filters": TypeFiltersTypeDef,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListTypesInputRequestTypeDef = TypedDict(
    "ListTypesInputRequestTypeDef",
    {
        "Visibility": VisibilityType,
        "ProvisioningType": ProvisioningTypeType,
        "DeprecatedStatus": DeprecatedStatusType,
        "Type": RegistryTypeType,
        "Filters": TypeFiltersTypeDef,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListTypesOutputTypeDef = TypedDict(
    "ListTypesOutputTypeDef",
    {
        "TypeSummaries": List[TypeSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ParameterDeclarationTypeDef = TypedDict(
    "ParameterDeclarationTypeDef",
    {
        "ParameterKey": str,
        "DefaultValue": str,
        "ParameterType": str,
        "NoEcho": bool,
        "Description": str,
        "ParameterConstraints": ParameterConstraintsTypeDef,
    },
    total=False,
)

_RequiredStackResourceDriftTypeDef = TypedDict(
    "_RequiredStackResourceDriftTypeDef",
    {
        "StackId": str,
        "LogicalResourceId": str,
        "ResourceType": str,
        "StackResourceDriftStatus": StackResourceDriftStatusType,
        "Timestamp": datetime,
    },
)
_OptionalStackResourceDriftTypeDef = TypedDict(
    "_OptionalStackResourceDriftTypeDef",
    {
        "PhysicalResourceId": str,
        "PhysicalResourceIdContext": List[PhysicalResourceIdContextKeyValuePairTypeDef],
        "ExpectedProperties": str,
        "ActualProperties": str,
        "PropertyDifferences": List[PropertyDifferenceTypeDef],
        "ModuleInfo": ModuleInfoTypeDef,
    },
    total=False,
)


class StackResourceDriftTypeDef(
    _RequiredStackResourceDriftTypeDef, _OptionalStackResourceDriftTypeDef
):
    pass


ResourceChangeDetailTypeDef = TypedDict(
    "ResourceChangeDetailTypeDef",
    {
        "Target": ResourceTargetDefinitionTypeDef,
        "Evaluation": EvaluationTypeType,
        "ChangeSource": ChangeSourceType,
        "CausingEntity": str,
    },
    total=False,
)

RollbackConfigurationResponseMetadataTypeDef = TypedDict(
    "RollbackConfigurationResponseMetadataTypeDef",
    {
        "RollbackTriggers": List[RollbackTriggerTypeDef],
        "MonitoringTimeInMinutes": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RollbackConfigurationTypeDef = TypedDict(
    "RollbackConfigurationTypeDef",
    {
        "RollbackTriggers": Sequence[RollbackTriggerTypeDef],
        "MonitoringTimeInMinutes": int,
    },
    total=False,
)

_RequiredStackSummaryTypeDef = TypedDict(
    "_RequiredStackSummaryTypeDef",
    {
        "StackName": str,
        "CreationTime": datetime,
        "StackStatus": StackStatusType,
    },
)
_OptionalStackSummaryTypeDef = TypedDict(
    "_OptionalStackSummaryTypeDef",
    {
        "StackId": str,
        "TemplateDescription": str,
        "LastUpdatedTime": datetime,
        "DeletionTime": datetime,
        "StackStatusReason": str,
        "ParentId": str,
        "RootId": str,
        "DriftInformation": StackDriftInformationSummaryTypeDef,
    },
    total=False,
)


class StackSummaryTypeDef(_RequiredStackSummaryTypeDef, _OptionalStackSummaryTypeDef):
    pass


StackInstanceSummaryTypeDef = TypedDict(
    "StackInstanceSummaryTypeDef",
    {
        "StackSetId": str,
        "Region": str,
        "Account": str,
        "StackId": str,
        "Status": StackInstanceStatusType,
        "StatusReason": str,
        "StackInstanceStatus": StackInstanceComprehensiveStatusTypeDef,
        "OrganizationalUnitId": str,
        "DriftStatus": StackDriftStatusType,
        "LastDriftCheckTimestamp": datetime,
    },
    total=False,
)

StackInstanceTypeDef = TypedDict(
    "StackInstanceTypeDef",
    {
        "StackSetId": str,
        "Region": str,
        "Account": str,
        "StackId": str,
        "ParameterOverrides": List[ParameterTypeDef],
        "Status": StackInstanceStatusType,
        "StackInstanceStatus": StackInstanceComprehensiveStatusTypeDef,
        "StatusReason": str,
        "OrganizationalUnitId": str,
        "DriftStatus": StackDriftStatusType,
        "LastDriftCheckTimestamp": datetime,
    },
    total=False,
)

_RequiredStackResourceDetailTypeDef = TypedDict(
    "_RequiredStackResourceDetailTypeDef",
    {
        "LogicalResourceId": str,
        "ResourceType": str,
        "LastUpdatedTimestamp": datetime,
        "ResourceStatus": ResourceStatusType,
    },
)
_OptionalStackResourceDetailTypeDef = TypedDict(
    "_OptionalStackResourceDetailTypeDef",
    {
        "StackName": str,
        "StackId": str,
        "PhysicalResourceId": str,
        "ResourceStatusReason": str,
        "Description": str,
        "Metadata": str,
        "DriftInformation": StackResourceDriftInformationTypeDef,
        "ModuleInfo": ModuleInfoTypeDef,
    },
    total=False,
)


class StackResourceDetailTypeDef(
    _RequiredStackResourceDetailTypeDef, _OptionalStackResourceDetailTypeDef
):
    pass


_RequiredStackResourceTypeDef = TypedDict(
    "_RequiredStackResourceTypeDef",
    {
        "LogicalResourceId": str,
        "ResourceType": str,
        "Timestamp": datetime,
        "ResourceStatus": ResourceStatusType,
    },
)
_OptionalStackResourceTypeDef = TypedDict(
    "_OptionalStackResourceTypeDef",
    {
        "StackName": str,
        "StackId": str,
        "PhysicalResourceId": str,
        "ResourceStatusReason": str,
        "Description": str,
        "DriftInformation": StackResourceDriftInformationTypeDef,
        "ModuleInfo": ModuleInfoTypeDef,
    },
    total=False,
)


class StackResourceTypeDef(_RequiredStackResourceTypeDef, _OptionalStackResourceTypeDef):
    pass


_RequiredStackResourceSummaryTypeDef = TypedDict(
    "_RequiredStackResourceSummaryTypeDef",
    {
        "LogicalResourceId": str,
        "ResourceType": str,
        "LastUpdatedTimestamp": datetime,
        "ResourceStatus": ResourceStatusType,
    },
)
_OptionalStackResourceSummaryTypeDef = TypedDict(
    "_OptionalStackResourceSummaryTypeDef",
    {
        "PhysicalResourceId": str,
        "ResourceStatusReason": str,
        "DriftInformation": StackResourceDriftInformationSummaryTypeDef,
        "ModuleInfo": ModuleInfoTypeDef,
    },
    total=False,
)


class StackResourceSummaryTypeDef(
    _RequiredStackResourceSummaryTypeDef, _OptionalStackResourceSummaryTypeDef
):
    pass


StackSetOperationTypeDef = TypedDict(
    "StackSetOperationTypeDef",
    {
        "OperationId": str,
        "StackSetId": str,
        "Action": StackSetOperationActionType,
        "Status": StackSetOperationStatusType,
        "OperationPreferences": StackSetOperationPreferencesTypeDef,
        "RetainStacks": bool,
        "AdministrationRoleARN": str,
        "ExecutionRoleName": str,
        "CreationTimestamp": datetime,
        "EndTimestamp": datetime,
        "DeploymentTargets": DeploymentTargetsTypeDef,
        "StackSetDriftDetectionDetails": StackSetDriftDetectionDetailsTypeDef,
        "StatusReason": str,
    },
    total=False,
)

StackSetTypeDef = TypedDict(
    "StackSetTypeDef",
    {
        "StackSetName": str,
        "StackSetId": str,
        "Description": str,
        "Status": StackSetStatusType,
        "TemplateBody": str,
        "Parameters": List[ParameterTypeDef],
        "Capabilities": List[CapabilityType],
        "Tags": List[TagTypeDef],
        "StackSetARN": str,
        "AdministrationRoleARN": str,
        "ExecutionRoleName": str,
        "StackSetDriftDetectionDetails": StackSetDriftDetectionDetailsTypeDef,
        "AutoDeployment": AutoDeploymentTypeDef,
        "PermissionModel": PermissionModelsType,
        "OrganizationalUnitIds": List[str],
        "ManagedExecution": ManagedExecutionTypeDef,
    },
    total=False,
)

ValidateTemplateOutputTypeDef = TypedDict(
    "ValidateTemplateOutputTypeDef",
    {
        "Parameters": List[TemplateParameterTypeDef],
        "Description": str,
        "Capabilities": List[CapabilityType],
        "CapabilitiesReason": str,
        "DeclaredTransforms": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStackSetOperationResultsOutputTypeDef = TypedDict(
    "ListStackSetOperationResultsOutputTypeDef",
    {
        "Summaries": List[StackSetOperationResultSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDescribeTypeConfigurationsOutputTypeDef = TypedDict(
    "BatchDescribeTypeConfigurationsOutputTypeDef",
    {
        "Errors": List[BatchDescribeTypeConfigurationsErrorTypeDef],
        "UnprocessedTypeConfigurations": List[TypeConfigurationIdentifierTypeDef],
        "TypeConfigurations": List[TypeConfigurationDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ChangeSetHookTypeDef = TypedDict(
    "ChangeSetHookTypeDef",
    {
        "InvocationPoint": Literal["PRE_PROVISION"],
        "FailureMode": HookFailureModeType,
        "TypeName": str,
        "TypeVersionId": str,
        "TypeConfigurationVersionId": str,
        "TargetDetails": ChangeSetHookTargetDetailsTypeDef,
    },
    total=False,
)

ListStackSetsOutputTypeDef = TypedDict(
    "ListStackSetsOutputTypeDef",
    {
        "Summaries": List[StackSetSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetTemplateSummaryOutputTypeDef = TypedDict(
    "GetTemplateSummaryOutputTypeDef",
    {
        "Parameters": List[ParameterDeclarationTypeDef],
        "Description": str,
        "Capabilities": List[CapabilityType],
        "CapabilitiesReason": str,
        "ResourceTypes": List[str],
        "Version": str,
        "Metadata": str,
        "DeclaredTransforms": List[str],
        "ResourceIdentifierSummaries": List[ResourceIdentifierSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackResourceDriftsOutputTypeDef = TypedDict(
    "DescribeStackResourceDriftsOutputTypeDef",
    {
        "StackResourceDrifts": List[StackResourceDriftTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectStackResourceDriftOutputTypeDef = TypedDict(
    "DetectStackResourceDriftOutputTypeDef",
    {
        "StackResourceDrift": StackResourceDriftTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResourceChangeTypeDef = TypedDict(
    "ResourceChangeTypeDef",
    {
        "Action": ChangeActionType,
        "LogicalResourceId": str,
        "PhysicalResourceId": str,
        "ResourceType": str,
        "Replacement": ReplacementType,
        "Scope": List[ResourceAttributeType],
        "Details": List[ResourceChangeDetailTypeDef],
        "ChangeSetId": str,
        "ModuleInfo": ModuleInfoTypeDef,
    },
    total=False,
)

_RequiredCreateChangeSetInputRequestTypeDef = TypedDict(
    "_RequiredCreateChangeSetInputRequestTypeDef",
    {
        "StackName": str,
        "ChangeSetName": str,
    },
)
_OptionalCreateChangeSetInputRequestTypeDef = TypedDict(
    "_OptionalCreateChangeSetInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "UsePreviousTemplate": bool,
        "Parameters": Sequence[ParameterTypeDef],
        "Capabilities": Sequence[CapabilityType],
        "ResourceTypes": Sequence[str],
        "RoleARN": str,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "NotificationARNs": Sequence[str],
        "Tags": Sequence[TagTypeDef],
        "ClientToken": str,
        "Description": str,
        "ChangeSetType": ChangeSetTypeType,
        "ResourcesToImport": Sequence[ResourceToImportTypeDef],
        "IncludeNestedStacks": bool,
    },
    total=False,
)


class CreateChangeSetInputRequestTypeDef(
    _RequiredCreateChangeSetInputRequestTypeDef, _OptionalCreateChangeSetInputRequestTypeDef
):
    pass


_RequiredCreateStackInputRequestTypeDef = TypedDict(
    "_RequiredCreateStackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalCreateStackInputRequestTypeDef = TypedDict(
    "_OptionalCreateStackInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "Parameters": Sequence[ParameterTypeDef],
        "DisableRollback": bool,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "TimeoutInMinutes": int,
        "NotificationARNs": Sequence[str],
        "Capabilities": Sequence[CapabilityType],
        "ResourceTypes": Sequence[str],
        "RoleARN": str,
        "OnFailure": OnFailureType,
        "StackPolicyBody": str,
        "StackPolicyURL": str,
        "Tags": Sequence[TagTypeDef],
        "ClientRequestToken": str,
        "EnableTerminationProtection": bool,
    },
    total=False,
)


class CreateStackInputRequestTypeDef(
    _RequiredCreateStackInputRequestTypeDef, _OptionalCreateStackInputRequestTypeDef
):
    pass


_RequiredCreateStackInputServiceResourceCreateStackTypeDef = TypedDict(
    "_RequiredCreateStackInputServiceResourceCreateStackTypeDef",
    {
        "StackName": str,
    },
)
_OptionalCreateStackInputServiceResourceCreateStackTypeDef = TypedDict(
    "_OptionalCreateStackInputServiceResourceCreateStackTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "Parameters": Sequence[ParameterTypeDef],
        "DisableRollback": bool,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "TimeoutInMinutes": int,
        "NotificationARNs": Sequence[str],
        "Capabilities": Sequence[CapabilityType],
        "ResourceTypes": Sequence[str],
        "RoleARN": str,
        "OnFailure": OnFailureType,
        "StackPolicyBody": str,
        "StackPolicyURL": str,
        "Tags": Sequence[TagTypeDef],
        "ClientRequestToken": str,
        "EnableTerminationProtection": bool,
    },
    total=False,
)


class CreateStackInputServiceResourceCreateStackTypeDef(
    _RequiredCreateStackInputServiceResourceCreateStackTypeDef,
    _OptionalCreateStackInputServiceResourceCreateStackTypeDef,
):
    pass


_RequiredStackTypeDef = TypedDict(
    "_RequiredStackTypeDef",
    {
        "StackName": str,
        "CreationTime": datetime,
        "StackStatus": StackStatusType,
    },
)
_OptionalStackTypeDef = TypedDict(
    "_OptionalStackTypeDef",
    {
        "StackId": str,
        "ChangeSetId": str,
        "Description": str,
        "Parameters": List[ParameterTypeDef],
        "DeletionTime": datetime,
        "LastUpdatedTime": datetime,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "StackStatusReason": str,
        "DisableRollback": bool,
        "NotificationARNs": List[str],
        "TimeoutInMinutes": int,
        "Capabilities": List[CapabilityType],
        "Outputs": List[OutputTypeDef],
        "RoleARN": str,
        "Tags": List[TagTypeDef],
        "EnableTerminationProtection": bool,
        "ParentId": str,
        "RootId": str,
        "DriftInformation": StackDriftInformationTypeDef,
    },
    total=False,
)


class StackTypeDef(_RequiredStackTypeDef, _OptionalStackTypeDef):
    pass


_RequiredUpdateStackInputRequestTypeDef = TypedDict(
    "_RequiredUpdateStackInputRequestTypeDef",
    {
        "StackName": str,
    },
)
_OptionalUpdateStackInputRequestTypeDef = TypedDict(
    "_OptionalUpdateStackInputRequestTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "UsePreviousTemplate": bool,
        "StackPolicyDuringUpdateBody": str,
        "StackPolicyDuringUpdateURL": str,
        "Parameters": Sequence[ParameterTypeDef],
        "Capabilities": Sequence[CapabilityType],
        "ResourceTypes": Sequence[str],
        "RoleARN": str,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "StackPolicyBody": str,
        "StackPolicyURL": str,
        "NotificationARNs": Sequence[str],
        "Tags": Sequence[TagTypeDef],
        "DisableRollback": bool,
        "ClientRequestToken": str,
    },
    total=False,
)


class UpdateStackInputRequestTypeDef(
    _RequiredUpdateStackInputRequestTypeDef, _OptionalUpdateStackInputRequestTypeDef
):
    pass


UpdateStackInputStackUpdateTypeDef = TypedDict(
    "UpdateStackInputStackUpdateTypeDef",
    {
        "TemplateBody": str,
        "TemplateURL": str,
        "UsePreviousTemplate": bool,
        "StackPolicyDuringUpdateBody": str,
        "StackPolicyDuringUpdateURL": str,
        "Parameters": Sequence[ParameterTypeDef],
        "Capabilities": Sequence[CapabilityType],
        "ResourceTypes": Sequence[str],
        "RoleARN": str,
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "StackPolicyBody": str,
        "StackPolicyURL": str,
        "NotificationARNs": Sequence[str],
        "Tags": Sequence[TagTypeDef],
        "DisableRollback": bool,
        "ClientRequestToken": str,
    },
    total=False,
)

ListStacksOutputTypeDef = TypedDict(
    "ListStacksOutputTypeDef",
    {
        "StackSummaries": List[StackSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStackInstancesOutputTypeDef = TypedDict(
    "ListStackInstancesOutputTypeDef",
    {
        "Summaries": List[StackInstanceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackInstanceOutputTypeDef = TypedDict(
    "DescribeStackInstanceOutputTypeDef",
    {
        "StackInstance": StackInstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackResourceOutputTypeDef = TypedDict(
    "DescribeStackResourceOutputTypeDef",
    {
        "StackResourceDetail": StackResourceDetailTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackResourcesOutputTypeDef = TypedDict(
    "DescribeStackResourcesOutputTypeDef",
    {
        "StackResources": List[StackResourceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStackResourcesOutputTypeDef = TypedDict(
    "ListStackResourcesOutputTypeDef",
    {
        "StackResourceSummaries": List[StackResourceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackSetOperationOutputTypeDef = TypedDict(
    "DescribeStackSetOperationOutputTypeDef",
    {
        "StackSetOperation": StackSetOperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStackSetOutputTypeDef = TypedDict(
    "DescribeStackSetOutputTypeDef",
    {
        "StackSet": StackSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeChangeSetHooksOutputTypeDef = TypedDict(
    "DescribeChangeSetHooksOutputTypeDef",
    {
        "ChangeSetId": str,
        "ChangeSetName": str,
        "Hooks": List[ChangeSetHookTypeDef],
        "Status": ChangeSetHooksStatusType,
        "NextToken": str,
        "StackId": str,
        "StackName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ChangeTypeDef = TypedDict(
    "ChangeTypeDef",
    {
        "Type": Literal["Resource"],
        "HookInvocationCount": int,
        "ResourceChange": ResourceChangeTypeDef,
    },
    total=False,
)

DescribeStacksOutputTypeDef = TypedDict(
    "DescribeStacksOutputTypeDef",
    {
        "Stacks": List[StackTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeChangeSetOutputTypeDef = TypedDict(
    "DescribeChangeSetOutputTypeDef",
    {
        "ChangeSetName": str,
        "ChangeSetId": str,
        "StackId": str,
        "StackName": str,
        "Description": str,
        "Parameters": List[ParameterTypeDef],
        "CreationTime": datetime,
        "ExecutionStatus": ExecutionStatusType,
        "Status": ChangeSetStatusType,
        "StatusReason": str,
        "NotificationARNs": List[str],
        "RollbackConfiguration": RollbackConfigurationTypeDef,
        "Capabilities": List[CapabilityType],
        "Tags": List[TagTypeDef],
        "Changes": List[ChangeTypeDef],
        "NextToken": str,
        "IncludeNestedStacks": bool,
        "ParentChangeSetId": str,
        "RootChangeSetId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
