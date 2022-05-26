def migrate(cr, version):
    cr.execute(
        "UPDATE adsl_service_contract_info "
        "SET phone_number = '-' "
        "WHERE phone_number in ('0','_')"
    )
    cr.execute(
        "UPDATE vodafone_fiber_service_contract_info "
        "SET phone_number = '-' "
        "WHERE phone_number in ('0','_')"
    )
    cr.execute(
        "UPDATE mm_fiber_service_contract_info "
        "SET phone_number = '-' "
        "WHERE phone_number in ('0','_')"
    )
    cr.execute(
        "UPDATE contract_contract "
        "SET phone_number='-' "
        "WHERE phone_number in ('0','_')"
    )
    cr.execute(
        "UPDATE contract_contract "
        "SET name = '-' "
        "WHERE name in ('0','_')"
    )
