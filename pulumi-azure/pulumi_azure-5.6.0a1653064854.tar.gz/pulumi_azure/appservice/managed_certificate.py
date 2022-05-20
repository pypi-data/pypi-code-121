# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ManagedCertificateArgs', 'ManagedCertificate']

@pulumi.input_type
class ManagedCertificateArgs:
    def __init__(__self__, *,
                 custom_hostname_binding_id: pulumi.Input[str],
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ManagedCertificate resource.
        :param pulumi.Input[str] custom_hostname_binding_id: The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the App Service Managed Certificate.
        """
        pulumi.set(__self__, "custom_hostname_binding_id", custom_hostname_binding_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="customHostnameBindingId")
    def custom_hostname_binding_id(self) -> pulumi.Input[str]:
        """
        The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        """
        return pulumi.get(self, "custom_hostname_binding_id")

    @custom_hostname_binding_id.setter
    def custom_hostname_binding_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "custom_hostname_binding_id", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the App Service Managed Certificate.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _ManagedCertificateState:
    def __init__(__self__, *,
                 canonical_name: Optional[pulumi.Input[str]] = None,
                 custom_hostname_binding_id: Optional[pulumi.Input[str]] = None,
                 expiration_date: Optional[pulumi.Input[str]] = None,
                 friendly_name: Optional[pulumi.Input[str]] = None,
                 host_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 issue_date: Optional[pulumi.Input[str]] = None,
                 issuer: Optional[pulumi.Input[str]] = None,
                 subject_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 thumbprint: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ManagedCertificate resources.
        :param pulumi.Input[str] canonical_name: The Canonical Name of the Certificate.
        :param pulumi.Input[str] custom_hostname_binding_id: The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        :param pulumi.Input[str] expiration_date: The expiration date of the Certificate.
        :param pulumi.Input[str] friendly_name: The friendly name of the Certificate.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] host_names: The list of Host Names for the Certificate.
        :param pulumi.Input[str] issue_date: The Start date for the Certificate.
        :param pulumi.Input[str] issuer: The issuer of the Certificate.
        :param pulumi.Input[str] subject_name: The Subject Name for the Certificate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the App Service Managed Certificate.
        :param pulumi.Input[str] thumbprint: The Certificate Thumbprint.
        """
        if canonical_name is not None:
            pulumi.set(__self__, "canonical_name", canonical_name)
        if custom_hostname_binding_id is not None:
            pulumi.set(__self__, "custom_hostname_binding_id", custom_hostname_binding_id)
        if expiration_date is not None:
            pulumi.set(__self__, "expiration_date", expiration_date)
        if friendly_name is not None:
            pulumi.set(__self__, "friendly_name", friendly_name)
        if host_names is not None:
            pulumi.set(__self__, "host_names", host_names)
        if issue_date is not None:
            pulumi.set(__self__, "issue_date", issue_date)
        if issuer is not None:
            pulumi.set(__self__, "issuer", issuer)
        if subject_name is not None:
            pulumi.set(__self__, "subject_name", subject_name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if thumbprint is not None:
            pulumi.set(__self__, "thumbprint", thumbprint)

    @property
    @pulumi.getter(name="canonicalName")
    def canonical_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Canonical Name of the Certificate.
        """
        return pulumi.get(self, "canonical_name")

    @canonical_name.setter
    def canonical_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "canonical_name", value)

    @property
    @pulumi.getter(name="customHostnameBindingId")
    def custom_hostname_binding_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        """
        return pulumi.get(self, "custom_hostname_binding_id")

    @custom_hostname_binding_id.setter
    def custom_hostname_binding_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "custom_hostname_binding_id", value)

    @property
    @pulumi.getter(name="expirationDate")
    def expiration_date(self) -> Optional[pulumi.Input[str]]:
        """
        The expiration date of the Certificate.
        """
        return pulumi.get(self, "expiration_date")

    @expiration_date.setter
    def expiration_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "expiration_date", value)

    @property
    @pulumi.getter(name="friendlyName")
    def friendly_name(self) -> Optional[pulumi.Input[str]]:
        """
        The friendly name of the Certificate.
        """
        return pulumi.get(self, "friendly_name")

    @friendly_name.setter
    def friendly_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "friendly_name", value)

    @property
    @pulumi.getter(name="hostNames")
    def host_names(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The list of Host Names for the Certificate.
        """
        return pulumi.get(self, "host_names")

    @host_names.setter
    def host_names(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "host_names", value)

    @property
    @pulumi.getter(name="issueDate")
    def issue_date(self) -> Optional[pulumi.Input[str]]:
        """
        The Start date for the Certificate.
        """
        return pulumi.get(self, "issue_date")

    @issue_date.setter
    def issue_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "issue_date", value)

    @property
    @pulumi.getter
    def issuer(self) -> Optional[pulumi.Input[str]]:
        """
        The issuer of the Certificate.
        """
        return pulumi.get(self, "issuer")

    @issuer.setter
    def issuer(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "issuer", value)

    @property
    @pulumi.getter(name="subjectName")
    def subject_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Subject Name for the Certificate.
        """
        return pulumi.get(self, "subject_name")

    @subject_name.setter
    def subject_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subject_name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags which should be assigned to the App Service Managed Certificate.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter
    def thumbprint(self) -> Optional[pulumi.Input[str]]:
        """
        The Certificate Thumbprint.
        """
        return pulumi.get(self, "thumbprint")

    @thumbprint.setter
    def thumbprint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "thumbprint", value)


class ManagedCertificate(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 custom_hostname_binding_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        This certificate can be used to secure custom domains on App Services (Windows and Linux) hosted on an App Service Plan of Basic and above (free and shared tiers are not supported).

        > NOTE: A certificate is valid for six months, and about a month before the certificate’s expiration date, App Services renews/rotates the certificate. This is managed by Azure and doesn't require this resource to be changed or reprovisioned. It will change the `thumbprint` computed attribute the next time the resource is refreshed after rotation occurs, so keep that in mind if you have any dependencies on this attribute directly.

        ## Import

        App Service Managed Certificates can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/managedCertificate:ManagedCertificate example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/resGroup1/providers/Microsoft.Web/certificates/customhost.contoso.com
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] custom_hostname_binding_id: The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the App Service Managed Certificate.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ManagedCertificateArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        This certificate can be used to secure custom domains on App Services (Windows and Linux) hosted on an App Service Plan of Basic and above (free and shared tiers are not supported).

        > NOTE: A certificate is valid for six months, and about a month before the certificate’s expiration date, App Services renews/rotates the certificate. This is managed by Azure and doesn't require this resource to be changed or reprovisioned. It will change the `thumbprint` computed attribute the next time the resource is refreshed after rotation occurs, so keep that in mind if you have any dependencies on this attribute directly.

        ## Import

        App Service Managed Certificates can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/managedCertificate:ManagedCertificate example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/resGroup1/providers/Microsoft.Web/certificates/customhost.contoso.com
        ```

        :param str resource_name: The name of the resource.
        :param ManagedCertificateArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ManagedCertificateArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 custom_hostname_binding_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ManagedCertificateArgs.__new__(ManagedCertificateArgs)

            if custom_hostname_binding_id is None and not opts.urn:
                raise TypeError("Missing required property 'custom_hostname_binding_id'")
            __props__.__dict__["custom_hostname_binding_id"] = custom_hostname_binding_id
            __props__.__dict__["tags"] = tags
            __props__.__dict__["canonical_name"] = None
            __props__.__dict__["expiration_date"] = None
            __props__.__dict__["friendly_name"] = None
            __props__.__dict__["host_names"] = None
            __props__.__dict__["issue_date"] = None
            __props__.__dict__["issuer"] = None
            __props__.__dict__["subject_name"] = None
            __props__.__dict__["thumbprint"] = None
        super(ManagedCertificate, __self__).__init__(
            'azure:appservice/managedCertificate:ManagedCertificate',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            canonical_name: Optional[pulumi.Input[str]] = None,
            custom_hostname_binding_id: Optional[pulumi.Input[str]] = None,
            expiration_date: Optional[pulumi.Input[str]] = None,
            friendly_name: Optional[pulumi.Input[str]] = None,
            host_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            issue_date: Optional[pulumi.Input[str]] = None,
            issuer: Optional[pulumi.Input[str]] = None,
            subject_name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            thumbprint: Optional[pulumi.Input[str]] = None) -> 'ManagedCertificate':
        """
        Get an existing ManagedCertificate resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] canonical_name: The Canonical Name of the Certificate.
        :param pulumi.Input[str] custom_hostname_binding_id: The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        :param pulumi.Input[str] expiration_date: The expiration date of the Certificate.
        :param pulumi.Input[str] friendly_name: The friendly name of the Certificate.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] host_names: The list of Host Names for the Certificate.
        :param pulumi.Input[str] issue_date: The Start date for the Certificate.
        :param pulumi.Input[str] issuer: The issuer of the Certificate.
        :param pulumi.Input[str] subject_name: The Subject Name for the Certificate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags which should be assigned to the App Service Managed Certificate.
        :param pulumi.Input[str] thumbprint: The Certificate Thumbprint.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ManagedCertificateState.__new__(_ManagedCertificateState)

        __props__.__dict__["canonical_name"] = canonical_name
        __props__.__dict__["custom_hostname_binding_id"] = custom_hostname_binding_id
        __props__.__dict__["expiration_date"] = expiration_date
        __props__.__dict__["friendly_name"] = friendly_name
        __props__.__dict__["host_names"] = host_names
        __props__.__dict__["issue_date"] = issue_date
        __props__.__dict__["issuer"] = issuer
        __props__.__dict__["subject_name"] = subject_name
        __props__.__dict__["tags"] = tags
        __props__.__dict__["thumbprint"] = thumbprint
        return ManagedCertificate(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="canonicalName")
    def canonical_name(self) -> pulumi.Output[str]:
        """
        The Canonical Name of the Certificate.
        """
        return pulumi.get(self, "canonical_name")

    @property
    @pulumi.getter(name="customHostnameBindingId")
    def custom_hostname_binding_id(self) -> pulumi.Output[str]:
        """
        The ID of the App Service Custom Hostname Binding for the Certificate. Changing this forces a new App Service Managed Certificate to be created.
        """
        return pulumi.get(self, "custom_hostname_binding_id")

    @property
    @pulumi.getter(name="expirationDate")
    def expiration_date(self) -> pulumi.Output[str]:
        """
        The expiration date of the Certificate.
        """
        return pulumi.get(self, "expiration_date")

    @property
    @pulumi.getter(name="friendlyName")
    def friendly_name(self) -> pulumi.Output[str]:
        """
        The friendly name of the Certificate.
        """
        return pulumi.get(self, "friendly_name")

    @property
    @pulumi.getter(name="hostNames")
    def host_names(self) -> pulumi.Output[Sequence[str]]:
        """
        The list of Host Names for the Certificate.
        """
        return pulumi.get(self, "host_names")

    @property
    @pulumi.getter(name="issueDate")
    def issue_date(self) -> pulumi.Output[str]:
        """
        The Start date for the Certificate.
        """
        return pulumi.get(self, "issue_date")

    @property
    @pulumi.getter
    def issuer(self) -> pulumi.Output[str]:
        """
        The issuer of the Certificate.
        """
        return pulumi.get(self, "issuer")

    @property
    @pulumi.getter(name="subjectName")
    def subject_name(self) -> pulumi.Output[str]:
        """
        The Subject Name for the Certificate.
        """
        return pulumi.get(self, "subject_name")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags which should be assigned to the App Service Managed Certificate.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter
    def thumbprint(self) -> pulumi.Output[str]:
        """
        The Certificate Thumbprint.
        """
        return pulumi.get(self, "thumbprint")

