from ekp_sdk.util.clean_null_terms import clean_null_terms


def Chart(
        type,
        series,
        title=None,
        card=None,
        data=None,
        height=400,
        busy_when=None,
        options=None,
        class_name=None
):
    return {
        "_type": "Chart",
        "props": clean_null_terms({
            "busyWhen": busy_when,
            "card": card,
            "className": class_name,
            "data": data,
            "height": height,
            "options": options,
            "series": series,
            "title": title,
            "type": type,
        })
    }