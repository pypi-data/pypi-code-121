from pdfform import context
from model.tr.m1295 import M1295Model
from model.tr.m5708 import M5708Model
from model.tr.m5709 import M5709Model
from model.tr.m5710 import M5710Model

test_1295 = {
    ## ------- header -------
    "uci": "91075022",
    "service_language": "English",
    ## ------ personal details ------
    "last_name": "ZHANG",
    "first_name": "SAN",
    #'used_first_name': '',
    #'used_last_name': '',
    "sex": "Female",
    "dob": "1976-06-29",
    "city_of_birth": "SHANGHAI",
    "country_of_birth": "China",
    "citizenship": "China",
    "current_residence": {
        "country": "China",
        "status": "Citizen",
        "other": "",
        "from": "",
        "to": "",
    },
    #'previous_residence': [],
    #'applying_country': {},
    "current_mariage": {
        "status": "Married",
        "married_date": "2004-02-14",
        "spouse_last_name": "LI",
        "spouse_first_name": "SI",
    },
    "previous_mariage": {
        "spouse_last_name": "WANG",
        "spouse_first_name": "WU",
        "spouse_dob": "1972-07-04",
        "type": "Married",
        "from": "1999-10-28",
        "to": "2000-10-20",
    },
    ## ------ language ------
    "native_language": "Mandarin",
    "english_french": "Neither",
    #'preferred_language': '',
    "language_test": "No",
    ## ------ passport ------
    "passport": {
        "number": "EJ4484570",
        "country_of_issue": "China",
        "issue_date": "2021-02-25",
        "expiry_date": "2031-02-24",
        #'taiwan_issued': '',
        #'israel_issued': '',
    },
    ## ------ national ID ------
    "national_id": {
        "number": "42010419760629202X",
        "country_of_issue": "CHN (China)",  # TODO: how to convert to normal country name?
        "issue_date": "2005-12-20",
        "expiry_date": "2025-12-20",
    },
    ## ------ US PR card ------
    # "us_pr_card": {
    #     "number": "",
    #     "expiry_date": "",
    # },
    ## ------ contact information ------
    "mailing_address": {
        "po_box": "",
        "apt": "41-501",
        "street_no": "380",
        "street_name": "XINGZHI ROAD",
        "city": "SHANGHAI",
        "country": "China",
        "province": "",
        "postal_code": "200442",
        "district": "BAOSHAN",
    },
    #'residential_address': {},
    "telephone_no": {
        "canada": "No",
        "type": "Cellular",
        "country_code": "86",
        "number": "18917872110",
        "ext": "",
    },
    #'alternate_no': {},
    #'fax_no': {},
    "email": "yaozhenyu2005@gmail.com",
    ## ------ work detail ------
    "work_detail": {
        "type": "Open Work Permit",
        #'employer_name': 'Not applicable',
        #'employer_address': 'Not applicable',
        "province": "BC",
        "city": "Nanaimo",
        #'address': 'TO BE DETERMINED',
        #'job_title': 'TO BE DETERMINED',
        #'description': 'TO BE DETERMINED',
        "from": "2022-07-01",
        "to": "2024-05-01",
        #'lmia_no': '',
    },
    ## ------ education ------
    "education": {
        "from": "2002-09",
        "to": "2005-01",
        "field": "Accounting, Diploma",
        "school": "China Central Radio & TV University",
        "city": "WUHAN",
        "country": "China",
        #'province': '',
    },
    ## ------ Employment ------
    "employment": [
        {
            "from": "2012-02",
            "to": "2021-11",
            "occupation": "PRESIDENTT, OWNER-GENERAL-MANAGER",
            "company": "SHANGHAI CHONGYUAN MEDICAL DEVICE CO.,LTD",
            "city": "SHANGHAI",
            "country": "China",
            #'province': '',
        },
        {
            "from": "2006-05",
            "to": "2012-01",
            "occupation": "OWNER-GENERAL-MANAGER",
            "company": "SHANGHAI CHONGYUAN MEDICAL DEVICE CO.,LTD",
            "city": "SHANGHAI",
            "country": "China",
            #'province': '',
        },
    ],
}

test_5708 = {
    ## ------- header -------
    "uci": "1120956934",
    "service_language": "English",
    "extend_visitor": True,
    "restore_visitor": False,
    "new_permit": False,
    ## ------ personal details ------
    "last_name": "JIA",
    "first_name": "LIU",
    "used_first_name": "JIA",
    "used_last_name": "QI",
    "sex": "Male",
    "dob": "1971-10-28",
    "city_of_birth": "SHANGHAI",
    "country_of_birth": "China",
    "citizenship": "China",
    "current_residence": {
        "country": "Canada",
        "status": "Visitor",
        "other": "",
        "from": "2020-08-17",
        "to": "2022-08-06",
    },
    #'previous_residence': [],
    #'applying_country': {},
    "current_mariage": {
        "status": "Married",
        "married_date": "2004-02-14",
        "spouse_last_name": "LI",
        "spouse_first_name": "YIN",
        "spouse_is_canadian": False,
    },
    # "previous_mariage": {},
    ## ------ language ------
    "native_language": "Mandarin",
    "english_french": "English",
    #'preferred_language': '',
    "language_test": "No",
    ## ------ passport ------
    "passport": {
        "number": "EJ4692323",
        "country_of_issue": "China",
        "issue_date": "2021-04-01",
        "expiry_date": "2031-03-31",
        #'taiwan_issued': '',
        #'israel_issued': '',
    },
    ## ------ national ID ------
    "national_id": {
        "number": "310108197110285213",
        "country_of_issue": "CHN (China)",  # TODO: how to convert to normal country name?
        "issue_date": "",
        "expiry_date": "",
    },
    ## ------ US PR card ------
    # "us_pr_card": {
    #     "number": "",
    #     "expiry_date": "",
    # },
    ## ------ contact information ------
    "mailing_address": {
        "po_box": "",
        "apt": "",
        "street_no": "6499",
        "street_name": "RAVEN RD",
        "city": "NANAIMO",
        "country": "Canada",
        "province": "BC",
        "postal_code": "V9V 1V7",
    },
    #'residential_address': {},
    "telephone_no": {
        "canada": "No",
        "type": "Cellular",
        "country_code": "86",
        "number": "18917872110",
        "ext": "",
    },
    #'alternate_no': {},
    #'fax_no': {},
    "email": "",
    ## ------ coming into Canada ------
    "coming_into_canada": {
        "date": "2020-01-02",
        "place": "Vancouver",
        "purpose": "Family Visit",
        #'other': '',
        #'last_date': '',
        #'last_place': '',
        #'last_document_number': '',
    },
    ## ------ details of visit to Canada ------
    "visit_detail": {
        "purpose": "Family Visit",
        #'other': '',
        "from": "2022-06-15",
        "to": "2023-09-30",
        "funds": "15000",
        "expense_by": "Myself",
        #'other': '',
        "persons": [
            {
                "name": "YAO ZICHENG",
                "relation": "",
                "address": "6499 RAVEN RD NANAIMO BC  V9V 1V7",
            },
        ],
    },
    ## ------ education ------
    "education": {
        "from": "1997-04",
        "to": "2004-12",
        "field": "DIPLOMA",
        "school": "FUDAN UNIVERSITY",
        "city": "SHANGHAI",
        "country": "China",
        #'province': '',
    },
    ## ------ Employment ------
    "employment": [
        {
            "from": "2012-02",
            "to": "2020-08",
            "occupation": "MANAGER",
            "company": "SHANGHAI CHONGYUAN MEDICAL DEVICE CO.,LTD",
            "city": "SHANGHAI",
            "country": "China",
            #'province': '',
        },
        {
            "from": "2006-07",
            "to": "2012-02",
            "occupation": "OWNER-GENERAL-MANAGER",
            "company": "SHANGHAI CHONGYUAN MEDICAL DEVICE CO.,LTD",
            "city": "SHANGHAI",
            "country": "China",
            #'province': '',
        },
    ],
}

test_5709 = {
    ## ------- header -------
    "uci": "93379194",
    "service_language": "English",
    "apply_extend_student": True,
    "restore_student": False,
    "new_permit": False,
    ## ------ personal details ------
    "last_name": "Wu",
    "first_name": "Yifan",
    "used_first_name": "Bufan",
    "used_last_name": "Wu",
    "sex": "Male",
    "dob": "1997-10-08",
    "city_of_birth": "Suzhou",
    "country_of_birth": "China",
    "citizenship": "China",
    "current_residence": {
        "country": "Canada",
        "status": "Student",
        "other": "",
        "from": "2019-05-19",
        "to": "2022-08-29",
    },
    #'previous_residence': [],
    #'applying_country': {},
    "current_mariage": {
        "status": "Common-Law",
        "married_date": "2021-01-01",
        "spouse_last_name": "Li",
        "spouse_first_name": "Xiaolu",
        "spouse_is_canadian": False,
    },
    # "previous_mariage": {},
    ## ------ language ------
    "native_language": "Mandarin",
    "english_french": "English",
    #'preferred_language': '',
    "language_test": "Yes",
    ## ------ passport ------
    "passport": {
        "number": "E18826275",
        "country_of_issue": "China",
        "issue_date": "2014-06-09",
        "expiry_date": "2024-06-08",
        #'taiwan_issued': '',
        #'israel_issued': '',
    },
    ## ------ national ID ------
    "national_id": {
        "number": "32050319971008001x",
        "country_of_issue": "CHN (China)",
        "issue_date": "2018-07-12",
        "expiry_date": "2028-07-12",
    },
    ## ------ US PR card ------
    # "us_pr_card": {
    #     "number": "",
    #     "expiry_date": "",
    # },
    ## ------ contact information ------
    "mailing_address": {
        "po_box": "",
        "apt": "302",
        "street_no": "2048",
        "street_name": "W 41st Ave",
        "city": "Vancouver",
        "country": "Canada",
        "province": "AB",
        "postal_code": "V6M 1Y8",
    },
    #'residential_address': {},
    "telephone_no": {
        "canada": "Yes",
        "type": "Cellular",
        "country_code": "1",
        "number": "6047820166",
        "ext": "",
    },
    #'alternate_no': {},
    #'fax_no': {},
    "email": "wyf19971008@gmail.com",
    ## ------ coming into Canada ------
    "coming_into_canada": {
        "date": "2015-12-23",
        "place": "Vancouver",
        "purpose": "Study",
        #'other': '',
        "last_date": "2019-05-19",
        "last_place": "Vancouver",
        "last_document_number": "F313325360",
    },
    ## ------ details of study in Canada ------
    "study_detail": {
        "school": "Hanson College",
        "level": "College - Diploma",
        "field": "Business/Commerce",
        # CAUSION!!! the city list not 100 percent match with option_list cities
        "address_of_school": {
            "province": "BC",
            "city": "New Westminster",
            "address": "206-960 Quayside Drive",
        },
        "institution": "O19618862812",
        "student_id": "H10003244",
        "from": "2022-09-01",
        "to": "2023-12-31",
        "cost": {
            "tuition": "5000",
            "room": "10000",
            "other": "",
        },
        "funds": "30000",
        "expense_by": "Myself",
        #'other': '',
        "apply_for_work": False,
        #'work_permit_type': '',
        # "caq": {
        #    "cert_number": "",
        #    "expiry_date": "",
        # },
    },
    ## ------ education ------
    "education": {
        "from": "2019-09",
        "to": "2021-12",
        "field": "Business,diploma",
        "school": "Hanson College (Cambrian College New Westminster)",
        "city": "New Westminster",
        "country": "Canada",
        "province": "BC",
    },
    ## ------ Employment ------
    "employment": [
        {
            "from": "2020-09",
            "to": "2021-12",
            "occupation": "Part-time working /Office Assistant",
            "company": "Beeta International Education Group",
            "city": "Vancouver",
            "country": "Canada",
            "province": "BC",
        },
    ],
}

test_5710 = {
    ## ------- header -------
    "uci": "93390605",
    "service_language": "English",
    "apply_same_employer": True,
    "apply_new_employer": False,
    "restore_worker": False,
    "new_permit": False,
    ## ------ personal details ------
    "last_name": "Li",
    "first_name": "Haiqiao",
    # "used_first_name": "",
    # "used_last_name": "",
    "sex": "Female",
    "dob": "1971-01-10",
    "city_of_birth": "Xi an, Shannxi",
    "country_of_birth": "China",
    "citizenship": "China",
    "current_residence": {
        "country": "Canada",
        "status": "Worker",
        "other": "",
        "from": "2018-12-28",
        "to": "2022-08-04",
    },
    #'previous_residence': [],
    #'applying_country': {},
    "current_mariage": {
        "status": "Married",
        "married_date": "1999-12-23",
        "spouse_last_name": "Li",
        "spouse_first_name": "Quhu",
        "spouse_is_canadian": False,
    },
    # "previous_mariage": {},
    ## ------ language ------
    "native_language": "Mandarin",
    "english_french": "Neither",
    #'preferred_language': '',
    "language_test": "No",
    ## ------ passport ------
    "passport": {
        "number": "E12745538",
        "country_of_issue": "China",
        "issue_date": "2013-02-05",
        "expiry_date": "2023-02-04",
        #'taiwan_issued': '',
        #'israel_issued': '',
    },
    ## ------ national ID ------
    "national_id": {
        "number": "610103197101100423",
        "country_of_issue": "CHN (China)",
        "issue_date": "2014-04-17",
        "expiry_date": "2034-04-17",
    },
    ## ------ US PR card ------
    # "us_pr_card": {
    #     "number": "",
    #     "expiry_date": "",
    # },
    ## ------ contact information ------
    "mailing_address": {
        "po_box": "",
        "apt": "",
        "street_no": "2963",
        "street_name": "Constellation Ave",
        "city": "Victoria",
        "country": "Canada",
        "province": "AB",
        "postal_code": "V9B 0L9",
    },
    #'residential_address': {},
    "telephone_no": {
        "canada": "Yes",
        "type": "Cellular",
        "country_code": "1",
        "number": "2505802709",
        "ext": "",
    },
    "alternate_no": {
        "canada": "Yes",
        "type": "Business",
        "country_code": "1",
        "number": "2507482575",
        "ext": "",
    },
    "fax_no": {
        "canada": "Yes",
        "country_code": "1",
        "number": "2507483562",
        "ext": "",
    },
    "email": "750024046@qq.com",
    ## ------ coming into Canada ------
    "coming_into_canada": {
        "date": "2018-12-28",
        "place": "Pacific Highway,BC",
        "purpose": "Work",
        #'other': '',
        "last_date": "2019-09-12",
        "last_place": "Vancouver, BC",
        "last_document_number": "U512109881",
    },
    ## ------ details of intended work in Canada ------
    "work_detail": {
        "type": "Exemption from labour Market Impact Assessment",
        # "other": "",
        "employer_name": "CENTRAL GLASS(DUNCAN)LTD.",
        "employer_address": "2856 ROBERTS ROAD, DUNCAN, BC V9L 6W3 CANADA",
        "province": "BC",
        "city": "Duncan",
        "address": "2856 ROBERTS ROAD",
        "job_title": "DIRECTOR OF OPERATIONS",
        "description": "DAILY OPERATIONS INCLUDING PURCHASING,PRODUCTION,QUALITY CONTROL,STAFFING, FINANCING,ETC.",
        "from": "2022-09-01",
        "to": "2023-02-04",
        "lmia_no": "A0651459",
        # "caq_number": "",
        # "caq_expire": "",
        "pnp": False,
    },
    ## ------ education ------
    "education": {
        "from": "1993-09",
        "to": "1995-07",
        "field": "Decoration, Diploma",
        "school": "Xi'an Academy of Arts",
        "city": "Xi'an",
        "country": "China",
    },
    ## ------ Employment ------
    "employment": [
        {
            "from": "2018-12",
            "to": "2022-01",
            "occupation": "Director of Operations",
            "company": "Central Glass (Duncan), Ltd.",
            "city": "Duncan",
            "country": "Canada",
            "province": "BC",
        },
        {
            "from": "2016-08",
            "to": "2018-07",
            "occupation": "Unemployed, accompany child",
            "company": "N/A",
            "city": "Victoria",
            "country": "Canada",
            "province": "BC",
        },
        {
            "from": "2010-03",
            "to": "2016-07",
            "occupation": "Director of Administration& Artistic Design",
            "company": "Shaanxi Ximei Environmental Art Design Co., Ltd.",
            "city": "Xi'an",
            "country": "China",
        },
    ],
}


def load_form_data(file, form_name):
    model = {
        "1295": M1295Model,
        "5708": M5708Model,
        "5709": M5709Model,
        "5710": M5710Model,
    }
    applicant = model[form_name]([file.name])
    return applicant
