data_model={
    'trcasein':{
        'service_in':'Page1/PersonalDetails/ServiceIn/ServiceIn',
        "original_entry_date":"Page3/ComingIntoCda/OrigEntry/DateLastEntry",
        "original_entry_place":"Page3/ComingIntoCda/OrigEntry/Place",
        "original_purpose":"Page3/ComingIntoCda/PurposeOfVisit/PurposeOfVisit",
        "original_other_reason":"Page3/ComingIntoCda/PurposeOfVisit/Other",
        "most_recent_entry_date":"Page3/ComingIntoCda/RecentEntry/DateLastEntry",
        "most_recent_entry_place":"Page3/ComingIntoCda/RecentEntry/Place",
        "doc_number":"Page3/ComingIntoCda/PrevDocNum/docNum",
        "is_spouse_canadian":"Page1/MaritalStatus/d/SpouseStatus",
        "submission_date":"Page4/Signature/C1CertificateIssueDate",
        "consent_of_info_release":"Page4/Signature/FutureComm"
    },
    "spincanada":{
        "application_purpose1":"Page1/PersonalDetails/ApplyingFor/RestoreStat",
        "application_purpose2":"Page1/PersonalDetails/ApplyingFor/Extend",
        "application_purpose3":"Page1/PersonalDetails/ApplyingFor/TRP",
        "apply_work_permit":"Page3/WorkPermit/a/WorkPermit",
        "work_permit_type":"Page3/WorkPermit/PermitType",
        "caq_number":"Page3/CAQ/CertNum",
        "expiry_date":"Page3/CAQ/CertExpiry",
        "school_name":"Page3/DetailsOfStudy/SchoolDetails/SchoolName",
        "study_level":"Page3/DetailsOfStudy/SchoolDetails/StudyMajor/Level",
        "study_field":"Page3/DetailsOfStudy/SchoolDetails/StudyMajor/Program",
        "province":"Page3/DetailsOfStudy/SchoolDetails/Prov",
        "city":"Page3/DetailsOfStudy/SchoolDetails/CityTown",
        "address":"Page3/DetailsOfStudy/SchoolDetails/Address",
        "dli":"Page3/DetailsOfStudy/SchoolDetails/DLI",
        "student_id":"Page3/DetailsOfStudy/SchoolDetails/StudentNo",
        "duration_from":"Page3/DetailsOfStudy/SchoolDetails/StudyTerm/FromDate",
        "duration_to":"Page3/DetailsOfStudy/SchoolDetails/StudyTerm/ToDate",
        "tuition_cost":"Page3/DetailsOfStudy/SchoolDetails/EduCosts/Tuition",
        "room_cost":"Page3/DetailsOfStudy/SchoolDetails/EduCosts/Room",
        "other_cost":"Page3/DetailsOfStudy/SchoolDetails/EduCosts/OtherCosts",
        "fund_available":"Page3/DetailsOfStudy/SchoolDetails/Funds/FundsAvail",
        "paid_person":"Page3/DetailsOfStudy/SchoolDetails/Funds/ExpPaidBy",
        "other":"Page3/DetailsOfStudy/SchoolDetails/Funds/Other"
    },
    'personal':{
        'uci':"Page1/PersonalDetails/ServiceIn/UCIClientID",
        'last_name':"Page1/PersonalDetails/Name/FamilyName",
        'first_name':"Page1/PersonalDetails/Name/GivenName",
        'has_alias_name':"Page1/PersonalDetails/AliasName/AliasNameIndicator/AliasNameIndicator",
        'used_last_name':"Page1/PersonalDetails/AliasName/AliasFamilyName",
        'used_first_name':"Page1/PersonalDetails/AliasName/AliasGivenName",
        'sex':"Page1/PersonalDetails/q3-4-5/sex/Sex",
        'dob_year':"Page1/PersonalDetails/q3-4-5/dob/DOBYear",
        'dob_month':"Page1/PersonalDetails/q3-4-5/dob/DOBMonth",
        'dob_day':"Page1/PersonalDetails/q3-4-5/dob/DOBDay",
        'place_of_birth':"Page1/PersonalDetails/q3-4-5/pob/PlaceBirthCity",
        'country_of_birth':"Page1/PersonalDetails/q3-4-5/pob/PlaceBirthCountry",
        'citizen':"Page1/PersonalDetails/Citizenship/Citizenship",
        "native_language":"Page2/Languages/nativeLang",
        "english_french":"Page2/Languages/communicateLang",
        "which_one_better":"Page2/Languages/FreqLang",
        "language_test":"Page2/Languages/LangTestIndicator",
        "email":"Page2/ContactInformation/q5-6/Email/Email"
    },
    #country of residence: current and past for over 6 months. table model
    'cor':{
        'current_cor_country':"Page1/PersonalDetails/CurrentCOR/CurrentCOR/Row2/Country",
        'current_cor_status':"Page1/PersonalDetails/CurrentCOR/CurrentCOR/Row2/Status",
        'current_cor_other':"Page1/PersonalDetails/CurrentCOR/CurrentCOR/Row2/Other",
        'current_cor_start_date':"Page1/PersonalDetails/CurrentCOR/CurrentCOR/Row2/FromDate",
        'current_cor_end_date':"Page1/PersonalDetails/CurrentCOR/CurrentCOR/Row2/ToDate",
        "previous_cor_country1":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row2/Country",
        "previous_cor_status1":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row2/Status",
        "previous_cor_other1":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row2/Other",
        "previous_cor_start_date1":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row2/FromDate",
        "previous_cor_end_date1":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row2/ToDate",
        "previous_cor_country2":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row3/Country",
        "previous_cor_status2":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row3/Status",
        "previous_cor_other2":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row3/Other",
        "previous_cor_start_date2":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row3/FromDate",
        "previous_cor_end_date2":"Page1/PersonalDetails/PrevCOR/PreviousCOR/Row3/ToDate"
    },

    # marriage
    'marriage':{
        "marital_status":"Page1/MaritalStatus/Current/MaritalStatus",
        "married_date":"Page1/MaritalStatus/Current/b/DateOfMarriage",
        "sp_last_name":"Page1/MaritalStatus/Current/c/FamilyName",
        "sp_first_name":"Page1/MaritalStatus/Current/c/GivenName",
        "previous_married":"Page2/MaritalStatus/PrevMarriage/PrevMarriedIndicator",
        "pre_sp_last_name":"Page2/MaritalStatus/PrevMarriage/PMFamilyName",
        "pre_sp_first_name":"Page2/MaritalStatus/PrevMarriage/PMGivenName",
        "pre_relationship_type":"Page2/MaritalStatus/PrevMarriage/TypeOfRelationship",
        "pre_sp_dob_year":"Page2/MaritalStatus/PrevMarriage/dob/DOBYear",
        "pre_sp_dob_month":"Page2/MaritalStatus/PrevMarriage/dob/DOBMonth",
        "pre_sp_dob_day":"Page2/MaritalStatus/PrevMarriage/dob/DOBDay",
        "pre_start_date":"Page2/MaritalStatus/PrevMarriage/From/FromDate",
        "pre_end_date":"Page2/MaritalStatus/PrevMarriage/To/ToDate"
    },

    'passport':{
        "number":"Page2/Passport/PassportNum",
        "country":"Page2/Passport/CountryofIssue",
        "issue_date":"Page2/Passport/IssueDate",
        "expiry_date":"Page2/Passport/ExpiryDate"
    },
    'national_id':{
        "has_id":"Page2/natID/q1/natIDIndicator",
        "number":"Page2/natID/natIDdocs/DocNum/DocNum",
        "country":"Page2/natID/natIDdocs/CountryofIssue/CountryofIssue",
        "issue_date":"Page2/natID/natIDdocs/IssueDate/IssueDate",
        "expiry_date":"Page2/natID/natIDdocs/ExpiryDate"
    },
    'us_pr':{
        "has_id":"Page2/USCard/q1/usCardIndicator",
        "number":"Page2/USCard/usCarddocs/DocNum/DocNum",
        "expiry_date":"Page2/USCard/usCarddocs/ExpiryDate"
    },

    'mailing_address':{
        'po_box':"Page2/ContactInformation/Mailing/AddrLine1/POBox",
        'unit':"Page2/ContactInformation/Mailing/AddrLine1/AptUnit",
        'street_number':"Page2/ContactInformation/Mailing/AddrLine1/StreetNum",
        'street_name':"Page2/ContactInformation/Mailing/AddrLine1/Streetname",
        'city':"Page2/ContactInformation/Mailing/AddrLine2/City",
        'country':"Page2/ContactInformation/Mailing/AddrLine2/Country",
        'province':"Page2/ContactInformation/Mailing/AddrLine2/Prov",
        'post_code':"Page2/ContactInformation/Mailing/AddrLine2/PostalCode",
        'district':"Page2/ContactInformation/Mailing/AddrLine2/District"
    },

    'residential_address':{
        'same_as_mailing':"Page2/ContactInformation/Resi/SameAsAddr/SameAsMailingInd",
        'unit':"Page2/ContactInformation/Resi/AddrLine1/AptUnit",
        'street_number':"Page2/ContactInformation/Resi/AddrLine1/StreetNum",
        'street_name':"Page2/ContactInformation/Resi/AddrLine1/Streetname",
        'city':"Page2/ContactInformation/Resi/AddrLine2/City",
        'country':"Page2/ContactInformation/Resi/AddrLine2/Country",
        'province':"Page2/ContactInformation/Resi/AddrLine2/Prov",
        'post_code':"Page2/ContactInformation/Resi/AddrLine2/PostalCode",
        'district':"Page2/ContactInformation/Resi/AddrLine2/District"
    },

    'phone':{
        "variable_type":"Page2/ContactInformation/q3-4/Phone/Type",
        "canada_us":"Page2/ContactInformation/q3-4/Phone/CanOtherInd/CanadaUS",
        "other":"Page2/ContactInformation/q3-4/Phone/CanOtherInd/Other",
        'ext':"Page2/ContactInformation/q3-4/Phone/NumberExt",
        'country_code':"Page2/ContactInformation/q3-4/Phone/NumberCountry",
        'number':"Page2/ContactInformation/q3-4/Phone/ActualNumber",
        'na_area':"Page2/ContactInformation/q3-4/Phone/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/q3-4/Phone/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/q3-4/Phone/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/q3-4/Phone/IntlNumber/IntlNumber"
    },

    'altphone':{
        "variable_type":"Page2/ContactInformation/q3-4/AltPhone/Type",
        "canada_us":"Page2/ContactInformation/q3-4/AltPhone/CanOtherInd/CanadaUS",
        "other":"Page2/ContactInformation/q3-4/AltPhone/CanOtherInd/Other",
        'ext':"Page2/ContactInformation/q3-4/AltPhone/NumberExt",
        'country_code':"Page2/ContactInformation/q3-4/AltPhone/NumberCountry",
        'number':"Page2/ContactInformation/q3-4/AltPhone/ActualNumber",
        'na_area':"Page2/ContactInformation/q3-4/AltPhone/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/q3-4/AltPhone/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/q3-4/AltPhone/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/q3-4/AltPhone/IntlNumber/IntlNumber"
    },

    'fax':{
        "canada_us":"Page2/ContactInformation/q5-6/Fax/CanOtherInd/CanadaUS",
        "other":"Page2/ContactInformation/q5-6/Fax/CanOtherInd/Other",
        'ext':"Page2/ContactInformation/q5-6/Fax/NumberExt",
        'country_code':"Page2/ContactInformation/q5-6/Fax/NumberCountry",
        'number':"Page2/ContactInformation/q5-6/Fax/ActualNumber",
        'na_area':"Page2/ContactInformation/q5-6/Fax/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/q5-6/Fax/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/q5-6/Fax/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/q5-6/Fax/IntlNumber/IntlNumber"
    },

    'education':{
        "start_date_year":"Page3/Education/EduLine1/From/YYYY",
        "start_date_month":"Page3/Education/EduLine1/From/MM",
        "end_date_year":"Page3/Education/EduLine2/To/YYYY",
        "end_date_month":"Page3/Education/EduLine2/To/MM",
        "school_name":"Page3/Education/EduLine1/School",
        "field_of_study":"Page3/Education/EduLine1/FieldOfStudy",
        "city":"Page3/Education/EduLine2/City",
        "country":"Page3/Education/EduLine2/Country",
        "province":"Page3/Education/EduLine2/Prov"
    },
    # occupation is a special dict, and will be handled seperately
    'occupation':{
        "start_date_year":"Line1/From/YYYY",
        "start_date_month":"Line1/From/MM",
        "end_date_year":"Line2/To/YYYY",
        "end_date_month":"Line2/To/MM",
        "job_title":"Line1/Occupation",
        "company":"Line1/Employer",
        "city":"Line2/City",
        "province":"Line2/ProvState",
        "country":"Line2/Country"
    },

    'trbackground':{
        "q1a":"Page4/BackgroundInfo/HealthQ/qANY",
        "q1b":"Page4/BackgroundInfo/HealthQ/qBNY",
        "q1c":"Page4/BackgroundInfo/HealthQ/MedicalDetails",
        "q2a":"Page4/BackgroundInfo/PrevApplied/qANY",
        "q2b":"Page4/BackgroundInfo/PrevApplied/qBNY",
        "q2c":"Page4/BackgroundInfo/PrevApplied/qCNY",
        "q2d":"Page4/BackgroundInfo/PrevApplied/refusedDetails",
        "q3a":"Page4/BackgroundInfo/Criminal/qANY",
        "q3b":"Page4/BackgroundInfo/Criminal/refusedDetails",
        "q4a":"Page4/BackgroundInfo/Military/qANY",
        "q4b":"Page4/BackgroundInfo/Military/militaryServiceDetails",
        "q5":"Page4/BackgroundInfo/GovPosition/qGovtNY",
        "q6":"Page4/BackgroundInfo/Illtreatment/qWitnessNY"
    }
}

convert_model = {
    "country_pairs": {
        "trcase": ["applying_country"],
        "personal": ['country_of_birth', 'citizen'],
        'passport': ['country'],
        'national_id': ['country'],
        'education': ['country'],
        'cor': ['current_cor_country', 'previous_cor_country1', 'previous_cor_country2']
    },
    'canada_province_pairs': {
        'spincanada': ["province"],
        'address': ['province'],
        'education': ['province'],
        'employment': ['province']
    },
    'language_pairs': {
        'personal': ['native_language']
    },
    'phone_type_pairs': {
        'phone': ["variable_type"],
        'altphone': ["variable_type"]
    },

    'tr_form_study_level_pairs': {
        'spincanada': ["study_level"]
    },
    'tr_form_study_field_pairs': {
        'spincanada': ["study_field"]
    },

    'tr_canada_status_pairs': {
        'cor': ['current_cor_status', 'previous_cor_status1', 'previous_cor_status2']
    },
    'tr_marital_status_pairs': {
        'marriage': ['marital_status', 'pre_relationship_type']
    }
}

remove_model = {
    'personal': ['dob_year', 'dob_month', 'dob_day'],
    'marriage': ['pre_sp_dob_year', 'pre_sp_dob_month', 'pre_sp_dob_day']
}
