import streamlit as st
from lumipy.atlas.utility_functions import (
    _query_data_provider_metadata,
    _build_data_provider_factories,
)
from lumipy.client import get_client
from lumipy.atlas.atlas import Atlas
from typing import Optional, NoReturn

from lumipy.common.string_utils import random_globe
from lumipy.streamlit.reporter import Reporter
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from pandas import DataFrame


def get_atlas(container, secrets: Optional[str] = None, token: Optional[str] = None) -> Atlas:
    """Get luminesce data provider atlas instance.

    Args:
        container: streamlit container to display running query information in.
        secrets (Optional[str]): path to secrets file. If not supplied authentication information will be retrieved
        from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Atlas: the atlas instance.

    """
    title = container.empty()
    log = container.empty()

    title.subheader(f'[lumipy]: initial atlas setup{random_globe()}')

    report = Reporter(log)

    client = get_client(secrets, token)

    if 'atlas_df' not in st.session_state:
        report.update("Getting provider metadata... ")
        st.session_state['atlas_df'] = _query_data_provider_metadata(client)
        report.update('done!\n')

    at_df = st.session_state['atlas_df']

    report.update("Building the definition list... ")
    prov_defs = _build_data_provider_factories(at_df, client)
    report.update("done!\n")

    report.update("Building the atlas... ")
    atlas = Atlas(prov_defs, atlas_type='All available data providers')
    report.update("done!\n")
    report.empty()

    title.empty()

    return atlas


def run_and_report(query: BaseTableExpression, container) -> DataFrame:
    """Runs lumipy query and publishes the progress infomation to a given container in your streamlit app. Also
    implements a cancel button that will stop the monitoring process and delete the running query.

    Args:
        query (BaseTableExpression): lumipy query expression object to run.
        container: streamlit container to display running query information in.

    Returns:
        DataFrame: dataframe containing the result of the query.
    """

    title = container.empty()
    cancel = container.empty()
    log = container.empty()

    report = Reporter(log)

    title.subheader('[lumipy]: running query... 🚀')

    job = query.go_async()

    stop = cancel.button(key=job.ex_id, label='Cancel Query', on_click=job.delete)

    status = job.get_status()
    while status == 'WaitingForActivation':
        status = job.get_status()
        progress = f"{job.get_progress()}"
        report.empty()
        report.update(progress)

        if stop:
            report.empty()
            cancel.empty()
            title.empty()
            return DataFrame()

    report.update("\n\nFetching results... ")
    df = job.get_result()
    report.update("done!\n")

    report.empty()
    cancel.empty()
    title.empty()

    return df


def use_full_width() -> NoReturn:
    """Make streamlit use the full width of the screen.

    Use by calling this function at the top of your application.

    """

    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
