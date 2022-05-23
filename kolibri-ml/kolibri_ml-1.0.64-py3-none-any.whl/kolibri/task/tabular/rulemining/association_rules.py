
import random
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from IPython.display import display

class AssociationRules():

    defaults={
        "fixed":{
            "seed": None,
            "ignore-items": None,
            "metric" : "confidence",
            "threshold" : 0.5,
            "min-support" : 0.05,
            "round" : 4,
            "low-memory" : False,
            "max-len" : None
        }
    }

    def __init__(self, data, transaction_id, item_id, ignore_items=None, seed=None):

        # exception checking
        import sys

        # checking data type
        if isinstance(data, pd.DataFrame) is False:
            sys.exit("(Type Error): data passed must be of type pandas.DataFrame")

        # ignore warnings
        import warnings

        warnings.filterwarnings("ignore")

        self.seed=seed

        self.X=None
        self.txid=None
        self.iid=None
        self.ignore_list=ignore_items
        self.experiment__=None

        # create an empty list for pickling later.
        self.experiment__ = []

        # storing items in variable
        self.X = data
        self.txid = transaction_id
        self.iid = item_id
        self.ignore_list = ignore_items

        # generate seed to be used globally
        if seed is None:
            self.seed = random.randint(150, 9000)
        else:
            self.seed = seed

        tx_unique = len(data[transaction_id].unique())
        item_unique = len(data[item_id].unique())
        if ignore_items is None:
            ignore_flag = "None"
        else:
            ignore_flag = ignore_items

        functions = pd.DataFrame(
            [
                ["session_id", seed],
                ["# Transactions", tx_unique],
                ["# Items", item_unique],
                ["Ignore Items", ignore_flag],
            ],
            columns=["Description", "Value"],
        )

        functions_ = functions.style.hide_index()
        display(functions_)



    def create_model(self):

        """
        This function creates an association rules model_type using data and identifiers
        passed at setup stage. This function internally transforms the data for
        association rule mining.




        metric: str, default = 'confidence'
            Metric to evaluate if a rule is of interest. Default is set to confidence.
            Other available metrics include 'support', 'lift', 'leverage', 'conviction'.
            These metrics are computed as follows:

            * support(A->C) = support(A+C) [aka 'support'], range: [0, 1]
            * confidence(A->C) = support(A+C) / support(A), range: [0, 1]
            * lift(A->C) = confidence(A->C) / support(C), range: [0, inf]
            * leverage(A->C) = support(A->C) - support(A)*support(C), range: [-1, 1]
            * conviction = [1 - support(C)] / [1 - confidence(A->C)], range: [0, inf]


        threshold: float, default = 0.5
            Minimal threshold for the evaluation metric, via the `metric` parameter,
            to decide whether a candidate rule is of interest.


        min_support: float, default = 0.05
            A float between 0 and 1 for minumum support of the itemsets returned.
            The support is computed as the fraction `transactions_where_item(s)_occur /
            total_transactions`.


        round: int, default = 4
            Number of decimal places metrics in score grid will be rounded to.

        low_memory: bool, default = False
            If `True`, uses an iterator for apriori to search for combinations above
          `min_support`.
          Note that while `low_memory=True` should only be used for large dataset
          if memory resources are limited, because this implementation is approx.
          3-6x slower than the default.

        max_len: int, default = None
            Maximum length of the itemsets generated in apriori. If `None` (default) all
          possible itemsets lengths (under the apriori condition) are evaluated.


        Returns:
            pandas.DataFrame


        Warnings
        --------
        - Setting low values for min_support may increase training time.

        """



        # reshaping the dataframe
        basket = (
            self.X.groupby([self.txid, self.iid])[self.iid]
            .count()
            .unstack()
            .reset_index()
            .fillna(0)
            .set_index(self.txid)
        )
        if self.ignore_list is not None:
            basket = basket.drop(self.ignore_list, axis=1)

        def encode_units(x):

            if x <= 0:
                return 0
            if x >= 1:
                return 1

        min_support=self.defaults["fixed"]["min-support"]
        low_memory=self.defaults["fixed"]["low-memory"]
        max_len=self.defaults["fixed"]["max-len"]
        metric=self.defaults["fixed"]["metric"]
        threshold=self.defaults["fixed"]["threshold"]

        basket = basket.applymap(encode_units)
        round=self.defaults["fixed"]["round"]
        frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True, low_memory=low_memory, max_len=max_len)
        rules = association_rules(frequent_itemsets, metric=metric, min_threshold=threshold)
        rules = rules.sort_values(by=[metric], ascending=False).reset_index(drop=True)
        rules = rules.round(round)

        # storing into experiment
        tup = ("Basket", basket)
        self.experiment__.append(tup)

        tup = ("Frequent Itemsets", frequent_itemsets)
        self.experiment__.append(tup)

        tup = ("Rules", rules)
        self.experiment__.append(tup)

        return rules


    def plot_model(self, model, plot="2d", scale=1, display_format=None):

        """
        This function takes a model_type dataframe returned by create_model() function.
        '2d' and '3d' plots are available.



        model_type: pandas.DataFrame, default = none
            pandas.DataFrame returned by trained model_type using create_model().


        plot: str, default = '2d'
            Enter abbreviation of type of plot. The current list of plots supported are
            (Name - Abbreviated String):

            * Support, Confidence and Lift (2d) - '2d'
            * Support, Confidence and Lift (3d) - '3d'


        scale: float, default = 1
            The resolution scale of the figure.

        display_format: str, default = None
            To display plots in Streamlit (https://www.streamlit.io/), set this to 'streamlit'.

        Returns:
            None

        """

        # error handling
        import pandas as pd

        # check if model_type is a pandas dataframe
        if not isinstance(model, pd.DataFrame):
            raise TypeError("Model needs to be a pandas.DataFrame object.")

        # check plot parameter
        plot_types = ["2d", "3d"]

        if plot not in plot_types:
            raise ValueError("Plots can only be '2d' or '3d'.")

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

        # loading libraries
        import numpy as np
        import pandas as pd
        import plotly.express as px
        from IPython.display import display, HTML, clear_output, update_display

        try:
            # import cufflinks
            import cufflinks as cf
        except:
            print("cufflinks is  ot installed. Please intall it: pip install cufflinks")

        cf.go_offline()
        cf.set_config_file(offline=False, world_readable=True)

        # copy dataframe
        data_ = model.copy()

        antecedents = []
        for i in data_["antecedents"]:
            i = str(i)
            a = i.split(sep="'")
            a = a[1]
            antecedents.append(a)

        data_["antecedents"] = antecedents

        antecedents_short = []

        for i in antecedents:
            a = i[:10]
            antecedents_short.append(a)

        data_["antecedents_short"] = antecedents_short

        consequents = []
        for i in data_["consequents"]:
            i = str(i)
            a = i.split(sep="'")
            a = a[1]
            consequents.append(a)

        data_["consequents"] = consequents

        if plot == "2d":

            fig = px.scatter(
                data_,
                x="support",
                y="confidence",
                text="antecedents_short",
                log_x=True,
                size_max=600,
                color="lift",
                hover_data=["antecedents", "consequents"],
                opacity=0.5,
            )

            fig.update_traces(textposition="top center")
            fig.update_layout(plot_bgcolor="rgb(240,240,240)")

            fig.update_layout(
                height=800 * scale, title_text="2D Plot of Support, Confidence and Lift"
            )

        if plot == "3d":

            fig = px.scatter_3d(
                data_,
                x="support",
                y="confidence",
                z="lift",
                color="antecedent support",
                title="3d Plot for Rule Mining",
                opacity=0.7,
                width=900 * scale,
                height=800 * scale,
                hover_data=["antecedents", "consequents"],
            )

        if display_format == "streamlit":
            st.write(fig)
        else:
            fig.show()

