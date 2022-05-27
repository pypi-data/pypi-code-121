from collections import OrderedDict
from typing import Any
from typing import Dict


async def convert_raw_acm_to_present(
    hub,
    ctx,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    result = dict(comment=(), result=True, ret=None)
    resource_id = raw_resource.get("CertificateArn")
    resource_parameters = OrderedDict(
        {
            "DomainName": "domain_name",
            "CertificateAuthorityArn": "certificate_authority_arn",
            "Status": "status",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    domain_validation_options_list = []
    # Creating domain_validation_options_list_validation list for Certificate Validation
    domain_validation_options_list_validation = []
    validation_option_list = OrderedDict(
        {
            "DomainName": "domain_name",
            "ValidationDomain": "validation_domain",
        }
    )
    if raw_resource.get("DomainValidationOptions"):
        for validation_option in raw_resource.get("DomainValidationOptions"):
            validation_option_dict = {}
            validation_option_dict_validation = {}
            for option_raw, option_present in validation_option_list.items():
                if option_raw in validation_option:
                    validation_option_dict[option_present] = validation_option.get(
                        option_raw
                    )
                    validation_option_dict_validation[
                        option_present
                    ] = validation_option.get(option_raw)

            domain_validation_options_list.append(validation_option_dict)
            if (
                not "validation_method" in resource_translated
                and "ValidationMethod" in validation_option
            ):
                resource_translated["validation_method"] = validation_option.get(
                    "ValidationMethod"
                )

            if "ResourceRecord" in validation_option:
                validation_option_dict_validation[
                    "resource_record"
                ] = validation_option.get("ResourceRecord")
            if (
                "ValidationEmails" in validation_option
                and len(validation_option.get("ValidationEmails")) > 0
            ):
                validation_option_dict_validation[
                    "validation_emails"
                ] = validation_option.get("ValidationEmails")
            if "ValidationStatus" in validation_option:
                validation_option_dict_validation[
                    "validation_status"
                ] = validation_option.get("ValidationStatus")
            domain_validation_options_list_validation.append(
                validation_option_dict_validation
            )

        resource_translated[
            "domain_validation_options"
        ] = domain_validation_options_list
        resource_translated[
            "domain_validation_options_validation"
        ] = domain_validation_options_list_validation
    if "Options" in raw_resource:
        resource_translated["options"] = {
            "CertificateTransparencyLoggingPreference": str(
                raw_resource.get("Options").get(
                    "CertificateTransparencyLoggingPreference"
                )
            )
        }

    # Cleanup SubjectAlternativeNames(As it can contain primary domain names also, so no need to keep in SubjectAlternativeNames)
    resource_translated["subject_alternative_names"] = list(
        filter(
            (raw_resource.get("DomainName")).__ne__,
            raw_resource.get("SubjectAlternativeNames"),
        )
    )
    tags = await hub.exec.boto3.client.acm.list_tags_for_certificate(
        ctx, CertificateArn=resource_id
    )
    result["result"] = tags["result"]
    if tags["result"] and tags.get("ret"):
        resource_translated["tags"] = tags["ret"]["Tags"]
    if not tags["result"]:
        result["comment"] = result["comment"] + tags["comment"]
    result["ret"] = resource_translated
    return result


def convert_raw_acm_validation_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    result = dict(comment=(), result=True, ret=None)

    certificate_arn = raw_resource.get("CertificateArn")
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": certificate_arn,
        "certificate_arn": certificate_arn,
    }
    if raw_resource.get("DomainValidationOptions"):
        validation_record_fqdns = []
        for option in raw_resource.get("DomainValidationOptions"):
            if option.get("ResourceRecord"):
                if option.get("ResourceRecord").get("Name"):
                    validation_record_fqdns.append(
                        option.get("ResourceRecord").get("Name")
                    )
        resource_translated["validation_record_fqdns"] = validation_record_fqdns

    result["ret"] = resource_translated
    return result
