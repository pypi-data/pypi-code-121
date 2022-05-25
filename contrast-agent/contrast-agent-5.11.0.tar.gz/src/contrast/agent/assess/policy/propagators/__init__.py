# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from . import stream_propagator
from .base_propagator import BasePropagator, SUPPORTED_TYPES
from .append_propagator import AppendPropagator
from .center_propagator import CenterPropagator
from .codecs_splat_propagator import CodecsSplatPropagator
from .format_propagator import FormatPropagator
from .join_propagator import JoinPropagator
from .json_propagator import JsonPropagator
from .keep_propagator import KeepPropagator
from .prepend_propagator import PrependPropagator
from .replace_propagator import ReplacePropagator
from .safe_join_propagator import SafeJoinPropagator
from .safe_join_propagator_django import SafeJoinDjangoPropagator
from .slice_propagator import SlicePropagator
from .splat_propagator import SplatPropagator
from .split_propagator import SplitPropagator
from .reductive_propagator import ReductivePropagator
from .regex_propagator import RegexFindallPropagator, RegexSplitPropagator
from .db_write_propagator import DBWritePropagator
from .encode_html_splat_propagator import EncodeHtmlSplatPropagator
from .repr_propagator import ReprPropagator


APPEND_ACTION = "APPEND"
CENTER_ACTION = "CENTER"
CODECS_SPLAT_ACTION = "CODECS_SPLAT"
FORMAT_ACTION = "FORMAT"
JOIN_ACTION = "JOIN"
JSON_ACTION = "JSON"
KEEP_ACTION = "KEEP"
PREPEND_ACTION = "PREPEND"
REGEX_FINDALL_ACTION = "REGEX_FINDALL"
REGEX_SPLIT_ACTION = "REGEX_SPLIT"
REPLACE_ACTION = "REPLACE"
REPR_ACTION = "REPR"
REMOVE_ACTION = "REMOVE"
SAFE_JOIN_ACTION = "SAFE_JOIN"
SAFE_JOIN_DJANGO_ACTION = "SAFE_JOIN_DJANGO"
SLICE_ACTION = "SLICE"
SPLAT_ACTION = "SPLAT"
SPLIT_ACTION = "SPLIT"
TAG_ACTION = "TAG"
DB_WRITE_ACTION = "DB_WRITE"
ENCODE_HTML_SPLAT_ACTION = "ENCODE_HTML_SPLAT"

# These propagators should not check the length of the target in order to determine
# whether to propagate.
IGNORE_LENGTH_ACTIONS = [DB_WRITE_ACTION, KEEP_ACTION, REPLACE_ACTION, SPLAT_ACTION]

PROPAGATOR_ACTIONS = {
    KEEP_ACTION: KeepPropagator,
    REPLACE_ACTION: ReplacePropagator,
    REMOVE_ACTION: ReductivePropagator,
    PREPEND_ACTION: PrependPropagator,
    APPEND_ACTION: AppendPropagator,
    CENTER_ACTION: CenterPropagator,
    SPLAT_ACTION: SplatPropagator,
    FORMAT_ACTION: FormatPropagator,
    SLICE_ACTION: SlicePropagator,
    JOIN_ACTION: JoinPropagator,
    SPLIT_ACTION: SplitPropagator,
    REGEX_FINDALL_ACTION: RegexFindallPropagator,
    REGEX_SPLIT_ACTION: RegexSplitPropagator,
    JSON_ACTION: JsonPropagator,
    ENCODE_HTML_SPLAT_ACTION: EncodeHtmlSplatPropagator,
    REPR_ACTION: ReprPropagator,
    DB_WRITE_ACTION: DBWritePropagator,
    SAFE_JOIN_ACTION: SafeJoinPropagator,
    SAFE_JOIN_DJANGO_ACTION: SafeJoinDjangoPropagator,
    CODECS_SPLAT_ACTION: CodecsSplatPropagator,
}

STREAM_ACTIONS = {
    "read": stream_propagator.propagate_stream_read,
    "read1": stream_propagator.propagate_stream_read,
    "readline": stream_propagator.propagate_stream_read,
    "readlines": stream_propagator.propagate_stream_readlines,
    "getvalue": stream_propagator.propagate_stream_getvalue,
}
