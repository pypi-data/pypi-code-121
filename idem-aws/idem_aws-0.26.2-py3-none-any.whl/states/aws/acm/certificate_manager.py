"""
hub.exec.boto3.client.acm.import_certificate
hub.exec.boto3.client.acm.request_certificate
hub.exec.boto3.client.acm.describe_certificate
"""
import copy
from typing import Any
from typing import Dict
from typing import List


__contracts__ = ["resource"]
__reconcile_wait__ = {"static": {"wait_in_seconds": 60}}

acceptors = [
    {
        "matcher": "error",
        "expected": "ResourceNotFoundException",
        "state": "retry",
        "argument": "Error.Code",
    },
    {
        "matcher": "path",
        "expected": "ISSUED",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "PENDING_VALIDATION",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "FAILED",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "VALIDATION_TIMED_OUT",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "INACTIVE",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "EXPIRED",
        "state": "success",
        "argument": "Certificate.Status",
    },
    {
        "matcher": "path",
        "expected": "REVOKED",
        "state": "success",
        "argument": "Certificate.Status",
    },
]


async def present(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    certificate_arn: str = None,
    certificate: str = None,
    private_key: str = None,
    certificate_chain: str = None,
    domain_name: str = None,
    validation_method: str = None,
    subject_alternative_names: List = None,
    idempotency_token: str = None,
    domain_validation_options: List = None,
    options: {} = None,
    certificate_authority_arn: str = None,
    timeout: Dict = None,
    tags: List = None,
) -> Dict[str, Any]:
    r"""

    You can use ACM to manage SSL/TLS certificates for your AWS-based websites and applications.
    Imports a certificate into AWS Certificate Manager (ACM) to use with services that are integrated with ACM.
    Note that integrated services allow only certificate types and keys they support to be associated with their
    resources. Further, their support differs depending on whether the certificate is imported into IAM or into ACM.
    Requests an ACM certificate for use with other AWS services. To request an ACM certificate, you must specify a
    fully qualified domain name (FQDN) in the DomainName parameter. You can also specify additional FQDNs in the
    SubjectAlternativeNames parameter.
    If you are requesting a private certificate, domain validation is not required. If you are requesting a public
    certificate, each domain name that you specify must be validated to verify that you own or control the domain.
    You can use DNS validation or email validation.

    Args:
        name(Text): An Idem name of the resource.
        resource_id(Text, optional): The Amazon Resource Name (ARN) of certificate to identify the resource.
        certificate_arn(Text, optional): The Amazon Resource Name (ARN) of an imported certificate to replace.
            To import a new certificate, omit this field.
        certificate(Bytes, optional): The certificate to import.
        private_key(Bytes, optional): The private key that matches the public key in the certificate.
        certificate_chain(Bytes, optional): The PEM encoded certificate chain.

        domain_name(Text, optional): Fully qualified domain name (FQDN), such as www.example.com, that you want to
            secure with an ACM certificate.,
        validation_method(Text, optional): The method you want to use if you are requesting a public certificate to
            validate that you own or control domain.,
        subject_alternative_names(List, optional): Additional FQDNs to be included in the Subject Alternative Name
            extension of the ACM certificate.,
        idempotency_token(Text,Optional): Customer chosen string that can be used to distinguish between calls to
            RequestCertificate .,
        domain_validation_options(List, optional): The domain name that you want ACM to use to send you emails so that
            you can validate domain ownership.,
        options(Dict): to specify whether to add the certificate to a certificate transparency log. Certificate
            transparency makes it possible to detect SSL/TLS certificates that have been mistakenly or maliciously issued.,
        certificate_authority_arn(Text, optional): The Amazon Resource Name (ARN) of the private certificate authority
            (CA) that will be used to issue the certificate.,
        tags(List, optional): One or more resource tags to associate with the certificate.
            * Key (Text) --  The key of the tag.
            * Value (Text) -- The value of the tag.
        timeout(Dict, optional): Timeout configuration for request/import AWS Certificate.
            * create (Dict) -- Timeout configuration for request/imporng AWS Certificate
                * delay -- The amount of time in seconds to wait between attempts.
                * max_attempts -- Customized timeout configuration containing delay and max attempts.



    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls
            (For requesting a certificate: )
            [name]
              aws.acm.certificate_manager.present:
              - domain_name: www.example.com
              - validation_method: DNS
              - subject_alternative_names:
                  - www.example.net
              - idempotency_token: ExampleIdempotancyToken
              - domain_validation_options:
                  - domain_name: testing.example.com
                  - validation_domain: example.com
              - options:
                  - certificate_transparency_loggingPreference: DISABLED
              - certificate_authority_arn: arn:aws:acm-pca:region:account:certificate-authority/12345678-1234-1234-1234-123456789012
              - tags:
                  - Key: class
                    Value: test

            (For importing a certificate: )
            [name]
              aws.acm.certificate_manager.present:
              - resource_id: arn:aws:acm-pca:region:account:certificate-authority/12345678-1234-1234-1234-123456789012
              - certificate_arn: arn:aws:acm-pca:region:account:certificate-authority/12345678-1234-1234-1234-123456789012
              - certificate: example_certificate
              - private_key: -----BEGIN RSA PRIVATE KEY-----
                  MIIEpQIBAAKCAQEA3Tz2mr7SZiAMfQyuvBjM9Oi..Z1BjP5CE/Wm/Rr500P
                  RK+Lh9x5eJPo5CAZ3/ANBE0sTK0ZsDGMak2m1g7..3VHqIxFTz0Ta1d+NAj
                  -----END RSA PRIVATE KEY-----
              - certificate_chain: example_certificate_chain
              - tags:
                  - Key: class
                    Value: test


    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    if resource_id:
        before = await hub.exec.boto3.client.acm.describe_certificate(
            ctx, CertificateArn=resource_id
        )

    are_tags_updated = False
    is_reimported = False
    old_tag_list = None
    if before and before["result"]:
        try:
            convert_ret = (
                await hub.tool.aws.acm.conversion_utils.convert_raw_acm_to_present(
                    ctx,
                    raw_resource=before["ret"].get("Certificate"),
                    idem_resource_name=resource_id,
                )
            )
            result["result"] = convert_ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + convert_ret["comment"]
            result["old_state"] = convert_ret.get("ret")
            old_tag_list = result["old_state"].get("tags")
            plan_state = copy.deepcopy(result["old_state"])

            # Reimport certificate if certificate arn,private key and certificate body is given as input
            # In Idem we cannot check if these properties are changed because they are not retrievable from other APIs
            # We cannot provide tags when reimporting a certificate.
            if private_key and certificate:
                re_imported = await hub.exec.boto3.client.acm.import_certificate(
                    ctx=ctx,
                    CertificateArn=resource_id,
                    Certificate=certificate,
                    PrivateKey=private_key,
                    CertificateChain=certificate_chain,
                )
                result["result"] = re_imported["result"]
                if not result["result"]:
                    result["comment"] = re_imported["comment"]
                    return result
                is_reimported = re_imported["result"]
                result["comment"] = result["comment"] + (
                    f"Re-Imported aws.acm.certificate_manager '{name}'",
                )
                if ctx.get("test", False) and is_reimported:
                    plan_state["private_key"] = private_key
                    plan_state["certificate"] = certificate
                    if certificate_chain:
                        plan_state["certificate_chain"] = certificate_chain
                    result["comment"] = result["comment"] + (
                        f"Would reimport certificate for aws.acm.certificate_manager {name}",
                    )
            if (
                tags is not None
                and not hub.tool.aws.state_comparison_utils.are_lists_identical(
                    tags, old_tag_list
                )
            ):
                update_tags_ret = await hub.exec.aws.acm.tag.update_tags(
                    ctx=ctx,
                    resource_id=resource_id,
                    old_tags=old_tag_list,
                    new_tags=tags,
                )
                if not update_tags_ret["result"]:
                    result["comment"] = result["comment"] + update_tags_ret["comment"]
                    result["result"] = False
                    return result
                are_tags_updated = bool(update_tags_ret["ret"])
                if ctx.get("test", False) and are_tags_updated:
                    plan_state["tags"] = update_tags_ret["ret"].get("tags")
                    result["comment"] = result["comment"] + (
                        f"Would update tags for aws.acm.certificate_manager {name}",
                    )
                elif are_tags_updated:
                    result["comment"] = result["comment"] + (
                        f"Updated tags for aws.acm.certificate_manager '{name}'",
                    )
            if not are_tags_updated and not is_reimported:
                result["comment"] = result["comment"] + (
                    f"aws.acm.certificate_manager '{name}' has no property that needs to be updated",
                )
        except Exception as e:
            result["comment"] = result["comment"] + (str(e),)
            result["result"] = False
    else:
        # If private key is provided as an input then certificate needs to be imported
        # To import new certificate, CertificateArn should not be provided
        if private_key:
            try:
                if ctx.get("test", False):
                    result[
                        "new_state"
                    ] = hub.tool.aws.test_state_utils.generate_test_state(
                        enforced_state={},
                        desired_state={
                            "name": name,
                            "certificate": certificate,
                            "private_key": private_key,
                            "certificate_chain": certificate_chain,
                            "tags": tags,
                        },
                    )
                    result["comment"] = result["comment"] + (
                        f"Would import aws.acm.certificate_manager {name}",
                    )
                    return result
                imported = await hub.exec.boto3.client.acm.import_certificate(
                    ctx=ctx,
                    Certificate=certificate,
                    PrivateKey=private_key,
                    CertificateChain=certificate_chain,
                    Tags=tags,
                )
                result["result"] = imported["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + imported["comment"]
                    return result

                resource_id = imported["ret"]["CertificateArn"]

                # Custom waiter for import
                # When the certificate is just created, there is a delay of several seconds before we can retrieve information about it.
                waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                    default_delay=10,
                    default_max_attempts=6,
                    timeout_config=timeout.get("create") if timeout else None,
                )
                certificate_waiter = hub.tool.boto3.custom_waiter.waiter_wrapper(
                    name="CertificateCreated",
                    operation="DescribeCertificate",
                    argument=["Error.Code", "Certificate.Status"],
                    acceptors=acceptors,
                    client=hub.tool.boto3.client.get_client(ctx, "acm"),
                )
                await hub.tool.boto3.client.wait(
                    ctx,
                    "acm",
                    "CertificateCreated",
                    certificate_waiter,
                    CertificateArn=resource_id,
                    WaiterConfig=waiter_config,
                )

                result["comment"] = result["comment"] + (
                    f"Imported aws.acm.certificate_manager '{name}'",
                )

            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
        # If domain name is provided as an input then certificate needs to be requested/created
        elif domain_name:
            try:
                if ctx.get("test", False):
                    result[
                        "new_state"
                    ] = hub.tool.aws.test_state_utils.generate_test_state(
                        enforced_state={},
                        desired_state={
                            "name": name,
                            "domain_name": domain_name,
                            "validation_method": validation_method,
                            "subject_alternative_names": subject_alternative_names,
                            "idempotency_token": idempotency_token,
                            "domain_validation_options": domain_validation_options,
                            "options": options,
                            "certificate_authority_arn": certificate_authority_arn,
                            "tags": tags,
                        },
                    )
                    result["comment"] = result[
                        "comment"
                    ] + hub.tool.aws.comment_utils.would_create_comment(
                        resource_type="aws.acm.certificate_manager", name=name
                    )
                    return result

                requested = await hub.exec.boto3.client.acm.request_certificate(
                    ctx=ctx,
                    DomainName=domain_name,
                    ValidationMethod=validation_method,
                    SubjectAlternativeNames=subject_alternative_names,
                    IdempotencyToken=idempotency_token,
                    DomainValidationOptions=domain_validation_options,
                    Options=options,
                    CertificateAuthorityArn=certificate_authority_arn,
                    Tags=tags,
                )
                result["result"] = requested["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + requested["comment"]
                    return result
                resource_id = requested["ret"]["CertificateArn"]

                # Custom waiter for request
                # When the certificate is just created, there is a delay of several seconds before we can retrieve information about it.
                waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                    default_delay=10,
                    default_max_attempts=6,
                    timeout_config=timeout.get("create") if timeout else None,
                )
                certificate_waiter = hub.tool.boto3.custom_waiter.waiter_wrapper(
                    name="CertificateCreated",
                    operation="DescribeCertificate",
                    argument=["Error.Code", "Certificate.Status"],
                    acceptors=acceptors,
                    client=hub.tool.boto3.client.get_client(ctx, "acm"),
                )
                await hub.tool.boto3.client.wait(
                    ctx,
                    "acm",
                    "CertificateCreated",
                    certificate_waiter,
                    CertificateArn=resource_id,
                    WaiterConfig=waiter_config,
                )

                result["comment"] = result[
                    "comment"
                ] + hub.tool.aws.comment_utils.create_comment(
                    resource_type="aws.acm.certificate_manager", name=name
                )

            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
                return result
        # If neither of private key and domain name is provided
        else:
            hub.log.debug(
                "AWS Certificate must be imported (private_key) or created (domain_name)"
            )
            result["comment"] = (
                "AWS Certificate must be imported (private_key) or created (domain_name)",
            )
            result["result"] = False
            return result
    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif not (before and before["result"]) or are_tags_updated or is_reimported:
            after = await hub.exec.boto3.client.acm.describe_certificate(
                ctx, CertificateArn=resource_id
            )
            if after and after.get("ret"):
                convert_ret = (
                    await hub.tool.aws.acm.conversion_utils.convert_raw_acm_to_present(
                        ctx,
                        raw_resource=after["ret"].get("Certificate"),
                        idem_resource_name=resource_id,
                    )
                )
                result["result"] = convert_ret["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + convert_ret["comment"]
                result["new_state"] = convert_ret["ret"]
            else:
                result["result"] = result["result"] and after["result"]
                if not result["result"]:
                    result["comment"] = result["comment"] + after["comment"]
                    return result
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])

    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    r"""

    Deletes a certificate and its associated private key. If this action succeeds, the certificate no longer appears in
    the list that can be displayed by calling the ListCertificates action or be retrieved by calling the GetCertificate
    action. The certificate will not be available for use by Amazon Web Services services integrated with ACM.

    Args:
        name(Text): An Idem name of the resource.
        resource_id(Text, optional): The Amazon Resource Name (ARN) of certificate to identify the resource.
    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.acm.certificate.absent:
                - name: value
                - resource_id: value
    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.acm.certificate_manager", name=name
        )
        return result
    before = await hub.exec.boto3.client.acm.describe_certificate(
        ctx, CertificateArn=resource_id
    )
    if not before["result"]:
        if "ResourceNotFoundException" in str(before["comment"]):
            result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
                resource_type="aws.acm.certificate_manager", name=name
            )
        else:
            result["comment"] = before["comment"]
            result["result"] = False
        return result
    if not (before["ret"].get("Certificate")):
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.acm.certificate_manager", name=name
        )
        return result
    else:
        convert_ret = (
            await hub.tool.aws.acm.conversion_utils.convert_raw_acm_to_present(
                ctx,
                raw_resource=before["ret"].get("Certificate"),
                idem_resource_name=resource_id,
            )
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
        result["old_state"] = convert_ret["ret"]
        if ctx.get("test", False):
            result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
                resource_type="aws.acm.certificate_manager", name=name
            )
            return result
        else:
            ret = await hub.exec.boto3.client.acm.delete_certificate(
                ctx, CertificateArn=resource_id
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = hub.tool.aws.comment_utils.delete_comment(
                resource_type="aws.acm.certificate_manager", name=name
            )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Returns detailed metadata about the specified ACM certificate.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.acm.certificate
    """
    result = {}
    certificate_list_ret = await hub.exec.boto3.client.acm.list_certificates(
        ctx,
        Includes={
            "keyTypes": [
                "RSA_1024",
                "RSA_2048",
                "RSA_3072",
                "RSA_4096",
                "EC_prime256v1",
                "EC_secp384r1",
                "EC_secp521r1",
            ]
        },
    )
    if not certificate_list_ret["result"]:
        hub.log.debug(
            f"Could not list AWS Certificates {certificate_list_ret['comment']}"
        )
        return {}
    certificate_list = certificate_list_ret["ret"].get("CertificateSummaryList")

    for certificate in certificate_list:

        resource_id = certificate.get("CertificateArn")
        ret = await hub.exec.boto3.client.acm.describe_certificate(
            ctx, CertificateArn=resource_id
        )
        if not ret["result"]:
            hub.log.debug(
                f"Could not describe AWS Certificate '{resource_id}' {ret['comment']}"
            )
            continue

        resource = ret["ret"].get("Certificate")

        convert_ret = (
            await hub.tool.aws.acm.conversion_utils.convert_raw_acm_to_present(
                ctx,
                raw_resource=resource,
                idem_resource_name=resource_id,
            )
        )
        if not convert_ret["result"]:
            hub.log.debug(
                f"Could not describe AWS Certificate '{resource_id}' {convert_ret['comment']}"
            )
            continue
        resource_translated = convert_ret.get("ret")
        result[resource_id] = {
            "aws.acm.certificate_manager.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }

    return result


def is_pending(hub, ret):
    new_state = ret.get("new_state", None)
    resource_id = new_state.get("resource_id") if new_state else None
    status = None
    state_list = []
    if new_state:
        domain_validation_options_validation = new_state.get(
            "domain_validation_options_validation"
        )
        for domain_validation_option in domain_validation_options_validation:
            status = domain_validation_option.get("validation_status")
            if not status:
                hub.log.debug(
                    f"Asynchronous ACM service domain validation assignment not complete, need to retry {new_state}"
                )
                return True
            elif status and isinstance(status, str):
                hub.log.debug(
                    f"ACM certificate {resource_id} is_pending() status {status}"
                )
                if status.casefold() == "success" or status.casefold() == "failed":
                    hub.log.debug(
                        f"No need to reconcile new state {new_state} with status {status}"
                    )
                    state_list.append(False)
                if status.casefold() == "pending_validation":
                    hub.log.debug(
                        f"Reconcile new state {new_state} with status {status}"
                    )
                    state_list.append(True)
            resource_record = domain_validation_option.get("resource_record")
            if not resource_record:
                state_list.append(True)
        # Returns true if any of the domain validation options need to be reconciled
        return any(state_list)
    return (not ret["result"]) or (bool(ret["changes"]))
