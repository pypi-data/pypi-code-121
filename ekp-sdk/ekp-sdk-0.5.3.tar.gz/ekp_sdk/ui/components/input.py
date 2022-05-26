
from ekp_sdk.util.clean_null_terms import clean_null_terms


def Input(
    label,
    name,
    class_name=None,
    style=None,
    tooltip=None
):
    return {
        "_type": "Input",
        "props": clean_null_terms({
            "className": class_name,
            "label": label,
            "name": name,
            "style": style,
            "tooltip": tooltip
        })
    }
