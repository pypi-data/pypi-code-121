from nubium_schemas.people_stream.hash_fields import eloqua_person_mask


expected_eloqua_person_mask = {
    "last_evaluated_by_dwm": True,
    "last_submission": {
        "campaign_response_metadata": {
            "ext_tactic_id": False,
            "int_tactic_id": False,
            "is_lead_activity": False,
            "offer_consumption_timestamp": False,
            "offer_id": False,
        },
        "location": {
            "city_from_ip": False,
            "country_from_dns": True,
            "country_from_ip": True,
            "postal_code_from_ip": False,
            "state_province_from_ip": False,
        },
        "opt_in": {"f_formdata_optin": False, "f_formdata_optin_phone": False, "f_formdata_sharetopartner": False},
        "submission_date": False,
        "submission_source": False,
    },
    "marketing_descriptors": {
        "lead_score": {
            "mlsm": {
                "all_scores": True,
                "interest_level": True,
                "lead_ranking": True,
                "lead_rating": True,
                "qualification_level": True,
            }
        },
        "penalty_box_expiration": True,
        "penalty_box_reason": False,
        "persona": True,
        "sub_region": True,
        "super_region": True,
        "provisional_account_match": True,
    },
    "personal_facts": {
        "address": {
            "address_city": True,
            "address_postal_code": True,
            "address_state_province": True,
            "address_street_1": True,
            "address_street_2": True,
            "address_street_3": True,
            "combined_statistical_area": True,
            "core_based_statistical_area": True,
            "country_code": True,
            "country_name": True,
        },
        "email_address": True,
        "first_name": True,
        "is_a_test_contact": False,
        "is_bounceback": True,
        "job": {
            "annual_revenue": True,
            "business_phone": True,
            "company": True,
            "company_size": True,
            "department": True,
            "fax_number": True,
            "industry": True,
            "job_function": True,
            "job_level": True,
            "job_role": True,
            "job_title": True,
        },
        "language_preference": True,
        "last_name": True,
        "middle_name": True,
        "mobile_phone": True,
        "salutation": True,
    },
    "privacy": {
        "consent_email_marketing": True,
        "consent_email_marketing_source": False,
        "consent_email_marketing_timestamp": False,
        "consent_phone_marketing": False,
        "consent_phone_marketing_source": False,
        "consent_phone_marketing_timestamp": False,
        "consent_share_to_partner": False,
        "consent_share_to_partner_source": False,
        "consent_share_to_partner_timestamp": False,
    },
    "tombstone": {
        "delete_all_data": False,
        "is_tombstoned": False,
        "tombstone_source": False,
        "tombstone_timestamp": False,
    },
    "tracking_ids": False,
}


def test_bool_hash_dict_can_be_generated_from_schema_classes():
    assert eloqua_person_mask == expected_eloqua_person_mask
