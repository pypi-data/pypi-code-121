import plotnine as p9
import streamlit as st
from pandaslearn import pd

from .stglance import (
    display_baselinerf,
    display_data,
    display_data_cleanup,
    display_missingvalues,
    display_numeric_explorer,
    display_pandas_profile,
    display_summary,
)

st.set_page_config(layout="wide")

st.sidebar.markdown("# stglance sample app")
st.sidebar.markdown("## Upload data")
uploaded_csv = st.sidebar.file_uploader("Upload CSV", type="csv", key="csv")

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    # df = df.drop("Sl", axis=1)
    st.sidebar.write(f"{df.shape[0]} rows and {df.shape[1]} columns")

if not uploaded_csv:
    st.write("Please upload a csv file to continue")
    st.stop()

st.sidebar.markdown("---")
task = st.sidebar.radio(
    label="Select Task",
    options=["Exploratory Data Analysis", "Model Training", "Model Evaluation"],
    index=0,
)

if task == "Exploratory Data Analysis":
    expander01 = st.beta_expander("Display data", expanded=False)
    with expander01:
        display_data(df)

    expander01_xx = st.beta_expander("Data cleanup", expanded=False)
    with expander01_xx:
        df = display_data_cleanup(df)

    expander02 = st.beta_expander("Statistical summary (numeric)", expanded=False)
    with expander02:
        display_summary(df)

    expander03 = st.beta_expander("Pandas profile", expanded=False)
    with expander03:
        display_pandas_profile(df)

    expander04 = st.beta_expander("Missing values", expanded=False)
    with expander04:
        display_missingvalues(df)

    expander05 = st.beta_expander("Explore numeric variables", expanded=False)
    with expander05:
        display_numeric_explorer(df)

    expander06 = st.beta_expander("Baseline RF", expanded=False)
    with expander06:
        display_baselinerf(df)

tabular_app = st
