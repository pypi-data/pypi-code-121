from ekp_sdk.util.clean_null_terms import clean_null_terms


def Link(
        class_name=None,
        content=None,
        external=None,
        external_icon=None,
        href=None,
        style=None,
        tooltip=None
):
    return {
        "_type": "Link",
        "props": clean_null_terms({
            "className": class_name,
            "content": content,
            "external": external,
            "externalIcon": external_icon,
            "href": href,
            "style": style,
            "tooltip": tooltip,
        })
    }
