import sys

supported_major_python_v = 3
supported_minor_python_v = [6, 7, 8, 9, 10]


def check_python_version():
    """
    Confirms that the current Python version is compatible with practicus
    :return: None
    """
    assert sys.version_info.major == supported_major_python_v and sys.version_info.minor in supported_minor_python_v, \
        "Active Python version %s.%s is not supported. \npracticuscore currently supports the following Python versions: " \
        "%s.%s" % (sys.version_info.major, sys.version_info.minor, supported_major_python_v,
                   str(supported_minor_python_v))


check_python_version()


from practicuscore.steps import Step, StepType, StepParam
from practicuscore.dataprep import DataPrepC, DataPrepC2
from practicuscore.core_def import Err, CoreDef, PRTEng
from practicuscore.core_conf import core_conf_glbl, log_manager_glbl
from practicuscore.dataprep3 import DataPrepC3

__version__ = CoreDef.CORE_VERSION


class DataPrep3:

    def __new__(cls) -> DataPrepC3:
        return DataPrepC3(core_conf_glbl)


class DataPrep:
    def __init__(self, df, preview=True, preview_in_notebook_style=True):
        """
        Initializes DataPrep engine
        :param df: Pandas, DASK, RAPIDS (cudf) or Spark dataframe
        :param preview: Preview the new dataframe after each step
        :param preview_in_notebook_style: If True, previews dataframe using Jupyter (IPython) style table.
        If False, prints preview regularly
        """
        _ = core_conf_glbl  # this needs to be imported to make sure logging config is also loaded
        self.logger = log_manager_glbl.get_logger()
        self.logger.info("Initialized practicuscore version %s (active Python v%d.%d.%d)" %
                         (CoreDef.CORE_VERSION, sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

        self.__dpc = DataPrepC()
        self.__preview = preview
        self.__preview_in_notebook_style = preview_in_notebook_style
        self.__dpc.update_engine(df)
        self.__validate_df()
        self.__display_df(df)

    def __validate_df(self):
        # todo: check column names (no numeric only column name, no []) , column data types at design time
        # no backticks in column names `
        # cannot start with a number
        # not ideal to have __ (eval/exec)
        # what else?
        pass

    def __display_df(self, df):
        if not self.__preview:
            return
        try:
            # using exec to avoid ipython dependency in design time
            if self.__dpc.engine == PRTEng.SPARK:
                if self.__preview_in_notebook_style:
                    exec("display(df.limit(10).toPandas())")
                else:
                    df.show()
            elif self.__dpc.engine == PRTEng.DASK or self.__dpc.engine == PRTEng.RAPIDS_MULTI:
                exec("display(df.compute())")
            else:  # pandas and rapids
                exec("display(df)")
        except:
            if self.__dpc.engine == PRTEng.SPARK:
                df.show()
            else:
                print(df.head())

    def __record_step(self, step):
        self.__dpc.record_step(step)

    def __run_step(self, df, step):
        df = self.__dpc.run_step(df, step)
        self.__record_step(step)
        print("\x1b[0;32mSuccess: %s\033[0m" % step.get_friendly_name())
        self.__display_df(df)
        return df

    def reset_steps(self):
        self.__dpc.reset_recorded_steps()

    def show_steps(self):
        self.__dpc.show_recorded_steps()

    def save_worksheet(self, file_path, sample_df=None, sample_size=100):
        if file_path[-4:] != ".prt":
            file_path += ".prt"
        if sample_df is not None:
            sampling_message = "A sample of %d rows are included" % sample_size
        else:
            sampling_message = "No sample included. \nPlease consider using dp.save_worksheet(file_path, " \
                               "sample_df=df, sample_size=100) to include 100 samples of the dataframe in the saved " \
                               "worksheet "
        self.__dpc.save_default_ws(file_path, sample_df, sample_size)
        print("Worksheet saved to %s. %s" % (file_path, sampling_message))

    def run_steps(self, df):
        try:
            df = self.__dpc.run_recorded_steps(df)
            print("\x1b[0;32mSuccessfully executed recorded steps\033[0m")
            self.__display_df(df)
        except:
            self.logger.error("Error occurred while running recorded steps", exc_info=True)
        finally:
            return df

    def show_activity_log(self):
        try:
            print(self.__dpc.get_default_ws_activity_log(use_markdown=False))
        except:
            self.logger.error("Error occurred while displaying Activity Log", exc_info=True)

    def delete_steps(self, *args):
        try:
            self.__dpc.delete_recorded_steps(*args)

            deleted_steps = ""
            for step in args:
                if len(deleted_steps) == 0:
                    deleted_steps = str(step)
                else:
                    deleted_steps += ", %d" % step

            print("\x1b[0;32mSuccessfully deleted step(s):", deleted_steps, "\033[0m")
        except:
            self.logger.error("Error occurred while deleting step(s)", exc_info=True)

    def delete_columns(self, df, arr_column):
        """
        Deletes columns from the Pandas DataFrame with inplace editing
        :param df: Pandas DataFrame
        :param arr_column: Column list
        :return: None
        """
        try:
            step = Step(StepType.DELETE_COLUMNS,
                        {StepParam.COLUMN_LIST: arr_column})
            return self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while deleting column(s) %s" % arr_column, exc_info=True)
            return df

    def rename_column(self, df, from_column_name, to_column_name):
        """
        Renames a columns with inplace editing
        :param df: Pandas DataFrame
        :param from_column_name: Existing column name
        :param to_column_name: New column name
        :return: None
        """
        try:
            if from_column_name not in df.columns:
                Err.print_err("Error: Column %s doesn't exist" % from_column_name)
                return
            step = Step(StepType.RENAME_COLUMN,
                        {StepParam.FROM_COLUMN_NAME: from_column_name,
                         StepParam.TO_COLUMN_NAME: to_column_name})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while renaming %s to %s" % (from_column_name, to_column_name),
                              exc_info=True)
        finally:
            return df

    def change_column_type(self, df, column_name, new_column_type):
        """
        Changes column data type
        :param df: DataFrame
        :param column_name: Column name to change
        :param new_column_type: New Column Type- Text, Numeric, Date Time, Boolean
        :return: None
        """
        try:
            if column_name not in df.columns:
                Err.print_err("Error: Column %s doesn't exist" % column_name)
                return
            step = Step(StepType.CHANGE_COLUMN_TYPE,
                        {StepParam.COLUMN_NAME: column_name,
                         StepParam.COLUMN_TYPE: new_column_type})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while changing type of column %s to %s" % (column_name, new_column_type),
                              exc_info=True)
        finally:
            return df

    def filter(self, df, filter_expression):
        try:
            step = Step(StepType.RUN_FILTER,
                        {StepParam.FILTER_EXPRESSION: filter_expression})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while filtering with %s" % filter_expression, exc_info=True)
        finally:
            return df

    def register_udf(self, udf):
        try:
            self.__dpc.register_udf_code(udf)
        except:
            self.logger.error("Error occurred while registering User Defined Function (UDF)", exc_info=True)

    def run_formula(self, df, new_column_name, formula_expression, return_type=""):
        try:
            step_param = {StepParam.NEW_COLUMN_NAME: new_column_name,
                          StepParam.FORMULA_EXPRESSION: formula_expression,
                          StepParam.FORMULA_RETURN_TYPE: return_type}

            udf_code_list = self.__dpc.get_registered_udf_code_list()
            if len(udf_code_list) > 0:
                step_param[StepParam.UDF_DEF_CODE_LIST] = udf_code_list

            step = Step(StepType.RUN_FORMULA,
                        step_param)
            if self.__dpc.engine != PRTEng.PANDAS and len(return_type) == 0:
                # todo: create debug_pid warning code
                # todo: for the below- do we really?
                print("No return_type provided for the formula. %s engine prefers to have one. \nPlease consider using "
                      "return_type='Text | Integer | Double | DateTime | Boolean'" % self.__dpc.engine.lower())
            df = self.__run_step(df, step)
            self.__dpc.reset_registered_udf_code_list()
        except:
            self.logger.error("Error occurred while running formula %s" % formula_expression, exc_info=True)
        finally:
            return df

    def run_code(self, df, custom_function_or_functions):
        try:
            df, step = self.__dpc.run_custom_code(df, custom_function_or_functions)
            self.__record_step(step)
            print("\x1b[0;32mSuccessfully executed custom code\033[0m")
            self.__display_df(df)
        except:
            self.logger.error("Error occurred while running custom code", exc_info=True)
        finally:
            return df

    def join(self, left_df, left_key_col_name, right_key_col_name, join_technique='left',
             suffix_for_overlap='', summary_column=False):
        step_def = ""
        try:
            # todo:  add connconf
            step = Step(StepType.JOIN,
                        {StepParam.LEFT_KEY_COLUMN_NAME: left_key_col_name,
                         StepParam.RIGHT_KEY_COLUMN_NAME: right_key_col_name,
                         StepParam.JOIN_TECHNIQUE: join_technique,
                         StepParam.JOIN_SUFFIX_FOR_OVERLAP: suffix_for_overlap,
                         StepParam.JOIN_SUMMARY_COLUMN: summary_column})

            step_def = step.get_friendly_name()
            left_df = self.__run_step(left_df, step)
        except:
            self.logger.error("Error occurred while joining. %s" % step_def, exc_info=True)
        finally:
            return left_df

    def one_hot_encode(self, df, column_name, column_prefix):
        try:
            if column_name not in df.columns:
                Err.print_err("Error: Column %s doesn't exist" % column_name)
                return
            step = Step(StepType.ONE_HOT,
                        {StepParam.COLUMN_NAME: column_name,
                         StepParam.COLUMN_PREFIX: column_prefix})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while creating one hot encoding for column %s" % column_name,
                              exc_info=True)
        finally:
            return df

    def categorical_map(self, df, column_name, column_suffix):
        try:
            if column_name not in df.columns:
                Err.print_err("Error: Column %s doesn't exist" % column_name)
                return
            step = Step(StepType.CATEGORICAL_MAP,
                        {StepParam.COLUMN_NAME: column_name,
                         StepParam.COLUMN_SUFFIX: column_suffix})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while categorical mapping for column %s" % column_name, exc_info=True)
        finally:
            return df

    def split_column(self, df, column_name, split_using, number_of_splits=-1):
        try:
            if column_name not in df.columns:
                Err.print_err("Error: Column %s doesn't exist" % column_name)
                return
            step = Step(StepType.SPLIT_COLUMN,
                        {StepParam.COLUMN_NAME: column_name,
                         StepParam.SPLIT_USING: split_using,
                         StepParam.NUMBER_OF_SPLITS: number_of_splits})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while splitting column %s" % column_name, exc_info=True)
        finally:
            return df

    def handle_missing(self, df, technique, column_names=None, custom_value=None):
        try:
            step = Step(StepType.HANDLE_MISSING,
                        {StepParam.HANDLE_MISSING_TECHNIQUE: technique,
                         StepParam.COLUMN_LIST: column_names,
                         StepParam.HANDLE_MISSING_CUSTOM_VALUE: custom_value})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while handling missing values", exc_info=True)
        finally:
            return df

    def update_column(self, df, column_name, old_value, new_value):
        try:
            step = Step(StepType.UPDATE_COLUMN,
                        {StepParam.COLUMN_NAME: column_name,
                         StepParam.OLD_VALUE: old_value,
                         StepParam.NEW_VALUE: new_value})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while updating column values", exc_info=True)
        finally:
            return df

    def sort(self, df, columns, ascending=None):
        try:
            step_param = {StepParam.COLUMN_LIST: columns}

            if ascending is not None:
                step_param[StepParam.ASCENDING_LIST] = ascending

            step = Step(StepType.SORT, step_param)
            return self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while sorting column(s) %s" % columns, exc_info=True)
            return df

    def group_by(self, df, columns, aggregation):
        try:
            step = Step(StepType.GROUP_BY,
                        {StepParam.COLUMN_LIST: columns,
                         StepParam.GROUP_BY_AGG_DICT: aggregation})
            return self.__run_step(df, step)
        except:
            self.logger.error(
                "Error occurred while grouping by column(s) %s using aggregation %s" % (columns, aggregation),
                exc_info=True)
            return df

    def handle_missing_infer(self, df, column_names=None):
        try:
            step = Step(StepType.NODE_HANDLE_MISSING_INFER,
                        {StepParam.COLUMN_LIST: column_names})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while handling missing values with AI (infer)", exc_info=True)
        finally:
            return df

    def predict(self, df, column_names, new_column_name, model_path):
        try:
            step = Step(StepType.NODE_PREDICT,
                        {StepParam.NODE_MODEL_CONF_PATH: model_path,
                         StepParam.COLUMN_LIST: column_names,
                         StepParam.NEW_COLUMN_NAME: new_column_name})
            df = self.__run_step(df, step)
        except:
            self.logger.error("Error occurred while predicting", exc_info=True)
        finally:
            return df


def test():
    print("Practicus AI test completed and is successfully installed.")


if __name__ == "__main__":
    pass
    # arr_step_dict = []
    #
    # from practicuscore.api_base import S3ConnConf, ConnConfFactory
    #
    # s3 = S3ConnConf(sampling_method=None, sample_size=None, aws_region="region", aws_access_key_id="access_key", aws_secret_access_key="secret",
    #                 s3_bucket="12", s3_keys=["key1", "key2"])
    # arr_step_dict.append(Step(StepType.LOAD_CSV, {StepParam.NODE_PATH: {"a": "1", "b": "2"}}).__dict__)
    # arr_step_dict.append(Step(StepType.LOAD_CSV, {StepParam.NODE_PATH: s3}).__dict__)
    #
    # from practicuscore.api_def import Steps
    # steps = Steps(step_list=arr_step_dict)
    #
    # from pprint import pprint
    # steps_json = steps.to_json()
    #
    # steps2 = Steps.from_json(steps_json)
    # arr_steps = []
    # for step_dict in steps2.step_list:
    #     step = Step.create_from_dict(step_dict)
    #     arr_steps.append(step)
    #
    # step: Step = arr_steps[1]
    # conn_conf = ConnConfFactory.create(step.step_params[StepParam.NODE_PATH])
    # print(type(conn_conf))
