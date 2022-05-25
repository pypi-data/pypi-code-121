import numpy as np
import pandas as pd
import argparse
import pickle

# <editor-fold desc="Helper Functions">
def getGroup(single_date, date_ranges):
    for idx, (start, end) in enumerate(date_ranges):
        if single_date >= pd.to_datetime(start, format="%d/%m/%Y") and single_date <= pd.to_datetime(end, format="%d/%m/%Y"):
            return str(idx + 1)

    print("Date couldn't find in any group")
    return "Not in any group"

# Save the object
def savePickle(obj, file_name):
    """
    Save a python object as a .pkl file
    """
    with open(file_name, mode="wb") as file:
        pickle.dump(obj, file)
        file.close()
        print(f"Saved the object to {file_name} successfully!")


# Load the object
def loadPickle(file_name):
    """
    Load a .pkl file
    """
    with open(file_name, mode="rb") as file:
        obj = pickle.load(file)
        file.close()
        return obj

# </editor-fold>


class PreProcessor():
    def __init__(self, querry_obj, initial_run=True):
        self.querry = querry_obj

        self.outliers = None
        self.group_names = None

        if initial_run:
            self.adjustInterpolatedDFDataTypes()
            self.sortColumns()
            self.generateSecondsBtwRecordings()

    def adjustInterpolatedDFDataTypes(self):

        self.querry.continuous = [k for (k, v) in self.querry.found_tag_dtypes.items() if
                                  v in [6, 8, 11, 12, 13]]  # 6 & 8 integer, 11-12-13 float
        self.querry.categorical = [k for (k, v) in self.querry.found_tag_dtypes.items() if v in [101, 105]] + ["g"]

        self.querry.df[self.querry.continuous] = self.querry.df[self.querry.continuous].apply(
            lambda x: pd.to_numeric(x, "coerce"))

    def sortColumns(self):
        self.querry.df = self.querry.df[["g", "DateTime"] + self.querry.df.columns[2:].sort_values().to_list()]
        self.querry.continuous.sort()
        self.querry.categorical.sort()

    def getQuerryObj(self):
        return self.querry

    def generateErr(self):
        # List of pv - sv column name tuples
        pairs = [(col, col[:-3] + "_pv") for col in self.querry.continuous if ((col[-3:] == "_sv") & (col[:-3] + "_pv" in self.querry.continuous))]
        for pair in pairs:
            # create a column name with _err by replacing _sv
            err_column_name = pair[0].replace("_sv", "_err")
            abs_err_column_name = pair[0].replace("_sv", "_absErr")
            self.querry.df[err_column_name] =  self.querry.df[pair[1]] - self.querry.df[pair[0]]
            self.querry.df[abs_err_column_name] =  abs(self.querry.df[err_column_name])
            self.querry.continuous.append(err_column_name)
            self.querry.continuous.append(abs_err_column_name)

    def create5mAgg(self, columns ,aggregation_function=np.mean, column_postfix="_mean"):
        grouper = [self.querry.df.DateTime.dt.date, self.querry.df.DateTime.dt.hour,
                         self.querry.df.DateTime.round("5min").dt.minute]

        # Aggregated originially querried df
        tmp = self.querry.df.groupby(grouper)[columns].apply(lambda x: aggregation_function(x))
        tmp.columns = [col + column_postfix for col in tmp.columns]
        # Create DateTime from index
        tmp["DateTime"] = tmp.index.map(
            lambda x: pd.to_datetime(x[0]) + pd.Timedelta(x[1], unit="hour") + pd.Timedelta(x[2], unit="minute"))
        tmp.reset_index(drop=True, inplace=True)
        # Add groups column
        tmp["g"] = tmp.DateTime.map(lambda x: getGroup(x,self.querry.dates))
        # Order columns
        tmp = tmp[["g", "DateTime"] + [col for col in tmp.columns if col not in ["g", "DateTime"]]]
        self.querry.__setattr__("df_m", tmp)

    def addTo5mAgg(self, columns, aggregation_function=np.std, column_postfix="_std" ):
        assert hasattr(self.querry, "df_m"), "5m aggregated DF doesn't exists"
        grouper = [self.querry.df.DateTime.dt.date, self.querry.df.DateTime.dt.hour,
         self.querry.df.DateTime.round("5min").dt.minute]

        tmp = self.querry.df.groupby(grouper)[columns].apply(lambda x: aggregation_function(x))
        tmp.reset_index(drop=True, inplace=True)
        tmp.columns = [col + column_postfix for col in tmp.columns]
        self.querry.df_m[tmp.columns] = tmp

    def applyFilterOnInterpolatedDF(self, filter):
        removed = self.querry.df.loc[~filter]
        self.querry.df = self.querry.df.loc[filter]

        print("Number of Removed records from each group:")
        print(removed.groupby("g").count().iloc[:, 1])

        return removed

    def generateSecondsBtwRecordings(self):
        if self.querry.recorded_values:
            self.querry.recording_df["sec_btw"] = self.querry.recording_df.groupby(["g", "tag_name"]).DateTime.diff().dt.seconds.shift(-1).values
        else:
            print("Recorded values is False in Query Object")

    def recordingDfToDict(self):
        if self.querry.recorded_values:
            self.querry.recording_dict = {k: self.querry.recording_df.loc[self.querry.recording_df.tag_name == k] for k in self.querry.recording_df.tag_name.unique()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI Preprocessor Tool")
    parser.add_argument("-q", "--query_obj", help="Query object .pkl file path", metavar="", required=True)
    parser.add_argument("-o", "--output_file_name", help="Processed Query object .pkl file name to save", metavar="", required=True)
    parser.add_argument("-r", "--repeating_run", help="Have run the PreProcessor on the object before", action="store_false")
    args = parser.parse_args()

    q = loadPickle(args.query_obj)
    q = PreProcessor(q, initial_run=args.repeating_run).getQuerryObj()
    savePickle(q, args.output_file_name)
