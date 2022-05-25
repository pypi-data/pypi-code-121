from ekp_sdk.util.clean_null_terms import clean_null_terms


def Form(
    name, 
    schema, 
    children, 
    class_name=None,
    multi_record = None,
    on_submit = None,
    style=None,
    ):
    return {
        "_type": "Form",
        "props": clean_null_terms({
            "children": children,
            "className": class_name,
            "multiRecord": multi_record,
            "name": name,
            "onSubmit": on_submit,
            "schema": schema,
            "style": style
        })
    }

