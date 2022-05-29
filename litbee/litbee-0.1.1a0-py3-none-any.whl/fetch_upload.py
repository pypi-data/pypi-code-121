"""Fetch content from upload.

org ezbee_page.py.
"""
from functools import partial
from itertools import zip_longest

import logzero
import numpy as np
import pandas as pd
import streamlit as st
from dzbee import dzbee
from ezbee import ezbee, __version__
from debee import debee

# from ezbee.gen_pairs import gen_pairs  # aset2pairs?
from aset2pairs import aset2pairs
from fastlid import fastlid
from icecream import ic
from loguru import logger as loggu
from logzero import logger
from set_loglevel import set_loglevel
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
# from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit import session_state as state

logzero.loglevel(set_loglevel())


def fetch_upload():
    """Fetch content from upload."""

    # src_fileio tgt_fileio
    with st.form(key='upload_in_form'):
        sb_pick_files = st.expander("Pick two files", expanded=True)
        with sb_pick_files:
            col1, col2 = st.columns(2)
            with col1:
                src_fileio = st.file_uploader(
                    "Choose source file (utf8 txt)",
                    type=[
                        "txt",
                    ],
                    key="src_text",
                    # accept_multiple_files=True,
                    # accept_multiple_files=False,
                )

            with col2:
                tgt_fileio = st.file_uploader(
                    "Choose target file (utf8 txt)",
                    type=[
                        "txt",
                    ],
                    key="tgt_text",
                    # accept_multiple_files=True,
                )
        submitted = st.form_submit_button('Submit')

    if not submitted:
        return None

    # logger.debug(" len(src_fileio): %s", len(src_fileio))
    # logger.debug(" len(tgt_fileio): %s", len(tgt_fileio))

    if src_fileio:
        logger.debug(" type(src_fileio): %s", type(src_fileio))

        # for st.file_uploade accept_multiple_files=True
        if isinstance(src_fileio, list):
            logger.debug(" len(src_fileio): %s", len(src_fileio))
            filenames = []
            try:
                filenames = [elm.name for elm in src_fileio]  # type: ignore
            except Exception as exc:
                logger.error(exc)
            logger.debug("src_fileio  names: *%s*", filenames)

            # state.ns.src_fileio = src_fileio
            state.ns.src_file = src_fileio[-1].getvalue().decode()
            state.ns.src_filename = src_fileio[-1].name
        else:
            logger.debug("src_fileio.name: [%s]", src_fileio.name)
            filenames = [src_fileio.name]
            logger.debug("src_fileio  names: %s", filenames)

            # state.ns.src_fileio = src_fileio
            state.ns.src_file = src_fileio.getvalue().decode()
            state.ns.src_filename = src_fileio.name

    if tgt_fileio:
        if isinstance(tgt_fileio, list):
            logger.warning("not set to handle multiple files")
            logger.warning("set accept_multiple_files=False in the meantime")
        else:
            state.ns.tgt_file = tgt_fileio.getvalue().decode()
            state.ns.tgt_filename = tgt_fileio.name

    try:
        _ = state.ns.src_file.splitlines()
        list1 = [elm.strip() for elm in _ if elm.strip()]
        _ = state.ns.tgt_file.splitlines()
        list2 = [elm.strip() for elm in _ if elm.strip()]
    except Exception as exc:
        logger.error(exc)
        list1 = [""]
        list2 = [""]
    state.ns.list1 = list1[:]
    state.ns.list2 = list2[:]

    df = pd.DataFrame(zip_longest(list1, list2, fillvalue=""))
    try:
        df.columns = ["text1", "text2"]
    except Exception as exc:
        logger.debug("df: \n%s", df)
        logger.error("%s", exc)

    state.ns.df = df
    logger.debug("df: %s", df)

    # st.table(df)  # looks alright

    # stlyed pd dataframe?
    # bigger, no pagination
    # st.markdown(df.to_html(), unsafe_allow_html=True)

    # ag_grid smallish, editable, probably slower

    # if "df" not in globals() or "df" not in locals():
    if "df" not in locals():
        logger.debug(" df not defined, return")

    if df.empty:
        logger.debug(" df.empty, return")
        return None

    # df = pd.DataFrame([["", "", ""]], columns=["text1", "text2", "llh"])

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
    logger.debug("list1[:3]: %s", list1[:3])
    logger.debug("list2[:3]: %s", list2[:3])

    logger.info("Processing data... %s", state.ns.beetype)
    # if state.ns.beetype in ["ezbee", "dzbee"]:
    if state.ns.beetype in ["ezbee", "dzbee", "debee"]:
        # bug in json_de2zh.gen_cmat for dzbee and
        # fast_scores.gen_cmat  for ezbee
        # temp fix:
        if state.ns.beetype in ["dzbee"]:
            fastlid.set_languages = ["de", "zh"]
        elif state.ns.beetype in ["ezbee"]:
            fastlid.set_languages = ["en", "zh"]
        elif state.ns.beetype in ["debee"]:
            fastlid.set_languages = ["de", "en"]
        else:
            fastlid.set_languages = None

        fn = globals()[state.ns.beetype]
        logger.debug("type(fn): %s", fn)
        logger.debug("dir(fn): %s", dir(fn))
        logger.debug("fn.__doc__: %s", fn.__doc__)
        logger.debug("fn.__name__: %s", fn.__name__)
        logger.debug("ezbee __version__: %s", __version__)
        from inspect import getabsfile
        logger.debug("getabsfile(fn): %s", getabsfile(fn))

        try:
            # aset = ezbee/dzbee/debee
            aset = globals()[state.ns.beetype](
                list1,
                list2,
                # eps=eps,
                # min_samples=min_samples,
            )
        except Exception as e:
            # logger.error("aset = ezbee(...) exc: %s", e)
            logger.exception("aset = globals()[state.ns.beetype](...) exc: %s", e)
            aset = ""
            # st.write(e)
            st.write("Collecting inputs...")
            return None
    else:
        filename = inspect.currentframe().f_code.co_filename
        lineno = inspect.currentframe().f_lineno
        st.write(f"{state.ns.beetype} coming soon...{filenmae}:{lineno}")
        return None

    # fastlid changed logger.level to 20
    # turn back to loglevel
    logzero.loglevel(set_loglevel())
    if aset:
        logger.debug("aset: %s...%s", aset[:3], aset[-3:])
        # logger.debug("aset[:10]: %s", aset[:10])

    # st.write(aset)

    # aligned_pairs = gen_pairs(list1, list2, aset)
    aligned_pairs = aset2pairs(list1, list2, aset)
    if aligned_pairs:
        logger.debug("%s...%s", aligned_pairs[:3], aligned_pairs[-3:])
        # logger.debug("aligned_pairs[:20]: \n%s", aligned_pairs[:20])

    df_a = pd.DataFrame(aligned_pairs, columns=["text1", "text2", "llh"], dtype="object")

    st.table(df_a.astype(str))

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

    st.write("aligned (double-click a cell to edit, drag column header to adjust widths)")
    ag_df = AgGrid(
        # df,
        df_a,
        gridOptions=gridOptions,
        key="outside",
        reload_data=True,
        editable=True,
        # width="100%",  # width parameter is deprecated
        height=750,
        # fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.MODEL_CHANGED
    )
