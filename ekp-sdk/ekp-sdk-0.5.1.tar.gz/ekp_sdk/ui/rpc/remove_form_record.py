def remove_form_record(form_name, form_field, where_field_value):
    return {
        "method": "removeFormRecord",
        "params": [form_name, form_field, where_field_value]
    }