from ekp_sdk.util.clean_null_terms import clean_null_terms


def Tabs(
    children,
    class_name=None,
    style=None,
    tooltip=None,
):
    return {
        "_type": "Tabs",
        "props": clean_null_terms({
            "children": children,
            "className": class_name,
            "style": style,
            "tooltip": tooltip,
        })
    }


def Tab(
    label,
    children,
):
    return {
        "label": label,
        "children": children
    }
