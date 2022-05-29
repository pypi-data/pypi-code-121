"""Load content."""
# pylint: disable=invalid-name
from functools import partial

import streamlit as st
from loguru import logger as loggu
from logzero import logger
from streamlit import session_state as state

from litbee.fetch_paste import fetch_paste

# from litbee.ezbee_page import ezbee_page
# from litbee.dzbee_page import dzbee_page
# from litbee.xbee_page import xbee_page
from litbee.fetch_upload import fetch_upload
from litbee.fetch_urls import fetch_urls
from litbee.files2df import files2df
from litbee.utils import instructions, sb_front_cover


def options():
    """Load content."""
    sb_front_cover()

    try:
        _ = state.ns.df
        state.ns.count += 1
        logger.debug(" run: %s", state.ns.count)
    except AttributeError:
        logger.debug("first run")
        # df = files2df("data/en.txt", "data/zh.txt")
        df = files2df("data/test_en.txt", "data/test_zh.txt")
        state.ns.count = 1
        state.ns.df = df

    # horizonral radio
    st.sidebar.write(
        "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
        unsafe_allow_html=True,
    )

    beetype_list = ["ezbee", "dzbee", "debee", "xbee"]

    col1, col2 = st.columns(2)

    with col1:
        beetype = st.sidebar.radio("Pick a bee", beetype_list)
        state.ns.beetype = beetype

    # if beetype not in ["ezbee", "dzbee"]:
    if beetype not in ["ezbee", "dzbee", "debee"]:
        st.write("Coming soon")
        return None

    # multi-page setup
    menu = {
        "upload": fetch_upload,
        "paste": fetch_paste,
        "urls": fetch_urls,
    }

    with col2:
        source = st.sidebar.radio("Source", [*menu])

    # item = menu[source]
    # item()

    # fetch_upload()/fetch_paste()/fetch_urls()
    menu[source]()

    # if hasattr(state.ns, "df"): delattr(state.ns, "df")

    # logger.debug(" state.ns: %s", state.ns)

    # show state.ns[:6]
    loggu.debug(f" state.ns.list: {state.ns.list}")

    _ = map(partial(getattr, state.ns), state.ns.list[:3])
    logger.debug(" state.ns.list[:3]: %s", str([*_]))

    st.write(f"run: {state.ns.count}")
    loggu.debug(f"run: {state.ns.count}")

    fileio_slot = st.empty()
