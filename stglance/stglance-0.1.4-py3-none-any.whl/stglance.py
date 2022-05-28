import matplotlib.pyplot as plt
import missingno as msno
import numpy as np

# import pandas_profiling # this causes segfault!
import plotnine as p9
import scipy as sp
import streamlit as st
from pandaslearn import pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from streamlit_pandas_profiling import st_profile_report


def display_data(df):
    st.markdown(f"**{df.shape[0]}** rows and **{df.shape[1]}** columns")
    st.write(df)
    col1, col2 = st.beta_columns(2)
    with col1:
        st.header("Numeric variables")
        numerics = ""
        for item in df.ml.numerical_ix:
            numerics += f"\n* {item}"
        st.markdown(numerics)

    with col2:
        st.header("Categorical variables")
        categoricals = ""
        for item in df.ml.categorical_ix:
            categoricals += f"\n* {item}"
        st.markdown(categoricals)


def display_data_cleanup(df):
    col1, col2 = st.beta_columns(2)
    with col1:
        st.write("Placeholder: column drop recommendations to be displayed later.")
    with col2:
        form = st.form(key="column_drop_form")
        cols = form.multiselect(
            label="Choose variables to be dropped",
            options=list(df.columns),
        )
        submit_button = form.form_submit_button(label="Submit")
        if submit_button:
            df = df.drop(cols, axis=1)
    st.write(f"Column(s) dropped: {cols}")
    st.write(f"Current columns: {list(df.columns)}")
    return df


def display_summary(df):
    colcount = 4
    colcount = st.selectbox("Select number of columns in each table", [3, 4, 5, 6], 1)
    x = (df.ml.numerical_ix.shape[0]) // colcount
    y = (df.ml.numerical_ix.shape[0]) % colcount
    st.write(f"Total {df.ml.numerical_ix.shape[0]} numeric columns.")
    assert x * colcount + y == df.ml.numerical_ix.shape[0]
    for i in range(0, x):
        cols = df.ml.numerical_ix[i * colcount : i * colcount + colcount]
        st.write(df[cols].describe())
    if y != 0:
        cols = df.ml.numerical_ix[x * colcount : x * colcount + y]
        st.write(df[cols].describe())


def display_pandas_profile(df):
    if st.button("Generate pandas-profile report"):
        pr = df.profile_report()
        st_profile_report(pr)


def display_missingvalues(df):
    if st.button("Generate missing value report"):
        p = msno.matrix(df)
        st.pyplot(p.figure)
        q = msno.bar(df)
        st.pyplot(q.figure)
        r = msno.heatmap(df)
        st.pyplot(r.figure)
        s = msno.dendrogram(df)
        st.pyplot(s.figure)


def display_numeric_explorer(df):
    numvar = st.selectbox("Select numeric variable", df.ml.numerical_ix)
    c1, c2 = st.beta_columns((1, 2))
    with c1:
        st.write("Statistial Summary:")
        st.write(df[numvar].describe())
    with c2:
        st.write("Distribution plot:")
        p = (
            p9.ggplot(df, p9.mapping.aes(x=numvar))
            + p9.geoms.geom_histogram(p9.mapping.aes(fill=p9.mapping.after_stat("x")))
            # + p9.coords.coord_flip()
            + p9.themes.theme_xkcd()
            + p9.geoms.geom_text(
                p9.mapping.aes(label=p9.mapping.after_stat("count")),
                stat="count",
                nudge_x=-0.14,
                nudge_y=0.125,
                va="top",
            )
            + p9.geoms.geom_text(
                p9.mapping.aes(label=p9.mapping.after_stat("prop*100"), group=1),
                stat="count",
                nudge_x=0.14,
                nudge_y=0.125,
                va="bottom",
                format_string="{:.1f}% ",
            )
        )
        st.pyplot(p9.ggplot.draw(p))


def display_baselinerf(df):
    # TODO: Put training button here
    # TODO: Put st.empty() elements here, to be filled up ;ater after training completes
    n_iter = st.number_input("Choose number of iterations", min_value=1, max_value=1000, value=10)
    st.markdown("---")
    col1, col2 = st.beta_columns(2)
    with col1:
        st.write("Specify hyperparameters (optional)")
        hpdist_rf = {}
        max_features = st.checkbox("Include max_features", True)
        max_samples = st.checkbox("Include max_samples", True)
        n_estimators = st.checkbox("Include n_estimators", True)
        if n_estimators:
            n_estimators_ = st.slider("Choose max value", 1, 500, 100)
        max_depth = st.checkbox("Include max_depth", True)
        if max_depth:
            max_depth_ = st.slider("Choose max value", 1, 200, 40)
        min_samples_leaf = st.checkbox("Include min_samples_leaf", False)
    with col2:
        if max_features:
            hpdist_rf.update({"max_features": sp.stats.uniform(0, 1)})
        if max_samples:
            hpdist_rf.update({"max_samples": sp.stats.uniform(0, 1)})
        if n_estimators:
            hpdist_rf.update({"n_estimators": sp.stats.randint(10, n_estimators_)})
        if max_depth:
            hpdist_rf.update({"max_depth": sp.stats.randint(2, max_depth_)})
        if min_samples_leaf:
            hpdist_rf.update(
                {
                    "min_samples_leaf": sp.stats.randint(1, 15),
                }
            )
        for key, value in hpdist_rf.items():
            st.write(f"{key}: {value.__class__}")

    st.markdown("---")
    st.write("Specify training config (optional)")

    col1, col2 = st.beta_columns(2)
    with col1:
        st.write("placeholder for training_config widgets")

    with col2:
        config_rf = {
            "n_iter": n_iter,
            "param_distributions": hpdist_rf,
            "n_jobs": -1,
            "cv": TimeSeriesSplit(n_splits=3, gap=50),
            "random_state": 42,
            "verbose": 2,
        }
        for key, value in config_rf.items():
            st.write(f"{key}: {value.__class__}")
        st.write(config_rf)

    st.markdown("---")
    st.write("Choose features")
    col1, col2 = st.beta_columns(2)
    with col1:
        y_var = st.selectbox(
            label="Choose target variable for prediction",
            options=list(df.columns),
            index=len(df.columns) - 1,
        )

    with col2:
        x_vars = st.multiselect(
            label="Choose dependent variables to be used for modeling",
            options=list(df.columns),
        )

    st.write(f"x_vars: {x_vars}")
    st.write(f"y_var: {y_var}")
    df = df.loc[:, x_vars + [y_var]]
    st.write(df)

    if st.button("Start training"):
        (
            df.ml.assign_role(role="target", col=y_var)
            .step_normalize(normalizer="MinMaxScaler()")
            .train(
                model=RandomForestRegressor(),
                config=config_rf,
                sampling_strategy="timeseries",
            )
        )

        st.write(f"model performance: {df.ml.model_performance}")

        st.markdown("---")

        preds = df.ml.predict(df.ml.X_holdout)
        outcome = pd.DataFrame(
            {
                "preds": preds,
                "y_test": df.ml.y_holdout,
            }
        )
        outcome.loc[:, "dev_ratio"] = abs(outcome.preds - outcome.y_test) / outcome.y_test
        st.write(outcome)

        fig, ax = plt.subplots()
        plt.title("Moodel performance")
        plt.scatter(outcome["y_test"], outcome["preds"], c="blue")
        st.pyplot(fig)

        forest = df.ml.model.best_estimator_
        importances = forest.feature_importances_
        std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
        indices = np.argsort(importances)[::-1]

        st.markdown("## Feature ranking:")

        for f in range(len(x_vars)):
            print(f"{f + 1}. feature {indices[f]} ({importances[indices[f]]})")

        fig, ax = plt.subplots()
        # plt.figure()
        plt.title("Feature importances")
        plt.bar(
            range(len(x_vars)),
            importances[indices],
            color="r",
            yerr=std[indices],
            align="center",
        )
        plt.xticks(range(len(x_vars)), indices)
        plt.xlim([-1, len(x_vars)])
        st.pyplot(fig)
