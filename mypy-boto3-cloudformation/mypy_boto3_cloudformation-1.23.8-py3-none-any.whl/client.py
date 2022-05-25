"""
Type annotations for cloudformation service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_cloudformation.client import CloudFormationClient

    session = Session()
    client: CloudFormationClient = session.client("cloudformation")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    CallAsType,
    CapabilityType,
    ChangeSetTypeType,
    DeprecatedStatusType,
    HandlerErrorCodeType,
    OnFailureType,
    OperationStatusType,
    PermissionModelsType,
    ProvisioningTypeType,
    RegistrationStatusType,
    RegistryTypeType,
    ResourceSignalStatusType,
    StackResourceDriftStatusType,
    StackSetStatusType,
    StackStatusType,
    TemplateStageType,
    ThirdPartyTypeType,
    VersionBumpType,
    VisibilityType,
)
from .paginator import (
    DescribeAccountLimitsPaginator,
    DescribeChangeSetPaginator,
    DescribeStackEventsPaginator,
    DescribeStacksPaginator,
    ListChangeSetsPaginator,
    ListExportsPaginator,
    ListImportsPaginator,
    ListStackInstancesPaginator,
    ListStackResourcesPaginator,
    ListStackSetOperationResultsPaginator,
    ListStackSetOperationsPaginator,
    ListStackSetsPaginator,
    ListStacksPaginator,
    ListTypesPaginator,
)
from .type_defs import (
    ActivateTypeOutputTypeDef,
    AutoDeploymentTypeDef,
    BatchDescribeTypeConfigurationsOutputTypeDef,
    CreateChangeSetOutputTypeDef,
    CreateStackInstancesOutputTypeDef,
    CreateStackOutputTypeDef,
    CreateStackSetOutputTypeDef,
    DeleteStackInstancesOutputTypeDef,
    DeploymentTargetsTypeDef,
    DescribeAccountLimitsOutputTypeDef,
    DescribeChangeSetHooksOutputTypeDef,
    DescribeChangeSetOutputTypeDef,
    DescribePublisherOutputTypeDef,
    DescribeStackDriftDetectionStatusOutputTypeDef,
    DescribeStackEventsOutputTypeDef,
    DescribeStackInstanceOutputTypeDef,
    DescribeStackResourceDriftsOutputTypeDef,
    DescribeStackResourceOutputTypeDef,
    DescribeStackResourcesOutputTypeDef,
    DescribeStackSetOperationOutputTypeDef,
    DescribeStackSetOutputTypeDef,
    DescribeStacksOutputTypeDef,
    DescribeTypeOutputTypeDef,
    DescribeTypeRegistrationOutputTypeDef,
    DetectStackDriftOutputTypeDef,
    DetectStackResourceDriftOutputTypeDef,
    DetectStackSetDriftOutputTypeDef,
    EstimateTemplateCostOutputTypeDef,
    GetStackPolicyOutputTypeDef,
    GetTemplateOutputTypeDef,
    GetTemplateSummaryOutputTypeDef,
    ImportStacksToStackSetOutputTypeDef,
    ListChangeSetsOutputTypeDef,
    ListExportsOutputTypeDef,
    ListImportsOutputTypeDef,
    ListStackInstancesOutputTypeDef,
    ListStackResourcesOutputTypeDef,
    ListStackSetOperationResultsOutputTypeDef,
    ListStackSetOperationsOutputTypeDef,
    ListStackSetsOutputTypeDef,
    ListStacksOutputTypeDef,
    ListTypeRegistrationsOutputTypeDef,
    ListTypesOutputTypeDef,
    ListTypeVersionsOutputTypeDef,
    LoggingConfigTypeDef,
    ManagedExecutionTypeDef,
    ParameterTypeDef,
    PublishTypeOutputTypeDef,
    RegisterPublisherOutputTypeDef,
    RegisterTypeOutputTypeDef,
    ResourceToImportTypeDef,
    RollbackConfigurationTypeDef,
    RollbackStackOutputTypeDef,
    SetTypeConfigurationOutputTypeDef,
    StackInstanceFilterTypeDef,
    StackSetOperationPreferencesTypeDef,
    TagTypeDef,
    TestTypeOutputTypeDef,
    TypeConfigurationIdentifierTypeDef,
    TypeFiltersTypeDef,
    UpdateStackInstancesOutputTypeDef,
    UpdateStackOutputTypeDef,
    UpdateStackSetOutputTypeDef,
    UpdateTerminationProtectionOutputTypeDef,
    ValidateTemplateOutputTypeDef,
)
from .waiter import (
    ChangeSetCreateCompleteWaiter,
    StackCreateCompleteWaiter,
    StackDeleteCompleteWaiter,
    StackExistsWaiter,
    StackImportCompleteWaiter,
    StackRollbackCompleteWaiter,
    StackUpdateCompleteWaiter,
    TypeRegistrationCompleteWaiter,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("CloudFormationClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AlreadyExistsException: Type[BotocoreClientError]
    CFNRegistryException: Type[BotocoreClientError]
    ChangeSetNotFoundException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    CreatedButModifiedException: Type[BotocoreClientError]
    InsufficientCapabilitiesException: Type[BotocoreClientError]
    InvalidChangeSetStatusException: Type[BotocoreClientError]
    InvalidOperationException: Type[BotocoreClientError]
    InvalidStateTransitionException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    NameAlreadyExistsException: Type[BotocoreClientError]
    OperationIdAlreadyExistsException: Type[BotocoreClientError]
    OperationInProgressException: Type[BotocoreClientError]
    OperationNotFoundException: Type[BotocoreClientError]
    OperationStatusCheckFailedException: Type[BotocoreClientError]
    StackInstanceNotFoundException: Type[BotocoreClientError]
    StackNotFoundException: Type[BotocoreClientError]
    StackSetNotEmptyException: Type[BotocoreClientError]
    StackSetNotFoundException: Type[BotocoreClientError]
    StaleRequestException: Type[BotocoreClientError]
    TokenAlreadyExistsException: Type[BotocoreClientError]
    TypeConfigurationNotFoundException: Type[BotocoreClientError]
    TypeNotFoundException: Type[BotocoreClientError]


class CloudFormationClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        CloudFormationClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#exceptions)
        """

    def activate_type(
        self,
        *,
        Type: ThirdPartyTypeType = ...,
        PublicTypeArn: str = ...,
        PublisherId: str = ...,
        TypeName: str = ...,
        TypeNameAlias: str = ...,
        AutoUpdate: bool = ...,
        LoggingConfig: LoggingConfigTypeDef = ...,
        ExecutionRoleArn: str = ...,
        VersionBump: VersionBumpType = ...,
        MajorVersion: int = ...
    ) -> ActivateTypeOutputTypeDef:
        """
        Activates a public third-party extension, making it available for use in stack
        templates.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.activate_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#activate_type)
        """

    def batch_describe_type_configurations(
        self, *, TypeConfigurationIdentifiers: Sequence[TypeConfigurationIdentifierTypeDef]
    ) -> BatchDescribeTypeConfigurationsOutputTypeDef:
        """
        Returns configuration data for the specified CloudFormation extensions, from the
        CloudFormation registry for the account and region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.batch_describe_type_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#batch_describe_type_configurations)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#can_paginate)
        """

    def cancel_update_stack(self, *, StackName: str, ClientRequestToken: str = ...) -> None:
        """
        Cancels an update on the specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.cancel_update_stack)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#cancel_update_stack)
        """

    def continue_update_rollback(
        self,
        *,
        StackName: str,
        RoleARN: str = ...,
        ResourcesToSkip: Sequence[str] = ...,
        ClientRequestToken: str = ...
    ) -> Dict[str, Any]:
        """
        For a specified stack that's in the `UPDATE_ROLLBACK_FAILED` state, continues
        rolling it back to the `UPDATE_ROLLBACK_COMPLETE` state.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.continue_update_rollback)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#continue_update_rollback)
        """

    def create_change_set(
        self,
        *,
        StackName: str,
        ChangeSetName: str,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        UsePreviousTemplate: bool = ...,
        Parameters: Sequence[ParameterTypeDef] = ...,
        Capabilities: Sequence[CapabilityType] = ...,
        ResourceTypes: Sequence[str] = ...,
        RoleARN: str = ...,
        RollbackConfiguration: RollbackConfigurationTypeDef = ...,
        NotificationARNs: Sequence[str] = ...,
        Tags: Sequence[TagTypeDef] = ...,
        ClientToken: str = ...,
        Description: str = ...,
        ChangeSetType: ChangeSetTypeType = ...,
        ResourcesToImport: Sequence[ResourceToImportTypeDef] = ...,
        IncludeNestedStacks: bool = ...
    ) -> CreateChangeSetOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_change_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#create_change_set)
        """

    def create_stack(
        self,
        *,
        StackName: str,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        Parameters: Sequence[ParameterTypeDef] = ...,
        DisableRollback: bool = ...,
        RollbackConfiguration: RollbackConfigurationTypeDef = ...,
        TimeoutInMinutes: int = ...,
        NotificationARNs: Sequence[str] = ...,
        Capabilities: Sequence[CapabilityType] = ...,
        ResourceTypes: Sequence[str] = ...,
        RoleARN: str = ...,
        OnFailure: OnFailureType = ...,
        StackPolicyBody: str = ...,
        StackPolicyURL: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
        ClientRequestToken: str = ...,
        EnableTerminationProtection: bool = ...
    ) -> CreateStackOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#create_stack)
        """

    def create_stack_instances(
        self,
        *,
        StackSetName: str,
        Regions: Sequence[str],
        Accounts: Sequence[str] = ...,
        DeploymentTargets: DeploymentTargetsTypeDef = ...,
        ParameterOverrides: Sequence[ParameterTypeDef] = ...,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        OperationId: str = ...,
        CallAs: CallAsType = ...
    ) -> CreateStackInstancesOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#create_stack_instances)
        """

    def create_stack_set(
        self,
        *,
        StackSetName: str,
        Description: str = ...,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        StackId: str = ...,
        Parameters: Sequence[ParameterTypeDef] = ...,
        Capabilities: Sequence[CapabilityType] = ...,
        Tags: Sequence[TagTypeDef] = ...,
        AdministrationRoleARN: str = ...,
        ExecutionRoleName: str = ...,
        PermissionModel: PermissionModelsType = ...,
        AutoDeployment: AutoDeploymentTypeDef = ...,
        CallAs: CallAsType = ...,
        ClientRequestToken: str = ...,
        ManagedExecution: ManagedExecutionTypeDef = ...
    ) -> CreateStackSetOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#create_stack_set)
        """

    def deactivate_type(
        self, *, TypeName: str = ..., Type: ThirdPartyTypeType = ..., Arn: str = ...
    ) -> Dict[str, Any]:
        """
        Deactivates a public extension that was previously activated in this account and
        region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.deactivate_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#deactivate_type)
        """

    def delete_change_set(self, *, ChangeSetName: str, StackName: str = ...) -> Dict[str, Any]:
        """
        Deletes the specified change set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_change_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#delete_change_set)
        """

    def delete_stack(
        self,
        *,
        StackName: str,
        RetainResources: Sequence[str] = ...,
        RoleARN: str = ...,
        ClientRequestToken: str = ...
    ) -> None:
        """
        Deletes a specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#delete_stack)
        """

    def delete_stack_instances(
        self,
        *,
        StackSetName: str,
        Regions: Sequence[str],
        RetainStacks: bool,
        Accounts: Sequence[str] = ...,
        DeploymentTargets: DeploymentTargetsTypeDef = ...,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        OperationId: str = ...,
        CallAs: CallAsType = ...
    ) -> DeleteStackInstancesOutputTypeDef:
        """
        Deletes stack instances for the specified accounts, in the specified Amazon Web
        Services Regions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#delete_stack_instances)
        """

    def delete_stack_set(self, *, StackSetName: str, CallAs: CallAsType = ...) -> Dict[str, Any]:
        """
        Deletes a stack set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#delete_stack_set)
        """

    def deregister_type(
        self,
        *,
        Arn: str = ...,
        Type: RegistryTypeType = ...,
        TypeName: str = ...,
        VersionId: str = ...
    ) -> Dict[str, Any]:
        """
        Marks an extension or extension version as `DEPRECATED` in the CloudFormation
        registry, removing it from active use.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.deregister_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#deregister_type)
        """

    def describe_account_limits(
        self, *, NextToken: str = ...
    ) -> DescribeAccountLimitsOutputTypeDef:
        """
        Retrieves your account's CloudFormation limits, such as the maximum number of
        stacks that you can create in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_account_limits)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_account_limits)
        """

    def describe_change_set(
        self, *, ChangeSetName: str, StackName: str = ..., NextToken: str = ...
    ) -> DescribeChangeSetOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_change_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_change_set)
        """

    def describe_change_set_hooks(
        self,
        *,
        ChangeSetName: str,
        StackName: str = ...,
        NextToken: str = ...,
        LogicalResourceId: str = ...
    ) -> DescribeChangeSetHooksOutputTypeDef:
        """
        Returns hook-related information for the change set and a list of changes that
        CloudFormation makes when you run the change set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_change_set_hooks)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_change_set_hooks)
        """

    def describe_publisher(self, *, PublisherId: str = ...) -> DescribePublisherOutputTypeDef:
        """
        Returns information about a CloudFormation extension publisher.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_publisher)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_publisher)
        """

    def describe_stack_drift_detection_status(
        self, *, StackDriftDetectionId: str
    ) -> DescribeStackDriftDetectionStatusOutputTypeDef:
        """
        Returns information about a stack drift detection operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_drift_detection_status)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_drift_detection_status)
        """

    def describe_stack_events(
        self, *, StackName: str = ..., NextToken: str = ...
    ) -> DescribeStackEventsOutputTypeDef:
        """
        Returns all stack related events for a specified stack in reverse chronological
        order.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_events)
        """

    def describe_stack_instance(
        self,
        *,
        StackSetName: str,
        StackInstanceAccount: str,
        StackInstanceRegion: str,
        CallAs: CallAsType = ...
    ) -> DescribeStackInstanceOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_instance)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_instance)
        """

    def describe_stack_resource(
        self, *, StackName: str, LogicalResourceId: str
    ) -> DescribeStackResourceOutputTypeDef:
        """
        Returns a description of the specified resource in the specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_resource)
        """

    def describe_stack_resource_drifts(
        self,
        *,
        StackName: str,
        StackResourceDriftStatusFilters: Sequence[StackResourceDriftStatusType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> DescribeStackResourceDriftsOutputTypeDef:
        """
        Returns drift information for the resources that have been checked for drift in
        the specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_resource_drifts)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_resource_drifts)
        """

    def describe_stack_resources(
        self, *, StackName: str = ..., LogicalResourceId: str = ..., PhysicalResourceId: str = ...
    ) -> DescribeStackResourcesOutputTypeDef:
        """
        Returns Amazon Web Services resource descriptions for running and deleted
        stacks.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_resources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_resources)
        """

    def describe_stack_set(
        self, *, StackSetName: str, CallAs: CallAsType = ...
    ) -> DescribeStackSetOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_set)
        """

    def describe_stack_set_operation(
        self, *, StackSetName: str, OperationId: str, CallAs: CallAsType = ...
    ) -> DescribeStackSetOperationOutputTypeDef:
        """
        Returns the description of the specified stack set operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_set_operation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stack_set_operation)
        """

    def describe_stacks(
        self, *, StackName: str = ..., NextToken: str = ...
    ) -> DescribeStacksOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_stacks)
        """

    def describe_type(
        self,
        *,
        Type: RegistryTypeType = ...,
        TypeName: str = ...,
        Arn: str = ...,
        VersionId: str = ...,
        PublisherId: str = ...,
        PublicVersionNumber: str = ...
    ) -> DescribeTypeOutputTypeDef:
        """
        Returns detailed information about an extension that has been registered.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_type)
        """

    def describe_type_registration(
        self, *, RegistrationToken: str
    ) -> DescribeTypeRegistrationOutputTypeDef:
        """
        Returns information about an extension's registration, including its current
        status and type and version identifiers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_type_registration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#describe_type_registration)
        """

    def detect_stack_drift(
        self, *, StackName: str, LogicalResourceIds: Sequence[str] = ...
    ) -> DetectStackDriftOutputTypeDef:
        """
        Detects whether a stack's actual configuration differs, or has *drifted* , from
        it's expected configuration, as defined in the stack template and any values
        specified as template parameters.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.detect_stack_drift)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#detect_stack_drift)
        """

    def detect_stack_resource_drift(
        self, *, StackName: str, LogicalResourceId: str
    ) -> DetectStackResourceDriftOutputTypeDef:
        """
        Returns information about whether a resource's actual configuration differs, or
        has *drifted* , from it's expected configuration, as defined in the stack
        template and any values specified as template parameters.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.detect_stack_resource_drift)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#detect_stack_resource_drift)
        """

    def detect_stack_set_drift(
        self,
        *,
        StackSetName: str,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        OperationId: str = ...,
        CallAs: CallAsType = ...
    ) -> DetectStackSetDriftOutputTypeDef:
        """
        Detect drift on a stack set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.detect_stack_set_drift)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#detect_stack_set_drift)
        """

    def estimate_template_cost(
        self,
        *,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        Parameters: Sequence[ParameterTypeDef] = ...
    ) -> EstimateTemplateCostOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.estimate_template_cost)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#estimate_template_cost)
        """

    def execute_change_set(
        self,
        *,
        ChangeSetName: str,
        StackName: str = ...,
        ClientRequestToken: str = ...,
        DisableRollback: bool = ...
    ) -> Dict[str, Any]:
        """
        Updates a stack using the input information that was provided when the specified
        change set was created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.execute_change_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#execute_change_set)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#generate_presigned_url)
        """

    def get_stack_policy(self, *, StackName: str) -> GetStackPolicyOutputTypeDef:
        """
        Returns the stack policy for a specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_stack_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_stack_policy)
        """

    def get_template(
        self,
        *,
        StackName: str = ...,
        ChangeSetName: str = ...,
        TemplateStage: TemplateStageType = ...
    ) -> GetTemplateOutputTypeDef:
        """
        Returns the template body for a specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_template)
        """

    def get_template_summary(
        self,
        *,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        StackName: str = ...,
        StackSetName: str = ...,
        CallAs: CallAsType = ...
    ) -> GetTemplateSummaryOutputTypeDef:
        """
        Returns information about a new or existing template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_template_summary)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_template_summary)
        """

    def import_stacks_to_stack_set(
        self,
        *,
        StackSetName: str,
        StackIds: Sequence[str] = ...,
        StackIdsUrl: str = ...,
        OrganizationalUnitIds: Sequence[str] = ...,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        OperationId: str = ...,
        CallAs: CallAsType = ...
    ) -> ImportStacksToStackSetOutputTypeDef:
        """
        Import existing stacks into a new stack sets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.import_stacks_to_stack_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#import_stacks_to_stack_set)
        """

    def list_change_sets(
        self, *, StackName: str, NextToken: str = ...
    ) -> ListChangeSetsOutputTypeDef:
        """
        Returns the ID and status of each active change set for a stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_change_sets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_change_sets)
        """

    def list_exports(self, *, NextToken: str = ...) -> ListExportsOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_exports)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_exports)
        """

    def list_imports(self, *, ExportName: str, NextToken: str = ...) -> ListImportsOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_imports)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_imports)
        """

    def list_stack_instances(
        self,
        *,
        StackSetName: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        Filters: Sequence[StackInstanceFilterTypeDef] = ...,
        StackInstanceAccount: str = ...,
        StackInstanceRegion: str = ...,
        CallAs: CallAsType = ...
    ) -> ListStackInstancesOutputTypeDef:
        """
        Returns summary information about stack instances that are associated with the
        specified stack set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stack_instances)
        """

    def list_stack_resources(
        self, *, StackName: str, NextToken: str = ...
    ) -> ListStackResourcesOutputTypeDef:
        """
        Returns descriptions of all resources of the specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_resources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stack_resources)
        """

    def list_stack_set_operation_results(
        self,
        *,
        StackSetName: str,
        OperationId: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        CallAs: CallAsType = ...
    ) -> ListStackSetOperationResultsOutputTypeDef:
        """
        Returns summary information about the results of a stack set operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_set_operation_results)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stack_set_operation_results)
        """

    def list_stack_set_operations(
        self,
        *,
        StackSetName: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        CallAs: CallAsType = ...
    ) -> ListStackSetOperationsOutputTypeDef:
        """
        Returns summary information about operations performed on a stack set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_set_operations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stack_set_operations)
        """

    def list_stack_sets(
        self,
        *,
        NextToken: str = ...,
        MaxResults: int = ...,
        Status: StackSetStatusType = ...,
        CallAs: CallAsType = ...
    ) -> ListStackSetsOutputTypeDef:
        """
        Returns summary information about stack sets that are associated with the user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_sets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stack_sets)
        """

    def list_stacks(
        self, *, NextToken: str = ..., StackStatusFilter: Sequence[StackStatusType] = ...
    ) -> ListStacksOutputTypeDef:
        """
        Returns the summary information for stacks whose status matches the specified
        StackStatusFilter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stacks)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_stacks)
        """

    def list_type_registrations(
        self,
        *,
        Type: RegistryTypeType = ...,
        TypeName: str = ...,
        TypeArn: str = ...,
        RegistrationStatusFilter: RegistrationStatusType = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListTypeRegistrationsOutputTypeDef:
        """
        Returns a list of registration tokens for the specified extension(s).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_type_registrations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_type_registrations)
        """

    def list_type_versions(
        self,
        *,
        Type: RegistryTypeType = ...,
        TypeName: str = ...,
        Arn: str = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        DeprecatedStatus: DeprecatedStatusType = ...,
        PublisherId: str = ...
    ) -> ListTypeVersionsOutputTypeDef:
        """
        Returns summary information about the versions of an extension.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_type_versions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_type_versions)
        """

    def list_types(
        self,
        *,
        Visibility: VisibilityType = ...,
        ProvisioningType: ProvisioningTypeType = ...,
        DeprecatedStatus: DeprecatedStatusType = ...,
        Type: RegistryTypeType = ...,
        Filters: TypeFiltersTypeDef = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListTypesOutputTypeDef:
        """
        Returns summary information about extension that have been registered with
        CloudFormation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_types)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#list_types)
        """

    def publish_type(
        self,
        *,
        Type: ThirdPartyTypeType = ...,
        Arn: str = ...,
        TypeName: str = ...,
        PublicVersionNumber: str = ...
    ) -> PublishTypeOutputTypeDef:
        """
        Publishes the specified extension to the CloudFormation registry as a public
        extension in this region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.publish_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#publish_type)
        """

    def record_handler_progress(
        self,
        *,
        BearerToken: str,
        OperationStatus: OperationStatusType,
        CurrentOperationStatus: OperationStatusType = ...,
        StatusMessage: str = ...,
        ErrorCode: HandlerErrorCodeType = ...,
        ResourceModel: str = ...,
        ClientRequestToken: str = ...
    ) -> Dict[str, Any]:
        """
        Reports progress of a resource handler to CloudFormation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.record_handler_progress)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#record_handler_progress)
        """

    def register_publisher(
        self, *, AcceptTermsAndConditions: bool = ..., ConnectionArn: str = ...
    ) -> RegisterPublisherOutputTypeDef:
        """
        Registers your account as a publisher of public extensions in the CloudFormation
        registry.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.register_publisher)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#register_publisher)
        """

    def register_type(
        self,
        *,
        TypeName: str,
        SchemaHandlerPackage: str,
        Type: RegistryTypeType = ...,
        LoggingConfig: LoggingConfigTypeDef = ...,
        ExecutionRoleArn: str = ...,
        ClientRequestToken: str = ...
    ) -> RegisterTypeOutputTypeDef:
        """
        Registers an extension with the CloudFormation service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.register_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#register_type)
        """

    def rollback_stack(
        self, *, StackName: str, RoleARN: str = ..., ClientRequestToken: str = ...
    ) -> RollbackStackOutputTypeDef:
        """
        When specifying `RollbackStack` , you preserve the state of previously
        provisioned resources when an operation fails.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.rollback_stack)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#rollback_stack)
        """

    def set_stack_policy(
        self, *, StackName: str, StackPolicyBody: str = ..., StackPolicyURL: str = ...
    ) -> None:
        """
        Sets a stack policy for a specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.set_stack_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#set_stack_policy)
        """

    def set_type_configuration(
        self,
        *,
        Configuration: str,
        TypeArn: str = ...,
        ConfigurationAlias: str = ...,
        TypeName: str = ...,
        Type: ThirdPartyTypeType = ...
    ) -> SetTypeConfigurationOutputTypeDef:
        """
        Specifies the configuration data for a registered CloudFormation extension, in
        the given account and region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.set_type_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#set_type_configuration)
        """

    def set_type_default_version(
        self,
        *,
        Arn: str = ...,
        Type: RegistryTypeType = ...,
        TypeName: str = ...,
        VersionId: str = ...
    ) -> Dict[str, Any]:
        """
        Specify the default version of an extension.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.set_type_default_version)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#set_type_default_version)
        """

    def signal_resource(
        self,
        *,
        StackName: str,
        LogicalResourceId: str,
        UniqueId: str,
        Status: ResourceSignalStatusType
    ) -> None:
        """
        Sends a signal to the specified resource with a success or failure status.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.signal_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#signal_resource)
        """

    def stop_stack_set_operation(
        self, *, StackSetName: str, OperationId: str, CallAs: CallAsType = ...
    ) -> Dict[str, Any]:
        """
        Stops an in-progress operation on a stack set and its associated stack
        instances.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.stop_stack_set_operation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#stop_stack_set_operation)
        """

    def test_type(
        self,
        *,
        Arn: str = ...,
        Type: ThirdPartyTypeType = ...,
        TypeName: str = ...,
        VersionId: str = ...,
        LogDeliveryBucket: str = ...
    ) -> TestTypeOutputTypeDef:
        """
        Tests a registered extension to make sure it meets all necessary requirements
        for being published in the CloudFormation registry.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.test_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#test_type)
        """

    def update_stack(
        self,
        *,
        StackName: str,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        UsePreviousTemplate: bool = ...,
        StackPolicyDuringUpdateBody: str = ...,
        StackPolicyDuringUpdateURL: str = ...,
        Parameters: Sequence[ParameterTypeDef] = ...,
        Capabilities: Sequence[CapabilityType] = ...,
        ResourceTypes: Sequence[str] = ...,
        RoleARN: str = ...,
        RollbackConfiguration: RollbackConfigurationTypeDef = ...,
        StackPolicyBody: str = ...,
        StackPolicyURL: str = ...,
        NotificationARNs: Sequence[str] = ...,
        Tags: Sequence[TagTypeDef] = ...,
        DisableRollback: bool = ...,
        ClientRequestToken: str = ...
    ) -> UpdateStackOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#update_stack)
        """

    def update_stack_instances(
        self,
        *,
        StackSetName: str,
        Regions: Sequence[str],
        Accounts: Sequence[str] = ...,
        DeploymentTargets: DeploymentTargetsTypeDef = ...,
        ParameterOverrides: Sequence[ParameterTypeDef] = ...,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        OperationId: str = ...,
        CallAs: CallAsType = ...
    ) -> UpdateStackInstancesOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#update_stack_instances)
        """

    def update_stack_set(
        self,
        *,
        StackSetName: str,
        Description: str = ...,
        TemplateBody: str = ...,
        TemplateURL: str = ...,
        UsePreviousTemplate: bool = ...,
        Parameters: Sequence[ParameterTypeDef] = ...,
        Capabilities: Sequence[CapabilityType] = ...,
        Tags: Sequence[TagTypeDef] = ...,
        OperationPreferences: StackSetOperationPreferencesTypeDef = ...,
        AdministrationRoleARN: str = ...,
        ExecutionRoleName: str = ...,
        DeploymentTargets: DeploymentTargetsTypeDef = ...,
        PermissionModel: PermissionModelsType = ...,
        AutoDeployment: AutoDeploymentTypeDef = ...,
        OperationId: str = ...,
        Accounts: Sequence[str] = ...,
        Regions: Sequence[str] = ...,
        CallAs: CallAsType = ...,
        ManagedExecution: ManagedExecutionTypeDef = ...
    ) -> UpdateStackSetOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#update_stack_set)
        """

    def update_termination_protection(
        self, *, EnableTerminationProtection: bool, StackName: str
    ) -> UpdateTerminationProtectionOutputTypeDef:
        """
        Updates termination protection for the specified stack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_termination_protection)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#update_termination_protection)
        """

    def validate_template(
        self, *, TemplateBody: str = ..., TemplateURL: str = ...
    ) -> ValidateTemplateOutputTypeDef:
        """
        Validates a specified template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.validate_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#validate_template)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_account_limits"]
    ) -> DescribeAccountLimitsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_change_set"]
    ) -> DescribeChangeSetPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_stack_events"]
    ) -> DescribeStackEventsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["describe_stacks"]) -> DescribeStacksPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_change_sets"]) -> ListChangeSetsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_exports"]) -> ListExportsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_imports"]) -> ListImportsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_stack_instances"]
    ) -> ListStackInstancesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_stack_resources"]
    ) -> ListStackResourcesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_stack_set_operation_results"]
    ) -> ListStackSetOperationResultsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_stack_set_operations"]
    ) -> ListStackSetOperationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_stack_sets"]) -> ListStackSetsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_stacks"]) -> ListStacksPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_types"]) -> ListTypesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_paginator)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["change_set_create_complete"]
    ) -> ChangeSetCreateCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["stack_create_complete"]
    ) -> StackCreateCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["stack_delete_complete"]
    ) -> StackDeleteCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["stack_exists"]) -> StackExistsWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["stack_import_complete"]
    ) -> StackImportCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["stack_rollback_complete"]
    ) -> StackRollbackCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["stack_update_complete"]
    ) -> StackUpdateCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """

    @overload
    def get_waiter(
        self, waiter_name: Literal["type_registration_complete"]
    ) -> TypeRegistrationCompleteWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudformation/client/#get_waiter)
        """
