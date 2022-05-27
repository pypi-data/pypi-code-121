import copy
from typing import Any
from typing import Dict
from typing import List


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    url: str,
    thumbprint_list: List,
    resource_id: str = None,
    client_id_list: List = None,
    tags: List = None,
) -> Dict[str, Any]:
    r"""
    Creates an IAM entity to describe an identity provider (IdP) that supports OpenID Connect (OIDC).

    The OIDC provider that you create with this operation can be used as a principal in a role's trust policy.
    Such a policy establishes a trust relationship between Amazon Web Services and the OIDC provider.

    If you are using an OIDC identity provider from Google, Facebook, or Amazon Cognito, you don't need to create a
    separate IAM identity provider. These OIDC identity providers are already built-in to Amazon Web Services and are
    available for your use. Instead, you can move directly to creating new roles using your identity provider. To learn
    more, see Creating a role for web identity or OpenID connect federation in the IAM User Guide.

    When you create the IAM OIDC provider, you specify the following:
        * The URL of the OIDC identity provider (IdP) to trust
        * A list of client IDs (also known as audiences) that identify the application or applications allowed to
          authenticate using the OIDC provider.
        * A list of thumbprints of one or more server certificates that the IdP uses

    You get all of this information from the OIDC IdP you want to use to access Amazon Web Services.

    Args:
        name(Text): The idem name for IAM OIDC provider.

        url(Text): The URL of the identity provider. The URL must begin with https:// and should correspond to the iss
            claim in the provider's OpenID Connect ID tokens. Per the OIDC standard, path components are allowed but
            query parameters are not. Typically the URL consists of only a hostname, like https://server.example.org or
            https://example.com . The URL should not contain a port number.

            You cannot register the same provider multiple times in a single Amazon Web Services account. If you try to
            submit a URL that has already been used for an OpenID Connect provider in the Amazon Web Services account,
            you will get an error.

        thumbprint_list(List): A list of server certificate thumbprints for the OpenID Connect (OIDC) identity
            provider's server certificates. Typically this list includes only one entry. However, IAM lets you have up
            to five thumbprints for an OIDC provider. This lets you maintain multiple thumbprints if the identity
            provider is rotating certificates.

            The server certificate thumbprint is the hex-encoded SHA-1 hash value of the X.509 certificate used by the
            domain where the OpenID Connect provider makes its keys available. It is always a 40-character string.

            You must provide at least one thumbprint when creating an IAM OIDC provider. For example, assume that the
            OIDC provider is server.example.com and the provider stores its keys at
            https://keys.server.example.com/openid-connect. In that case, the thumbprint string would be the hex-encoded
             SHA-1 hash value of the certificate used by https://keys.server.example.com.

            For more information about obtaining the OIDC provider thumbprint, see Obtaining the thumbprint for an
            OpenID Connect provider in the IAM User Guide .

            (string) --
                Contains a thumbprint for an identity provider's server certificate.

                The identity provider's server certificate thumbprint is the hex-encoded SHA-1 hash value of the
                self-signed X.509 certificate. This thumbprint is used by the domain where the OpenID Connect provider
                makes its keys available. The thumbprint is always a 40-character string.

        resource_id(Text, optional): The Amazon Resource Name (ARN) of the IAM OpenID Connect provider resource object.

        client_id_list(List, optional): Provides a list of client IDs, also known as audiences. When a mobile or web
            app registers with an OpenID Connect provider, they establish a value that identifies the application. This
            is the value that's sent as the client_id parameter on OAuth requests.

            You can register multiple client IDs with the same provider. For example, you might have multiple
            applications that use the same OIDC provider. You cannot register more than 100 client IDs with a single
            IAM OIDC provider.

            There is no defined format for a client ID. The CreateOpenIDConnectProviderRequest operation accepts
            client IDs up to 255 characters long.

        tags(List, optional): A list of tags that you want to attach to the new IAM OpenID Connect (OIDC) provider.
            Each tag consists of a key name and an associated value. For more information about tagging, see Tagging
            IAM resources in the IAM User Guide .

            (dict) --
                A structure that represents user-provided metadata that can be associated with an IAM resource.
                For more information about tagging, see Tagging IAM resources in the IAM User Guide .

                Key (string)
                The key name that can be used to look up or retrieve the associated value. For example, Department or
                Cost Center are common choices.

                Value (string)
                The value associated with this tag. For example, tags with a key name of Department could have values
                such as Human Resources , Accounting , and Support . Tags with a key name of Cost Center might have
                values that consist of the number associated with the different cost centers in your company. Typically,
                 many resources have tags with the same key name but with different values.

    Request Syntax:
        [oidc-resource-name]:
          aws.iam.open_id_connect_provider.present:
          - name: 'string'
          - resource_id: 'string'
          - url: 'string'
          - client_id_list:
            - 'string'
          - thumbprint_list:
            - 'string'
          - tags:
            - Key: 'string'
              Value: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            oidcprovider-1:
              aws.iam.open_id_connect_provider.present:
              - name: oidcprovider-1
              - url: https://abc.example.com
              - client_id_list:
                - acd.amazonaws.com
                - xyz.com
              - thumbprint_list:
                - 9e99a48a9960b14926bb7f3b02e22da2b0ab7402
              - tags:
                - Key: Name
                  Value: oidc-name
                - Key: env
                  Value: dev

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False
    plan_state = None

    if resource_id:
        response = await hub.exec.boto3.client.iam.get_open_id_connect_provider(
            ctx, OpenIDConnectProviderArn=resource_id
        )
        if not response["result"]:
            result["comment"] = response["comment"]
            result["result"] = response["result"]
            return result
        before = response["ret"]

    if before:
        try:
            result[
                "old_state"
            ] = hub.tool.aws.iam.conversion_utils.convert_raw_oidc_provider_to_present(
                raw_resource=before, idem_resource_name=name, resource_id=resource_id
            )
            plan_state = copy.deepcopy(result["old_state"])

            # update clientIDs
            if client_id_list is not None:
                update_ret = (
                    await hub.exec.aws.iam.open_id_connect_provider.update_client_ids(
                        ctx=ctx,
                        resource_id=resource_id,
                        old_client_ids=result["old_state"].get("client_id_list", []),
                        new_client_ids=client_id_list,
                    )
                )
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = result["result"] and update_ret["result"]
                resource_updated = resource_updated or bool(update_ret["ret"])
                if ctx.get("test", False) and update_ret["ret"] is not None:
                    plan_state["client_id_list"] = update_ret["ret"].get(
                        "client_id_list"
                    )
                if not result["result"]:
                    return result

            # update thumbprints
            if (
                thumbprint_list is not None
                and not hub.tool.aws.state_comparison_utils.are_lists_identical(
                    result["old_state"].get("thumbprint_list"), thumbprint_list
                )
            ):
                update_ret = (
                    await hub.exec.aws.iam.open_id_connect_provider.update_thumbprints(
                        ctx=ctx,
                        resource_id=resource_id,
                        old_thumbprints=result["old_state"].get("thumbprint_list"),
                        new_thumbprints=thumbprint_list,
                    )
                )
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = result["result"] and update_ret["result"]
                resource_updated = resource_updated or bool(update_ret["ret"])
                if ctx.get("test", False) and update_ret["ret"] is not None:
                    plan_state["thumbprint_list"] = update_ret["ret"].get(
                        "thumbprint_list"
                    )
                if not result["result"]:
                    return result

            # update tags
            if tags is not None:
                update_ret = (
                    await hub.exec.aws.iam.open_id_connect_provider.update_tags(
                        ctx=ctx,
                        resource_id=resource_id,
                        old_tags=result["old_state"].get("tags"),
                        new_tags=tags,
                    )
                )
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = result["result"] and update_ret["result"]
                resource_updated = resource_updated or bool(update_ret["ret"])
                if ctx.get("test", False) and update_ret["ret"] is not None:
                    plan_state["tags"] = update_ret["ret"].get("tags")
                if not result["result"]:
                    return result
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "url": url,
                    "client_id_list": client_id_list,
                    "thumbprint_list": thumbprint_list,
                    "tags": tags,
                },
            )
            result["comment"] = (
                f"Would create aws.iam.open_id_connect_provider '{name}'",
            )
            return result

        try:
            ret = await hub.exec.boto3.client.iam.create_open_id_connect_provider(
                ctx,
                Url=url,
                ClientIDList=client_id_list,
                ThumbprintList=thumbprint_list,
                Tags=tags,
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = (f"Created '{name}'",)
            resource_id = ret["ret"]["OpenIDConnectProviderArn"]
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            after = await hub.exec.boto3.client.iam.get_open_id_connect_provider(
                ctx, OpenIDConnectProviderArn=resource_id
            )
            result[
                "new_state"
            ] = hub.tool.aws.iam.conversion_utils.convert_raw_oidc_provider_to_present(
                raw_resource=after["ret"],
                idem_resource_name=name,
                resource_id=resource_id,
            )
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False

    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    """
    Deletes an OpenID Connect identity provider (IdP) resource object in IAM.
    Deleting an IAM OIDC provider resource does not update any roles that reference the provider as a principal in their
    trust policies. Any attempt to assume a role that references a deleted provider fails.

    Args:
        name(Text): The idem name for IAM OIDC provider.
        resource_id(Text): The Amazon Resource Name (ARN) of the IAM OpenID Connect provider resource object to delete.

    Request Syntax:
        [oidc-resource-id]:
          aws.iam.open_id_connect_provider.absent:
          - name: 'string'
          - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            oidc-provider-1:
              aws.iam.open_id_connect_provider.absent:
                - name: oidc-provider-1
                - resource_id: arn:aws:iam::565284315989:oidc-provider/test.example.com

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.iam.open_id_connect_provider", name=name
        )
        return result
    before = await hub.exec.boto3.client.iam.get_open_id_connect_provider(
        ctx, OpenIDConnectProviderArn=resource_id
    )

    if not before["ret"]:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.iam.open_id_connect_provider", name=name
        )
    elif ctx.get("test", False):
        result[
            "old_state"
        ] = hub.tool.aws.iam.conversion_utils.convert_raw_oidc_provider_to_present(
            raw_resource=before["ret"], idem_resource_name=name, resource_id=resource_id
        )
        result["comment"] = (f"Would delete aws.iam.open_id_connect_provider '{name}'",)
        return result
    else:
        result[
            "old_state"
        ] = hub.tool.aws.iam.conversion_utils.convert_raw_oidc_provider_to_present(
            raw_resource=before["ret"], idem_resource_name=name, resource_id=resource_id
        )
        try:
            ret = await hub.exec.boto3.client.iam.delete_open_id_connect_provider(
                ctx, OpenIDConnectProviderArn=resource_id
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
            result["comment"] = (f"Deleted '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Gets information about the AWS IAM OpenID Connect provider

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.iam.open_id_connect_provider

    """
    result = {}
    ret = await hub.exec.boto3.client.iam.list_open_id_connect_providers(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe open id connect providers {ret['comment']}")
        return {}

    for provider in ret["ret"]["OpenIDConnectProviderList"]:
        resource_id = provider.get("Arn")
        connect_provider_resp = (
            await hub.exec.boto3.client.iam.get_open_id_connect_provider(
                ctx, OpenIDConnectProviderArn=resource_id
            )
        )
        if not connect_provider_resp["result"]:
            hub.log.warning(
                f"Failed on fetching open_id_connect_provider with arn {resource_id} "
                f"with error {connect_provider_resp['comment']}. Describe will skip this open_id_connect_provider and continue."
            )
            continue

        resource_translated = (
            hub.tool.aws.iam.conversion_utils.convert_raw_oidc_provider_to_present(
                raw_resource=connect_provider_resp["ret"],
                idem_resource_name=resource_id,
                resource_id=resource_id,
            )
        )

        result[resource_id] = {
            "aws.iam.open_id_connect_provider.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }
    return result
