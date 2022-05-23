from kolibri.core.component import Component
import numpy as np
import pandas as pd

# _________________________________________________________________________________________________________________________________________
class Fix_multicollinearity(Component):
    """
          Fixes multicollinearity between predictor variables , also considering the correlation between target variable.
          Only applies to regression or two class classification ML use case
          Takes numerical and one hot encoded variables only
            Args:
              threshold (float): The utmost absolute pearson correlation tolerated beyween featres from 0.0 to 1.0
              target_variable (str): The target variable/column name
              correlation_with_target_threshold: minimum absolute correlation required between every feature and the target variable , default 1.0 (0.0 to 1.0)
              correlation_with_target_preference: float (0.0 to 1.0), default .08 ,while choosing between a pair of features w.r.t multicol & correlation target , this gives
              the option to favour one measur to another. e.g. if value is .6 , during feature selection tug of war, correlation target measure will have a higher say.
              A value of .5 means both measure have equal say
  """

    # mamke a constructer
    defaults = {
        "fixed":
            {
                "colinearity-threshold":None,
                "correlation-with-target-threshold": 0.0,
                "correlation_with_target_preference": 1.0,
            }
    }
    def __init__(self, configs):
        super().__init__(configs)
        self.threshold = self.get_parameter("threshold")
        self.target_variable = self.get_parameter("target")
        self.correlation_with_target_threshold = self.get_parameter("correlation-with-target-threshold")
        self.target_corr_weight = self.get_parameter("correlation_with_target_preference")
        self.multicol_weight = 1 - self.get_parameter("correlation_with_target_preference")

    # Make fit method

    def fit(self, data, y=None):
        """
        Args:
            data = takes preprocessed data frame
        Returns:
            None
        """

        if data[self.target_variable].dtype not in ["int32", "int64", "float32", "float64"]:
            raise ValueError('dtype for the target variable should be int32, int64, float32, or float64 only')

        # global data1
        data1 = data.select_dtypes(include=["int32", "int64", "float32", "float64"])
        # try:
        #   self.data1 = self.data1.astype('float16')
        # except:
        #   None
        # make an correlation db with abs correlation db
        # self.data_c = self.data1.T.drop_duplicates()
        # self.data1 = self.data_c.T
        corr = pd.DataFrame(np.corrcoef(data1.T))
        corr.columns = data1.columns
        corr.index = data1.columns
        # corr_matrix = abs(data1.corr())
        corr_matrix = abs(corr)

        # for every diagonal value, make it Nan
        corr_matrix.values[
            tuple([np.arange(corr_matrix.shape[0])] * 2)
        ] = np.NaN

        # Now Calculate the average correlation of every feature with other, and get a pandas data frame
        avg_cor = pd.DataFrame(corr_matrix.mean())
        avg_cor["feature"] = avg_cor.index
        avg_cor.reset_index(drop=True, inplace=True)
        avg_cor.columns = ["avg_cor", "features"]

        # Calculate the correlation with the target
        targ_cor = pd.DataFrame(corr_matrix[self.target_variable].dropna())
        targ_cor["feature"] = targ_cor.index
        targ_cor.reset_index(drop=True, inplace=True)
        targ_cor.columns = ["target_variable", "features"]

        # Now, add a column for variable name and drop index
        corr_matrix["column"] = corr_matrix.index
        corr_matrix.reset_index(drop=True, inplace=True)

        # now we need to melt it , so that we can correlation pair wise , with two columns
        cols = corr_matrix.column
        melt = (
            corr_matrix.melt(id_vars=["column"], value_vars=cols)
            .sort_values(by="value", ascending=False)
            .dropna()
        )

        # now bring in the avg correlation for first of the pair
        merge = pd.merge(
            melt, avg_cor, left_on="column", right_on="features"
        ).drop("features", axis=1)

        # now bring in the avg correlation for second of the pair
        merge = pd.merge(
            merge, avg_cor, left_on="variable", right_on="features"
        ).drop("features", axis=1)

        # now bring in the target correlation for first of the pair
        merge = pd.merge(
            merge, targ_cor, left_on="column", right_on="features"
        ).drop("features", axis=1)

        # now bring in the avg correlation for second of the pair
        merge = pd.merge(
            merge, targ_cor, left_on="variable", right_on="features"
        ).drop("features", axis=1)

        # sort and save
        merge = merge.sort_values(by="value", ascending=False)

        # we need to now eleminate all the pairs that are actually duplicate e.g cor(x,y) = cor(y,x) , they are the same , we need to find these and drop them
        merge["all_columns"] = merge["column"] + merge["variable"]

        # this puts all the coresponding pairs of features togather , so that we can only take one, since they are just the duplicates
        merge["all_columns"] = [sorted(i) for i in merge["all_columns"]]

        # now sort by new column
        merge = merge.sort_values(by="all_columns")

        # take every second colums
        merge = merge.iloc[::2, :]

        # make a ranking column to eliminate features
        merge["rank_x"] = round(
            self.multicol_weight * (merge["avg_cor_y"] - merge["avg_cor_x"])
            + self.target_corr_weight
            * (merge["target_variable_x"] - merge["target_variable_y"]),
            6,
        )  # round it to 6 digits

        ## Now there will be rows where the rank will be exactly zero, these is where the value (corelartion between features) is exactly one ( like price and price^2)
        ## so in that case , we can simply pick one of the variable
        # but since , features can be in either column, we will drop one column (say 'column') , only if the feature is not in the second column (in variable column)
        # both equations below will return the list of columns to drop from here
        # this is how it goes

        ## For the portion where correlation is exactly one !
        one = merge[merge["rank_x"] == 0]

        # this portion is complicated
        # table one have all the paired variable having corelation of 1
        # in a nutshell, we can take any column (one side of pair) and delete the other columns (other side of the pair)
        # however one varibale can appear more than once on any of the sides , so we will run for loop to find all pairs...
        # here it goes
        # take a list of all (but unique ) variables that have correlation 1 for eachother, we will make two copies
        u_all = list(
            pd.unique(pd.concat((one["column"], one["variable"]), axis=0))
        )
        u_all_1 = list(
            pd.unique(pd.concat((one["column"], one["variable"]), axis=0))
        )
        # take a list of features (unique) for the first side of the pair
        u_column = pd.unique(one["column"])

        # now we are going to start picking each variable from one column (one side of the pair) , check it against the other column (other side of the pair)
        # to pull all coresponding / paired variables  , and delete thoes newly varibale names from all unique list

        for i in u_column:
            # print(i)
            r = one[one["column"] == i]["variable"]
            for q in r:
                if q in u_all:
                    # print("_"+q)
                    u_all.remove(q)

        # now the unique column contains the varibales that should remain, so in order to get the variables that should be deleted :
        to_drop = list(set(u_all_1) - set(u_all))

        # to_drop_a =(list(set(one['column'])-set(one['variable'])))
        # to_drop_b =(list(set(one['variable'])-set(one['column'])))
        # to_drop = to_drop_a + to_drop_b

        ## now we are to treat where rank is not Zero and Value (correlation) is greater than a specific threshold
        non_zero = merge[
            (merge["rank_x"] != 0.0) & (merge["value"] >= self.threshold)
        ]

        # pick the column to delete
        non_zero_list = list(
            np.where(
                non_zero["rank_x"] < 0,
                non_zero["column"],
                non_zero["variable"],
            )
        )

        # add two list
        self.to_drop = to_drop + non_zero_list

        # make sure that target column is not a part of the list
        try:
            self.to_drop.remove(self.target_variable)
        except:
            pass

        # now we want to keep only the columns that have more correlation with traget by a threshold
        self.to_drop_taret_correlation = []
        if self.correlation_with_target_threshold != 0.0:
            corr = pd.DataFrame(
                np.corrcoef(data.drop(self.to_drop, axis=1).T),
                columns=data.drop(self.to_drop, axis=1).columns,
                index=data.drop(self.to_drop, axis=1).columns,
            )
            self.to_drop_taret_correlation = corr[self.target_variable].abs()
            # to_drop_taret_correlation = data.drop(self.to_drop,axis=1).corr()[target_variable].abs()
            self.to_drop_taret_correlation = self.to_drop_taret_correlation[
                self.to_drop_taret_correlation < self.correlation_with_target_threshold
            ]
            self.to_drop_taret_correlation = list(self.to_drop_taret_correlation.index)
            # to_drop = corr + to_drop
            try:
                self.to_drop_taret_correlation.remove(self.target_variable)
            except:
                pass
        return self

    # now Transform
    def transform(self, dataset, y=None):
        """
        Args:f
            data = takes preprocessed data frame
        Returns:
            data frame
    """
        data = dataset
        data = data.drop(self.to_drop, axis=1)
        # now drop less correlated data
        data.drop(self.to_drop_taret_correlation, axis=1, inplace=True, errors="ignore")
        return data

    # fit_transform
    def fit_transform(self, data, y=None):

        """
        Args:
            data = takes preprocessed data frame
        Returns:
            data frame
    """
        self.fit(data)
        return self.transform(data)

class Fix_Perfect_collinearity(Component):
    """
    - Takes DF, return data frame while removing features that are perfectly correlated (droping one)
  """

    def __init__(self, config):

        super().__init__(config)
        self.target = self.get_parameter("target")
        self.columns_to_drop = []

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        return dataset.drop(self.columns_to_drop, axis=1)

    def fit_transform(self, dataset, y=None):
        data = dataset
        targetless_data=data
        if self.target !=None:
            targetless_data = data.drop(self.target, axis=1)

        # correlation should be calculated between at least two features, if there is only 1, there is nothing to delete
        if len(targetless_data.columns) <= 1:
            return data

        corr = pd.DataFrame(np.corrcoef(targetless_data.T))
        corr.columns = targetless_data.columns
        corr.index = targetless_data.columns
        corr_matrix = abs(corr)

        # Now, add a column for variable name and drop index
        corr_matrix["column"] = corr_matrix.index
        corr_matrix.reset_index(drop=True, inplace=True)

        # now we need to melt it , so that we can correlation pair wise , with two columns
        cols = corr_matrix.column
        melt = corr_matrix.melt(id_vars=["column"], value_vars=cols).sort_values(
            by="value", ascending=False
        )  # .dropna()
        melt["value"] = round(melt["value"], 2)  # round it to two digits

        # now pick variables where value is one and 'column' != variabe ( both columns are not same)
        c1 = melt["value"] == 1.00
        c2 = melt["column"] != melt["variable"]
        melt = melt[((c1 == True) & (c2 == True))]

        # we need to now eleminate all the pairs that are actually duplicate e.g cor(x,y) = cor(y,x) , they are the same , we need to find these and drop them
        melt["all_columns"] = melt["column"] + melt["variable"]

        # this puts all the coresponding pairs of features togather , so that we can only take one, since they are just the duplicates
        melt["all_columns"] = [sorted(i) for i in melt["all_columns"]]

        # # now sort by new column
        melt = melt.sort_values(by="all_columns")

        # # take every second colums
        melt = melt.iloc[::2, :]

        # lets keep the columns on the left hand side of the table
        self.columns_to_drop = melt["variable"]

        return data.drop(self.columns_to_drop, axis=1)
