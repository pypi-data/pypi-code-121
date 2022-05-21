# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'AssignmentIdentityArgs',
]

@pulumi.input_type
class AssignmentIdentityArgs:
    def __init__(__self__, *,
                 identity_ids: pulumi.Input[Sequence[pulumi.Input[str]]],
                 type: pulumi.Input[str]):
        """
        :param pulumi.Input[Sequence[pulumi.Input[str]]] identity_ids: Specifies a list of User Assigned Managed Identity IDs to be assigned to this Blueprint.
        :param pulumi.Input[str] type: Specifies the type of Managed Service Identity that should be configured on this Blueprint. Only possible value is `UserAssigned`.
        """
        pulumi.set(__self__, "identity_ids", identity_ids)
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="identityIds")
    def identity_ids(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        Specifies a list of User Assigned Managed Identity IDs to be assigned to this Blueprint.
        """
        return pulumi.get(self, "identity_ids")

    @identity_ids.setter
    def identity_ids(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "identity_ids", value)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        Specifies the type of Managed Service Identity that should be configured on this Blueprint. Only possible value is `UserAssigned`.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)


