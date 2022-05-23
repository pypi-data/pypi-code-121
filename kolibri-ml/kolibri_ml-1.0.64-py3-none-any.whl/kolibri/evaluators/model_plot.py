import matplotlib.pyplot as plt

from kolibri.config import TaskType
from kolibri.logger import get_logger
import pandas as pd
import numpy as np
from kolibri.utils.common import is_multiclass
import os

try:
    import streamlit as st
except ImportError:
    raise ImportError(
        "It appears that streamlit is not installed. Do: pip install streamlit"
    )

logger=get_logger(__name__)

_available_plots = {}

class ModelPlot():
    
    def __init__(self, pipeline, data,
    feature_name = None, target=None, system=True):
        self.model_loader=pipeline
        self.feature_name=feature_name
        self.data=data
        self.data_before_preprocess = data.copy()
        self.target=target
        self.system=system
        self.display_format="streamlit"



    def elbow(self, n_start=2, n_end=10):

        if self.model_loader.estimator.task_type()!=TaskType.CLUSTERING:
            raise ValueError("cannot plot elbow graph for this task type: " + self.model_loader.estimator.task_type)
        y=None
        if self.target is not None:
            y=self.data[self.target]
        X, y,_,_=self.model_loader.fit_transformers(self.data, y)

        sse = []
        for k in range(n_start, n_end):
            self.model_loader.estimator.reload_model({"n_clusters":k})
            self.model_loader.estimator.fit(X)
            sse.append(self.model_loader.estimator.model.inertia_)

        plt.style.use("fivethirtyeight")
        plt.plot(range(n_start, n_end), sse)
        plt.xticks(range(n_end, n_end))
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.show()

    def tsne(self, save_Path=None):

        b = self.model_loader.predict(self.data)

        class_col_name=""
        if self.model_loader.pipeline.estimator.task_type() == TaskType.ANOMALY_DETECTION:
            class_col_name="Anomaly"
        if self.model_loader.pipeline.estimator.task_type() == TaskType.TOPICS:
            class_col_name="Dominant_Topic"


        clusters = b[class_col_name].values
        b.dropna(axis=0, inplace=True)  # droping rows with NA's
        b.drop(class_col_name, axis=1, inplace=True)
        if "score" in b.columns:
            b.drop("score", axis=1, inplace=True)

        from sklearn.manifold import TSNE

        logger.info("Fitting TSNE()")
        X_embedded = TSNE(n_components=3).fit_transform(b)
        X = pd.DataFrame(X_embedded)

        X[class_col_name] =clusters
        X.sort_values(by=class_col_name, inplace=True)
        X.dropna(inplace=True)

        logger.info("Rendering Visual")
        import plotly.express as px

        df = X
        fig = px.scatter_3d(
                df,
                x=0,
                y=1,
                z=2,
                color=class_col_name,
                title="3d TSNE Plot for "+self.model_loader.pipeline.estimator.task_type(),
                opacity=0.7,
                width=900,
                height=800,
            )

        if self.system:
            if self.display_format == "streamlit":
                st.write(fig)
            else:
                fig.show()

        logger.info("Visual Rendered Successfully")

        if save_Path:
            if not isinstance(save_Path, bool):
                plot_filename = os.path.join(save_Path, "TSNE.html")
            else:
                plot_filename = "TSNE.html"
            logger.info(f"Saving 'TSNE.html'")
            fig.write_html(plot_filename)

        return fig

    def umap(self, feature_name=None, save_path=None):

        b = self.model_loader.predict(self.data)
        class_col_name=""
        if self.model_loader.pipeline.estimator.task_type() == TaskType.ANOMALY_DETECTION:
            class_col_name="Anomaly"
        if self.model_loader.pipeline.estimator.task_type() == TaskType.TOPICS:
            class_col_name="Dominant_Topic"

        label = pd.DataFrame(b[class_col_name])
        b.dropna(axis=0, inplace=True)  # droping rows with NA's
        b.drop([class_col_name], axis=1, inplace=True)

        import umap

        reducer = umap.UMAP(n_components=3)
        logger.info("Fitting UMAP()")
        embedding = reducer.fit_transform(b)
        X = pd.DataFrame(embedding)

        import plotly.express as px

        df = X
        df[class_col_name] = label

        if feature_name is not None:
            df["Feature"] = self.data_before_preprocess[feature_name]
        else:
            df["Feature"] = self.data_before_preprocess[
                    self.data_before_preprocess.columns[0]
                ]



        fig = px.scatter_3d(
                df,
                x=0,
                y=1,
                z=2,
                color="Anomaly",
                title="uMAP Plot for "+self.model_loader.pipeline.estimator.task_type(),
                hover_data=["Feature"],
                opacity=0.7,
                width=900,
                height=800,
            )
        plot_filename = f"UMAP.html"

        if save_path:
            if not isinstance(save_path, bool):
                plot_filename = os.path.join(save_path, plot_filename)
            else:
                plot_filename = "UMAP.html"
            logger.info(f"Saving '{plot_filename}'")
            fig.write_html(plot_filename)
        elif self.system:
            if self.display_format == "streamlit":
                st.write(fig)
            else:
                fig.show()

        logger.info("Visual Rendered Successfully")
        return fig

    def threshold(self,
            true_positive: int = 0,
            true_negative: int = 0,
            false_positive: int = 0,
            false_negative: int = 0,
    ):

        """
        This function optimizes probability threshold for a trained model using custom cost
        function that can be defined using combination of True Positives, True Negatives,
        False Positives (also known as Type I error), and False Negatives (Type II error).

        This function returns a plot of optimized cost as a function of probability
        threshold between 0 to 100.


        Parameters
        ----------
        estimator : object
            A trained model object should be passed as an estimator.

        true_positive : int, default = 0
            Cost function or returns when prediction is true positive.

        true_negative : int, default = 0
            Cost function or returns when prediction is true negative.

        false_positive : int, default = 0
            Cost function or returns when prediction is false positive.

        false_negative : int, default = 0
            Cost function or returns when prediction is false negative.


        Returns
        -------
        Visual_Plot
            Prints the visual plot.

        Warnings
        --------
        - This function is not supported for multiclass problems.


        """

        y_test=self.data[self.target]
        function_params_str = ", ".join([f"{k}={v}" for k, v in locals().items()])

        logger = get_logger()

        logger.info("Initializing optimize_threshold()")
        logger.info(f"optimize_threshold({function_params_str})")


        """
        ERROR HANDLING STARTS HERE
        """

        logger.info("Checking exceptions")

        # exception 1 for multi-class
        if is_multiclass(self.model_loader.pipeline.estimator.task_type(), y_test):
            raise TypeError(
                "optimize_threshold() cannot be used when target is multi-class."
            )

        # check cost function type
        allowed_types = [int, float]

        if type(true_positive) not in allowed_types:
            raise TypeError("true_positive parameter only accepts float or integer value.")

        if type(true_negative) not in allowed_types:
            raise TypeError("true_negative parameter only accepts float or integer value.")

        if type(false_positive) not in allowed_types:
            raise TypeError("false_positive parameter only accepts float or integer value.")

        if type(false_negative) not in allowed_types:
            raise TypeError("false_negative parameter only accepts float or integer value.")

        """
        ERROR HANDLING ENDS HERE
        """



        model_name = self.model_loader.pipeline.estimator.name

        # generate predictions and store actual on y_test in numpy array
        actual = np.array(y_test)

        predicted = self.model_loader.predict(self.data)
        predicted = predicted[:, 1]

        """
        internal function to calculate loss starts here
        """

        logger.info("Defining loss function")

        def calculate_loss(
                actual,
                predicted,
                tp_cost=true_positive,
                tn_cost=true_negative,
                fp_cost=false_positive,
                fn_cost=false_negative,
        ):

            # true positives
            tp = predicted + actual
            tp = np.where(tp == 2, 1, 0)
            tp = tp.sum()

            # true negative
            tn = predicted + actual
            tn = np.where(tn == 0, 1, 0)
            tn = tn.sum()

            # false positive
            fp = (predicted > actual).astype(int)
            fp = np.where(fp == 1, 1, 0)
            fp = fp.sum()

            # false negative
            fn = (predicted < actual).astype(int)
            fn = np.where(fn == 1, 1, 0)
            fn = fn.sum()

            total_cost = (tp_cost * tp) + (tn_cost * tn) + (fp_cost * fp) + (fn_cost * fn)

            return total_cost

        """
        internal function to calculate loss ends here
        """

        grid = np.arange(0, 1, 0.0001)

        # loop starts here

        cost = []
        # global optimize_results

        logger.info("Iteration starts at 0")

        for i in grid:
            pred_prob = (predicted >= i).astype(int)
            cost.append(calculate_loss(actual, pred_prob))

        optimize_results = pd.DataFrame(
            {"Probability Threshold": grid, "Cost Function": cost}
        )
        fig = px.line(
            optimize_results,
            x="Probability Threshold",
            y="Cost Function",
            line_shape="linear",
        )
        fig.update_layout(plot_bgcolor="rgb(245,245,245)")
        title = f"{model_name} Probability Threshold Optimization"

        # calculate vertical line
        y0 = optimize_results["Cost Function"].min()
        y1 = optimize_results["Cost Function"].max()
        x0 = optimize_results.sort_values(by="Cost Function", ascending=False).iloc[0][0]
        x1 = x0

        t = x0
        fig.add_shape(
                dict(
                    type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="red", width=2)
                )
            )
        fig.update_layout(
                title={
                    "text": title,
                    "y": 0.95,
                    "x": 0.45,
                    "xanchor": "center",
                    "yanchor": "top",
                }
            )
        logger.info("Figure ready for render")
        fig.show()
        print(f"Optimized Probability Threshold: {t} | Optimized Cost Function: {y1}")
        logger.info(
            "optimize_threshold() succesfully completed......................................"
        )

        return float(t)

    def plot(self, plot="frequency", topic_num=None, save=False, system=True, display_format=None):

        """
        This function takes a trained model_type object (optional) and returns a plot based
        on the inferred dataset by internally calling assign_model before generating a
        plot. Where a model_type parameter is not passed, a plot on the entire dataset will
        be returned instead of one at the topic level. As such, plot_model can be used
        with or without model_type. All plots with a model_type parameter passed as a trained
        model_type object will return a plot based on the first topic i.e.  'Topic 0'. This
        can be changed using the topic_num param.



        model_type: object, default = none
            Trained Model Object


        plot: str, default = 'frequency'
            List of available plots (ID - Name):

            * Word Token Frequency - 'frequency'
            * Word Distribution Plot - 'distribution'
            * Bigram Frequency Plot - 'bigram'
            * Trigram Frequency Plot - 'trigram'
            * Sentiment Polarity Plot - 'sentiment'
            * Part of Speech Frequency - 'pos'
            * t-SNE (3d) Dimension Plot - 'tsne'
            * Topic Model (pyLDAvis) - 'topic_model'
            * Topic Infer Distribution - 'topic_distribution'
            * Wordcloud - 'wordcloud'
            * UMAP Dimensionality Plot - 'umap'


        topic_num : str, default = None
            Topic number to be passed as a string. If set to None, default generation will
            be on 'Topic 0'


        save: string/bool, default = False
            Plot is saved as png file in local directory when save parameter set to True.
            Plot is saved as png file in the specified directory when the path to the directory is specified.


        system: bool, default = True
            Must remain True all times. Only to be changed by internal functions.


        display_format: str, default = None
            To display plots in Streamlit (https://www.streamlit.io/), set this to 'streamlit'.
            Currently, not all plots are supported.


        Returns:
            None


        Warnings
        --------
        -  'pos' and 'umap' plot not available at model_type level. Hence the model_type parameter is
           ignored. The result will always be based on the entire training corpus.

        -  'topic_model' plot is based on pyLDAVis implementation. Hence its not available
           for model_type = 'lsi', 'rp' and 'nmf'.
        """
        if topic_num != None:
            topic_num="Topic_" + str(topic_num)
        from IPython.display import display, HTML, clear_output, update_display
        # setting default of topic_num
        if self._model is not None and topic_num is None:
            topic_num = "Topic 0"
            logger.info("Topic selected. topic_num : " + str(topic_num))

        import sys

        # plot checking
        allowed_plots = [
            "frequency",
            "bigram",
            "trigram",
#            "sentiment",
            "tsne",
            "topic_model",
            "topic_distribution",
            "wordcloud",

        ]
        if plot not in allowed_plots:
            sys.exit(
                "(Value Error): Plot Not Available. Please see docstring for list of available plots."
            )

        # handle topic_model plot error
        if plot == "topic_model":
            not_allowed_tm = ["lsi", "rp", "nmf"]
            if self.model_type in not_allowed_tm:
                sys.exit(
                    "(Type Error): Model not supported for plot = topic_model. Please see docstring for list of available models supported for topic_model."
                )

        # checking display_format parameter
        plot_formats = [None, "streamlit"]

        if display_format not in plot_formats:
            raise ValueError("display_format can only be None or 'streamlit'.")

        if display_format == "streamlit":
            try:
                import streamlit as st
            except ImportError:
                raise ImportError(
                    "It appears that streamlit is not installed. Do: pip install streamlit"
                )

        """
        error handling ends here
        """

        logger.info("Importing libraries")
        # import dependencies
        import pandas as pd

        # import cufflinks -->binds plotly to pandas
        import cufflinks as cf

        cf.go_offline()
        cf.set_config_file(offline=False, world_readable=True)

        # save parameter

        if save:
            save_param = True
        else:
            save_param = False

        logger.info("save_param set to " + str(save_param))

        logger.info("plot type: " + str(plot))

        if plot == "frequency":

            try:

                from sklearn.feature_extraction.text import CountVectorizer



                def get_top_n_words(corpus, n=None):
                    corpus = self.model_interpreter.pipeline.transformers[-1].transform(corpus)
                    corpus=[" ".join(c) for c in corpus]
                    vec = CountVectorizer()
                    logger.info("Fitting CountVectorizer()")
                    bag_of_words = vec.fit_transform(corpus)
                    sum_words = bag_of_words.sum(axis=0)
                    words_freq = [
                        (word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()
                    ]
                    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
                    return words_freq[:n]

                logger.info("Rendering Visual")

                if topic_num is None:
                    logger.warning("topic_num set to None. Plot generated at corpus level.")
                    common_words=[(w, c) for w, c in self._model.indexer.token2count.items()][:100]
#                    common_words = get_top_n_words([str(v) for v in self.data[self.target].values if v is not None], n=100)
                    df2 = pd.DataFrame(common_words, columns=["Text", "count"])

                    if display_format == "streamlit":
                        df3 = (
                            df2.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 words after removing stop words",
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df2.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 words after removing stop words",
                                asFigure=save_param,
                            )
                        )

                else:
                    title = (
                            str(topic_num) + ": " + "Top 100 words after removing stop words"
                    )
                    logger.info(
                        "SubProcess predict() called =================================="
                    )
                    assigned_df = self( [v for v in self.data[self.target].values if v is not None])
                    logger.info(
                        "SubProcess () end =================================="
                    )
                    assigned_df[self.target]=self.data[self.target]
                    filtered_df = assigned_df.loc[
                        assigned_df["Dominant_Topic"] == topic_num
                        ]

#                    common_words=[(w, c) for w, c in self._model.indexer.token2count.items()][:100]
                    common_words = get_top_n_words([str(v) for v in filtered_df[self.target].values if v is not None], n=100)
                    df2 = pd.DataFrame(common_words, columns=["Text", "count"])

                    if display_format == "streamlit":
                        df3 = (
                            df2.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df2.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=save_param,
                            )
                        )

                logger.info("Visual Rendered Successfully")

                if save:
                    if not isinstance(save, bool):
                        plot_filename = os.path.join(self.defaults["output-folder"], "Word Frequency.html")
                    else:
                        plot_filename = "Word Frequency.html"
                    logger.info(f"Saving '{plot_filename}'")
                    df3.write_html(plot_filename)



            except Exception as e:
                logger.warning(
                    "Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )
                sys.exit(
                    "(Value Error): Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )

        elif plot == "bigram":

            try:

                from sklearn.feature_extraction.text import CountVectorizer

                def get_top_n_bigram(corpus, n=None):
                    logger.info("Fitting CountVectorizer()")
                    vec = CountVectorizer(ngram_range=(2, 2)).fit(corpus)
                    bag_of_words = vec.transform(corpus)
                    sum_words = bag_of_words.sum(axis=0)
                    words_freq = [
                        (word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()
                    ]
                    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
                    return words_freq[:n]

                if topic_num is None:
                    logger.warning("topic_num set to None. Plot generated at corpus level.")
                    common_words = get_top_n_bigram([v for v in self.data[self.target].values if v is not None], 100)
                    df3 = pd.DataFrame(common_words, columns=["Text", "count"])
                    logger.info("Rendering Visual")

                    if display_format == "streamlit":
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 bigrams after removing stop words",
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 bigrams after removing stop words",
                                asFigure=save_param
                            )
                        )

                else:
                    title = (
                            str(topic_num) + ": " + "Top 100 bigrams after removing stop words"
                    )
                    logger.info(
                        "SubProcess predict() called =================================="
                    )
                    assigned_df = self([v for v in self.data[self.target].values if v is not None])
                    assigned_df[self.target]=self.data[self.target]

                    logger.info(
                        "SubProcess predict() end =================================="
                    )
                    filtered_df = assigned_df.loc[
                        assigned_df["Dominant_Topic"] == topic_num
                        ]
                    common_words = get_top_n_bigram(filtered_df[self.target], 100)
                    df3 = pd.DataFrame(common_words, columns=["Text", "count"])
                    logger.info("Rendering Visual")

                    if display_format == "streamlit":
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=save_param
                            )
                        )

                logger.info("Visual Rendered Successfully")

                if save:
                    if not isinstance(save, bool):
                        plot_filename = os.path.join(save, "Bigram.html")
                    else:
                        plot_filename = "Bigram.html"
                    logger.info(f"Saving '{plot_filename}'")
                    df3.write_html(plot_filename)


            except:
                logger.warning(
                    "Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )
                sys.exit(
                    "(Value Error): Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )

        elif plot == "trigram":

            try:

                from sklearn.feature_extraction.text import CountVectorizer

                def get_top_n_trigram(corpus, n=None):
                    vec = CountVectorizer(ngram_range=(3, 3)).fit(corpus)
                    logger.info("Fitting CountVectorizer()")
                    bag_of_words = vec.transform(corpus)
                    sum_words = bag_of_words.sum(axis=0)
                    words_freq = [
                        (word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()
                    ]
                    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
                    return words_freq[:n]

                if topic_num is None:
                    logger.warning("topic_num set to None. Plot generated at corpus level.")
                    common_words = get_top_n_trigram([v for v in self.data[self.target].values if v is not None], 100)
                    df3 = pd.DataFrame(common_words, columns=["Text", "count"])
                    logger.info("Rendering Visual")

                    if display_format == "streamlit":
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 trigrams after removing stop words",
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title="Top 100 trigrams after removing stop words",
                                asFigure=save_param
                            )
                        )

                else:
                    title = (
                            str(topic_num) + ": " + "Top 100 trigrams after removing stop words"
                    )
                    logger.info(
                        "SubProcess predict() called =================================="
                    )
                    assigned_df = self([v for v in self.data[self.target].values if v is not None])
                    assigned_df[self.target]=self.data[self.target]

                    logger.info(
                        "SubProcess predict() end =================================="
                    )
                    filtered_df = assigned_df.loc[
                        assigned_df["Dominant_Topic"] == topic_num
                        ]
                    common_words = get_top_n_trigram(filtered_df[self.target], 100)
                    df3 = pd.DataFrame(common_words, columns=["Text", "count"])
                    logger.info("Rendering Visual")

                    if display_format == "streamlit":
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=True  # plotly obj needs to be returned for streamlit to interpret
                            )
                        )

                        st.write(df3)

                    else:
                        df3 = (
                            df3.groupby("Text")
                                .sum()["count"]
                                .sort_values(ascending=False)
                                .iplot(
                                kind="bar",
                                yTitle="Count",
                                linecolor="black",
                                title=title,
                                asFigure=save_param
                            )
                        )

                logger.info("Visual Rendered Successfully")

                if save:
                    if not isinstance(save, bool):
                        plot_filename = os.path.join(save, "Trigram.html")
                    else:
                        plot_filename = "Trigram.html"
                    logger.info(f"Saving '{plot_filename}'")
                    df3.write_html(plot_filename)

            except:
                logger.warning(
                    "Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )
                sys.exit(
                    "(Value Error): Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )

        elif plot == "sentiment":
            raise NotImplementedError

        elif plot == "tsne":

            logger.info(
                "SubProcess predict() called =================================="
            )
            b = self.model_interpreter.predict([v for v in self.data[self.target].values if v is not None], verbose=False)
            logger.info("SubProcess predict() end ==================================")
            b.dropna(axis=0, inplace=True)  # droping rows where Dominant_Topic is blank

            c = []
            for i in b.columns:
                if "Topic_" in i:
                    a = i
                    c.append(a)

            bb = b[c]

            from sklearn.manifold import TSNE

            logger.info("Fitting TSNE()")
            X_embedded = TSNE(n_components=3).fit_transform(bb)

            logger.info("Sorting Dataframe")
            X = pd.DataFrame(X_embedded)
            X["Dominant_Topic"] = b["Dominant_Topic"]
            X.sort_values(by="Dominant_Topic", inplace=True)
            X.dropna(inplace=True)

            logger.info("Rendering Visual")
            import plotly.express as px

            df = X
            fig = px.scatter_3d(
                df,
                x=0,
                y=1,
                z=2,
                color="Dominant_Topic",
                title="3d TSNE Plot for Topic Model",
                opacity=0.7,
                width=900,
                height=800,
            )

            if system:
                if display_format == "streamlit":
                    st.write(fig)
                else:
                    fig.show()

            logger.info("Visual Rendered Successfully")

            if save:
                if not isinstance(save, bool):
                    plot_filename = os.path.join(save, "TSNE.html")
                else:
                    plot_filename = "TSNE.html"
                logger.info(f"Saving '{plot_filename}'")
                fig.write_html(plot_filename)


        elif plot == "topic_model":

            import pyLDAvis
            import pyLDAvis.gensim  # don't skip this

            import warnings
            from gensim.corpora import Dictionary


            def convertldaGenToldaMallet(mallet_model):
                model_gensim = LdaModel(
                    id2word=mallet_model.id2word, num_topics=mallet_model.num_topics,
                    alpha=mallet_model.alpha, eta=0,
                )
                model_gensim.state.sstats[...] = mallet_model.wordtopics
                model_gensim.sync_state()
                return model_gensim


            warnings.filterwarnings("ignore")
#            if self.verbose:
            pyLDAvis.enable_notebook()
            logger.info("Preparing pyLDAvis visual")
            from gensim.models.ldamodel import LdaModel
            vis = pyLDAvis.gensim.prepare(convertldaGenToldaMallet(self._model.model), self._model.corpus, dictionary=self._model.indexer, mds="mmds")
            if self.verbose:
                display(vis)
            else:

                pyLDAvis.show(vis)
            logger.info("Visual Rendered Successfully")


        elif plot == "topic_distribution":

            try:

                iter1 = len(self._model.show_topics(999999))

            except:

                try:
                    iter1 = self._model.num_topics

                except:

                    iter1 = self._model.n_components_

            topic_name = []
            keywords = []

            for i in range(0, iter1):

                try:

                    s = self._model.show_topic(i, topn=10)
                    topic_name.append("Topic " + str(i))

                    kw = []

                    for i in s:
                        kw.append(i[0])

                    keywords.append(kw)

                except:

                    keywords.append("NA")
                    topic_name.append("Topic " + str(i))

            keyword = []
            for i in keywords:
                b = ", ".join(i)
                keyword.append(b)

            kw_df = pd.DataFrame({"Topic": topic_name, "Keyword": keyword}).set_index(
                "Topic"
            )
            logger.info(
                "SubProcess predict() called =================================="
            )
            ass_df = self.model_interpreter.predict([v for v in self.data[self.target].values if v is not None], verbose=False)
            logger.info("SubProcess predict() end ==================================")
            ass_df_pivot = ass_df.pivot_table(
                index="Dominant_Topic", values="Topic_0", aggfunc="count"
            )
            df2 = ass_df_pivot.join(kw_df)
            df2 = df2.reset_index()
            df2.columns = ["Topic", "Documents", "Keyword"]

            """
            sorting column starts

            """

            logger.info("Sorting Dataframe")

            topic_list = list(df2["Topic"])

            s = []
            for i in range(0, len(topic_list)):
                a = int(topic_list[i].split()[1])
                s.append(a)

            df2["Topic"] = s
            df2.sort_values(by="Topic", inplace=True)
            df2.sort_values(by="Topic", inplace=True)
            topic_list = list(df2["Topic"])
            topic_list = list(df2["Topic"])
            s = []
            for i in topic_list:
                a = "Topic " + str(i)
                s.append(a)

            df2["Topic"] = s
            df2.reset_index(drop=True, inplace=True)

            """
            sorting column ends
            """

            logger.info("Rendering Visual")

            import plotly.express as px

            fig = px.bar(
                df2,
                x="Topic",
                y="Documents",
                hover_data=["Keyword"],
                title="Document Distribution by Topics",
            )

            if system:
                if display_format == "streamlit":
                    st.write(fig)
                else:
                    fig.show()

            logger.info("Visual Rendered Successfully")

            if save:
                if not isinstance(save, bool):
                    plot_filename = os.path.join(save, "Topic Distribution.html")
                else:
                    plot_filename = "Topic Distribution.html"
                logger.info(f"Saving '{plot_filename}'")
                fig.write_html(plot_filename)

        elif plot == "wordcloud":

            try:

                from wordcloud import WordCloud
                import matplotlib.pyplot as plt

                stopwords = set(get_stop_words(self.defaults["language"]))

                if topic_num is None:
                    logger.warning("topic_num set to None. Plot generated at corpus level.")
                    atext = " ".join(review for review in self.data[self.target])

                else:

                    logger.info(
                        "SubProcess predict() called =================================="
                    )
                    assigned_df = self([v for v in self.data[self.target].values if v is not None])
                    assigned_df[self.target]=self.data[self.target]

                    logger.info(
                        "SubProcess predict() end =================================="
                    )
                    filtered_df = assigned_df.loc[
                        assigned_df["Dominant_Topic"] == topic_num
                        ]
                    atext = " ".join(review for review in filtered_df[self.target])

                logger.info("Fitting WordCloud()")
                wordcloud = WordCloud(
                    width=800,
                    height=800,
                    background_color="white",
                    stopwords=stopwords,
                    min_font_size=10,
                ).generate(atext)

                # plot the WordCloud image
                plt.figure(figsize=(8, 8), facecolor=None)
                plt.imshow(wordcloud)
                plt.axis("off")
                plt.tight_layout(pad=0)

                logger.info("Rendering Visual")

                if save:
                    if system:
                        plt.savefig("Wordcloud.png")
                    else:
                        plt.savefig("Wordcloud.png")
                        plt.close()

                    logger.info("Saving 'Wordcloud.png' in current active directory")

                else:
                    if display_format == "streamlit":
                        st.write(plt)
                    else:
                        plt.show()

                logger.info("Visual Rendered Successfully")

            except:
                logger.warning(
                    "Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )
                sys.exit(
                    "(Value Error): Invalid topic_num param or empty Vocab. Try changing Topic Number."
                )

        logger.info(
            "plot_model() succesfully completed......................................"
        )