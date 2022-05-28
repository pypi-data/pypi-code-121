"""Display ezbee page."""
from functools import partial

import logzero
import pandas as pd
import streamlit as st
from ezbee import ezbee
from ezbee.gen_pairs import gen_pairs
from loguru import logger as loggu
from logzero import logger
from set_loglevel import set_loglevel
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit import session_state as state

logzero.loglevel(set_loglevel())


def st_radio_horizontal(*args, **kwargs):
    """Trick to have horizontal st radio to simulate tabs."""
    col, _ = st.columns(2)
    with col:
        # st.write('<style> div[data-testid=column] > div > div > div > div.stRadio > div{flex-direction: row;}</style>', unsafe_allow_html=True)
        # return st.radio(*args, **kwargs)
        st.write(
            "<style> div[data-testid=stSidebar] > div > div > div > div > div > div > div.stRadio > div{flex-direction: row;}</style>",
            unsafe_allow_html=True,
        )
        return st.sidebar.radio(*args, **kwargs)


def ezbee_page():
    """Display ezbee page."""
    # st.title('ezbee')
    # st.write('### ezbee')
    # st.write('Welcome to app1')

    _ = """
    try:
        df = st.session_state.ns.df
    except Exception as exc:
        logger.error(exc)
        df = pd.DataFrame([[""]])
    # """

    # st.table(df)  # looks alright

    # stlyed pd dataframe?
    # bigger, no pagination
    # st.markdown(df.to_html(), unsafe_allow_html=True)

    # ag_grid smallish, editable, probably slower

    if "df" not in globals():
        logger.debug(" df not defined, return")
        return None

    df = pd.DataFrame([["", "", ""]], columns=["text1", "text2", "llh"])

    df_exp = st.expander("to be aligned", expanded=False)
    with df_exp:
        st.write(df)  # too small

    _ = """
    ag_exp = st.expander("done aligned")  # , expanded=False
    with ag_exp:
        agdf = AgGrid(
            df,
            # fit_columns_on_grid_load=True,
            editable=True,
            gridOptions=gridOptions,
            key="ag_exp",
        )
    # """

    list1 = [elm.strip() for elm in df.text1 if elm.strip()]
    list2 = [elm.strip() for elm in df.text2 if elm.strip()]
    logger.info("Processing data...")
    try:
        aset = ezbee(
            list1,
            list2,
            # eps=eps,
            # min_samples=min_samples,
        )
    except Exception as e:
        logger.error("aset = ezbee(...) exc: %s", e)
        aset = ""
        return None

    # fastlid changed logger.level is changed to 20
    # turn back to loglevel
    logzero.loglevel(set_loglevel())
    if aset:
        logger.debug("aset: %s...%s", aset[:3], aset[-3:])

    # st.write(aset)

    aligned_pairs = gen_pairs(list1, list2, aset)
    if aligned_pairs:
        logger.debug("%s...%s", aligned_pairs[:3], aligned_pairs[-3:])

    df_a = pd.DataFrame(aligned_pairs, columns=["text1", "text2", "llh"])

    # insert seq no
    df_a.insert(0, "sn", range(len(df_a)))

    gb = GridOptionsBuilder.from_dataframe(df_a)
    gb.configure_pagination(paginationAutoPageSize=True)
    options = {
        "resizable": True,
        "autoHeight": True,
        "wrapText": True,
        "editable": True,
    }
    gb.configure_default_column(**options)
    gridOptions = gb.build()

    st.write("aligned (double-click a cell to edit)")
    agdf = AgGrid(
        # df,
        df_a,
        gridOptions=gridOptions,
        key="outside",
        editable=True,
        width="100%",
        height=500,
        # fit_columns_on_grid_load=True,
    )
