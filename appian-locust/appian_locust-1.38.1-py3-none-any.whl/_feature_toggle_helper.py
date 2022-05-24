import re
from typing import Any, Dict, List, Tuple

from locust.clients import HttpSession

from ._feature_flag import FeatureFlag
from ._interactor import _Interactor
from ._locust_error_handler import test_response_for_error
from .logger import getLogger

log = getLogger(__name__)


def get_client_feature_toggles(interactor: _Interactor, session: HttpSession) -> Tuple[str, str]:
    """
    Given an authenticated user, recover the feature toggles from the minified javascript

    Returns: Returns feature flag if found, otherwise empty string

    """
    script_uri = _get_javascript_uri(interactor)
    if not script_uri:
        # TODO: Consider doing a graceful fallback here
        raise Exception(f"Could not find script uri to retrieve client feature toggles at {script_uri}")
    else:
        flag_str = _get_javascript_and_find_feature_flag(session,
                                                         script_uri)
        if flag_str:
            return _get_feature_flags_from_regex_match(flag_str)
        raise Exception(f"Could not find flag string within uri {script_uri}")


def _get_javascript_uri(interactor: _Interactor, headers: Dict[str, Any] = None) -> Any:
    """
    Gets the URI for the javascript file that contains the Feature Toggles
    """

    news_uri = interactor.replace_base_path_if_appropriate("/suite/sites")
    response = interactor.get_page(
        uri=news_uri, headers=headers, label="Login.Feature_Toggles.GetSites"
    )
    tempo_text = response.text
    relative_regex = r'<script src="(\/suite\/tempo\/ui\/sail-client\/sites-.*?.js)'
    cloud_regex = r'<script src="(https://web-assets.appiancloud.com/.*\/tempo\/ui\/sail-client\/sites-.*?.js)'
    for regex in [relative_regex, cloud_regex]:
        script_regex = interactor.replace_base_path_if_appropriate(regex)
        uri_match = re.search(script_regex, tempo_text)
        if uri_match:
            script_uri = uri_match.groups()[0]
            return script_uri
        log.info(f"Could not find feature toggle uri using regex {relative_regex}")
    return None


def _get_javascript_and_find_feature_flag(client: HttpSession, script_uri: str, headers: Dict[str, Any] = None) -> Any:
    """
    Read through minified javascript for feature flags
    """
    flag_str = None
    # Since this is a large request, read incrementally
    with client.get(
            script_uri,
            headers=headers,
            stream=True,
            name="Login.Feature_Toggles.GetJS",
            catch_response=True
    ) as res:
        test_response_for_error(res, script_uri)
        res.encoding = "utf-8"
        prev_chunk = ""
        """ Sample regexes for the feature flag are:
        var RAW_DEFAULT_FEATURE_FLAGS=0xdc9fffceebc;
        var RAW_DEFAULT_FEATURE_FLAGS=5802956083228348;
        var RAW_DEFAULT_FEATURE_FLAGS=jsbi__WEBPACK_IMPORTED_MODULE_10__["default"].BigInt("0b110100100111011100000111111111111111001110111010111100");
        """
        for chunk in res.iter_content(8192, decode_unicode=True):
            if flag_str:
                # Not reading the whole stream will throw errors, so continue reading once found
                continue
            script_regexes = [
                r'RAW_DEFAULT_FEATURE_FLAGS=(0x\w+|\d+);',
                r'RAW_DEFAULT_FEATURE_FLAGS=jsbi__WEBPACK_IMPORTED_MODULE_\d+__\["default"\].BigInt\("(0b[01]+)"\);',
            ]
            for script_regex in script_regexes:
                js_match = re.search(script_regex, prev_chunk + chunk)
                if js_match:
                    flag_str = js_match.groups()[0]
            prev_chunk = chunk
    return flag_str


def _get_feature_flags_from_regex_match(flag_str: str) -> Tuple[str, str]:
    """
    Coerce flags into proper format for sending as headers
    """

    if flag_str.startswith("0x"):
        flag_val = flag_str[2:]
    elif flag_str.startswith("0b"):
        flag_val = _to_hex_str(int(flag_str[2:], 2))
    else:
        flag_val = _to_hex_str(int(flag_str))
    old_flag_int_val = _truncate_flag_extended(int(flag_val, 16))
    old_flag_str = _to_hex_str(old_flag_int_val)
    return old_flag_str, flag_val


def _to_hex_str(flagVal: int) -> str:
    return ("%X" % flagVal).lower()


def _truncate_flag_extended(flag_extended: int) -> int:
    # This mask is a max int that will truncate the extended features to the size of an integer.
    old_flag_mask = 2147483647
    return flag_extended & old_flag_mask


def _create_override_flag_mask(flags_to_override: List[FeatureFlag]) -> int:
    """
    Given a list of flag enums from FeatureFlag, this will set that flag to 1 to override the default feature set.
    returns flag mask reflecting all the flags combined.
    """
    flags = 0
    for flag in flags_to_override:
        if isinstance(flag, FeatureFlag):
            flags |= (1 << flag.value)
    return flags


def override_default_flags(interactor: _Interactor, flags_to_override: List[FeatureFlag]) -> None:
    """
    Given a list of flag enums from FeatureFlag, override_default_flags gets the flag mask to
    set all of the flags to true, and it overrides the current feature flag extended value to
    set these flags to true.
    """
    override_flags_mask = _create_override_flag_mask(flags_to_override)
    feature_flag_with_override = int(interactor.client.feature_flag_extended, 16) | override_flags_mask
    interactor.client.feature_flag_extended = _to_hex_str(feature_flag_with_override)
    old_flag = _truncate_flag_extended(feature_flag_with_override)
    interactor.client.feature_flag = _to_hex_str(old_flag)


def set_mobile_feature_flags(interactor: _Interactor) -> None:
    """
    This overrides the feature flags to tell the service that the request is coming from a mobile device.
    """
    override_default_flags(interactor, [FeatureFlag.RECORD_LIST_FEED_ITEM_DTO])
