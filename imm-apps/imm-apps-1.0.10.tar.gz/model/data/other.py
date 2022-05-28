phone_type={
    'residential':'01',
    "cellular":"02",
    "business":"03"
}

tr_canada_status={
    "citizen":'01',
    'permanent resident':'02',
    'visitor':'03',
    'worker':'04',
    'student':'05',
    'other':'06',
    'protected person':'07',
    'refugee claimant':'08',
    'foreign national':'09'
}

# 编号有问题。 处理married和common law是对的。 其他不确定。
tr_marital_status={
    "annulled marriage":'09',
    'common-law':'03',
    'divorced':'04',
    'legally separated':'05',
    'married':'01',
    'single':'02',
    'unknown':'00',
    'widowed':'06'
}

marital_stauts_5645={
    "annulled marriage":'1',
    'common-law':'2',
    'divorced':'3',
    'legally separated':'4',
    'married':'5',
    'single':'6',
    'widowed':'7'
}

bool_convert={
    True: 'Y',
    False: "N",
    None:'N'
}
#TODO: 可以考虑分类，加拿大放一个特别类别

tr_portal_ca_province={
    "Newfoundland and Labrador": "01",
    "Prince Edward Island": "02",
    "Nova Scotia": "03",
    "New Brunswick": "04",
    "Quebec": "05",
    "Ontario": "06",
    "Manitoba": "07",
    "Saskatchewan": "08",
    "Alberta": "09",
    "British Columbia": "11",
    "Northwest Territories": "10",
    "Yukon": "12",
    "Nunavut": "64"
}
tr_portal_residence_status={
    "Citizen": "01",
    "Foreign National": "09",
    "Other": "06",
    "Permanent resident": "02",
    "Protected Person": "07",
    "Refugee Claimant": "08",
    "Student": "05",
    "Visitor": "03",
    "Worker": "04"
}

tr_portal_marital_status=[
    "Annulled Marriage",
    "Common Law",
    "Divorced",
    "Married",
    "Separated",
    "Single",
    "Widowed"
]

# PDF forms for imm1294 and imm5709 study format
tr_form_study_level={
    "Primary School":'1',
    "Secondary School":'2',
    "PTC/TCST/DVS/AVS":'10',
    "CEGEP - Pre-university":"11",
    "CEGEP - Technical":"12",
    "College - Certificate":"13",
    "College - Diploma":"14",
    "College - Applied degree":"15",
    "University - Bachelor's Deg.":"04",
    "University - Master's Deg.":"05",
    "University - Doctorate":"06",
    "University - Other Studies":"07",
    "ESL/FSL":"16",
    "ESL/FSL and College":"17",
    "ESL/FSL and University":"18",
    "Other Studies":"08",
    "Not Applicable":"19"
}

tr_form_study_field={
    "Arts/Humanities/Social Science":"01",
    "Arts, Fine/Visual/Performing":"02",
    "Business/Commerce":"03",
    "Computing/IT":"04",
    "ESL/FSL":"05",
    "Flight Training":"06",
    "Hospitality/Tourism":"07",
    "Law":"08",
    "Medicine":"09",
    "Science, Applied":"10",
    "Sciences, General":"11",
    "Sciences, Health":"12",
    "Trades/Vocational":"13",
    "Theology/Religious Studies":"14",
    "Other":"15",
    "Agric/Agric Ops/Rel Sciences":"16",
    "Architecture and Rel Services":"17",
    "Biological/Biomed Sciences":"18",
    "Business/Mgmt/Marketing":"19"
}

# tr portal study format
tr_portal_study_level={
    "Primary School": "01",
    "Secondary School": "02",
    "PTC/TCST/DVS/AVS": "10",
    "CEGEP - Pre-university": "11",
    "CEGEP - Technical": "12",
    "College - Certificate": "13",
    "College - Diploma": "14",
    "College - Applied degree": "15",
    "University - Bachelor's Deg.": "04",
    "University - Master's Deg.": "05",
    "University - Doctorate": "06",
    "University - Other Studies": "07",
    "ESL/FSL": "16",
    "ESL/FSL and College": "17",
    "ESL/FSL and University": "18",
    "Other Studies": "08",
    "Not Applicable": "19"
}
tr_portal_study_field={
    "Agric/Agric Ops/Rel Sciences": "16",
    "Architecture and Rel Services": "17",
    "Arts, Fine/Visual/Performing": "02",
    "Arts/Humanities/Social Science": "01",
    "Biological/Biomed Sciences": "18",
    "Business/Commerce": "03",
    "Business/Mgmt/Marketing": "19",
    "Computing/IT": "04",
    "ESL/FSL": "05",
    "Flight Training": "06",
    "Hospitality/Tourism": "07",
    "Law": "08",
    "Medicine": "09",
    "Other": "15",
    "Science, Applied": "10",
    "Sciences, General": "11",
    "Sciences, Health": "12",
    "Theology/Religious Studies": "14",
    "Trades/Vocational": "13"
}