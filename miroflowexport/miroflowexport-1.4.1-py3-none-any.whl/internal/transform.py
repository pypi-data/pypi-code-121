from miroflowexport.internal import sanitize
from miroflowexport.internal.task import Task

SUPPORTED_TASK_TYPE_INFO_FIELDS = {
    "sticker": "text",
    "card": "title",
}

SUPPORTED_TASK_TYPE_STYLE_FIELDS = {
    "sticker": "style",
    "card": "style",
}

STYLE_BG_COLOR = "backgroundColor"
DEFAULT_STYLE_BG_COLOR = "#fff9b1"

def filter_json_to_supported_task_types(log, data_list_of_dicts):
    supported_types = [typename for typename in SUPPORTED_TASK_TYPE_INFO_FIELDS.keys()]
    log.debug("Filter response to supported types. Supported types are: {}".format(", ".join(supported_types)))
    filtered = [
        entry
        for entry in data_list_of_dicts
        if entry["type"] in supported_types
    ]
    log.debug("Received {} entries that are eligible to create tasks.".format(len(filtered)))
    return filtered

def get_color_or_default(json_entry, entry_type):
    if not SUPPORTED_TASK_TYPE_STYLE_FIELDS[entry_type] in json_entry.keys():
        return DEFAULT_STYLE_BG_COLOR

    style = json_entry[SUPPORTED_TASK_TYPE_STYLE_FIELDS[entry_type]]

    if not STYLE_BG_COLOR in style.keys():
        return DEFAULT_STYLE_BG_COLOR

    bg_color = style[STYLE_BG_COLOR]
    if not bg_color:
        return DEFAULT_STYLE_BG_COLOR

    return bg_color

def convert_json_entry_to_task_entry(log, json_entry):
    entry_type = json_entry["type"]
    if not entry_type in SUPPORTED_TASK_TYPE_INFO_FIELDS.keys():
        log.error("Cannot convert widget of type '{}' into a task. This one is not supported.".format(entry_type))
        return None

    full_name = json_entry[SUPPORTED_TASK_TYPE_INFO_FIELDS[entry_type]]
    card_name = sanitize.trim_to_name(full_name)
    card_effort = sanitize.trim_to_effort(full_name)
    card_id = json_entry["id"]
    card_color = get_color_or_default(json_entry, entry_type)
    task = Task(card_id, card_name, card_effort, color_hex_code=card_color)
    return task

def create_pairs_from_link_widgets(log, tasks, links):
    pairs_of_ids = [
        (
            link["startWidget"]["id"], 
            link["endWidget"]["id"], 
            link["id"]
        )
        for link in links
        if "id" in link["startWidget"].keys()
        if "id" in link["endWidget"].keys()
    ]
    pairs = []
    for (id_left, id_right, id_link) in pairs_of_ids:
        if not id_left in tasks.keys():
            log.debug("Cannot find start widget with ID {} for connection with ID {}.".format(id_left, id_link))
            continue
        if not id_right in tasks.keys():
            log.debug("Cannot find end widget with ID {} for connection with ID {}.".format(id_right, id_link))
            continue

        pairs += [(tasks[id_left], tasks[id_right])]
    return pairs
