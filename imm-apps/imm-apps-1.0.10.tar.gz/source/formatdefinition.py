import xlsxwriter


TITLE_FORMAT = {
    "font_size": 24,
    "bold": True,
    "font_color": "000000",
    "align": "center",
    "valign": "middle",
    "bg_color": "C0C0C0",
    "border": 1
}

COLUMN_TITLE_FORMAT = {
    "font_size": 14,
    "bold": True,
    "font_color": "000000",
    "align": "center",
    "valign": "middle",
    "bg_color": "C0C0C0",
    "border": 1
}

VARIABLE_TITLE_FORMAT = {
    "font_size": 14,
    "font_color": "000000",
    "align": "center",
    "valign": "middle",
    "bg_color": "C0C0C0",
    "border": 1
}

DESCRIPTION_FORMAT = {
    "font_size": 14,
    "font_color": "000000",
    "align": "right",
    "valign": "vcenter",
    "bg_color": "f4f3ee",
    "border": 1
}

VALUE_FORMAT = {
    "font_size": 14,
    "font_color": "719c75",
    "align": "left",
    "valign": "vcenter",
    "locked": False,
    "border": 1,
    "text_wrap": 1
}

COMMENT_FORMAT = {
    "font_size": 12,
    # "font_color": "CCFFCC",
    "author": "Jacky Zhang",
    "width": 200,
    "heigth": 400
}

COLUMN_WIDTH = {
    "noc_code": 10,
    "date": 12,
    'name': 20,
    'fullname': 30,
    'country': 20,
    'relation': 15,
    'address': 30,
    'type': 20,
    'email': 25,
    'title': 20,
    'city': 15,
    'province': 15,
    'status': 20,
    'field_of_study': 20,
    'duties': 50,
    'company_brief': 30,
    'brief': 30
}

special_format = {
    'table-eraddress': {
        'variable_type': {'locked': True, "bg_color": "f4f3ee"},
        'display_type': {'locked': True, "bg_color": "f4f3ee"},
        'country': {'locked': True, "bg_color": "f4f3ee"}
    },
    "table-contact": {
        "contact_variable": {'locked': True, "bg_color": "f4f3ee"},
        "contact_type": {'locked': True, "bg_color": "f4f3ee"}
    },
    'table-employment': {
        "noc_code": {"num_format": "@"}
    },
    'table-finance': {
        "total_asset": {"num_format": "$#,##0"},
        "net_asset": {"num_format": "$#,##0"},
        "revenue": {"num_format": "$#,##0"},
        "net_income": {"num_format": "$#,##0"},
        "retained_earning": {"num_format": "$#,##0"}
    },
    'table-employee_list': {
        'noc': {"num_format": "@"},
        "percentage_to_median": {"num_format": "0.0%"}
    },
    'info-joboffer': {
        'noc': {"num_format": "@"},
    },
    "table-personid": {
        "variable_type": {'locked': True, "bg_color": "f4f3ee"},
        "display_type": {'locked': True, "bg_color": "f4f3ee"}
    },
    "type-assumption": {
        "noc_code": {"num_format": "@"}
    },
    "table-phone": {
        "variable_type": {'locked': True, "bg_color": "f4f3ee"},
        "display_type": {'locked': True, "bg_color": "f4f3ee"}
    },
    "table-address": {
        "variable_type": {'locked': True, "bg_color": "f4f3ee"},
        "display_type": {'locked': True, "bg_color": "f4f3ee"}
    },
    'table-employment': {
        'noc_code': {"num_format": "@"},
        "share_percentage": {"num_format": "0.0%"}
    }

}
