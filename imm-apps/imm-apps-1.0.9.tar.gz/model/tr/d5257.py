# before '_' is sheet name
# variable as key, xpath of xml as value. 
data_model={
    'trcase':{
        'service_in':'Page1/PersonalDetails/ServiceIn/ServiceIn',
        "application_purpose":"Page1/PersonalDetails/VisaType/VisaType",
        'same_as_cor':"Page1/PersonalDetails/SameAsCORIndicator",
        "applying_country":"Page1/PersonalDetails/CountryWhereApplying/Row2/Country",
        "applying_stauts":"Page1/PersonalDetails/CountryWhereApplying/Row2/Status",
        "applying_start_date":"Page1/PersonalDetails/CountryWhereApplying/Row2/FromDate",
        "applying_end_date":"Page1/PersonalDetails/CountryWhereApplying/Row2/ToDate",
        "consent_of_info_release":"Page3/Signature/Consent0/Choice",
        "submission_date":"Page3/Signature/C1CertificateIssueDate"
    },
    "visa":{
        "visit_purpose":"Page3/DetailsOfVisit/PurposeRow1/PurposeOfVisit/PurposeOfVisit",
        "other":"Page3/DetailsOfVisit/PurposeRow1/Other/Other",
        "duration_from":"Page3/DetailsOfVisit/PurposeRow1/HowLongStay/FromDate",
        "duration_to":"Page3/DetailsOfVisit/PurposeRow1/HowLongStay/ToDate",
        "funds_available":"Page3/DetailsOfVisit/PurposeRow1/Funds/Funds",
        "name1":"Page3/DetailsOfVisit/Contacts_Row1/Name/Name",
        "relationship1":"Page3/DetailsOfVisit/Contacts_Row1/RelationshipToMe/RelationshipToMe",
        "address1":"Page3/DetailsOfVisit/Contacts_Row1/AddressInCanada/AddressInCanada",
        "name2":"Page3/Contacts_Row2/Name/Name",
        "relationship":"Page3/Contacts_Row2/Relationship/RelationshipToMe",
        "address2":"Page3/Contacts_Row2/AddressInCanada/AddressInCanada"
    },
    'personal':{
        'uci':"Page1/PersonalDetails/UCIClientID",
        'last_name':"Page1/PersonalDetails/Name/FamilyName",
        'first_name':"Page1/PersonalDetails/Name/GivenName",
        'has_alias_name':"Page1/PersonalDetails/AliasName/AliasNameIndicator/AliasNameIndicator",
        'used_last_name':"Page1/PersonalDetails/AliasName/AliasFamilyName",
        'used_first_name':"Page1/PersonalDetails/AliasName/AliasGivenName",
        'sex':"Page1/PersonalDetails/Sex/Sex",
        'dob_year':"Page1/PersonalDetails/DOBYear",
        'dob_month':"Page1/PersonalDetails/DOBMonth",
        'dob_day':"Page1/PersonalDetails/DOBDay",
        'place_of_birth':"Page1/PersonalDetails/PlaceBirthCity",
        'country_of_birth':"Page1/PersonalDetails/PlaceBirthCountry",
        'citizen':"Page1/PersonalDetails/Citizenship/Citizenship",
        "native_language":"Page2/MaritalStatus/SectionA/Languages/languages/nativeLang/nativeLang",
        "english_french":"Page2/MaritalStatus/SectionA/Languages/languages/ableToCommunicate/ableToCommunicate",
        "which_one_better":"Page2/MaritalStatus/SectionA/Languages/languages/lov",
        "language_test":"Page2/MaritalStatus/SectionA/Languages/LanguageTest",
        "email":"Page2/ContactInformation/contact/FaxEmail/Email"
    },
    #country of residence: current and past for over 6 months. table model
    'cor':{
        'current_cor_country':"Page1/PersonalDetails/CurrentCOR/Row2/Country",
        'current_cor_status':"Page1/PersonalDetails/CurrentCOR/Row2/Status",
        'current_cor_other':"Page1/PersonalDetails/CurrentCOR/Row2/Other",
        'current_cor_start_date':"Page1/PersonalDetails/CurrentCOR/Row2/FromDate",
        'current_cor_end_date':"Page1/PersonalDetails/CurrentCOR/Row2/ToDate",
        "previous_cor_country1":"Page1/PersonalDetails/PreviousCOR/Row2/Country",
        "previous_cor_status1":"Page1/PersonalDetails/PreviousCOR/Row2/Status",
        "previous_cor_other1":"Page1/PersonalDetails/PreviousCOR/Row2/Other",
        "previous_cor_start_date1":"Page1/PersonalDetails/PreviousCOR/Row2/FromDate",
        "previous_cor_end_date1":"Page1/PersonalDetails/PreviousCOR/Row2/ToDate",
        "previous_cor_country2":"Page1/PersonalDetails/PreviousCOR/Row3/Country",
        "previous_cor_status2":"Page1/PersonalDetails/PreviousCOR/Row3/Status",
        "previous_cor_other2":"Page1/PersonalDetails/PreviousCOR/Row3/Other",
        "previous_cor_start_date2":"Page1/PersonalDetails/PreviousCOR/Row3/FromDate",
        "previous_cor_end_date2":"Page1/PersonalDetails/PreviousCOR/Row3/ToDate"
    },

    # marriage
    'marriage':{
        "marital_status":"Page1/MaritalStatus/SectionA/MaritalStatus",
        "married_date":"Page1/MaritalStatus/SectionA/DateOfMarriage",
        "sp_last_name":"Page1/MaritalStatus/SectionA/FamilyName",
        "sp_first_name":"Page1/MaritalStatus/SectionA/GivenName",
        "previous_married":"Page2/MaritalStatus/SectionA/PrevMarriedIndicator",
        "pre_sp_last_name":"Page2/MaritalStatus/SectionA/PMFamilyName",
        "pre_sp_first_name":"Page2/MaritalStatus/SectionA/GivenName/PMGivenName",
        "pre_relationship_type":"Page2/MaritalStatus/SectionA/TypeOfRelationship",
        "pre_sp_dob_year":"Page2/MaritalStatus/SectionA/PrevSpouseDOB/DOBYear",
        "pre_sp_dob_month":"Page2/MaritalStatus/SectionA/PrevSpouseDOB/DOBMonth",
        "pre_sp_dob_day":"Page2/MaritalStatus/SectionA/PrevSpouseDOB/DOBDay",
        "pre_start_date":"Page2/MaritalStatus/SectionA/FromDate",
        "pre_end_date":"Page2/MaritalStatus/SectionA/ToDate/ToDate"
    },

    'passport':{
        "number":"Page2/MaritalStatus/SectionA/Passport/PassportNum/PassportNum",
        "country":"Page2/MaritalStatus/SectionA/Passport/CountryofIssue/CountryofIssue",
        "issue_date":"Page2/MaritalStatus/SectionA/Passport/IssueDate/IssueDate",
        "expiry_date":"Page2/MaritalStatus/SectionA/Passport/ExpiryDate"
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
        'po_box':"Page2/ContactInformation/contact/AddressRow1/POBox/POBox",
        'unit':"Page2/ContactInformation/contact/AddressRow1/Apt/AptUnit",
        'street_number':"Page2/ContactInformation/contact/AddressRow1/StreetNum/StreetNum",
        'street_name':"Page2/ContactInformation/contact/AddressRow1/Streetname/Streetname",
        'city':"Page2/ContactInformation/contact/AddressRow2/CityTow/CityTown",
        'country':"Page2/ContactInformation/contact/AddressRow2/Country/Country",
        'province':"Page2/ContactInformation/contact/AddressRow2/ProvinceState/ProvinceState",
        'post_code':"Page2/ContactInformation/contact/AddressRow2/PostalCode/PostalCode",
        'district':"Page2/ContactInformation/contact/AddressRow2/District"
    },

    'residential_address':{
        'same_as_mailing':"Page2/ContactInformation/contact/SameAsMailingIndicator",
        'unit':"Page2/ContactInformation/contact/ResidentialAddressRow1/AptUnit/AptUnit",
        'street_number':"Page2/ContactInformation/contact/ResidentialAddressRow1/StreetNum/StreetNum",
        'street_name':"Page2/ContactInformation/contact/ResidentialAddressRow1/StreetName/Streetname",
        'city':"Page2/ContactInformation/contact/ResidentialAddressRow1/CityTown/CityTown",
        'country':"Page2/ContactInformation/contact/ResidentialAddressRow2/Country/Country",
        'province':"Page2/ContactInformation/contact/ResidentialAddressRow2/ProvinceState/ProvinceState",
        'post_code':"Page2/ContactInformation/contact/ResidentialAddressRow2/PostalCode/PostalCode",
        'district':"Page2/ContactInformation/contact/ResidentialAddressRow2/District"
    },

    'phone':{
        "variable_type":"Page2/ContactInformation/contact/PhoneNumbers/Phone/Type",
        "canada_us":"Page2/ContactInformation/contact/PhoneNumbers/Phone/CanadaUS",
        "other":"Page2/ContactInformation/contact/PhoneNumbers/Phone/Other",
        'ext':"Page2/ContactInformation/contact/PhoneNumbers/Phone/NumberExt",
        'country_code':"Page2/ContactInformation/contact/PhoneNumbers/Phone/NumberCountry",
        'number':"Page2/ContactInformation/contact/PhoneNumbers/Phone/ActualNumber",
        'na_area':"Page2/ContactInformation/contact/PhoneNumbers/Phone/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/contact/PhoneNumbers/Phone/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/contact/PhoneNumbers/Phone/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/contact/PhoneNumbers/Phone/IntlNumber/IntlNumber"
    },

    'altphone':{
        "variable_type":"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/Type",
        "canada_us":"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/CanadaUS",
        "other":"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/Other",
        'ext':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/NumberExt",
        'country_code':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/NumberCountry",
        'number':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/ActualNumber",
        'na_area':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/contact/PhoneNumbers/AltPhone/IntlNumber/IntlNumber"
    },

    'fax':{
        "canada_us":"Page2/ContactInformation/contact/FaxEmail/Phone/CanadaUS",
        "other":"Page2/ContactInformation/contact/FaxEmail/Phone/Other",
        'ext':"Page2/ContactInformation/contact/FaxEmail/Phone/NumberExt",
        'country_code':"Page2/ContactInformation/contact/FaxEmail/Phone/NumberCountry",
        'number':"Page2/ContactInformation/contact/FaxEmail/Phone/ActualNumber",
        'na_area':"Page2/ContactInformation/contact/FaxEmail/Phone/NANumber/AreaCode",
        'na_first_three':"Page2/ContactInformation/contact/FaxEmail/Phone/NANumber/FirstThree",
        'na_last_five':"Page2/ContactInformation/contact/FaxEmail/Phone/NANumber/LastFive",
        'int_number':"Page2/ContactInformation/contact/FaxEmail/Phone/IntlNumber/IntlNumber"
    },

    'education':{
        "start_date_year":"Page3/Education/Edu_Row1/FromYear",
        "start_date_month":"Page3/Education/Edu_Row1/FromMonth",
        "end_date_year":"Page3/Education/Edu_Row1/ToYear",
        "end_date_month":"Page3/Education/Edu_Row1/ToMonth",
        "school_name":"Page3/Education/Edu_Row1/School",
        "field_of_study":"Page3/Education/Edu_Row1/FieldOfStudy",
        "city":"Page3/Education/Edu_Row1/CityTown",
        "country":"Page3/Education/Edu_Row1/Country/Country",
        "province":"Page3/Education/Edu_Row1/ProvState"
    },
    # occupation is a special dict, and will be handled seperately
    'occupation':{
        "start_date_year":"FromYear",
        "start_date_month":"FromMonth",
        "end_date_year":"ToYear",
        "end_date_month":"ToMonth",
        "job_title":"Occupation/Occupation",
        "company":"Employer",
        "city":"CityTown/CityTown",
        "province":"ProvState",
        "country":"Country/Country"
    },

    'trbackground':{
        "q1a":"Page3/BackgroundInfo/Choice",
        "q1b":"Page3/BackgroundInfo/Choice",
        "q1c":"Page3/BackgroundInfo/Details/MedicalDetails",
        "q2a":"Page3/BackgroundInfo2/VisaChoice1",
        "q2b":"Page3/BackgroundInfo2/VisaChoice2",
        "q2c":"Page3/BackgroundInfo2/Details/VisaChoice3",
        "q2d":"Page3/BackgroundInfo2/Details/refusedDetails",
        "q3a":"Page3/BackgroundInfo3/Choice",
        "q3b":"Page3/PageWrapper/BackgroundInfo3/militaryServiceDetails",
        "q3a":"Page3/PageWrapper/Military/Choice",
        "q3b":"Page3/PageWrapper/Military/militaryServiceDetails",
        "q5":"Page3/PageWrapper/Occupation/Choice",
        "q6":"Page3/PageWrapper/GovPosition/Choice"
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
        'visa': ["province"],
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

    'tr_portal_study_level_pairs': {
        'sp': ["study_level"]
    },
    'tr_portal_study_field_pairs': {
        'sp': ["study_field"]
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