yes_no = {"validate": "list", "source": ["Yes", "No"]}
bcpnp_case_stream = {
    "validate": "list",
    "source": (
        [
            "EE-Skilled Worker",
            "EE-International Graduate",
            "EE-International Post-Graduate",
            "EE-Health Authority",
            "Skilled Worker",
            "International Graduate",
            "Entry-Level and Semi-Skilled Worker",
            "International Post-Graduate",
            "Health Authority",
        ]
    ),
}
corporate_structure = {
    "validate": "list",
    "source": [
        "Incorporated",
        "Limited Liability Partnership",
        "Extra-provincially-registered",
        "federally-incorporated",
        "Other",
    ],
}
canada_provinces = {
    "validate": "list",
    "source": [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NS",
        "NT",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ],
}
english_french = {
    "validate": "list",
    "source": ["English", "French", "Both", "Neither"],
}
english_or_french = {"validate": "list", "source": ["English", "French"]}
english_french_chinese = {
    "validate": "list",
    "source": ["Chinese", "English", "French"],
}
imm_status = {
    "validate": "list",
    "source": [
        "Citizen",
        "Permanent Resident",
        "Worker",
        "Student",
        "Visitor",
        "Refugess",
        "Other",
    ],
}

salary_payment_way = {
    "validate": "list",
    "source": ["weekly", "bi-weekly", "semi-monthly", "monthly"],
}
wage_unit = {"validate": "list", "source": ["hourly", "weekly", "monthly", "annually"]}
ot_after_hours_unit = {"validate": "list", "source": ["day", "week"]}
job_duration_unit = {"validate": "list", "source": ["day", "week", "month", "year"]}
purpose_of_lmia = {
    "validate": "list",
    "source": [
        "Support Permanent Resident only",
        "Support Work Permit only",
        "Support both Work Permit and Permanent Resident",
    ],
}
stream_of_lmia = {
    "validate": "list",
    "source": [
        "1. EE(Express Entry: 5593)",
        "2. HWS(High Wage Stream: 5626)",
        "3. LWS(Low Wage Stream: 5627)",
        "4. GTS(Global Talent Stream: 5624, 5625)",
        "5. AC (Academic: 5626)",
        "6. AG (Agriculture: 5519, 5510)",
    ],
}
rent_unit = {"validate": "list", "source": ["week", "month"]}
accommodation_type = {
    "validate": "list",
    "source": ["house", "apartment", "dorm", "other"],
}
sex = {"validate": "list", "source": ["Male", "Female"]}
workpermit_type = {
    "validate": "list",
    "source": [
        "Co-op Work Permit",
        "Exemption from Labour Market Impact Assessment",
        "Labour Market Impact Assessment Stream",
        "Live-in Caregiver Program",
        "Open Work Permit",
        "Open work permit for vulnerable workers",
        "Other",
        "Post Graduation Work Permit",
        "Start-up Business Class",
    ],
}
marital_status = {
    "validate": "list",
    "source": [
        "Annulled Marriage",
        "Common-Law",
        "Divorced",
        "Married",
        "Separated",
        "Single",
        "Unknown",
        "Widowed",
    ],
}
pre_relationship_type = {"validate": "list", "source": ["Common-Law", "Married"]}
language_test_type = {"validate": "list", "source": ["IELTS", "CELPIP", "TEF", "TCF"]}
education_level = {
    "validate": "list",
    "source": [
        "Doctor",
        "Master",
        "Post-graduate diploma",
        "Bachelor",
        "Associate",
        "Diploma/Certificate",
        "High school",
        "Less than high school",
    ],
}
relationship = {
    "validate": "list",
    "source": [
        "Grand Parent",
        "Parent",
        "Spouse",
        "Child",
        "Grand Child",
        "Sibling",
        "Aunt",
        "Uncle",
        "Niece",
        "Newphew",
        "Friend",
    ],
}
family_relationship = {
    "validate": "list",
    "source": ["Spouse", "Son", "Daughter", "Mother", "Father", "Brother", "Sister"],
}
pr_imm_program = {"validate": "list", "source": ["Economic", "Family"]}
pr_imm_category = {
    "validate": "list",
    "source": [
        "Provincial Nominee Program (PNP)",
        "Atlantic Immigration Program",
        "Spouse",
        "Common-law Partner",
        "Dependent Child",
        "Other Relative",
    ],
}
pr_imm_under = {
    "validate": "list",
    "source": [
        "Spouse or common-law partner in Canada class",
        "Family class (outside Canada)",
    ],
}
interview_canadian_status = {
    "validate": "list",
    "source": ["Citizen", "PR", "Foreigner", "Unknown"],
}
tr_application_purpose = {
    "validate": "list",
    "source": ["apply or extend", "restore status", "TRP"],
}
sp_paid_person = {"validate": "list", "source": ["Myself", "Parents", "Other"]}
vr_application_purpose = {
    "validate": "list",
    "source": ["apply or extend visitor record", "restore status as visotor", "TRP"],
}
sp_in_application_purpose = {
    "validate": "list",
    "source": ["apply or extend study permit", "restore status as student", "TRP"],
}
sp_apply_wp_type = {
    "validate": "list",
    "source": ["Co-op Work Permit", "Open Work Permit", "Post Graduation Work Permit"],
}
wp_in_application_purpose = {
    "validate": "list",
    "source": [
        "apply WP for same employer",
        "apply WP for new employer",
        "restore status as worker",
        "TRP with same employer",
        "TRP with new employer",
    ],
}
wp_apply_wp_type = {
    "validate": "list",
    "source": [
        "Co-op Work Permit",
        "Exemption from Labour Market Impact Assessment",
        "Labour Market Impact Assessment Stream",
        "Live-in Caregiver Program",
        "Open Work Permit",
        "Open Work Permit for Vulnerable Workers",
        "Other",
        "Post Graduation Work Permit",
        "Start-up Business Class",
    ],
}
visa_application_purpose = {"validate": "list", "source": ["Visitor Visa", "Transit"]}
tr_original_purpose = {
    "validate": "list",
    "source": ["Business", "Tourism", "Study", "Work", "Other", "Family Visit"],
}
# Validation data
validation = {
    # BCPNP
    "info-bcpnp": {
        "has_applied_before": yes_no,
        "case_stream": bcpnp_case_stream,
        "q1": yes_no,
        "q2": yes_no,
        "q3": yes_no,
        "q4": yes_no,
        "q5": yes_no,
        "q6": yes_no,
        "q7": yes_no,
    },
    # Employer
    "info-general": {"has_lmia_approved": yes_no},
    "table-eraddress": {"province": canada_provinces},
    "table-contact": {
        "preferred_language": english_french,
        "province": canada_provinces,
    },
    "table-employee_list": {"immigration_status": imm_status},
    "info-position": {
        "worked_working": yes_no,
        "under_cba": yes_no,
        "has_same": yes_no,
        "lmia_refused": yes_no,
    },
    "info-joboffer": {
        "license_request": yes_no,
        "union": yes_no,
        "payment_way": salary_payment_way,
        "wage_unit": wage_unit,
        "ot_after_hours_unit": ot_after_hours_unit,
        "is_working": yes_no,
        "permanent": yes_no,
        "job_duration_unit": job_duration_unit,
        "has_probation": yes_no,
        "disability_insurance": yes_no,
        "dental_insurance": yes_no,
        "empolyer_provided_persion": yes_no,
        "extended_medical_insurance": yes_no,
        "english_french": yes_no,
        "other_language_required": yes_no,
    },
    # LMIA
    "info-general": {
        "has_jobbank_account": yes_no,
        "has_bc_employer_certificate": yes_no,
    },
    "table-employee_list": {"immigration_status": imm_status},
    "info-lmiacase": {
        "is_in_10_days_priority": yes_no,
        "is_waived_from_advertisement": yes_no,
        "purpose_of_lmia": purpose_of_lmia,
        "stream_of_lmia": stream_of_lmia,
        "has_another_employer": yes_no,
        "is_positive_within_2": yes_no,
        "is_recent_positive": yes_no,
        "has_attestation": yes_no,
    },
    "info-lmi": {
        "laid_off_in_12": yes_no,
        "is_work_sharing": yes_no,
        "labour_dispute": yes_no,
    },
    "info-emp5624": {
        "hird_canadian": yes_no,
        "why_not": yes_no,
        "has_active_lmbp": yes_no,
    },
    "info-emp5627": {
        "provide_accommodation": yes_no,
        "rent_unit": rent_unit,
        "accommodation_type": accommodation_type,
    },
    # PA
    "info-personal": {
        "sex": sex,
        "english_french": english_french,
        "which_one_better": english_or_french,
        "language_test": yes_no,
        "did_eca": yes_no,
    },
    "info-status": {
        "current_country_status": imm_status,
        "current_status_type": workpermit_type,
        "has_vr": yes_no,
    },
    "info-marriage": {
        "marital_status": marital_status,
        "sp_in_canada": yes_no,
        "sp_language_type": language_test_type,
        "sp_canada_status": imm_status,
        "previous_married": yes_no,
        "pre_relationship_type": pre_relationship_type,
    },
    "table-assumption": {
        "work_permit_type": workpermit_type,
        "province": canada_provinces,
    },
    "table-language": {"test_type": language_test_type},
    "table-education": {"education_level": education_level, "is_trade": yes_no},
    "table-employment": {"bcpnp_qualified": yes_no, "ee_qualified": yes_no},
    "table-canadarelative": {
        "province": canada_provinces,
        "status": imm_status,
        "relationship": relationship,
    },
    "table-family": {
        "marital_status": marital_status,
        "relationship": family_relationship,
        "accompany_to_canada": yes_no,
    },
    "table-cor": {"status": imm_status},
    # PR
    "info-prcase": {
        "imm_program": pr_imm_program,
        "imm_category": pr_imm_category,
        "imm_under": pr_imm_under,
        "communication_language": english_or_french,
        "interview_language": english_french_chinese,
        "need_translator": yes_no,
        "intended_province": canada_provinces,
        "has_csq": yes_no,
        "consent_of_info_release": yes_no,
    },
    "info-background": {
        "q1a": yes_no,
        "q1b": yes_no,
        "q1c": yes_no,
        "q2a": yes_no,
        "q2b": yes_no,
        "q2c": yes_no,
        "q3a": yes_no,
        "q4a": yes_no,
        "q5": yes_no,
        "q6": yes_no,
    },
    # Recruitment
    "table-interviewrecord": {
        "canadian_status": interview_canadian_status,
        "interviewed": yes_no,
        "offered": yes_no,
        "accepted": yes_no,
    },
    "info-recruitmentsummary": {
        "reply2apply": yes_no,
        "emails_for_making_interview": yes_no,
        "interview_record": yes_no,
        "interview_process_evidence": yes_no,
        "emails_for_certificates": yes_no,
        "emais_for_references": yes_no,
        "reference_checked": yes_no,
        "reference_check_evidence": yes_no,
        "joboffer_email": yes_no,
        "joboffer_email_reply": yes_no,
        "after_offer_coomunication": yes_no,
    },
    # TR
    "info-trcasein": {
        "original_purpose": tr_original_purpose,
        "is_spouse_canadian": yes_no,
        "consent_of_info_release": yes_no,
    },
    "info-trcase": {
        "application_purpose": tr_application_purpose,
        "same_as_cor": yes_no,
        "applying_stauts": imm_status,
    },
    "info-sp": {
        "study_level": education_level,
        "province": canada_provinces,
        "paid_person": sp_paid_person,
    },
    "info-vrincanada": {
        "application_purpose": vr_application_purpose,
    },
    "info-spincanada": {
        "application_purpose": sp_in_application_purpose,
        "study_level": education_level,
        "province": canada_provinces,
        "paid_person": sp_paid_person,
        "apply_work_permit": yes_no,
        "work_permit_type": sp_apply_wp_type,
    },
    "info-wpincanada": {
        "application_purpose": wp_in_application_purpose,
        "work_province": canada_provinces,
        "work_permit_type": wp_apply_wp_type,
    },
    "info-wp": {
        "work_province": canada_provinces,
        "work_permit_type": wp_apply_wp_type,
    },
    "info-visa": {
        "application_purpose": visa_application_purpose,
        "work_province": canada_provinces,
        "work_permit_type": wp_apply_wp_type,
    },
    "info-incanadacommon": {
        "original_purpose": tr_original_purpose,
    },
    "info-trbackground": {
        "q1a": yes_no,
        "q1b": yes_no,
        "q1c": yes_no,
        "q2a": yes_no,
        "q2b": yes_no,
        "q2c": yes_no,
        "q3a": yes_no,
        "q4a": yes_no,
        "q5": yes_no,
        "q6": yes_no,
    },
    # PR
    "info-prbackground": {
        "q1": yes_no,
        "q2": yes_no,
        "q3": yes_no,
        "q4": yes_no,
        "q5": yes_no,
        "q6": yes_no,
        "q7": yes_no,
        "q8": yes_no,
        "q9": yes_no,
        "q10": yes_no,
        "q11": yes_no,
    },
}
