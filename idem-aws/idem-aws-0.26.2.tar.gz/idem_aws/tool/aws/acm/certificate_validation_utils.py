def validation_rec(hub, validation_rec_fqdns, certificate):
    """
    Implement additional sanity checks for all FQDNs
    Args:
        hub:
        validation_rec_fqdns(List): List of FQDNs that implement the validation.
        certificate(Dict): Certificate obtained from describe.

    Returns:
        {"result": True|False, "comment": "A tuple"}

    """
    resource_id = certificate.get("resource_id")
    expected_fqdns = {}
    ret = dict(result=True, comment=())
    if not certificate.get("DomainValidationOptions"):
        ret["comment"] = (f"domain_validation_options empty for {resource_id}",)
        ret["result"] = False
        return ret
    for validation_option in certificate.get("DomainValidationOptions"):
        if (
            validation_option.get("ValidationMethod")
            and validation_option.get("ValidationMethod")
            != hub.states.aws.acm.certificate_validation.DNS
        ):
            hub.log.debug("validation_record_fqdns is only valid for DNS validation")
            ret["comment"] = ret["comment"] + (
                "validation_record_fqdns is only valid for DNS validation",
            )
            ret["result"] = False
            return ret
        if validation_option.get("ResourceRecord") and validation_option.get(
            "ResourceRecord"
        ).get("Name"):
            new_expected_fqdn = (
                validation_option.get("ResourceRecord").get("Name").rstrip(".")
            )
            expected_fqdns[new_expected_fqdn] = validation_option
    for v in validation_rec_fqdns:
        expected_fqdns.pop(v.rstrip("."))
    if expected_fqdns:
        for expected_fqdn in expected_fqdns:
            hub.log.debug(
                f"missing DNS validation record {expected_fqdns.get(expected_fqdn).get('DomainName')} : {expected_fqdn}"
            )
            ret["comment"] = ret["comment"] + (
                f"missing DNS validation record {expected_fqdns.get(expected_fqdn).get('DomainName')} : {expected_fqdn}",
            )
        ret["result"] = False
    return ret


def extract_validation_method(hub, certificate):
    validation_method = None
    if certificate.get("DomainValidationOptions"):
        for validation_option in certificate.get("DomainValidationOptions"):
            if "ValidationMethod" in validation_option:
                validation_method = validation_option.get("ValidationMethod")
                return validation_method
    return validation_method
