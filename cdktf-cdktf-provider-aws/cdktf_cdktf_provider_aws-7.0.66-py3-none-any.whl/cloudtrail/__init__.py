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


class Cloudtrail(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudtrail.Cloudtrail",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail aws_cloudtrail}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        s3_bucket_name: builtins.str,
        advanced_event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailAdvancedEventSelector"]]] = None,
        cloud_watch_logs_group_arn: typing.Optional[builtins.str] = None,
        cloud_watch_logs_role_arn: typing.Optional[builtins.str] = None,
        enable_log_file_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailEventSelector"]]] = None,
        include_global_service_events: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        insight_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailInsightSelector"]]] = None,
        is_multi_region_trail: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        is_organization_trail: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        sns_topic_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail aws_cloudtrail} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#name Cloudtrail#name}.
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_bucket_name Cloudtrail#s3_bucket_name}.
        :param advanced_event_selector: advanced_event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#advanced_event_selector Cloudtrail#advanced_event_selector}
        :param cloud_watch_logs_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_group_arn Cloudtrail#cloud_watch_logs_group_arn}.
        :param cloud_watch_logs_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_role_arn Cloudtrail#cloud_watch_logs_role_arn}.
        :param enable_log_file_validation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_log_file_validation Cloudtrail#enable_log_file_validation}.
        :param enable_logging: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_logging Cloudtrail#enable_logging}.
        :param event_selector: event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#event_selector Cloudtrail#event_selector}
        :param include_global_service_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#include_global_service_events Cloudtrail#include_global_service_events}.
        :param insight_selector: insight_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#insight_selector Cloudtrail#insight_selector}
        :param is_multi_region_trail: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_multi_region_trail Cloudtrail#is_multi_region_trail}.
        :param is_organization_trail: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_organization_trail Cloudtrail#is_organization_trail}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#kms_key_id Cloudtrail#kms_key_id}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_key_prefix Cloudtrail#s3_key_prefix}.
        :param sns_topic_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#sns_topic_name Cloudtrail#sns_topic_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags Cloudtrail#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags_all Cloudtrail#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudtrailConfig(
            name=name,
            s3_bucket_name=s3_bucket_name,
            advanced_event_selector=advanced_event_selector,
            cloud_watch_logs_group_arn=cloud_watch_logs_group_arn,
            cloud_watch_logs_role_arn=cloud_watch_logs_role_arn,
            enable_log_file_validation=enable_log_file_validation,
            enable_logging=enable_logging,
            event_selector=event_selector,
            include_global_service_events=include_global_service_events,
            insight_selector=insight_selector,
            is_multi_region_trail=is_multi_region_trail,
            is_organization_trail=is_organization_trail,
            kms_key_id=kms_key_id,
            s3_key_prefix=s3_key_prefix,
            sns_topic_name=sns_topic_name,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAdvancedEventSelector")
    def reset_advanced_event_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdvancedEventSelector", []))

    @jsii.member(jsii_name="resetCloudWatchLogsGroupArn")
    def reset_cloud_watch_logs_group_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudWatchLogsGroupArn", []))

    @jsii.member(jsii_name="resetCloudWatchLogsRoleArn")
    def reset_cloud_watch_logs_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudWatchLogsRoleArn", []))

    @jsii.member(jsii_name="resetEnableLogFileValidation")
    def reset_enable_log_file_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLogFileValidation", []))

    @jsii.member(jsii_name="resetEnableLogging")
    def reset_enable_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLogging", []))

    @jsii.member(jsii_name="resetEventSelector")
    def reset_event_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSelector", []))

    @jsii.member(jsii_name="resetIncludeGlobalServiceEvents")
    def reset_include_global_service_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeGlobalServiceEvents", []))

    @jsii.member(jsii_name="resetInsightSelector")
    def reset_insight_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightSelector", []))

    @jsii.member(jsii_name="resetIsMultiRegionTrail")
    def reset_is_multi_region_trail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsMultiRegionTrail", []))

    @jsii.member(jsii_name="resetIsOrganizationTrail")
    def reset_is_organization_trail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsOrganizationTrail", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetS3KeyPrefix")
    def reset_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3KeyPrefix", []))

    @jsii.member(jsii_name="resetSnsTopicName")
    def reset_sns_topic_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsTopicName", []))

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
    @jsii.member(jsii_name="homeRegion")
    def home_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeRegion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedEventSelectorInput")
    def advanced_event_selector_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelector"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelector"]]], jsii.get(self, "advancedEventSelectorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchLogsGroupArnInput")
    def cloud_watch_logs_group_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWatchLogsGroupArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchLogsRoleArnInput")
    def cloud_watch_logs_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWatchLogsRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLogFileValidationInput")
    def enable_log_file_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableLogFileValidationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLoggingInput")
    def enable_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableLoggingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSelectorInput")
    def event_selector_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]]], jsii.get(self, "eventSelectorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeGlobalServiceEventsInput")
    def include_global_service_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeGlobalServiceEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightSelectorInput")
    def insight_selector_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]]], jsii.get(self, "insightSelectorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isMultiRegionTrailInput")
    def is_multi_region_trail_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isMultiRegionTrailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isOrganizationTrailInput")
    def is_organization_trail_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isOrganizationTrailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketNameInput")
    def s3_bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefixInput")
    def s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicNameInput")
    def sns_topic_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicNameInput"))

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
    @jsii.member(jsii_name="advancedEventSelector")
    def advanced_event_selector(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelector"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelector"]], jsii.get(self, "advancedEventSelector"))

    @advanced_event_selector.setter
    def advanced_event_selector(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelector"]],
    ) -> None:
        jsii.set(self, "advancedEventSelector", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchLogsGroupArn")
    def cloud_watch_logs_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudWatchLogsGroupArn"))

    @cloud_watch_logs_group_arn.setter
    def cloud_watch_logs_group_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudWatchLogsGroupArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchLogsRoleArn")
    def cloud_watch_logs_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudWatchLogsRoleArn"))

    @cloud_watch_logs_role_arn.setter
    def cloud_watch_logs_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudWatchLogsRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLogFileValidation")
    def enable_log_file_validation(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableLogFileValidation"))

    @enable_log_file_validation.setter
    def enable_log_file_validation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableLogFileValidation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLogging")
    def enable_logging(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableLogging"))

    @enable_logging.setter
    def enable_logging(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableLogging", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSelector")
    def event_selector(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]], jsii.get(self, "eventSelector"))

    @event_selector.setter
    def event_selector(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]],
    ) -> None:
        jsii.set(self, "eventSelector", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeGlobalServiceEvents")
    def include_global_service_events(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeGlobalServiceEvents"))

    @include_global_service_events.setter
    def include_global_service_events(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeGlobalServiceEvents", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightSelector")
    def insight_selector(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]], jsii.get(self, "insightSelector"))

    @insight_selector.setter
    def insight_selector(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]],
    ) -> None:
        jsii.set(self, "insightSelector", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isMultiRegionTrail")
    def is_multi_region_trail(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isMultiRegionTrail"))

    @is_multi_region_trail.setter
    def is_multi_region_trail(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isMultiRegionTrail", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isOrganizationTrail")
    def is_organization_trail(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isOrganizationTrail"))

    @is_organization_trail.setter
    def is_organization_trail(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isOrganizationTrail", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3BucketName"))

    @s3_bucket_name.setter
    def s3_bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "s3BucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @s3_key_prefix.setter
    def s3_key_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "s3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicName")
    def sns_topic_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicName"))

    @sns_topic_name.setter
    def sns_topic_name(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicName", value)

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
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailAdvancedEventSelector",
    jsii_struct_bases=[],
    name_mapping={"field_selector": "fieldSelector", "name": "name"},
)
class CloudtrailAdvancedEventSelector:
    def __init__(
        self,
        *,
        field_selector: typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailAdvancedEventSelectorFieldSelector"]],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param field_selector: field_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#field_selector Cloudtrail#field_selector}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#name Cloudtrail#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "field_selector": field_selector,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def field_selector(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelectorFieldSelector"]]:
        '''field_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#field_selector Cloudtrail#field_selector}
        '''
        result = self._values.get("field_selector")
        assert result is not None, "Required property 'field_selector' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CloudtrailAdvancedEventSelectorFieldSelector"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#name Cloudtrail#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailAdvancedEventSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailAdvancedEventSelectorFieldSelector",
    jsii_struct_bases=[],
    name_mapping={
        "field": "field",
        "ends_with": "endsWith",
        "equal_to": "equalTo",
        "not_ends_with": "notEndsWith",
        "not_equals": "notEquals",
        "not_starts_with": "notStartsWith",
        "starts_with": "startsWith",
    },
)
class CloudtrailAdvancedEventSelectorFieldSelector:
    def __init__(
        self,
        *,
        field: builtins.str,
        ends_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        equal_to: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_ends_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_equals: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_starts_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        starts_with: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#field Cloudtrail#field}.
        :param ends_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#ends_with Cloudtrail#ends_with}.
        :param equal_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#equals Cloudtrail#equals}.
        :param not_ends_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_ends_with Cloudtrail#not_ends_with}.
        :param not_equals: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_equals Cloudtrail#not_equals}.
        :param not_starts_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_starts_with Cloudtrail#not_starts_with}.
        :param starts_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#starts_with Cloudtrail#starts_with}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "field": field,
        }
        if ends_with is not None:
            self._values["ends_with"] = ends_with
        if equal_to is not None:
            self._values["equal_to"] = equal_to
        if not_ends_with is not None:
            self._values["not_ends_with"] = not_ends_with
        if not_equals is not None:
            self._values["not_equals"] = not_equals
        if not_starts_with is not None:
            self._values["not_starts_with"] = not_starts_with
        if starts_with is not None:
            self._values["starts_with"] = starts_with

    @builtins.property
    def field(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#field Cloudtrail#field}.'''
        result = self._values.get("field")
        assert result is not None, "Required property 'field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ends_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#ends_with Cloudtrail#ends_with}.'''
        result = self._values.get("ends_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def equal_to(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#equals Cloudtrail#equals}.'''
        result = self._values.get("equal_to")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_ends_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_ends_with Cloudtrail#not_ends_with}.'''
        result = self._values.get("not_ends_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_equals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_equals Cloudtrail#not_equals}.'''
        result = self._values.get("not_equals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_starts_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#not_starts_with Cloudtrail#not_starts_with}.'''
        result = self._values.get("not_starts_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def starts_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#starts_with Cloudtrail#starts_with}.'''
        result = self._values.get("starts_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailAdvancedEventSelectorFieldSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "s3_bucket_name": "s3BucketName",
        "advanced_event_selector": "advancedEventSelector",
        "cloud_watch_logs_group_arn": "cloudWatchLogsGroupArn",
        "cloud_watch_logs_role_arn": "cloudWatchLogsRoleArn",
        "enable_log_file_validation": "enableLogFileValidation",
        "enable_logging": "enableLogging",
        "event_selector": "eventSelector",
        "include_global_service_events": "includeGlobalServiceEvents",
        "insight_selector": "insightSelector",
        "is_multi_region_trail": "isMultiRegionTrail",
        "is_organization_trail": "isOrganizationTrail",
        "kms_key_id": "kmsKeyId",
        "s3_key_prefix": "s3KeyPrefix",
        "sns_topic_name": "snsTopicName",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CloudtrailConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        s3_bucket_name: builtins.str,
        advanced_event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[CloudtrailAdvancedEventSelector]]] = None,
        cloud_watch_logs_group_arn: typing.Optional[builtins.str] = None,
        cloud_watch_logs_role_arn: typing.Optional[builtins.str] = None,
        enable_log_file_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailEventSelector"]]] = None,
        include_global_service_events: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        insight_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailInsightSelector"]]] = None,
        is_multi_region_trail: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        is_organization_trail: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        sns_topic_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS CloudTrail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#name Cloudtrail#name}.
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_bucket_name Cloudtrail#s3_bucket_name}.
        :param advanced_event_selector: advanced_event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#advanced_event_selector Cloudtrail#advanced_event_selector}
        :param cloud_watch_logs_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_group_arn Cloudtrail#cloud_watch_logs_group_arn}.
        :param cloud_watch_logs_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_role_arn Cloudtrail#cloud_watch_logs_role_arn}.
        :param enable_log_file_validation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_log_file_validation Cloudtrail#enable_log_file_validation}.
        :param enable_logging: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_logging Cloudtrail#enable_logging}.
        :param event_selector: event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#event_selector Cloudtrail#event_selector}
        :param include_global_service_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#include_global_service_events Cloudtrail#include_global_service_events}.
        :param insight_selector: insight_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#insight_selector Cloudtrail#insight_selector}
        :param is_multi_region_trail: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_multi_region_trail Cloudtrail#is_multi_region_trail}.
        :param is_organization_trail: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_organization_trail Cloudtrail#is_organization_trail}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#kms_key_id Cloudtrail#kms_key_id}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_key_prefix Cloudtrail#s3_key_prefix}.
        :param sns_topic_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#sns_topic_name Cloudtrail#sns_topic_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags Cloudtrail#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags_all Cloudtrail#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "s3_bucket_name": s3_bucket_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if advanced_event_selector is not None:
            self._values["advanced_event_selector"] = advanced_event_selector
        if cloud_watch_logs_group_arn is not None:
            self._values["cloud_watch_logs_group_arn"] = cloud_watch_logs_group_arn
        if cloud_watch_logs_role_arn is not None:
            self._values["cloud_watch_logs_role_arn"] = cloud_watch_logs_role_arn
        if enable_log_file_validation is not None:
            self._values["enable_log_file_validation"] = enable_log_file_validation
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if event_selector is not None:
            self._values["event_selector"] = event_selector
        if include_global_service_events is not None:
            self._values["include_global_service_events"] = include_global_service_events
        if insight_selector is not None:
            self._values["insight_selector"] = insight_selector
        if is_multi_region_trail is not None:
            self._values["is_multi_region_trail"] = is_multi_region_trail
        if is_organization_trail is not None:
            self._values["is_organization_trail"] = is_organization_trail
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix
        if sns_topic_name is not None:
            self._values["sns_topic_name"] = sns_topic_name
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#name Cloudtrail#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_bucket_name Cloudtrail#s3_bucket_name}.'''
        result = self._values.get("s3_bucket_name")
        assert result is not None, "Required property 's3_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def advanced_event_selector(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CloudtrailAdvancedEventSelector]]]:
        '''advanced_event_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#advanced_event_selector Cloudtrail#advanced_event_selector}
        '''
        result = self._values.get("advanced_event_selector")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CloudtrailAdvancedEventSelector]]], result)

    @builtins.property
    def cloud_watch_logs_group_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_group_arn Cloudtrail#cloud_watch_logs_group_arn}.'''
        result = self._values.get("cloud_watch_logs_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_watch_logs_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#cloud_watch_logs_role_arn Cloudtrail#cloud_watch_logs_role_arn}.'''
        result = self._values.get("cloud_watch_logs_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_log_file_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_log_file_validation Cloudtrail#enable_log_file_validation}.'''
        result = self._values.get("enable_log_file_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#enable_logging Cloudtrail#enable_logging}.'''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event_selector(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]]]:
        '''event_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#event_selector Cloudtrail#event_selector}
        '''
        result = self._values.get("event_selector")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelector"]]], result)

    @builtins.property
    def include_global_service_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#include_global_service_events Cloudtrail#include_global_service_events}.'''
        result = self._values.get("include_global_service_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def insight_selector(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]]]:
        '''insight_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#insight_selector Cloudtrail#insight_selector}
        '''
        result = self._values.get("insight_selector")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailInsightSelector"]]], result)

    @builtins.property
    def is_multi_region_trail(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_multi_region_trail Cloudtrail#is_multi_region_trail}.'''
        result = self._values.get("is_multi_region_trail")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def is_organization_trail(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#is_organization_trail Cloudtrail#is_organization_trail}.'''
        result = self._values.get("is_organization_trail")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#kms_key_id Cloudtrail#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#s3_key_prefix Cloudtrail#s3_key_prefix}.'''
        result = self._values.get("s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_topic_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#sns_topic_name Cloudtrail#sns_topic_name}.'''
        result = self._values.get("sns_topic_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags Cloudtrail#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#tags_all Cloudtrail#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudtrailEventDataStore(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStore",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store aws_cloudtrail_event_data_store}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        advanced_event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailEventDataStoreAdvancedEventSelector"]]] = None,
        multi_region_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        organization_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["CloudtrailEventDataStoreTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store aws_cloudtrail_event_data_store} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#name CloudtrailEventDataStore#name}.
        :param advanced_event_selector: advanced_event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#advanced_event_selector CloudtrailEventDataStore#advanced_event_selector}
        :param multi_region_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#multi_region_enabled CloudtrailEventDataStore#multi_region_enabled}.
        :param organization_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#organization_enabled CloudtrailEventDataStore#organization_enabled}.
        :param retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#retention_period CloudtrailEventDataStore#retention_period}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags CloudtrailEventDataStore#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags_all CloudtrailEventDataStore#tags_all}.
        :param termination_protection_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#termination_protection_enabled CloudtrailEventDataStore#termination_protection_enabled}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#timeouts CloudtrailEventDataStore#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudtrailEventDataStoreConfig(
            name=name,
            advanced_event_selector=advanced_event_selector,
            multi_region_enabled=multi_region_enabled,
            organization_enabled=organization_enabled,
            retention_period=retention_period,
            tags=tags,
            tags_all=tags_all,
            termination_protection_enabled=termination_protection_enabled,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#create CloudtrailEventDataStore#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#delete CloudtrailEventDataStore#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#update CloudtrailEventDataStore#update}.
        '''
        value = CloudtrailEventDataStoreTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAdvancedEventSelector")
    def reset_advanced_event_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdvancedEventSelector", []))

    @jsii.member(jsii_name="resetMultiRegionEnabled")
    def reset_multi_region_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiRegionEnabled", []))

    @jsii.member(jsii_name="resetOrganizationEnabled")
    def reset_organization_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationEnabled", []))

    @jsii.member(jsii_name="resetRetentionPeriod")
    def reset_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionPeriod", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTerminationProtectionEnabled")
    def reset_termination_protection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationProtectionEnabled", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudtrailEventDataStoreTimeoutsOutputReference":
        return typing.cast("CloudtrailEventDataStoreTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedEventSelectorInput")
    def advanced_event_selector_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelector"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelector"]]], jsii.get(self, "advancedEventSelectorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiRegionEnabledInput")
    def multi_region_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "multiRegionEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationEnabledInput")
    def organization_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "organizationEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionPeriodInput")
    def retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionPeriodInput"))

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
    @jsii.member(jsii_name="terminationProtectionEnabledInput")
    def termination_protection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "terminationProtectionEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["CloudtrailEventDataStoreTimeouts"]:
        return typing.cast(typing.Optional["CloudtrailEventDataStoreTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedEventSelector")
    def advanced_event_selector(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelector"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelector"]], jsii.get(self, "advancedEventSelector"))

    @advanced_event_selector.setter
    def advanced_event_selector(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelector"]],
    ) -> None:
        jsii.set(self, "advancedEventSelector", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiRegionEnabled")
    def multi_region_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "multiRegionEnabled"))

    @multi_region_enabled.setter
    def multi_region_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "multiRegionEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationEnabled")
    def organization_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "organizationEnabled"))

    @organization_enabled.setter
    def organization_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "organizationEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionPeriod"))

    @retention_period.setter
    def retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "retentionPeriod", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminationProtectionEnabled")
    def termination_protection_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "terminationProtectionEnabled"))

    @termination_protection_enabled.setter
    def termination_protection_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "terminationProtectionEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStoreAdvancedEventSelector",
    jsii_struct_bases=[],
    name_mapping={"field_selector": "fieldSelector", "name": "name"},
)
class CloudtrailEventDataStoreAdvancedEventSelector:
    def __init__(
        self,
        *,
        field_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector"]]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param field_selector: field_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#field_selector CloudtrailEventDataStore#field_selector}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#name CloudtrailEventDataStore#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if field_selector is not None:
            self._values["field_selector"] = field_selector
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def field_selector(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector"]]]:
        '''field_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#field_selector CloudtrailEventDataStore#field_selector}
        '''
        result = self._values.get("field_selector")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#name CloudtrailEventDataStore#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventDataStoreAdvancedEventSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector",
    jsii_struct_bases=[],
    name_mapping={
        "ends_with": "endsWith",
        "equal_to": "equalTo",
        "field": "field",
        "not_ends_with": "notEndsWith",
        "not_equals": "notEquals",
        "not_starts_with": "notStartsWith",
        "starts_with": "startsWith",
    },
)
class CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector:
    def __init__(
        self,
        *,
        ends_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        equal_to: typing.Optional[typing.Sequence[builtins.str]] = None,
        field: typing.Optional[builtins.str] = None,
        not_ends_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_equals: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_starts_with: typing.Optional[typing.Sequence[builtins.str]] = None,
        starts_with: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param ends_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#ends_with CloudtrailEventDataStore#ends_with}.
        :param equal_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#equals CloudtrailEventDataStore#equals}.
        :param field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#field CloudtrailEventDataStore#field}.
        :param not_ends_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_ends_with CloudtrailEventDataStore#not_ends_with}.
        :param not_equals: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_equals CloudtrailEventDataStore#not_equals}.
        :param not_starts_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_starts_with CloudtrailEventDataStore#not_starts_with}.
        :param starts_with: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#starts_with CloudtrailEventDataStore#starts_with}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ends_with is not None:
            self._values["ends_with"] = ends_with
        if equal_to is not None:
            self._values["equal_to"] = equal_to
        if field is not None:
            self._values["field"] = field
        if not_ends_with is not None:
            self._values["not_ends_with"] = not_ends_with
        if not_equals is not None:
            self._values["not_equals"] = not_equals
        if not_starts_with is not None:
            self._values["not_starts_with"] = not_starts_with
        if starts_with is not None:
            self._values["starts_with"] = starts_with

    @builtins.property
    def ends_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#ends_with CloudtrailEventDataStore#ends_with}.'''
        result = self._values.get("ends_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def equal_to(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#equals CloudtrailEventDataStore#equals}.'''
        result = self._values.get("equal_to")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#field CloudtrailEventDataStore#field}.'''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_ends_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_ends_with CloudtrailEventDataStore#not_ends_with}.'''
        result = self._values.get("not_ends_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_equals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_equals CloudtrailEventDataStore#not_equals}.'''
        result = self._values.get("not_equals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_starts_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#not_starts_with CloudtrailEventDataStore#not_starts_with}.'''
        result = self._values.get("not_starts_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def starts_with(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#starts_with CloudtrailEventDataStore#starts_with}.'''
        result = self._values.get("starts_with")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStoreConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "advanced_event_selector": "advancedEventSelector",
        "multi_region_enabled": "multiRegionEnabled",
        "organization_enabled": "organizationEnabled",
        "retention_period": "retentionPeriod",
        "tags": "tags",
        "tags_all": "tagsAll",
        "termination_protection_enabled": "terminationProtectionEnabled",
        "timeouts": "timeouts",
    },
)
class CloudtrailEventDataStoreConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        advanced_event_selector: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[CloudtrailEventDataStoreAdvancedEventSelector]]] = None,
        multi_region_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        organization_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["CloudtrailEventDataStoreTimeouts"] = None,
    ) -> None:
        '''AWS CloudTrail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#name CloudtrailEventDataStore#name}.
        :param advanced_event_selector: advanced_event_selector block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#advanced_event_selector CloudtrailEventDataStore#advanced_event_selector}
        :param multi_region_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#multi_region_enabled CloudtrailEventDataStore#multi_region_enabled}.
        :param organization_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#organization_enabled CloudtrailEventDataStore#organization_enabled}.
        :param retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#retention_period CloudtrailEventDataStore#retention_period}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags CloudtrailEventDataStore#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags_all CloudtrailEventDataStore#tags_all}.
        :param termination_protection_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#termination_protection_enabled CloudtrailEventDataStore#termination_protection_enabled}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#timeouts CloudtrailEventDataStore#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = CloudtrailEventDataStoreTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if advanced_event_selector is not None:
            self._values["advanced_event_selector"] = advanced_event_selector
        if multi_region_enabled is not None:
            self._values["multi_region_enabled"] = multi_region_enabled
        if organization_enabled is not None:
            self._values["organization_enabled"] = organization_enabled
        if retention_period is not None:
            self._values["retention_period"] = retention_period
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if termination_protection_enabled is not None:
            self._values["termination_protection_enabled"] = termination_protection_enabled
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#name CloudtrailEventDataStore#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def advanced_event_selector(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CloudtrailEventDataStoreAdvancedEventSelector]]]:
        '''advanced_event_selector block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#advanced_event_selector CloudtrailEventDataStore#advanced_event_selector}
        '''
        result = self._values.get("advanced_event_selector")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CloudtrailEventDataStoreAdvancedEventSelector]]], result)

    @builtins.property
    def multi_region_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#multi_region_enabled CloudtrailEventDataStore#multi_region_enabled}.'''
        result = self._values.get("multi_region_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def organization_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#organization_enabled CloudtrailEventDataStore#organization_enabled}.'''
        result = self._values.get("organization_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#retention_period CloudtrailEventDataStore#retention_period}.'''
        result = self._values.get("retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags CloudtrailEventDataStore#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#tags_all CloudtrailEventDataStore#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#termination_protection_enabled CloudtrailEventDataStore#termination_protection_enabled}.'''
        result = self._values.get("termination_protection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudtrailEventDataStoreTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#timeouts CloudtrailEventDataStore#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudtrailEventDataStoreTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventDataStoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStoreTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class CloudtrailEventDataStoreTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#create CloudtrailEventDataStore#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#delete CloudtrailEventDataStore#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#update CloudtrailEventDataStore#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#create CloudtrailEventDataStore#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#delete CloudtrailEventDataStore#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail_event_data_store#update CloudtrailEventDataStore#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventDataStoreTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudtrailEventDataStoreTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventDataStoreTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudtrailEventDataStoreTimeouts]:
        return typing.cast(typing.Optional[CloudtrailEventDataStoreTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudtrailEventDataStoreTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventSelector",
    jsii_struct_bases=[],
    name_mapping={
        "data_resource": "dataResource",
        "exclude_management_event_sources": "excludeManagementEventSources",
        "include_management_events": "includeManagementEvents",
        "read_write_type": "readWriteType",
    },
)
class CloudtrailEventSelector:
    def __init__(
        self,
        *,
        data_resource: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["CloudtrailEventSelectorDataResource"]]] = None,
        exclude_management_event_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_management_events: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        read_write_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_resource: data_resource block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#data_resource Cloudtrail#data_resource}
        :param exclude_management_event_sources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#exclude_management_event_sources Cloudtrail#exclude_management_event_sources}.
        :param include_management_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#include_management_events Cloudtrail#include_management_events}.
        :param read_write_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#read_write_type Cloudtrail#read_write_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if data_resource is not None:
            self._values["data_resource"] = data_resource
        if exclude_management_event_sources is not None:
            self._values["exclude_management_event_sources"] = exclude_management_event_sources
        if include_management_events is not None:
            self._values["include_management_events"] = include_management_events
        if read_write_type is not None:
            self._values["read_write_type"] = read_write_type

    @builtins.property
    def data_resource(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelectorDataResource"]]]:
        '''data_resource block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#data_resource Cloudtrail#data_resource}
        '''
        result = self._values.get("data_resource")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CloudtrailEventSelectorDataResource"]]], result)

    @builtins.property
    def exclude_management_event_sources(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#exclude_management_event_sources Cloudtrail#exclude_management_event_sources}.'''
        result = self._values.get("exclude_management_event_sources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_management_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#include_management_events Cloudtrail#include_management_events}.'''
        result = self._values.get("include_management_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def read_write_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#read_write_type Cloudtrail#read_write_type}.'''
        result = self._values.get("read_write_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailEventSelectorDataResource",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "values": "values"},
)
class CloudtrailEventSelectorDataResource:
    def __init__(
        self,
        *,
        type: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#type Cloudtrail#type}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#values Cloudtrail#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "values": values,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#type Cloudtrail#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#values Cloudtrail#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailEventSelectorDataResource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.CloudtrailInsightSelector",
    jsii_struct_bases=[],
    name_mapping={"insight_type": "insightType"},
)
class CloudtrailInsightSelector:
    def __init__(self, *, insight_type: builtins.str) -> None:
        '''
        :param insight_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#insight_type Cloudtrail#insight_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "insight_type": insight_type,
        }

    @builtins.property
    def insight_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudtrail#insight_type Cloudtrail#insight_type}.'''
        result = self._values.get("insight_type")
        assert result is not None, "Required property 'insight_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudtrailInsightSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudtrailServiceAccount(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudtrail.DataAwsCloudtrailServiceAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudtrail_service_account aws_cloudtrail_service_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        region: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudtrail_service_account aws_cloudtrail_service_account} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudtrail_service_account#region DataAwsCloudtrailServiceAccount#region}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudtrailServiceAccountConfig(
            region=region,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudtrail.DataAwsCloudtrailServiceAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "region": "region",
    },
)
class DataAwsCloudtrailServiceAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudTrail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudtrail_service_account#region DataAwsCloudtrailServiceAccount#region}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if region is not None:
            self._values["region"] = region

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
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudtrail_service_account#region DataAwsCloudtrailServiceAccount#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudtrailServiceAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Cloudtrail",
    "CloudtrailAdvancedEventSelector",
    "CloudtrailAdvancedEventSelectorFieldSelector",
    "CloudtrailConfig",
    "CloudtrailEventDataStore",
    "CloudtrailEventDataStoreAdvancedEventSelector",
    "CloudtrailEventDataStoreAdvancedEventSelectorFieldSelector",
    "CloudtrailEventDataStoreConfig",
    "CloudtrailEventDataStoreTimeouts",
    "CloudtrailEventDataStoreTimeoutsOutputReference",
    "CloudtrailEventSelector",
    "CloudtrailEventSelectorDataResource",
    "CloudtrailInsightSelector",
    "DataAwsCloudtrailServiceAccount",
    "DataAwsCloudtrailServiceAccountConfig",
]

publication.publish()
