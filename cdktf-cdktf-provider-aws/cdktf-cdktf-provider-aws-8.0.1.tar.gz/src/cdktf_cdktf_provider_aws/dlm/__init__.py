import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class DlmLifecyclePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy aws_dlm_lifecycle_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        description: builtins.str,
        execution_role_arn: builtins.str,
        policy_details: "DlmLifecyclePolicyPolicyDetails",
        id: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy aws_dlm_lifecycle_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.
        :param policy_details: policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#id DlmLifecyclePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DlmLifecyclePolicyConfig(
            description=description,
            execution_role_arn=execution_role_arn,
            policy_details=policy_details,
            id=id,
            state=state,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putPolicyDetails")
    def put_policy_details(
        self,
        *,
        action: typing.Optional["DlmLifecyclePolicyPolicyDetailsAction"] = None,
        event_source: typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSource"] = None,
        parameters: typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"] = None,
        policy_type: typing.Optional[builtins.str] = None,
        resource_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        schedule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DlmLifecyclePolicyPolicyDetailsSchedule"]]] = None,
        target_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param action: action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#action DlmLifecyclePolicy#action}
        :param event_source: event_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_source DlmLifecyclePolicy#event_source}
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        :param policy_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_type DlmLifecyclePolicy#policy_type}.
        :param resource_locations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_locations DlmLifecyclePolicy#resource_locations}.
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        :param target_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.
        '''
        value = DlmLifecyclePolicyPolicyDetails(
            action=action,
            event_source=event_source,
            parameters=parameters,
            policy_type=policy_type,
            resource_locations=resource_locations,
            resource_types=resource_types,
            schedule=schedule,
            target_tags=target_tags,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyDetails", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDetails")
    def policy_details(self) -> "DlmLifecyclePolicyPolicyDetailsOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsOutputReference", jsii.get(self, "policyDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArnInput")
    def execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDetailsInput")
    def policy_details_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetails"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetails"], jsii.get(self, "policyDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "description": "description",
        "execution_role_arn": "executionRoleArn",
        "policy_details": "policyDetails",
        "id": "id",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DlmLifecyclePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        description: builtins.str,
        execution_role_arn: builtins.str,
        policy_details: "DlmLifecyclePolicyPolicyDetails",
        id: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Data Lifecycle Manager.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.
        :param policy_details: policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#id DlmLifecyclePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(policy_details, dict):
            policy_details = DlmLifecyclePolicyPolicyDetails(**policy_details)
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "execution_role_arn": execution_role_arn,
            "policy_details": policy_details,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if state is not None:
            self._values["state"] = state
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.'''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.'''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_details(self) -> "DlmLifecyclePolicyPolicyDetails":
        '''policy_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        '''
        result = self._values.get("policy_details")
        assert result is not None, "Required property 'policy_details' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetails", result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#id DlmLifecyclePolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetails",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "event_source": "eventSource",
        "parameters": "parameters",
        "policy_type": "policyType",
        "resource_locations": "resourceLocations",
        "resource_types": "resourceTypes",
        "schedule": "schedule",
        "target_tags": "targetTags",
    },
)
class DlmLifecyclePolicyPolicyDetails:
    def __init__(
        self,
        *,
        action: typing.Optional["DlmLifecyclePolicyPolicyDetailsAction"] = None,
        event_source: typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSource"] = None,
        parameters: typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"] = None,
        policy_type: typing.Optional[builtins.str] = None,
        resource_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        schedule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DlmLifecyclePolicyPolicyDetailsSchedule"]]] = None,
        target_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param action: action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#action DlmLifecyclePolicy#action}
        :param event_source: event_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_source DlmLifecyclePolicy#event_source}
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        :param policy_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_type DlmLifecyclePolicy#policy_type}.
        :param resource_locations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_locations DlmLifecyclePolicy#resource_locations}.
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        :param target_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.
        '''
        if isinstance(action, dict):
            action = DlmLifecyclePolicyPolicyDetailsAction(**action)
        if isinstance(event_source, dict):
            event_source = DlmLifecyclePolicyPolicyDetailsEventSource(**event_source)
        if isinstance(parameters, dict):
            parameters = DlmLifecyclePolicyPolicyDetailsParameters(**parameters)
        self._values: typing.Dict[str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action
        if event_source is not None:
            self._values["event_source"] = event_source
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy_type is not None:
            self._values["policy_type"] = policy_type
        if resource_locations is not None:
            self._values["resource_locations"] = resource_locations
        if resource_types is not None:
            self._values["resource_types"] = resource_types
        if schedule is not None:
            self._values["schedule"] = schedule
        if target_tags is not None:
            self._values["target_tags"] = target_tags

    @builtins.property
    def action(self) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsAction"]:
        '''action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#action DlmLifecyclePolicy#action}
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsAction"], result)

    @builtins.property
    def event_source(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSource"]:
        '''event_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_source DlmLifecyclePolicy#event_source}
        '''
        result = self._values.get("event_source")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSource"], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"]:
        '''parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"], result)

    @builtins.property
    def policy_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_type DlmLifecyclePolicy#policy_type}.'''
        result = self._values.get("policy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_locations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_locations DlmLifecyclePolicy#resource_locations}.'''
        result = self._values.get("resource_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.'''
        result = self._values.get("resource_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]]]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]]], result)

    @builtins.property
    def target_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.'''
        result = self._values.get("target_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsAction",
    jsii_struct_bases=[],
    name_mapping={"cross_region_copy": "crossRegionCopy", "name": "name"},
)
class DlmLifecyclePolicyPolicyDetailsAction:
    def __init__(
        self,
        *,
        cross_region_copy: typing.Union[cdktf.IResolvable, typing.Sequence["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy"]],
        name: builtins.str,
    ) -> None:
        '''
        :param cross_region_copy: cross_region_copy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy DlmLifecyclePolicy#cross_region_copy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cross_region_copy": cross_region_copy,
            "name": name,
        }

    @builtins.property
    def cross_region_copy(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy"]]:
        '''cross_region_copy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy DlmLifecyclePolicy#cross_region_copy}
        '''
        result = self._values.get("cross_region_copy")
        assert result is not None, "Required property 'cross_region_copy' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy"]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_configuration": "encryptionConfiguration",
        "target": "target",
        "retain_rule": "retainRule",
    },
)
class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy:
    def __init__(
        self,
        *,
        encryption_configuration: "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration",
        target: builtins.str,
        retain_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule"] = None,
    ) -> None:
        '''
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encryption_configuration DlmLifecyclePolicy#encryption_configuration}
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.
        :param retain_rule: retain_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        if isinstance(encryption_configuration, dict):
            encryption_configuration = DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration(**encryption_configuration)
        if isinstance(retain_rule, dict):
            retain_rule = DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule(**retain_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "encryption_configuration": encryption_configuration,
            "target": target,
        }
        if retain_rule is not None:
            self._values["retain_rule"] = retain_rule

    @builtins.property
    def encryption_configuration(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration":
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encryption_configuration DlmLifecyclePolicy#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        assert result is not None, "Required property 'encryption_configuration' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration", result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retain_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule"]:
        '''retain_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        result = self._values.get("retain_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"cmk_arn": "cmkArn", "encrypted": "encrypted"},
)
class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration:
    def __init__(
        self,
        *,
        cmk_arn: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cmk_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cmk_arn is not None:
            self._values["cmk_arn"] = cmk_arn
        if encrypted is not None:
            self._values["encrypted"] = encrypted

    @builtins.property
    def cmk_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.'''
        result = self._values.get("cmk_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfigurationOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCmkArn")
    def reset_cmk_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCmkArn", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cmkArnInput")
    def cmk_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cmkArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cmkArn")
    def cmk_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cmkArn"))

    @cmk_arn.setter
    def cmk_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cmkArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(
        self,
        *,
        cmk_arn: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cmk_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration(
            cmk_arn=cmk_arn, encrypted=encrypted
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="putRetainRule")
    def put_retain_rule(
        self,
        *,
        interval: jsii.Number,
        interval_unit: builtins.str,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule(
            interval=interval, interval_unit=interval_unit
        )

        return typing.cast(None, jsii.invoke(self, "putRetainRule", [value]))

    @jsii.member(jsii_name="resetRetainRule")
    def reset_retain_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainRule", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfigurationOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfigurationOutputReference, jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRule")
    def retain_rule(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRuleOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRuleOutputReference", jsii.get(self, "retainRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRuleInput")
    def retain_rule_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule"], jsii.get(self, "retainRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "interval_unit": "intervalUnit"},
)
class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule:
    def __init__(self, *, interval: jsii.Number, interval_unit: builtins.str) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "interval_unit": interval_unit,
        }

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        assert result is not None, "Required property 'interval_unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsActionOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCrossRegionCopy")
    def put_cross_region_copy(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCrossRegionCopy", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRegionCopy")
    def cross_region_copy(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyList:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyList, jsii.get(self, "crossRegionCopy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRegionCopyInput")
    def cross_region_copy_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]]], jsii.get(self, "crossRegionCopyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsAction]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsAction],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsEventSource",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters", "type": "type"},
)
class DlmLifecyclePolicyPolicyDetailsEventSource:
    def __init__(
        self,
        *,
        parameters: "DlmLifecyclePolicyPolicyDetailsEventSourceParameters",
        type: builtins.str,
    ) -> None:
        '''
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#type DlmLifecyclePolicy#type}.
        '''
        if isinstance(parameters, dict):
            parameters = DlmLifecyclePolicyPolicyDetailsEventSourceParameters(**parameters)
        self._values: typing.Dict[str, typing.Any] = {
            "parameters": parameters,
            "type": type,
        }

    @builtins.property
    def parameters(self) -> "DlmLifecyclePolicyPolicyDetailsEventSourceParameters":
        '''parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        '''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsEventSourceParameters", result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#type DlmLifecyclePolicy#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsEventSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsEventSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsEventSourceOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        *,
        description_regex: builtins.str,
        event_type: builtins.str,
        snapshot_owner: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param description_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description_regex DlmLifecyclePolicy#description_regex}.
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_type DlmLifecyclePolicy#event_type}.
        :param snapshot_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#snapshot_owner DlmLifecyclePolicy#snapshot_owner}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsEventSourceParameters(
            description_regex=description_regex,
            event_type=event_type,
            snapshot_owner=snapshot_owner,
        )

        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsEventSourceParametersOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsEventSourceParametersOutputReference", jsii.get(self, "parameters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSourceParameters"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsEventSourceParameters"], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSource]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSource],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsEventSourceParameters",
    jsii_struct_bases=[],
    name_mapping={
        "description_regex": "descriptionRegex",
        "event_type": "eventType",
        "snapshot_owner": "snapshotOwner",
    },
)
class DlmLifecyclePolicyPolicyDetailsEventSourceParameters:
    def __init__(
        self,
        *,
        description_regex: builtins.str,
        event_type: builtins.str,
        snapshot_owner: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param description_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description_regex DlmLifecyclePolicy#description_regex}.
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_type DlmLifecyclePolicy#event_type}.
        :param snapshot_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#snapshot_owner DlmLifecyclePolicy#snapshot_owner}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description_regex": description_regex,
            "event_type": event_type,
            "snapshot_owner": snapshot_owner,
        }

    @builtins.property
    def description_regex(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description_regex DlmLifecyclePolicy#description_regex}.'''
        result = self._values.get("description_regex")
        assert result is not None, "Required property 'description_regex' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#event_type DlmLifecyclePolicy#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def snapshot_owner(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#snapshot_owner DlmLifecyclePolicy#snapshot_owner}.'''
        result = self._values.get("snapshot_owner")
        assert result is not None, "Required property 'snapshot_owner' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsEventSourceParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsEventSourceParametersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsEventSourceParametersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionRegexInput")
    def description_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventTypeInput")
    def event_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotOwnerInput")
    def snapshot_owner_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "snapshotOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionRegex")
    def description_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "descriptionRegex"))

    @description_regex.setter
    def description_regex(self, value: builtins.str) -> None:
        jsii.set(self, "descriptionRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventType"))

    @event_type.setter
    def event_type(self, value: builtins.str) -> None:
        jsii.set(self, "eventType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotOwner")
    def snapshot_owner(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "snapshotOwner"))

    @snapshot_owner.setter
    def snapshot_owner(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "snapshotOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSourceParameters]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSourceParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSourceParameters],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAction")
    def put_action(
        self,
        *,
        cross_region_copy: typing.Union[cdktf.IResolvable, typing.Sequence[DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy]],
        name: builtins.str,
    ) -> None:
        '''
        :param cross_region_copy: cross_region_copy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy DlmLifecyclePolicy#cross_region_copy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsAction(
            cross_region_copy=cross_region_copy, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putAction", [value]))

    @jsii.member(jsii_name="putEventSource")
    def put_event_source(
        self,
        *,
        parameters: DlmLifecyclePolicyPolicyDetailsEventSourceParameters,
        type: builtins.str,
    ) -> None:
        '''
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#parameters DlmLifecyclePolicy#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#type DlmLifecyclePolicy#type}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsEventSource(
            parameters=parameters, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putEventSource", [value]))

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        *,
        exclude_boot_volume: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        no_reboot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param exclude_boot_volume: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#exclude_boot_volume DlmLifecyclePolicy#exclude_boot_volume}.
        :param no_reboot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#no_reboot DlmLifecyclePolicy#no_reboot}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsParameters(
            exclude_boot_volume=exclude_boot_volume, no_reboot=no_reboot
        )

        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DlmLifecyclePolicyPolicyDetailsSchedule"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @jsii.member(jsii_name="resetEventSource")
    def reset_event_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSource", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPolicyType")
    def reset_policy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyType", []))

    @jsii.member(jsii_name="resetResourceLocations")
    def reset_resource_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceLocations", []))

    @jsii.member(jsii_name="resetResourceTypes")
    def reset_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypes", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetTargetTags")
    def reset_target_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> DlmLifecyclePolicyPolicyDetailsActionOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsActionOutputReference, jsii.get(self, "action"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSource")
    def event_source(self) -> DlmLifecyclePolicyPolicyDetailsEventSourceOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsEventSourceOutputReference, jsii.get(self, "eventSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "DlmLifecyclePolicyPolicyDetailsParametersOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsParametersOutputReference", jsii.get(self, "parameters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DlmLifecyclePolicyPolicyDetailsScheduleList":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleList", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsAction]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsAction], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceInput")
    def event_source_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSource]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsEventSource], jsii.get(self, "eventSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsParameters"], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyTypeInput")
    def policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceLocationsInput")
    def resource_locations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceLocationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesInput")
    def resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]]], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTagsInput")
    def target_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "targetTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyType"))

    @policy_type.setter
    def policy_type(self, value: builtins.str) -> None:
        jsii.set(self, "policyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceLocations")
    def resource_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceLocations"))

    @resource_locations.setter
    def resource_locations(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceLocations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypes")
    def resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypes"))

    @resource_types.setter
    def resource_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTags")
    def target_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "targetTags"))

    @target_tags.setter
    def target_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "targetTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DlmLifecyclePolicyPolicyDetails]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsParameters",
    jsii_struct_bases=[],
    name_mapping={"exclude_boot_volume": "excludeBootVolume", "no_reboot": "noReboot"},
)
class DlmLifecyclePolicyPolicyDetailsParameters:
    def __init__(
        self,
        *,
        exclude_boot_volume: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        no_reboot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param exclude_boot_volume: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#exclude_boot_volume DlmLifecyclePolicy#exclude_boot_volume}.
        :param no_reboot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#no_reboot DlmLifecyclePolicy#no_reboot}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude_boot_volume is not None:
            self._values["exclude_boot_volume"] = exclude_boot_volume
        if no_reboot is not None:
            self._values["no_reboot"] = no_reboot

    @builtins.property
    def exclude_boot_volume(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#exclude_boot_volume DlmLifecyclePolicy#exclude_boot_volume}.'''
        result = self._values.get("exclude_boot_volume")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def no_reboot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#no_reboot DlmLifecyclePolicy#no_reboot}.'''
        result = self._values.get("no_reboot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsParametersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsParametersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExcludeBootVolume")
    def reset_exclude_boot_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeBootVolume", []))

    @jsii.member(jsii_name="resetNoReboot")
    def reset_no_reboot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoReboot", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeBootVolumeInput")
    def exclude_boot_volume_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "excludeBootVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noRebootInput")
    def no_reboot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noRebootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeBootVolume")
    def exclude_boot_volume(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "excludeBootVolume"))

    @exclude_boot_volume.setter
    def exclude_boot_volume(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "excludeBootVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noReboot")
    def no_reboot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noReboot"))

    @no_reboot.setter
    def no_reboot(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noReboot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsParameters]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsParameters],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "create_rule": "createRule",
        "name": "name",
        "retain_rule": "retainRule",
        "copy_tags": "copyTags",
        "cross_region_copy_rule": "crossRegionCopyRule",
        "deprecate_rule": "deprecateRule",
        "fast_restore_rule": "fastRestoreRule",
        "share_rule": "shareRule",
        "tags_to_add": "tagsToAdd",
        "variable_tags": "variableTags",
    },
)
class DlmLifecyclePolicyPolicyDetailsSchedule:
    def __init__(
        self,
        *,
        create_rule: "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
        name: builtins.str,
        retain_rule: "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
        copy_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cross_region_copy_rule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]]] = None,
        deprecate_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule"] = None,
        fast_restore_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule"] = None,
        share_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleShareRule"] = None,
        tags_to_add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        variable_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param create_rule: create_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#create_rule DlmLifecyclePolicy#create_rule}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.
        :param retain_rule: retain_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        :param copy_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.
        :param cross_region_copy_rule: cross_region_copy_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy_rule DlmLifecyclePolicy#cross_region_copy_rule}
        :param deprecate_rule: deprecate_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        :param fast_restore_rule: fast_restore_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#fast_restore_rule DlmLifecyclePolicy#fast_restore_rule}
        :param share_rule: share_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#share_rule DlmLifecyclePolicy#share_rule}
        :param tags_to_add: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_to_add DlmLifecyclePolicy#tags_to_add}.
        :param variable_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#variable_tags DlmLifecyclePolicy#variable_tags}.
        '''
        if isinstance(create_rule, dict):
            create_rule = DlmLifecyclePolicyPolicyDetailsScheduleCreateRule(**create_rule)
        if isinstance(retain_rule, dict):
            retain_rule = DlmLifecyclePolicyPolicyDetailsScheduleRetainRule(**retain_rule)
        if isinstance(deprecate_rule, dict):
            deprecate_rule = DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule(**deprecate_rule)
        if isinstance(fast_restore_rule, dict):
            fast_restore_rule = DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule(**fast_restore_rule)
        if isinstance(share_rule, dict):
            share_rule = DlmLifecyclePolicyPolicyDetailsScheduleShareRule(**share_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "create_rule": create_rule,
            "name": name,
            "retain_rule": retain_rule,
        }
        if copy_tags is not None:
            self._values["copy_tags"] = copy_tags
        if cross_region_copy_rule is not None:
            self._values["cross_region_copy_rule"] = cross_region_copy_rule
        if deprecate_rule is not None:
            self._values["deprecate_rule"] = deprecate_rule
        if fast_restore_rule is not None:
            self._values["fast_restore_rule"] = fast_restore_rule
        if share_rule is not None:
            self._values["share_rule"] = share_rule
        if tags_to_add is not None:
            self._values["tags_to_add"] = tags_to_add
        if variable_tags is not None:
            self._values["variable_tags"] = variable_tags

    @builtins.property
    def create_rule(self) -> "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule":
        '''create_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#create_rule DlmLifecyclePolicy#create_rule}
        '''
        result = self._values.get("create_rule")
        assert result is not None, "Required property 'create_rule' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleCreateRule", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retain_rule(self) -> "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule":
        '''retain_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        result = self._values.get("retain_rule")
        assert result is not None, "Required property 'retain_rule' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleRetainRule", result)

    @builtins.property
    def copy_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.'''
        result = self._values.get("copy_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cross_region_copy_rule(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]]]:
        '''cross_region_copy_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy_rule DlmLifecyclePolicy#cross_region_copy_rule}
        '''
        result = self._values.get("cross_region_copy_rule")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]]], result)

    @builtins.property
    def deprecate_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule"]:
        '''deprecate_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        '''
        result = self._values.get("deprecate_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule"], result)

    @builtins.property
    def fast_restore_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule"]:
        '''fast_restore_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#fast_restore_rule DlmLifecyclePolicy#fast_restore_rule}
        '''
        result = self._values.get("fast_restore_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule"], result)

    @builtins.property
    def share_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleShareRule"]:
        '''share_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#share_rule DlmLifecyclePolicy#share_rule}
        '''
        result = self._values.get("share_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleShareRule"], result)

    @builtins.property
    def tags_to_add(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_to_add DlmLifecyclePolicy#tags_to_add}.'''
        result = self._values.get("tags_to_add")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def variable_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#variable_tags DlmLifecyclePolicy#variable_tags}.'''
        result = self._values.get("variable_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "interval": "interval",
        "interval_unit": "intervalUnit",
        "location": "location",
        "times": "times",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleCreateRule:
    def __init__(
        self,
        *,
        cron_expression: typing.Optional[builtins.str] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        times: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cron_expression DlmLifecyclePolicy#cron_expression}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#location DlmLifecyclePolicy#location}.
        :param times: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#times DlmLifecyclePolicy#times}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cron_expression is not None:
            self._values["cron_expression"] = cron_expression
        if interval is not None:
            self._values["interval"] = interval
        if interval_unit is not None:
            self._values["interval_unit"] = interval_unit
        if location is not None:
            self._values["location"] = location
        if times is not None:
            self._values["times"] = times

    @builtins.property
    def cron_expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cron_expression DlmLifecyclePolicy#cron_expression}.'''
        result = self._values.get("cron_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#location DlmLifecyclePolicy#location}.'''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def times(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#times DlmLifecyclePolicy#times}.'''
        result = self._values.get("times")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCronExpression")
    def reset_cron_expression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCronExpression", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetIntervalUnit")
    def reset_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalUnit", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @jsii.member(jsii_name="resetTimes")
    def reset_times(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cronExpressionInput")
    def cron_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronExpressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timesInput")
    def times_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cronExpression")
    def cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cronExpression"))

    @cron_expression.setter
    def cron_expression(self, value: builtins.str) -> None:
        jsii.set(self, "cronExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        jsii.set(self, "location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="times")
    def times(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "times"))

    @times.setter
    def times(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "times", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule",
    jsii_struct_bases=[],
    name_mapping={
        "encrypted": "encrypted",
        "target": "target",
        "cmk_arn": "cmkArn",
        "copy_tags": "copyTags",
        "deprecate_rule": "deprecateRule",
        "retain_rule": "retainRule",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule:
    def __init__(
        self,
        *,
        encrypted: typing.Union[builtins.bool, cdktf.IResolvable],
        target: builtins.str,
        cmk_arn: typing.Optional[builtins.str] = None,
        copy_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deprecate_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"] = None,
        retain_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"] = None,
    ) -> None:
        '''
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.
        :param cmk_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.
        :param copy_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.
        :param deprecate_rule: deprecate_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        :param retain_rule: retain_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        if isinstance(deprecate_rule, dict):
            deprecate_rule = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule(**deprecate_rule)
        if isinstance(retain_rule, dict):
            retain_rule = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule(**retain_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "encrypted": encrypted,
            "target": target,
        }
        if cmk_arn is not None:
            self._values["cmk_arn"] = cmk_arn
        if copy_tags is not None:
            self._values["copy_tags"] = copy_tags
        if deprecate_rule is not None:
            self._values["deprecate_rule"] = deprecate_rule
        if retain_rule is not None:
            self._values["retain_rule"] = retain_rule

    @builtins.property
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.'''
        result = self._values.get("encrypted")
        assert result is not None, "Required property 'encrypted' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cmk_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.'''
        result = self._values.get("cmk_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.'''
        result = self._values.get("copy_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def deprecate_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"]:
        '''deprecate_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        '''
        result = self._values.get("deprecate_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"], result)

    @builtins.property
    def retain_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"]:
        '''retain_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        result = self._values.get("retain_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "interval_unit": "intervalUnit"},
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule:
    def __init__(self, *, interval: jsii.Number, interval_unit: builtins.str) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "interval_unit": interval_unit,
        }

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        assert result is not None, "Required property 'interval_unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDeprecateRule")
    def put_deprecate_rule(
        self,
        *,
        interval: jsii.Number,
        interval_unit: builtins.str,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule(
            interval=interval, interval_unit=interval_unit
        )

        return typing.cast(None, jsii.invoke(self, "putDeprecateRule", [value]))

    @jsii.member(jsii_name="putRetainRule")
    def put_retain_rule(
        self,
        *,
        interval: jsii.Number,
        interval_unit: builtins.str,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule(
            interval=interval, interval_unit=interval_unit
        )

        return typing.cast(None, jsii.invoke(self, "putRetainRule", [value]))

    @jsii.member(jsii_name="resetCmkArn")
    def reset_cmk_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCmkArn", []))

    @jsii.member(jsii_name="resetCopyTags")
    def reset_copy_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTags", []))

    @jsii.member(jsii_name="resetDeprecateRule")
    def reset_deprecate_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecateRule", []))

    @jsii.member(jsii_name="resetRetainRule")
    def reset_retain_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainRule", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecateRule")
    def deprecate_rule(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference, jsii.get(self, "deprecateRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRule")
    def retain_rule(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference", jsii.get(self, "retainRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cmkArnInput")
    def cmk_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cmkArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsInput")
    def copy_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecateRuleInput")
    def deprecate_rule_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule], jsii.get(self, "deprecateRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRuleInput")
    def retain_rule_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"], jsii.get(self, "retainRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cmkArn")
    def cmk_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cmkArn"))

    @cmk_arn.setter
    def cmk_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cmkArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTags")
    def copy_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTags"))

    @copy_tags.setter
    def copy_tags(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "copyTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "interval_unit": "intervalUnit"},
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule:
    def __init__(self, *, interval: jsii.Number, interval_unit: builtins.str) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "interval_unit": interval_unit,
        }

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        assert result is not None, "Required property 'interval_unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule",
    jsii_struct_bases=[],
    name_mapping={
        "count": "count",
        "interval": "interval",
        "interval_unit": "intervalUnit",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule:
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if interval is not None:
            self._values["interval"] = interval
        if interval_unit is not None:
            self._values["interval_unit"] = interval_unit

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.'''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetIntervalUnit")
    def reset_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zones": "availabilityZones",
        "count": "count",
        "interval": "interval",
        "interval_unit": "intervalUnit",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule:
    def __init__(
        self,
        *,
        availability_zones: typing.Sequence[builtins.str],
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#availability_zones DlmLifecyclePolicy#availability_zones}.
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "availability_zones": availability_zones,
        }
        if count is not None:
            self._values["count"] = count
        if interval is not None:
            self._values["interval"] = interval
        if interval_unit is not None:
            self._values["interval_unit"] = interval_unit

    @builtins.property
    def availability_zones(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#availability_zones DlmLifecyclePolicy#availability_zones}.'''
        result = self._values.get("availability_zones")
        assert result is not None, "Required property 'availability_zones' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.'''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetIntervalUnit")
    def reset_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "availabilityZones", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsScheduleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DlmLifecyclePolicyPolicyDetailsScheduleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsSchedule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsSchedule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsSchedule]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DlmLifecyclePolicyPolicyDetailsScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCreateRule")
    def put_create_rule(
        self,
        *,
        cron_expression: typing.Optional[builtins.str] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        times: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cron_expression DlmLifecyclePolicy#cron_expression}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#location DlmLifecyclePolicy#location}.
        :param times: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#times DlmLifecyclePolicy#times}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleCreateRule(
            cron_expression=cron_expression,
            interval=interval,
            interval_unit=interval_unit,
            location=location,
            times=times,
        )

        return typing.cast(None, jsii.invoke(self, "putCreateRule", [value]))

    @jsii.member(jsii_name="putCrossRegionCopyRule")
    def put_cross_region_copy_rule(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCrossRegionCopyRule", [value]))

    @jsii.member(jsii_name="putDeprecateRule")
    def put_deprecate_rule(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule(
            count=count, interval=interval, interval_unit=interval_unit
        )

        return typing.cast(None, jsii.invoke(self, "putDeprecateRule", [value]))

    @jsii.member(jsii_name="putFastRestoreRule")
    def put_fast_restore_rule(
        self,
        *,
        availability_zones: typing.Sequence[builtins.str],
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#availability_zones DlmLifecyclePolicy#availability_zones}.
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule(
            availability_zones=availability_zones,
            count=count,
            interval=interval,
            interval_unit=interval_unit,
        )

        return typing.cast(None, jsii.invoke(self, "putFastRestoreRule", [value]))

    @jsii.member(jsii_name="putRetainRule")
    def put_retain_rule(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleRetainRule(
            count=count, interval=interval, interval_unit=interval_unit
        )

        return typing.cast(None, jsii.invoke(self, "putRetainRule", [value]))

    @jsii.member(jsii_name="putShareRule")
    def put_share_rule(
        self,
        *,
        target_accounts: typing.Sequence[builtins.str],
        unshare_interval: typing.Optional[jsii.Number] = None,
        unshare_interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_accounts DlmLifecyclePolicy#target_accounts}.
        :param unshare_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval DlmLifecyclePolicy#unshare_interval}.
        :param unshare_interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval_unit DlmLifecyclePolicy#unshare_interval_unit}.
        '''
        value = DlmLifecyclePolicyPolicyDetailsScheduleShareRule(
            target_accounts=target_accounts,
            unshare_interval=unshare_interval,
            unshare_interval_unit=unshare_interval_unit,
        )

        return typing.cast(None, jsii.invoke(self, "putShareRule", [value]))

    @jsii.member(jsii_name="resetCopyTags")
    def reset_copy_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTags", []))

    @jsii.member(jsii_name="resetCrossRegionCopyRule")
    def reset_cross_region_copy_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrossRegionCopyRule", []))

    @jsii.member(jsii_name="resetDeprecateRule")
    def reset_deprecate_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecateRule", []))

    @jsii.member(jsii_name="resetFastRestoreRule")
    def reset_fast_restore_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFastRestoreRule", []))

    @jsii.member(jsii_name="resetShareRule")
    def reset_share_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShareRule", []))

    @jsii.member(jsii_name="resetTagsToAdd")
    def reset_tags_to_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsToAdd", []))

    @jsii.member(jsii_name="resetVariableTags")
    def reset_variable_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariableTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createRule")
    def create_rule(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference, jsii.get(self, "createRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRegionCopyRule")
    def cross_region_copy_rule(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleList:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleList, jsii.get(self, "crossRegionCopyRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecateRule")
    def deprecate_rule(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRuleOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRuleOutputReference, jsii.get(self, "deprecateRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fastRestoreRule")
    def fast_restore_rule(
        self,
    ) -> DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRuleOutputReference:
        return typing.cast(DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRuleOutputReference, jsii.get(self, "fastRestoreRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRule")
    def retain_rule(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference", jsii.get(self, "retainRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareRule")
    def share_rule(
        self,
    ) -> "DlmLifecyclePolicyPolicyDetailsScheduleShareRuleOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleShareRuleOutputReference", jsii.get(self, "shareRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsInput")
    def copy_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createRuleInput")
    def create_rule_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule], jsii.get(self, "createRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRegionCopyRuleInput")
    def cross_region_copy_rule_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule]]], jsii.get(self, "crossRegionCopyRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecateRuleInput")
    def deprecate_rule_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule], jsii.get(self, "deprecateRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fastRestoreRuleInput")
    def fast_restore_rule_input(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule], jsii.get(self, "fastRestoreRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainRuleInput")
    def retain_rule_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleRetainRule"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleRetainRule"], jsii.get(self, "retainRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareRuleInput")
    def share_rule_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleShareRule"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleShareRule"], jsii.get(self, "shareRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsToAddInput")
    def tags_to_add_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsToAddInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variableTagsInput")
    def variable_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "variableTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTags")
    def copy_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTags"))

    @copy_tags.setter
    def copy_tags(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "copyTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsToAdd")
    def tags_to_add(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsToAdd"))

    @tags_to_add.setter
    def tags_to_add(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsToAdd", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variableTags")
    def variable_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "variableTags"))

    @variable_tags.setter
    def variable_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "variableTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsSchedule, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsSchedule, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DlmLifecyclePolicyPolicyDetailsSchedule, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
    jsii_struct_bases=[],
    name_mapping={
        "count": "count",
        "interval": "interval",
        "interval_unit": "intervalUnit",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleRetainRule:
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[jsii.Number] = None,
        interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if interval is not None:
            self._values["interval"] = interval
        if interval_unit is not None:
            self._values["interval_unit"] = interval_unit

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.'''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetIntervalUnit")
    def reset_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleShareRule",
    jsii_struct_bases=[],
    name_mapping={
        "target_accounts": "targetAccounts",
        "unshare_interval": "unshareInterval",
        "unshare_interval_unit": "unshareIntervalUnit",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleShareRule:
    def __init__(
        self,
        *,
        target_accounts: typing.Sequence[builtins.str],
        unshare_interval: typing.Optional[jsii.Number] = None,
        unshare_interval_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_accounts DlmLifecyclePolicy#target_accounts}.
        :param unshare_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval DlmLifecyclePolicy#unshare_interval}.
        :param unshare_interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval_unit DlmLifecyclePolicy#unshare_interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_accounts": target_accounts,
        }
        if unshare_interval is not None:
            self._values["unshare_interval"] = unshare_interval
        if unshare_interval_unit is not None:
            self._values["unshare_interval_unit"] = unshare_interval_unit

    @builtins.property
    def target_accounts(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_accounts DlmLifecyclePolicy#target_accounts}.'''
        result = self._values.get("target_accounts")
        assert result is not None, "Required property 'target_accounts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def unshare_interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval DlmLifecyclePolicy#unshare_interval}.'''
        result = self._values.get("unshare_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def unshare_interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#unshare_interval_unit DlmLifecyclePolicy#unshare_interval_unit}.'''
        result = self._values.get("unshare_interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleShareRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleShareRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleShareRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetUnshareInterval")
    def reset_unshare_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnshareInterval", []))

    @jsii.member(jsii_name="resetUnshareIntervalUnit")
    def reset_unshare_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnshareIntervalUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccountsInput")
    def target_accounts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetAccountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unshareIntervalInput")
    def unshare_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unshareIntervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unshareIntervalUnitInput")
    def unshare_interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unshareIntervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccounts")
    def target_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetAccounts"))

    @target_accounts.setter
    def target_accounts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetAccounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unshareInterval")
    def unshare_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unshareInterval"))

    @unshare_interval.setter
    def unshare_interval(self, value: jsii.Number) -> None:
        jsii.set(self, "unshareInterval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unshareIntervalUnit")
    def unshare_interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unshareIntervalUnit"))

    @unshare_interval_unit.setter
    def unshare_interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "unshareIntervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleShareRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleShareRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleShareRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DlmLifecyclePolicy",
    "DlmLifecyclePolicyConfig",
    "DlmLifecyclePolicyPolicyDetails",
    "DlmLifecyclePolicyPolicyDetailsAction",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopy",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfiguration",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyEncryptionConfigurationOutputReference",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyList",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyOutputReference",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRule",
    "DlmLifecyclePolicyPolicyDetailsActionCrossRegionCopyRetainRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsActionOutputReference",
    "DlmLifecyclePolicyPolicyDetailsEventSource",
    "DlmLifecyclePolicyPolicyDetailsEventSourceOutputReference",
    "DlmLifecyclePolicyPolicyDetailsEventSourceParameters",
    "DlmLifecyclePolicyPolicyDetailsEventSourceParametersOutputReference",
    "DlmLifecyclePolicyPolicyDetailsOutputReference",
    "DlmLifecyclePolicyPolicyDetailsParameters",
    "DlmLifecyclePolicyPolicyDetailsParametersOutputReference",
    "DlmLifecyclePolicyPolicyDetailsSchedule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleList",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleDeprecateRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleFastRestoreRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleList",
    "DlmLifecyclePolicyPolicyDetailsScheduleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleShareRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleShareRuleOutputReference",
]

publication.publish()
