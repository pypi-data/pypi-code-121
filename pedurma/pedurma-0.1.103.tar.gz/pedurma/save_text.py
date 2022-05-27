import copy
from pathlib import Path

from openpecha.blupdate import Blupdate, update_ann_layer
from openpecha.github_utils import commit
from openpecha.utils import download_pecha, dump_yaml, load_yaml

from pedurma.texts import get_pecha_paths, remove_last_pages, serialize_text_obj
from pedurma.utils import from_yaml, notes_to_original_view


def get_old_base(pecha_opf_path, pecha_id, text_base_span):
    """Generate old base text in which text is located

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id 
        text_base_span (list): list of volume ids in which text is located

    Returns:
        dict: volid as key and base as value
    """
    old_bases = {}
    for base_name in text_base_span:
        old_bases[base_name] = Path(
            f"{pecha_opf_path}/{pecha_id}.opf/base/{base_name}.txt"
        ).read_text(encoding="utf-8")
    return old_bases


def get_old_text_base(old_pecha_idx, old_base, text_id, base_name):
    """Return old text base

    Args:
        old_pecha_idx (dict): old index
        old_base (dict): old vol base and its vol id
        text_id (str): text id
        text_base (str): text vol id

    Returns:
        str: text basetext in that volume
    """
    text_span = old_pecha_idx["annotations"][text_id]["span"]
    for base_span in text_span:
        if base_span["base"] == base_name:
            return old_base[base_span["start"] : base_span["end"] + 1]
    return ""


def get_new_base(old_bases, old_pecha_idx, text_obj):
    """Return new base text by replacing updated text from text object

    Args:
        old_bases (dict): old vol and its id
        old_pecha_idx (dict): old pecha index
        text_obj (obj): text object

    Returns:
        dict: new basetext and its id
    """
    new_bases = {}
    new_text = serialize_text_obj(text_obj)
    for base_name, new_text_base in new_text.items():
        old_base = old_bases[base_name]
        old_text_base = get_old_text_base(
            old_pecha_idx, old_base, text_obj.id, base_name
        )
        old_text_base = old_text_base.strip()
        new_text_base = new_text_base.strip()
        new_base = old_base.replace(old_text_base, new_text_base)
        new_bases[base_name] = new_base
    return new_bases


def get_text_base_span(pecha_idx, text_uuid):
    """Return list of volume ids in which text span

    Args:
        pecha_idx (dict): pecha index
        text_uuid (uuid): text uuid

    Returns:
        list: vol ids
    """
    text_base_span = []
    for span in pecha_idx["annotations"][text_uuid]["span"]:
        base_name = span["base"]
        text_base_span.append(base_name)
    return text_base_span


def update_base(pecha_opf_path, pecha_id, text_obj, old_pecha_idx):
    """Update base text using text obj

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        text_obj (obj): text object
        old_pecha_idx (dict): old pecha index
    """
    text_base_span = get_text_base_span(old_pecha_idx, text_obj.id)
    old_bases = get_old_base(pecha_opf_path, pecha_id, text_base_span)
    new_bases = get_new_base(old_bases, old_pecha_idx, text_obj)
    for base_name, new_base in new_bases.items():
        Path(f"{pecha_opf_path}/{pecha_id}.opf/base/{base_name}.txt").write_text(
            new_base, encoding="utf-8"
        )
        print(f"INFO: {base_name} base updated..")


def get_old_layers(pecha_opf_path, pecha_id, vol_id):
    """Return all the layers belonging in volume

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        vol_id (str): volume id

    Returns:
        dict: layer name as key and layer annotations as value
    """
    old_layers = {}
    layer_paths = list(
        Path(f"{pecha_opf_path}/{pecha_id}.opf/layers/{vol_id}").iterdir()
    )
    for layer_path in layer_paths:
        layer_name = layer_path.stem
        layer_content = from_yaml(layer_path)
        old_layers[layer_name] = layer_content
    return old_layers


def update_layer(pecha_opf_path, pecha_id, vol_id, old_layers, updater):
    """Update particular layers belonging in given volume id 

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        vol_id (str): volume id
        old_layers (dict): layer name as key and annotations as value
        updater (obj): updater object
    """
    for layer_name, old_layer in old_layers.items():
        if layer_name not in ["Pagination", "Durchen", "PedurmaNote"]:
            update_ann_layer(old_layer, updater)
            new_layer_path = Path(
                f"{pecha_opf_path}/{pecha_id}.opf/layers/{vol_id}/{layer_name}.yml"
            )
            dump_yaml(old_layer, new_layer_path)
            print(f"INFO: {vol_id} {layer_name} has been updated...")


# def update_old_layers(pecha_opf_path, pecha_id, text_obj, old_pecha_idx):
#     """Update all the layers related to text object

#     Args:
#         pecha_opf_path (str): pecha opf path
#         pecha_id (str): pecha id
#         text_obj (obj): text object
#         old_pecha_idx (dict): old pecha index
#     """
#     text_base_span = get_text_base_span(old_pecha_idx, text_obj.id)
#     old_vols = get_old_vol(pecha_opf_path, pecha_id, text_base_span)
#     new_vols = get_new_vol(old_vols, old_pecha_idx, text_obj)
#     for (vol_id, old_vol_base), (_, new_vol_base) in zip(
#         old_vols.items(), new_vols.items()
#     ):
#         updater = Blupdate(old_vol_base, new_vol_base)
#         old_layers = get_old_layers(pecha_opf_path, pecha_id, vol_id)
#         update_layer(pecha_opf_path, pecha_id, vol_id, old_layers, updater)


def update_other_text_index(
    old_pecha_idx, text_id, cur_base_offset, base_name, pecha_meta
):
    check_flag = False
    for text_uuid, text in old_pecha_idx["annotations"].items():
        if check_flag:
            for vol_walker, vol_span in enumerate(text["span"]):
                if vol_span["base"] == base_name:
                    old_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "start"
                    ] += cur_base_offset
                    old_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "end"
                    ] += cur_base_offset
                elif (
                    pecha_meta["source_metadata"]["base"][vol_span["base"]]["order"]
                    > pecha_meta["source_metadata"]["base"][base_name]["order"]
                ):
                    return old_pecha_idx
        if text_uuid == text_id:
            check_flag = True
    return old_pecha_idx


def update_index(pecha_opf_path, pecha_id, text_obj, old_pecha_idx, pecha_meta):
    """Update pecha index according to text obj content

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        text_obj (obj): text object
        old_pecha_idx (dict): old pecha index

    Returns:
        dict: new pecha index
    """
    text_base_span = get_text_base_span(old_pecha_idx, text_obj.id)
    old_bases = get_old_base(pecha_opf_path, pecha_id, text_base_span)
    new_bases = get_new_base(old_bases, old_pecha_idx, text_obj)
    for (base_name, old_base), (_, new_base) in zip(
        old_bases.items(), new_bases.items()
    ):
        cur_base_order = pecha_meta["source_metadata"]["base"][base_name]["order"]
        check_next_text = True
        cur_base_offset = len(new_base) - len(old_base)
        if cur_base_offset != 0:
            for base_walker, base_span in enumerate(
                old_pecha_idx["annotations"][text_obj.id]["span"]
            ):
                if base_span["base"] == base_name:
                    old_pecha_idx["annotations"][text_obj.id]["span"][base_walker][
                        "end"
                    ] += cur_base_offset
                elif (
                    pecha_meta["source_metadata"]["base"][base_span["base"]]["order"]
                    > cur_base_order
                ):
                    check_next_text = False
                    break
            if check_next_text:
                old_pecha_idx = update_other_text_index(
                    old_pecha_idx, text_obj.id, cur_base_offset, base_name, pecha_meta
                )
    return old_pecha_idx


def update_durchen_span(durchen_layer, text, base_name, char_walker):
    durchen_start = char_walker
    for note in text.notes:
        if note.base_name == base_name:
            char_walker += len(note.content) + 2
    durchen_end = char_walker - 3
    for id, ann in durchen_layer["annotations"].items():
        durchen_layer["annotations"][id]["span"]["start"] = durchen_start
        durchen_layer["annotations"][id]["span"]["end"] = durchen_end
        break
    return durchen_layer


def update_durchen_layer(text, pecha_id, pecha_opf_path):
    base_name = text.pages[0].base_name
    durchen_layer, durchen_path = get_layer(
        pecha_opf_path, pecha_id, base_name, "Durchen"
    )
    char_walker = 0
    for page in text.pages:
        if base_name != page.base_name:
            update_durchen_span(durchen_layer, text, base_name, char_walker)
            char_walker = 0
            base_name = page.base_name
            dump_yaml(durchen_layer, durchen_path)
            durchen_layer, durchen_path = get_layer(
                pecha_opf_path, pecha_id, base_name, "Durchen"
            )
        char_walker += len(page.content) + 2
    update_durchen_span(durchen_layer, text, base_name, char_walker)
    dump_yaml(durchen_layer, durchen_path)


def update_page_span(page, prev_page_end, old_page_ann):
    new_page_len = len(page.content)
    new_page_end = prev_page_end + new_page_len
    old_page_ann["span"]["start"] = prev_page_end
    old_page_ann["span"]["end"] = new_page_end
    return old_page_ann, new_page_end + 2


def update_note_span(pagination_layer, text, prev_page_end):
    for note in text.notes:
        old_page_ann = pagination_layer["annotations"].get(note.id, {})
        if old_page_ann:
            pagination_layer["annotations"][note.id], prev_page_end = update_page_span(
                note, prev_page_end, old_page_ann
            )


def get_layer(pecha_opf_path, pecha_id, base_name, layer_name):
    layer_path = (
        Path(pecha_opf_path)
        / f"{pecha_id}.opf"
        / "layers"
        / base_name
        / f"{layer_name}.yml"
    )
    layer = load_yaml(layer_path)
    return layer, layer_path


# def get_updated_page_number(old_span, new_pg_ann, updated_pg_number):
#     if (
#         updated_pg_number != 0
#         and old_span["start"] != new_pg_ann["span"]["start"]
#         or old_span["end"] != new_pg_ann["span"]["end"]
#     ):
#         return new_pg_ann["imgnum"]
#     else:
#         return updated_pg_number


def update_page_layer(text, pecha_id, pecha_opf_path):
    base_name = text.pages[0].base_name
    pagination_layer, pagination_path = get_layer(
        pecha_opf_path, pecha_id, base_name, "Pagination"
    )
    pagination_annotations = pagination_layer.get("annotations", {})
    prev_page_end = 0
    for page in text.pages:
        if base_name != page.base_name:
            update_note_span(pagination_layer, text, prev_page_end)
            prev_page_end = 0
            base_name = page.base_name
            dump_yaml(pagination_layer, pagination_path)
            pagination_layer, pagination_path = get_layer(
                pecha_opf_path, pecha_id, base_name, "Pagination"
            )
            pagination_annotations = pagination_layer.get("annotations", {})
        old_page_ann = pagination_annotations[page.id]
        old_span = copy.deepcopy(old_page_ann["span"])
        pagination_layer["annotations"][page.id], prev_page_end = update_page_span(
            page, prev_page_end, old_page_ann
        )
    update_note_span(pagination_layer, text, prev_page_end)
    dump_yaml(pagination_layer, pagination_path)


def save_text(pecha_id, text_obj, pecha_opf_path=None, **kwargs):
    """Update pecha opf according to text object content

    Args:
        pecha_id (str): pecha id
        text_obj (text obj): text object
        pecha_opf_path (str, optional): pecha path. Defaults to None.

    Returns:
        path: pecha opf path
    """
    if not pecha_opf_path:
        pecha_opf_path = download_pecha(pecha_id, **kwargs)
    old_pecha_idx = from_yaml(Path(f"{pecha_opf_path}/{pecha_id}.opf/index.yml"))
    pecha_meta = from_yaml(Path(f"{pecha_opf_path}/{pecha_id}.opf/meta.yml"))
    prev_pecha_idx = copy.deepcopy(old_pecha_idx)
    text_obj = remove_last_pages(text_obj)
    new_pecha_idx = update_index(
        pecha_opf_path, pecha_id, text_obj, old_pecha_idx, pecha_meta
    )
    # update_old_layers(pecha_opf_path, pecha_id, text_obj, prev_pecha_idx)
    update_base(pecha_opf_path, pecha_id, text_obj, prev_pecha_idx)
    update_page_layer(text_obj, pecha_id, pecha_opf_path)
    update_durchen_layer(text_obj, pecha_id, pecha_opf_path)
    new_pecha_idx_path = Path(f"{pecha_opf_path}/{pecha_id}.opf/index.yml")
    dump_yaml(new_pecha_idx, new_pecha_idx_path)
    # if commit_flag:
    #     commit(pecha_opf_path, f"Page no {updated_page_number} is updated")
    return pecha_opf_path


def get_pedurma_text_mapping(pedurma_text_obj):
    """Pedurma text obj are parse and added pecha path

    Args:
        pedurma_text_obj (obj): pedurma text obj

    Returns:
        dict: ocr engine as key and associated text data as value
    """
    pedurma_text_mapping = {}
    pecha_paths = get_pecha_paths(text_id=pedurma_text_obj.text_id)
    for pecha_src, pecha_path in pecha_paths.items():
        if pecha_src == "namsel":
            text_obj = pedurma_text_obj.namsel
        else:
            text_obj = pedurma_text_obj.google
        pedurma_text_mapping[pecha_src] = {
            "pecha_id": Path(pecha_path).stem,
            "text_obj": text_obj,
            "pecha_path": pecha_path,
        }
    return pedurma_text_mapping


def save_pedurma_text(pedurma_text_obj, pedurma_text_mapping=None):
    """Save changes to respective pedurma opfs according to pedurma text object content

    Args:
        pedurma_text_obj (obj): pedurma text object
        pedurma_text_mapping (dict, optional): pedurma text data mapping. Defaults to None.
    """
    if not pedurma_text_mapping:
        pedurma_text_mapping = get_pedurma_text_mapping(pedurma_text_obj)
    for ocr_engine, pedurma_text in pedurma_text_mapping.items():
        text_obj = pedurma_text["text_obj"]
        text_obj.notes = notes_to_original_view(text_obj.notes, ocr_engine)
        save_text(pedurma_text["pecha_id"], text_obj, pedurma_text["pecha_path"])
