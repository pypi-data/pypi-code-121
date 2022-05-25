from ekp_sdk.util.clean_null_terms import clean_null_terms


def Paragraphs(children, class_name=None):
    return {
        "_type": "Paragraphs",
        "props": clean_null_terms({
            "class_name": class_name,
            "children": children,
        })
    }


def Fragment(children, class_name=None):
    return {
        "_type": "Fragment",
        "props": clean_null_terms({
            "className": class_name,
            "children": children,
        })
    }


def Span(content, class_name=None):
    return {
        "_type": "Span",
        "props": clean_null_terms({
            "className": class_name,
            "content": content,
        })
    }


def Container(children, class_name=None, context=None):
    return {
        "_type": "Container",
        "props": clean_null_terms({
            "className": class_name,
            "children": children,
            "context": context
        })
    }


def Row(children, class_name=None):
    return {
        "_type": "Row",
        "props": clean_null_terms({
            "className": class_name,
            "children": children
        })
    }


def Div(children=None, class_name=None, style=None):
    return {
        "_type": "Div",
        "props": clean_null_terms({
            "className": class_name,
            "children": children or [],
            "style": style,
        })
    }


def Col(class_name=None, children=None):
    return {
        "_type": "Col",
        "props": clean_null_terms({
            "className": class_name,
            "children": children or []
        })
    }


def Icon(name, class_name=None, size=None):
    return {
        "_type": "Icon",
        "props": clean_null_terms({
            "className": class_name,
            "name": name,
            "size": size
        })
    }


def Datatable(
    data,
    columns,
    busy_when=None,
    class_name=None,
    default_sort_asc=None,
    default_sort_field_id=None,
    default_view=None,
    disable_list_view=None,
    filters=None,
    grid_view=None,
    on_row_clicked=None,
    pagination=None,
    pagination_per_page=None,
    search_hint=None,
    show_export=None,
):
    return {
        "_type": "Datatable",
        "props": clean_null_terms({
            "busyWhen": busy_when,
            "className": class_name,
            "columns": columns,
            "data": data,
            "defaultSortAsc": default_sort_asc,
            "defaultSortFieldId": default_sort_field_id,
            "defaultView": default_view,
            "disableListView": disable_list_view,
            "filters": filters,
            "gridView": grid_view,
            "onRowClicked": on_row_clicked,
            "pagination": pagination,
            "paginationPerPage": pagination_per_page,
            "searchHint": search_hint,
            "showExport": show_export,
        })
    }


def Hr():
    return {
        "_type": "Hr",
        "props": {}
    }


def Badge(color, children, class_name=None):
    return {
        "_type": "Badge",
        "props": clean_null_terms({
            "children": children,
            "className": class_name,
            "color": color,
        })
    }


def Column(
    id,
    cell=None,
    format=None,
    grow=None,
    omit=None,
    min_width=None,
    right=None,
    searchable=None,
    sortable=None,
    title=None,
    value=None,
    width=None,
):
    return clean_null_terms({
        "cell": cell,
        "format": format,
        "grow": grow,
        "id": id,
        "minWidth": min_width,
        "omit": omit,
        "right": right,
        "searchable": searchable,
        "sortable": sortable,
        "title": title,
        "value": value,
        "width": width,
    })


def Card(children=None, class_name=None):
    return {
        "_type": "Card",
        "props": clean_null_terms({
            "children": children,
            "className": class_name
        })
    }


def Select(label, name, options, min_width=None, class_name=None):
    return {
        "_type": "Select",
        "props": clean_null_terms({
            "className": class_name,
            "label": label,
            "name": name,
            "options": options,
            "minWidth": min_width,
        })
    }


def Button(
    busy_when=None,
    class_name=None,
    color=None,
    icon=None,
    is_submit=None,
    label=None,
    on_click=None,
    size=None,
    tooltip=None
):
    return {
        "_type": "Button",
        "props": clean_null_terms({
            "busyWhen": busy_when,
            "className": class_name,
            "color": color,
            "icon": icon,
            "isSubmit": is_submit,
            "label": label,
            "onClick": on_click,
            "size": size,
            "tooltip": tooltip,
        })
    }


def collection(collectionName):
    return collectionName


def documents(collectionName):
    return f'$["{collection(collectionName)}"].*'


def is_busy(collection):
    return f'$.busy[?(@.id=="{collection}")]'


def format_currency(rpc, symbol):
    return {
        "method": "formatCurrency",
        "params": [rpc, symbol]
    }


def format_age(value):
    return {
        "method": "formatAge",
        "params": [value]
    }


def format_datetime(value):
    return {
        "method": "formatDatetime",
        "params": [value]
    }


def format_template(template, values):
    return {
        "method": "formatTemplate",
        "params": [template, values]
    }


def switch_case(on, cases):
    return {
        "method": "switchCase",
        "params": [on, cases]
    }


def json_array(values):
    return {
        "method": "jsonArray",
        "params": [values]
    }


def ekp_map(source, projection):
    return {
        "method": "map",
        "params": [source, projection]
    }


def sort_by(source, comparator):
    return {
        "method": "sortBy",
        "params": [source, comparator]
    }


def format_percent(value):
    return {
        "method": "formatPercent",
        "params": [value]
    }


def Image(src, style=None, class_name=None):
    return {
        "_type": "Image",
        "props": clean_null_terms({
            "src": src,
            "style": style,
            "className": class_name
        })
    }


def Avatar(icon, size=None, color=None):
    return {
        "_type": "Avatar",
        "props": clean_null_terms({
            "color": color,
            "icon": icon,
            "size": size
        })
    }
