# -*- coding: utf-8 -*-
"""Query PDB for structures."""
# standard library imports
import json
import operator
import time
from copy import deepcopy
from functools import reduce
from itertools import product as iproduct
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pandas as pd
from Bio import SeqIO  # type: ignore
from Bio.Seq import Seq  # type: ignore
from Bio.SeqRecord import SeqRecord  # type: ignore
from dotli import Dotli  # type: ignore
from gql import Client
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from loguru import logger
from rcsbsearch import Attr as RCSBAttr  # type: ignore
from rcsbsearch import rcsb_attributes  # type: ignore
from rcsbsearch.search import Terminal  # type: ignore
from statsdict import Stat  # type: ignore

from .common import APP
from .common import NAME
from .common import RCSB_DATA_GRAPHQL_URL
from .common import STATS
from .config import read_config

RCSB_ATTRIBUTES = [a.attribute for a in rcsb_attributes]
OPERATOR_DICT = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}
ID_FIELD = "rcsb_id"
ID_FIELD_LEN = 4
SUB_FIELD = "sub"
RESOLUTION_FIELD = "rcsb_entry_info.diffrn_resolution_high.value"
RESOLUTION_LABEL = "resolution, Å"
SEQ_FIELD = "polymer_entities.entity_poly.pdbx_seq_one_letter_code_can"
NAME_FIELD = "polymer_entities.rcsb_polymer_entity.pdbx_description"
FIXED_METADATA = [
    {"field": ID_FIELD, "type": "str", "name": "rcsb_id"},
    {"field": RESOLUTION_FIELD, "type": "float", "name": RESOLUTION_LABEL},
    {"field": SEQ_FIELD, "type": "seq", "name": "seq"},
    {"field": NAME_FIELD, "type": "str", "name": "macromolecule"},
]
METADATA_TIMEOUT = 120
CONFIG = read_config(NAME)


@APP.command()
def print_rcsb_attributes() -> None:
    """Print RCSB attributes list."""
    for attrib in RCSB_ATTRIBUTES:
        print(f"{attrib}")


def check_against_rcsb_attributes(field: str) -> None:
    """Raise Value Error if field is not a known RCSB attribute."""
    for sub_attr in RCSB_ATTRIBUTES:
        if sub_attr in field:
            return
    raise ValueError(f'Unrecognized RCSB field "{field}"')


def rcsb_search_query(
    field: str, op_str: str, val: Union[int, float, str]
) -> Terminal:
    """Convert query specifiers to queries."""
    check_against_rcsb_attributes(field)
    try:
        op = OPERATOR_DICT[op_str]
    except KeyError:
        raise ValueError(
            f'Unrecognized RCSB operator string "{op_str}"'
        ) from None
    return op(RCSBAttr(field), val)


def construct_rcsb_structure_query(
    id_list: List[str], fields: List[str]
) -> str:
    """Construct an GraphQL query string for RCSB structure fields.

    We use the flattened field names from rcsbsearch in dot-separated form
    for input because they are much easier to specify and check.
    """
    for field in fields:
        check_against_rcsb_attributes(field)
    unflattener = Dotli().unflatten
    fixed_query_dict = unflattener(dict.fromkeys(fields, 0))
    fixed_query_str = json.dumps(fixed_query_dict, indent=1)
    query_set = (
        fixed_query_str.replace(": 0", "")
        .replace(":", "")
        .replace('"', "")
        .replace(",", "")
    )
    id_list_str = json.dumps(id_list)
    query_str = f"""query {{
  entries(entry_ids: {id_list_str})
  {query_set}
}}"""
    return query_str


def yield_nested_lists(
    d: Dict[str, Any], prefix: Union[List[str], None] = None
) -> Iterator[Tuple[List[str], Any]]:
    """Recursively yield all lists in a nested dictionary."""
    if prefix is None:
        prefix = []
    for k, v in d.items():
        if isinstance(v, dict):
            yield from yield_nested_lists(v, prefix + [k])
        elif type(v) is list:
            yield (prefix + [k], v)
            for i in v:
                if type(i) is dict:
                    yield from yield_nested_lists(i, prefix + [k])


def set_nested(
    d: Dict[str, Any], keys: List[str], value: Any
) -> Dict[str, Any]:
    """Set a value in a nested dictionary using a list of keys."""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
    return d


def delist_responses(
    responses: Tuple[Dict[str, Any], ...]
) -> List[Dict[str, Any]]:
    """Replace lists inside query with iteration over values."""
    out_list = []
    for response in responses:
        list_kvs = list(yield_nested_lists(response))
        if len(list_kvs) == 0:  # no lists contained
            out_list.append(deepcopy(response))
        else:
            list_keys = [k for k, v in list_kvs]
            for sub, val_tuple in enumerate(
                iproduct(*[v for k, v in list_kvs])
            ):
                new_response = deepcopy(response)
                new_response[SUB_FIELD] = sub
                [
                    set_nested(new_response, key, val_tuple[i])
                    for i, key in enumerate(list_keys)
                ]
                out_list.append(new_response)
    return out_list


def delete_unknown_fields(
    rawdict: Dict[str, Any], known_fields: List[str]
) -> Dict[str, Any]:
    """Delete any entries with key not known, flat dict only."""
    unknown = [k for k in rawdict.keys() if k not in known_fields]
    for item in unknown:
        logger.debug(f"deleting unknown key {item} in {rawdict[ID_FIELD]}")
        del rawdict[item]
    return rawdict


def unify_id(id: str, sub_id: str) -> str:
    """Make concatenated ID and sub ID, if subID exists."""
    if pd.isnull(sub_id):
        return id
    return f"{id}.{int(sub_id)}"


@APP.command()
def rcsb_metadata(
    id_list: List[str], show_frame: Optional[bool] = False
) -> Tuple[pd.DataFrame, List[Any]]:
    """Query the RCSB GraphQL endpoint for metadata.

    Example:
        rcsb_metadata 1STP 2JEF
    """
    myconfig = CONFIG.metadata
    # Do asynchronous I/O to RCSB.
    transport = AIOHTTPTransport(url=RCSB_DATA_GRAPHQL_URL)
    # Create a GraphQL client.
    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,
        execute_timeout=METADATA_TIMEOUT,
    )
    # Construct the query from a query string.
    metadata_list = FIXED_METADATA + myconfig.extras
    query_fields = [f["field"] for f in metadata_list]
    result_fields = query_fields + [SUB_FIELD]
    query_str = construct_rcsb_structure_query(id_list, query_fields)
    logger.debug(f"GraphQL query={query_str}")
    query = gql(query_str)
    # Execute the query.
    responses = client.execute(query)["entries"]
    # RCSB's GraphQL returns a rather complex object
    # with both trivial (one per entry) and non-trivial
    # lists (e.g., multiple sequences) to be interated
    # over.  One response may turn into more than one
    # result.
    results = delist_responses(responses)
    flattener = Dotli().flatten
    results = [flattener(e) for e in results]
    if myconfig.delete_unknown_fields:
        # If a query field returns "none" and it is
        # the only field in that query category,
        # the parent field will get returned by
        # itself.  Deleting all unknown fields
        # prevents putting parents in the output
        # table.
        results = [delete_unknown_fields(e, result_fields) for e in results]
    # Now create a data frame from the list of result dictionaries.
    df = pd.DataFrame.from_dict(results)  # type:ignore
    seq_list = [
        SeqRecord(Seq(seq), unify_id(id, sub), description=desc)
        for seq, id, sub, desc in zip(
            df[SEQ_FIELD], df[ID_FIELD], df[SUB_FIELD], df[NAME_FIELD]
        )
        if pd.notnull(seq)
    ]
    df["has_seq"] = [pd.notnull(seq) for seq in df[SEQ_FIELD]]
    df = df.rename(columns={f["field"]: f["name"] for f in metadata_list})
    del df["seq"]
    if myconfig.delete_unknown_fields:
        # order output columns in order in extras
        col_order = [SUB_FIELD] + [
            f["name"] for f in metadata_list if f["name"] in df.columns
        ]
        df = df[col_order]
    if show_frame:
        print(df)
    return df, seq_list


@APP.command()
@STATS.auto_save_and_report
def query(
    set_name: str,
    neutron_only: Optional[bool] = False,
    query_only: Optional[bool] = False,
) -> None:
    """Query PDB for structures as defined in config file."""
    myconfig = CONFIG.query
    extra_queries = [rcsb_search_query(**e) for e in myconfig.extras]
    if neutron_only:
        subtypes = ["neutron"]
    else:
        subtypes = myconfig.subtypes
    all_keys = []
    all_types = []
    metadata_frames = []
    for subtype in subtypes:
        resolution = myconfig[subtype].resolution
        label = myconfig[subtype].label
        STATS[f"{label}_resolution"] = Stat(
            resolution, units="Å", desc="Minimum resolution"
        )
        query_list = (
            [rcsb_search_query(RESOLUTION_FIELD, "<=", resolution)]
            + [rcsb_search_query(**e) for e in myconfig[subtype].extras]
            + extra_queries
        )
        combined_query = reduce(operator.iand, query_list)
        start_time = time.time()
        results = list(combined_query().iquery())
        n_results = len(results)
        if not query_only:
            category_frame, seqs = rcsb_metadata(results)
            category_frame["category"] = label
            metadata_frames.append(category_frame)
        elapsed_time = round(time.time() - start_time, 1)
        logger.info(
            f"RCSB returned {n_results} {label} structures <= {resolution} Å"
            + f" in {elapsed_time} s."
        )
        STATS[f"{label}_structures"] = Stat(
            n_results, desc=f"{label} structures in PDB"
        )
        all_keys += results
        all_types += [subtype] * n_results
    STATS["total_structures"] = Stat(len(all_keys), desc="Total structures")
    if not query_only:
        df = pd.concat(metadata_frames)
        df.sort_values(by=RESOLUTION_LABEL, inplace=True)
        STATS["metadata_cols"] = Stat(
            len(df.columns), desc="# of metadata fields"
        )
        df.to_csv(set_name + ".tsv", sep="\t")
        STATS["missing_seqs"] = Stat(
            len(df) - len(seqs), desc="# of RCSB entries w/o sequence"
        )
        SeqIO.write(seqs, set_name + ".fa", "fasta")
