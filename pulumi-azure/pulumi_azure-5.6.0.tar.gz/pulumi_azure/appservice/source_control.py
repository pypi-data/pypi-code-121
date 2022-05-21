# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['SourceControlArgs', 'SourceControl']

@pulumi.input_type
class SourceControlArgs:
    def __init__(__self__, *,
                 app_id: pulumi.Input[str],
                 branch: Optional[pulumi.Input[str]] = None,
                 github_action_configuration: Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']] = None,
                 repo_url: Optional[pulumi.Input[str]] = None,
                 rollback_enabled: Optional[pulumi.Input[bool]] = None,
                 use_local_git: Optional[pulumi.Input[bool]] = None,
                 use_manual_integration: Optional[pulumi.Input[bool]] = None,
                 use_mercurial: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a SourceControl resource.
        :param pulumi.Input[str] app_id: The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        :param pulumi.Input[str] branch: The branch name to use for deployments. Changing this forces a new resource to be created.
        :param pulumi.Input['SourceControlGithubActionConfigurationArgs'] github_action_configuration: A `github_action_configuration` block as defined below.
        :param pulumi.Input[str] repo_url: The URL for the repository. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] rollback_enabled: Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_local_git: Should the App use local Git configuration. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_manual_integration: Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_mercurial: The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        """
        pulumi.set(__self__, "app_id", app_id)
        if branch is not None:
            pulumi.set(__self__, "branch", branch)
        if github_action_configuration is not None:
            pulumi.set(__self__, "github_action_configuration", github_action_configuration)
        if repo_url is not None:
            pulumi.set(__self__, "repo_url", repo_url)
        if rollback_enabled is not None:
            pulumi.set(__self__, "rollback_enabled", rollback_enabled)
        if use_local_git is not None:
            pulumi.set(__self__, "use_local_git", use_local_git)
        if use_manual_integration is not None:
            pulumi.set(__self__, "use_manual_integration", use_manual_integration)
        if use_mercurial is not None:
            pulumi.set(__self__, "use_mercurial", use_mercurial)

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> pulumi.Input[str]:
        """
        The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "app_id")

    @app_id.setter
    def app_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "app_id", value)

    @property
    @pulumi.getter
    def branch(self) -> Optional[pulumi.Input[str]]:
        """
        The branch name to use for deployments. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "branch")

    @branch.setter
    def branch(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "branch", value)

    @property
    @pulumi.getter(name="githubActionConfiguration")
    def github_action_configuration(self) -> Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']]:
        """
        A `github_action_configuration` block as defined below.
        """
        return pulumi.get(self, "github_action_configuration")

    @github_action_configuration.setter
    def github_action_configuration(self, value: Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']]):
        pulumi.set(self, "github_action_configuration", value)

    @property
    @pulumi.getter(name="repoUrl")
    def repo_url(self) -> Optional[pulumi.Input[str]]:
        """
        The URL for the repository. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "repo_url")

    @repo_url.setter
    def repo_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repo_url", value)

    @property
    @pulumi.getter(name="rollbackEnabled")
    def rollback_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "rollback_enabled")

    @rollback_enabled.setter
    def rollback_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "rollback_enabled", value)

    @property
    @pulumi.getter(name="useLocalGit")
    def use_local_git(self) -> Optional[pulumi.Input[bool]]:
        """
        Should the App use local Git configuration. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_local_git")

    @use_local_git.setter
    def use_local_git(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_local_git", value)

    @property
    @pulumi.getter(name="useManualIntegration")
    def use_manual_integration(self) -> Optional[pulumi.Input[bool]]:
        """
        Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_manual_integration")

    @use_manual_integration.setter
    def use_manual_integration(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_manual_integration", value)

    @property
    @pulumi.getter(name="useMercurial")
    def use_mercurial(self) -> Optional[pulumi.Input[bool]]:
        """
        The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_mercurial")

    @use_mercurial.setter
    def use_mercurial(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_mercurial", value)


@pulumi.input_type
class _SourceControlState:
    def __init__(__self__, *,
                 app_id: Optional[pulumi.Input[str]] = None,
                 branch: Optional[pulumi.Input[str]] = None,
                 github_action_configuration: Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']] = None,
                 repo_url: Optional[pulumi.Input[str]] = None,
                 rollback_enabled: Optional[pulumi.Input[bool]] = None,
                 scm_type: Optional[pulumi.Input[str]] = None,
                 use_local_git: Optional[pulumi.Input[bool]] = None,
                 use_manual_integration: Optional[pulumi.Input[bool]] = None,
                 use_mercurial: Optional[pulumi.Input[bool]] = None,
                 uses_github_action: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering SourceControl resources.
        :param pulumi.Input[str] app_id: The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        :param pulumi.Input[str] branch: The branch name to use for deployments. Changing this forces a new resource to be created.
        :param pulumi.Input['SourceControlGithubActionConfigurationArgs'] github_action_configuration: A `github_action_configuration` block as defined below.
        :param pulumi.Input[str] repo_url: The URL for the repository. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] rollback_enabled: Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] scm_type: The SCM Type in use. This value is decoded by the service from the repository information supplied.
        :param pulumi.Input[bool] use_local_git: Should the App use local Git configuration. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_manual_integration: Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_mercurial: The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] uses_github_action: Indicates if the Slot uses a GitHub action for deployment. This value is decoded by the service from the repository information supplied.
        """
        if app_id is not None:
            pulumi.set(__self__, "app_id", app_id)
        if branch is not None:
            pulumi.set(__self__, "branch", branch)
        if github_action_configuration is not None:
            pulumi.set(__self__, "github_action_configuration", github_action_configuration)
        if repo_url is not None:
            pulumi.set(__self__, "repo_url", repo_url)
        if rollback_enabled is not None:
            pulumi.set(__self__, "rollback_enabled", rollback_enabled)
        if scm_type is not None:
            pulumi.set(__self__, "scm_type", scm_type)
        if use_local_git is not None:
            pulumi.set(__self__, "use_local_git", use_local_git)
        if use_manual_integration is not None:
            pulumi.set(__self__, "use_manual_integration", use_manual_integration)
        if use_mercurial is not None:
            pulumi.set(__self__, "use_mercurial", use_mercurial)
        if uses_github_action is not None:
            pulumi.set(__self__, "uses_github_action", uses_github_action)

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "app_id")

    @app_id.setter
    def app_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_id", value)

    @property
    @pulumi.getter
    def branch(self) -> Optional[pulumi.Input[str]]:
        """
        The branch name to use for deployments. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "branch")

    @branch.setter
    def branch(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "branch", value)

    @property
    @pulumi.getter(name="githubActionConfiguration")
    def github_action_configuration(self) -> Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']]:
        """
        A `github_action_configuration` block as defined below.
        """
        return pulumi.get(self, "github_action_configuration")

    @github_action_configuration.setter
    def github_action_configuration(self, value: Optional[pulumi.Input['SourceControlGithubActionConfigurationArgs']]):
        pulumi.set(self, "github_action_configuration", value)

    @property
    @pulumi.getter(name="repoUrl")
    def repo_url(self) -> Optional[pulumi.Input[str]]:
        """
        The URL for the repository. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "repo_url")

    @repo_url.setter
    def repo_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repo_url", value)

    @property
    @pulumi.getter(name="rollbackEnabled")
    def rollback_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "rollback_enabled")

    @rollback_enabled.setter
    def rollback_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "rollback_enabled", value)

    @property
    @pulumi.getter(name="scmType")
    def scm_type(self) -> Optional[pulumi.Input[str]]:
        """
        The SCM Type in use. This value is decoded by the service from the repository information supplied.
        """
        return pulumi.get(self, "scm_type")

    @scm_type.setter
    def scm_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "scm_type", value)

    @property
    @pulumi.getter(name="useLocalGit")
    def use_local_git(self) -> Optional[pulumi.Input[bool]]:
        """
        Should the App use local Git configuration. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_local_git")

    @use_local_git.setter
    def use_local_git(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_local_git", value)

    @property
    @pulumi.getter(name="useManualIntegration")
    def use_manual_integration(self) -> Optional[pulumi.Input[bool]]:
        """
        Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_manual_integration")

    @use_manual_integration.setter
    def use_manual_integration(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_manual_integration", value)

    @property
    @pulumi.getter(name="useMercurial")
    def use_mercurial(self) -> Optional[pulumi.Input[bool]]:
        """
        The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_mercurial")

    @use_mercurial.setter
    def use_mercurial(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_mercurial", value)

    @property
    @pulumi.getter(name="usesGithubAction")
    def uses_github_action(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if the Slot uses a GitHub action for deployment. This value is decoded by the service from the repository information supplied.
        """
        return pulumi.get(self, "uses_github_action")

    @uses_github_action.setter
    def uses_github_action(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "uses_github_action", value)


class SourceControl(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_id: Optional[pulumi.Input[str]] = None,
                 branch: Optional[pulumi.Input[str]] = None,
                 github_action_configuration: Optional[pulumi.Input[pulumi.InputType['SourceControlGithubActionConfigurationArgs']]] = None,
                 repo_url: Optional[pulumi.Input[str]] = None,
                 rollback_enabled: Optional[pulumi.Input[bool]] = None,
                 use_local_git: Optional[pulumi.Input[bool]] = None,
                 use_manual_integration: Optional[pulumi.Input[bool]] = None,
                 use_mercurial: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        Manages an App Service Web App or Function App Source Control Configuration.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_service_plan = azure.appservice.ServicePlan("exampleServicePlan",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            os_type="Linux",
            sku_name="P1v2")
        example_linux_web_app = azure.appservice.LinuxWebApp("exampleLinuxWebApp",
            resource_group_name=example_resource_group.name,
            location=example_service_plan.location,
            service_plan_id=example_service_plan.id,
            site_config=azure.appservice.LinuxWebAppSiteConfigArgs())
        example_source_control = azure.appservice.SourceControl("exampleSourceControl",
            app_id=example_linux_web_app.id,
            repo_url="https://github.com/Azure-Samples/python-docs-hello-world",
            branch="master")
        ```

        ## Import

        App Service Source Controls can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/sourceControl:SourceControl example /subscriptions/12345678-1234-9876-4563-123456789012/resourceGroups/resGroup1/providers/Microsoft.Web/sites/site1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] app_id: The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        :param pulumi.Input[str] branch: The branch name to use for deployments. Changing this forces a new resource to be created.
        :param pulumi.Input[pulumi.InputType['SourceControlGithubActionConfigurationArgs']] github_action_configuration: A `github_action_configuration` block as defined below.
        :param pulumi.Input[str] repo_url: The URL for the repository. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] rollback_enabled: Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_local_git: Should the App use local Git configuration. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_manual_integration: Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_mercurial: The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SourceControlArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an App Service Web App or Function App Source Control Configuration.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_service_plan = azure.appservice.ServicePlan("exampleServicePlan",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            os_type="Linux",
            sku_name="P1v2")
        example_linux_web_app = azure.appservice.LinuxWebApp("exampleLinuxWebApp",
            resource_group_name=example_resource_group.name,
            location=example_service_plan.location,
            service_plan_id=example_service_plan.id,
            site_config=azure.appservice.LinuxWebAppSiteConfigArgs())
        example_source_control = azure.appservice.SourceControl("exampleSourceControl",
            app_id=example_linux_web_app.id,
            repo_url="https://github.com/Azure-Samples/python-docs-hello-world",
            branch="master")
        ```

        ## Import

        App Service Source Controls can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appservice/sourceControl:SourceControl example /subscriptions/12345678-1234-9876-4563-123456789012/resourceGroups/resGroup1/providers/Microsoft.Web/sites/site1
        ```

        :param str resource_name: The name of the resource.
        :param SourceControlArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SourceControlArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_id: Optional[pulumi.Input[str]] = None,
                 branch: Optional[pulumi.Input[str]] = None,
                 github_action_configuration: Optional[pulumi.Input[pulumi.InputType['SourceControlGithubActionConfigurationArgs']]] = None,
                 repo_url: Optional[pulumi.Input[str]] = None,
                 rollback_enabled: Optional[pulumi.Input[bool]] = None,
                 use_local_git: Optional[pulumi.Input[bool]] = None,
                 use_manual_integration: Optional[pulumi.Input[bool]] = None,
                 use_mercurial: Optional[pulumi.Input[bool]] = None,
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
            __props__ = SourceControlArgs.__new__(SourceControlArgs)

            if app_id is None and not opts.urn:
                raise TypeError("Missing required property 'app_id'")
            __props__.__dict__["app_id"] = app_id
            __props__.__dict__["branch"] = branch
            __props__.__dict__["github_action_configuration"] = github_action_configuration
            __props__.__dict__["repo_url"] = repo_url
            __props__.__dict__["rollback_enabled"] = rollback_enabled
            __props__.__dict__["use_local_git"] = use_local_git
            __props__.__dict__["use_manual_integration"] = use_manual_integration
            __props__.__dict__["use_mercurial"] = use_mercurial
            __props__.__dict__["scm_type"] = None
            __props__.__dict__["uses_github_action"] = None
        super(SourceControl, __self__).__init__(
            'azure:appservice/sourceControl:SourceControl',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            app_id: Optional[pulumi.Input[str]] = None,
            branch: Optional[pulumi.Input[str]] = None,
            github_action_configuration: Optional[pulumi.Input[pulumi.InputType['SourceControlGithubActionConfigurationArgs']]] = None,
            repo_url: Optional[pulumi.Input[str]] = None,
            rollback_enabled: Optional[pulumi.Input[bool]] = None,
            scm_type: Optional[pulumi.Input[str]] = None,
            use_local_git: Optional[pulumi.Input[bool]] = None,
            use_manual_integration: Optional[pulumi.Input[bool]] = None,
            use_mercurial: Optional[pulumi.Input[bool]] = None,
            uses_github_action: Optional[pulumi.Input[bool]] = None) -> 'SourceControl':
        """
        Get an existing SourceControl resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] app_id: The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        :param pulumi.Input[str] branch: The branch name to use for deployments. Changing this forces a new resource to be created.
        :param pulumi.Input[pulumi.InputType['SourceControlGithubActionConfigurationArgs']] github_action_configuration: A `github_action_configuration` block as defined below.
        :param pulumi.Input[str] repo_url: The URL for the repository. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] rollback_enabled: Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] scm_type: The SCM Type in use. This value is decoded by the service from the repository information supplied.
        :param pulumi.Input[bool] use_local_git: Should the App use local Git configuration. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_manual_integration: Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] use_mercurial: The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] uses_github_action: Indicates if the Slot uses a GitHub action for deployment. This value is decoded by the service from the repository information supplied.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SourceControlState.__new__(_SourceControlState)

        __props__.__dict__["app_id"] = app_id
        __props__.__dict__["branch"] = branch
        __props__.__dict__["github_action_configuration"] = github_action_configuration
        __props__.__dict__["repo_url"] = repo_url
        __props__.__dict__["rollback_enabled"] = rollback_enabled
        __props__.__dict__["scm_type"] = scm_type
        __props__.__dict__["use_local_git"] = use_local_git
        __props__.__dict__["use_manual_integration"] = use_manual_integration
        __props__.__dict__["use_mercurial"] = use_mercurial
        __props__.__dict__["uses_github_action"] = uses_github_action
        return SourceControl(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> pulumi.Output[str]:
        """
        The ID of the Windows or Linux Web App. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "app_id")

    @property
    @pulumi.getter
    def branch(self) -> pulumi.Output[str]:
        """
        The branch name to use for deployments. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "branch")

    @property
    @pulumi.getter(name="githubActionConfiguration")
    def github_action_configuration(self) -> pulumi.Output[Optional['outputs.SourceControlGithubActionConfiguration']]:
        """
        A `github_action_configuration` block as defined below.
        """
        return pulumi.get(self, "github_action_configuration")

    @property
    @pulumi.getter(name="repoUrl")
    def repo_url(self) -> pulumi.Output[str]:
        """
        The URL for the repository. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "repo_url")

    @property
    @pulumi.getter(name="rollbackEnabled")
    def rollback_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Should the Deployment Rollback be enabled? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "rollback_enabled")

    @property
    @pulumi.getter(name="scmType")
    def scm_type(self) -> pulumi.Output[str]:
        """
        The SCM Type in use. This value is decoded by the service from the repository information supplied.
        """
        return pulumi.get(self, "scm_type")

    @property
    @pulumi.getter(name="useLocalGit")
    def use_local_git(self) -> pulumi.Output[Optional[bool]]:
        """
        Should the App use local Git configuration. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_local_git")

    @property
    @pulumi.getter(name="useManualIntegration")
    def use_manual_integration(self) -> pulumi.Output[Optional[bool]]:
        """
        Should code be deployed manually. Set to `false` to enable continuous integration, such as webhooks into online repos such as GitHub. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_manual_integration")

    @property
    @pulumi.getter(name="useMercurial")
    def use_mercurial(self) -> pulumi.Output[Optional[bool]]:
        """
        The repository specified is Mercurial. Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "use_mercurial")

    @property
    @pulumi.getter(name="usesGithubAction")
    def uses_github_action(self) -> pulumi.Output[bool]:
        """
        Indicates if the Slot uses a GitHub action for deployment. This value is decoded by the service from the repository information supplied.
        """
        return pulumi.get(self, "uses_github_action")

