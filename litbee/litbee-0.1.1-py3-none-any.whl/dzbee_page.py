"""Display dzbee page."""
import pandas as pd
import streamlit as st
from loguru import logger as loggu
from logzero import logger


def dzbee_page():
    """Display dzbee page."""
    # st.title('dzbee')
    # st.write('Welcome to app1')

    try:
        df = st.session_state.ns.df
    except Exception as exc:
        logger.error(exc)
        df = pd.DataFrame([[""]])

    loggu.debug(" df ")
    st.table(df)
