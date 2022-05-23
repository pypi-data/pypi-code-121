import json
import pandas as pd
from io import StringIO
from pathlib import Path
import warnings
import pypandoc
from enum import Enum, auto
import itertools
import operator
import logging


class Severity(Enum):
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))


class Check(object):
    def __init__(self, severity, message, check_name):
        self.message = message
        self.check_name = check_name
        self._display_severity = None
        self.display_severity = severity

    def update_value(self, new_severity):
        self.display_severity = new_severity

    @property
    def display_severity(self):
        return self._display_severity

    @display_severity.setter
    def display_severity(self, value):
        if isinstance(value, Severity):
            self._display_severity = value.name
        elif isinstance(value, str) and value in Severity.list():
            self._display_severity = value
        else:
            raise ValueError(f"{self.check_name} only accepts: "
                             f" {', '.join([x.name for x in Severity])}")


class CheckThresholds(Check):
    def __init__(self, thresholds, message, handler, check_name):
        self.handler = handler
        self.check_name = check_name
        self.thresholds = thresholds
        self._default_message = message
        self.message = None

    def update_severity_and_message(self, check_out):
        # using check specific handlers to set the severity and the message
        pct_fails, mssg_elements = self.handler.process_check_returns(
                                                                     check_out)
        self.message = self._default_message.format(*mssg_elements)
        self.display_severity = self.get_severity(pct_fails)

    def update_value(self, new_thresholds):
        self.thresholds = new_thresholds

    @property
    def thresholds(self):
        return self._thresholds

    @thresholds.setter
    def thresholds(self, thresholds):
        if isinstance(thresholds, dict):
            self._thresholds = thresholds
        else:
            raise TypeError(f"{self.check_name} only accepts dictionaries.")

    def get_severity(self, value):
        if value < self.thresholds[Severity.WARNING.name]:
            return Severity.WARNING
        elif value >= self.thresholds[Severity.CRITICAL.name]:
            return Severity.CRITICAL
        else:
            return Severity.ERROR


class MissingValuesHandler(object):
    # this is used when checking missing values in the data
    @staticmethod
    def process_check_returns(check_out):
        pct_fails = 100 * check_out[0] / check_out[1]
        message_elements = [check_out[0], pct_fails]

        return pct_fails, message_elements


class MissingValuesSeriesHandler(object):
    # this one is used when checking the number of missing values in the series
    @staticmethod
    def process_check_returns(check_out):
        pct_fails = 100 * check_out[0] / check_out[1]
        message_elements = [check_out[0], pct_fails]

        return pct_fails, message_elements


class MissingValuesDataHandler(object):
    # this is used when checking missing values in the data, and returns the
    # list of series values for which the missing values where found.
    # this is only used when missing = yes is set for [All] or for [Dataseries]
    # in the config file
    @staticmethod
    def process_check_returns(check_out):
        number_missing = check_out[0][0]  # number fails
        total_values = check_out[0][1]  # total number of data values

        # list of series values where there are missing values for the data
        list_series_values = check_out[1]

        pct_fails = 100 * number_missing / total_values
        message_elements = [number_missing, pct_fails, list_series_values]

        return pct_fails, message_elements


class OutlierValuesHandler(object):
    @staticmethod
    def process_check_returns(check_out):

        if all(map(lambda x: type(x) in [int, float], check_out[0])):
            num_outliers = len(check_out[0])
        else:
            num_outliers = len(list(itertools.chain(*check_out[0])))

        pct_fails = 100 * num_outliers / check_out[1]
        message_elements = [num_outliers,
                            pct_fails, check_out[0]]

        return pct_fails, message_elements


class Report(object):
    # values are pandoc output formats
    valid_report_formats = {
        "html": "html",
        "md": "gfm",
        "pdf": "pdf",
        "docx": "docx"}
    default_report_columns_passing = [
        "original_name",
        "check_name",
        "data_origin",
        "check_pass"  # this is dropped when the report is generated

    ]
    default_report_columns_failing = [
        "original_name",
        "check_name",
        "data_origin",
        "severity",
        "issue_message"
    ]
    default_group_by = ["original_name", "check_name"]
    default_report_file_path = Path.joinpath(Path.cwd(), "report.html")
    default_report_format = "html"
    default_report_config_file = "report-conf.json"
    column_names_map = {
        "original_name": "Parameter name",
        "data_origin": "Data origin",
        "check_name": "Type of check",
        "check_pass": "check_pass",
        "check_out": "Issue details",
        "py_name": "Python-safe parameter name (long)",
        "py_short_name": "Python-safe parameter name (long)",
        "file": "File name",
        "sheet": "Sheet name",
        "transposed": "Transposed",
        "cell": "Cell code",
        "coords": "Coordinates",
        "check_description": "Description of the check",
        "check_target": "Target of the check",
        "check_arg": "Check arguments",
        "x_row_or_col": "Row or column number of the x axis",
        "severity": "Issue severity",
        "issue_message": "Issue description",
    }
    check_names_map = {
        "outlier_values": "Outlier detection",
        "missing_values": "Missing values",
        "missing_values_data": "Missing values in data",
        "missing_values_series": "Missing values in series",
        "series_monotony": "Series monotony",
        "series_range": "Series range",
        "series_increment_type": "Series trend"
    }
    report_messages = {
        "PASSING_HEADER": "<h2>Passing tests</h2>\n<br>\n",
        "FAILING_HEADER": "<h1>Failing tests</h1>\n<br>\n",
        "SUMMARY_HEADER": "<h1>Summary</h1>\n<br>\n",
        "NUM_PARAMS_ANALYZED_BOLD":
        "<b>Number of model parameters analyzed</b>: {}\n",
        "NUM_FAILING_CHECKS_BOLD":
        "<b>Number of failing checks</b>: {} ({:.2f} %)\n",
        "NUM_CHECKS_EVALUATED_BOLD": "<b>Number of checks evaluated</b>: {}\n",
        "NUMBER_ISSUES_PARAMETER": "<h2>Number of issues per parameter</h2>\n",
        "NUMBER_ISSUES_PARAMETER_BY_TYPE":
        "<h2>Number of issues of each severity for each parameter</h2>\n",
        "NUMBER_TYPE_ISSUES": "<h2>Number of issues of each type</h2>\n",
        "NUMBER_SEVERITY_ISSUES": "<h2>Number of issues of each severity</h2>\n",
        "NUMBER_DATA_ORIGIN": "<h2>Number of issues in each data file</h2>\n",
        "WHITESPACE": "<br>\n",
        "NO_FAILING_CHECKS": "All checks passed.\n",
        "NO_PASSING_CHECKS": "All checks failed.\n"
    }

    default_values = {
        "outlier_values": {"WARNING": 20, "ERROR": 30, "CRITICAL": 50},
        "missing_values": {"WARNING": 20, "ERROR": 30, "CRITICAL": 50},
        "missing_values_data": {"WARNING": 20, "ERROR": 30, "CRITICAL": 50},
        "missing_values_series": {"WARNING": 20, "ERROR": 30, "CRITICAL": 50},
        "series_monotony": "CRITICAL",
        "series_range": "ERROR",
        "series_increment_type": "ERROR"}

    # the severity of the issues of these types are accompained with a
    # percentage of fails defines the handler that is needed to process the
    # thresholds
    handler_map = {
        "outlier_values": OutlierValuesHandler,
        "missing_values": MissingValuesHandler,
        "missing_values_data": MissingValuesDataHandler,
        "missing_values_series": MissingValuesSeriesHandler,
        "series_monotony": None,
        "series_range": None,
        "series_increment_type": None}

    default_check_messages = {
     "outlier_values": "The field has {} ({:.1f}%) potential outliers ({})",
     "missing_values": "The field has {} ({:.1f}%) missing values.",
     "missing_values_data": "The field has {} ({:.1f}%) missing values "
                            "corresponding to series values: {}.",
     "missing_values_series": "The field has {} ({:.1f}%) missing series "
                              "values.",
     "series_monotony": "The series is not monotonic.",
     "series_range": "The series values are outside the given range.",
     "series_increment_type":
     "The series trend does not follow the expected trend."}

    def __init__(self, out):

        self.data = out
        self.buffer = StringIO()
        self.verbose = None
        self.report_format = None
        self.report_file_path = None
        self.report_config = None
        self.check_objects = {}

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, out):
        df = pd.DataFrame(out)

        def generate_data_origin_column(x):
            final_result = []
            for i in range(len(x.file)):
                if x.check_target in ["data", "constant"]:
                    columns = ['file', 'sheet', 'cell']
                    names = ["file", "tab", "cell/range name"]

                elif x.check_target == "series":
                    columns = ['file', 'sheet', 'x_row_or_col']
                    names = ["file", "tab", "series cell/range name"]
                elif x.check_target == "dataseries":
                    columns = ['file', 'sheet', 'x_row_or_col', 'cell']
                    names = ["file", "tab", "series cell/range name",
                             "data cell/range name"]
                else:
                    raise ValueError(
                        f"Invalid check_target '{x.check_target}'")
                string = ", ".join(
                    [
                        f"{name}: {x[col][i]}"
                        for name, col in zip(names, columns)
                    ])
                if string not in final_result:
                    final_result.append(string)

            return " \n".join(final_result)

        if df.empty:
            warnings.warn("Nothing to report. The dataframe is empty.")
        else:
            # adding column with the location of the data in the spreadsheet,
            # and keeping only unique values
            df["data_origin"] = df.apply(
                lambda x: generate_data_origin_column(x),
                axis=1,
                ).astype(str)
        self._data = df

    @property
    def report_config_path(self):
        return self._report_config_path

    @report_config_path.setter
    def report_config_path(self, file_path):
        """
        Checks if the file exists and is a JSON file and sets the
        report_config_file attribute.
        """
        if Path(file_path).is_file():
            if Path(file_path).suffix == ".json":
                self._report_config_path = file_path
            else:
                raise ValueError("Report configuration file must be a JSON "
                                 "file.")
        else:
            raise FileNotFoundError("Report configuration file not found.")

    def __update_report_config(self):
        """
        Updates the check_objects attribute with the values of the
        report_config attribute.
        """

        for check, value in self.report_config.items():
            self.check_objects[check].update_value(value)

    def build_report(self, report_conf=None, verbose=False):

        """
        Generate a StringIO containing the report.
        Every time the method is called, the report configuration is reset to
        defaults, and then updated with the value passed in report_conf.

        Parameters
        -----------
        report_conf: dict or str or Path (optional)
            If a str or Path is passed, it is used as the path to the report
            configuration.
            If a dict is passed, it is used as the report configuration itself.

        verbose: bool (optional)
            If True, the report contains more statistics and passing tests.

        Returns
        --------
        buffer: StringIO
            Containing the report content in html
        """

        # clean the buffer
        self.buffer.truncate(0)
        self.buffer.seek(0)
        self.verbose = verbose

        # neither passing nor failing checks
        if self.data.empty:
            warnings.warn("Nothing to report. The dataframe is empty.")
            return self.buffer

        # generate default check_objects configuration
        self.check_objects = self.__build_default_check_objects()

        if not report_conf:
            warnings.warn("No report configuration provided. Using default.")
            default_config_path = Path(__file__).parent \
                / "default-report-conf.json"
            self.report_config = self.__validate_json(default_config_path)
        else:
            # the user can pass a new configuration file or a dictionary
            if isinstance(report_conf, (str, Path)):
                # check that the report configuration file is valid and load it
                self.report_config = self.__validate_json(report_conf)
            elif isinstance(report_conf, dict):
                self.report_config = report_conf
            else:
                raise ValueError("report_conf must be a str, Path or dict.")

        # check that the configuration defined by the user is valid
        self.__validate_report_configuration()

        # update default self.check_objects with those from the config file
        self.__update_report_config()

        # assign it again to avoid modifying the original dataframe
        # also, the write report may be called multiple times, so we need to
        # keep the original dataframe untouched
        df = self.data.copy(deep=True)
        passing = df.loc[df["check_pass"].isin([True])]
        failing = df.loc[df["check_pass"].isin([False])]

        # renaming columns of the full df and of the group_by columns
        df.rename(columns=self.__class__.column_names_map, inplace=True)
        group_by = [self.__class__.column_names_map[x] for x in
                    self.__class__.default_group_by]

        # generate the report main body (failing checks only)
        if not failing.empty:  # if there are failing checks
            # adds the severity and issue description columns to the failing df
            failing = self.__grade_issue_severity(failing)

        self.__write_report_body(failing, group_by)

        # write the summary of failing tests and display the passing tests
        if self.verbose:
            self.__write_report_summary(df, passing, failing, group_by)

        return self.buffer

    def report_to_file(self, report=None, report_filename=None):
        """
        Writes the report to a file. Uses pandoc to convert the default html
        report to the rest of supported formats.

        Parameters:
        -----------
        report: StringIO (optional)
            StringIO containing the report content in html

        report_filename: str or Path (optional)
            The path of the resulting report file.

        Returns:
        --------
        None

        """
        pandoc_version = pypandoc.get_pandoc_version().split(".")[:2]

        if tuple(int(i) for i in pandoc_version) < (2, 17):
            warnings.warn(f"pandoc version in your system is "
                          f"{'.'.join(pandoc_version)}. "
                          "Please install pandoc version 2.17 or above.")

        # TODO add support for other formats available in pandoc

        # if the report argument is None but the buffer contains the report
        # result, use the buffer, else raise
        if not report:
            if self.buffer.getvalue():  # buffer not empty
                report = self.buffer
                warnings.warn("No report provided. Using that in the buffer.")
            else:
                raise ValueError("No report provided.")

        report = report.getvalue()

        # get report format and path from the argument report_filename
        self.report_format, self.report_file_path = \
            self.__get_report_path_and_suffix(report_filename)

        with open(self.report_file_path, "w") as f:
            if self.report_format == "html":
                f.write(report)
            elif self.report_format == "md":
                pandoc_fmt = self.__class__.valid_report_formats[
                    self.report_format]
                output = pypandoc.convert_text(
                    report.replace('\n', ' ').replace('\r', ''),
                    pandoc_fmt,
                    format="html",
                    extra_args=[]
                )
                f.write(output)
            elif self.report_format == "pdf":
                output = pypandoc.convert_text(
                    report,
                    "pdf",
                    format="html",
                    outputfile=str(self.report_file_path),
                    extra_args=['--pdf-engine', 'xelatex',
                                '-V', 'geometry:landscape',
                                '-V', 'fontsize:6pt']
                )
            elif self.report_format == "docx":
                output = pypandoc.convert_text(
                    report,
                    "docx",
                    format="html",
                    outputfile=str(self.report_file_path),
                    extra_args=[]
                )

    def __build_default_check_objects(self):

        check_objects = {}

        for check_name, defaults in self.__class__.default_values.items():

            if self.__class__.handler_map[check_name] is None:
                # does not need a handler
                check_objects[check_name] = Check(
                    defaults,
                    self.__class__.default_check_messages[check_name],
                    check_name)
            else:
                check_objects[check_name] = CheckThresholds(
                    defaults,
                    self.__class__.default_check_messages[check_name],
                    self.__class__.handler_map[check_name], check_name)

        return check_objects

    def __validate_json(self, report_config_path):
        """
        Validate the report_config_path and load the configuration.

        Parameters
        -----------
        report_config_path: str or Path
            Path to the report configuration file.

        Returns
        --------
        config: dict
            The report configuration.
        """

        if isinstance(report_config_path, str):
            report_config_path = Path(report_config_path)

        self.report_config_path = report_config_path

        try:
            config = json.load(open(self.report_config_path,))
        except ValueError:
            raise ValueError("Report configuration file not correctly"
                             " formatted.")
        return config

    def __validate_report_configuration(self):
        """
        Validate that the report configuration check names are correct.
        Update the default report configuration with the values from the user
        configuration (json).

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        for check_name, value in self.report_config.items():

            # verify that the check name is correct
            if check_name not in self.handler_map.keys():
                raise ValueError("Invalid key in report configuration"
                                 f" ({check_name}).")
            # verify that the value type is correct
            if not isinstance(value,
                              type(self.__class__.default_values[check_name])):
                raise ValueError(
                    f"{check_name} in the report configuration file should be "
                    f"a {type(self.__class__.default_values[check_name])}.")

            # update the default values with the user configuration
            if isinstance(value, dict):
                # verify that the keys in the Severity thresholds dict are ok
                if not all(map(lambda x: x in Severity.list(), value.keys())):
                    raise ValueError(
                        f"Invalid severity name for {check_name}.")
                # check that all values are integers
                if not all(map(lambda x: type(x) == int, value.values())):
                    raise TypeError(
                        f"{check_name} thresholds must be integers.")

                # check that all values are between 0 and 100
                if not all(map(lambda x: x in range(0, 101, 1),
                               value.values())):
                    raise ValueError(
                        f"{check_name} thresholds must be between 0 and 100.")

                # check that the values are higher for higher severities (e.g.
                # WARNING < CRITICAL < ERROR))
                if list(
                    dict(sorted(value.items(), key=operator.itemgetter(1))
                         ).keys()) != Severity.list():
                    raise ValueError(
                        f"{check_name} thresholds must be defined in "
                        "ascending order, corresponding to the tolerances for:"
                        f" {', '.join(Severity.list())}")

    def __get_report_path_and_suffix(self, report_file_path=None):
        """
        Validates the report path and returns the suffix and the absolute path.

        Parameters
        ----------
        report_filename: str or Path
            The path of the results file passed by the user.

        Returns
        -------
        report_file_path: Path (optional)
            The absolute path of the report file.

        """
        if not report_file_path:
            warnings.warn("No report file path defined. Using default"
                          " (report.html).")
            return "html", Path(__file__).parent.parent / "report.html"

        # check if the report_path passed by the user is a valid path
        if isinstance(report_file_path, (Path, str)):
            if isinstance(report_file_path, str):
                report_file_path = Path(report_file_path)

            if not report_file_path.suffix:
                raise ValueError(
                    "Report path must include the file type suffix "
                    "(e.g. report.html)."
                )
            else:
                suffix = self.__validate_report_file_format(
                    report_file_path.suffix)

                if not report_file_path.is_absolute():
                    logging.info(
                        "Relative path provided for the report file."
                    )
                    return suffix, report_file_path.absolute()
                else:
                    return suffix, report_file_path
        else:
            raise TypeError("Report path must be a string or a Path object.")

    def __validate_report_file_format(self, fmt):
        """
        Validates the format of the json in which the configuration of the
        report is detailed.

        Parameters
        -----------
        fmt: str
            Report format.

        Returns
        --------
        fmt: str
            Validated report format.
        """
        fmt_ = fmt[1:]

        if fmt_ in self.__class__.valid_report_formats:
            return fmt_
        else:
            raise ValueError(
                "The only supported report formats are {}.".format(
                 ", ".join(self.__class__.valid_report_formats.keys()))
                )

    def __grade_issue_severity(self, df_fail):
        """
        Adds severity and issue_message columns to the dataframe of failed
        checks.

        Parameters
        ----------
        df_fail : pandas.DataFrame
            Dataframe with the failed checks

        Returns
        -------
        df_fail : pandas.DataFrame
            Dataframe with the failed checks and the added columns.
        """
        def issue_severity_and_description(check_out, check_object):
            if isinstance(check_object, CheckThresholds):
                check_object.update_severity_and_message(check_out)
            return pd.Series({"severity": check_object.display_severity,
                              "issue_message": check_object.message})

        new_cols = df_fail.apply(
            lambda x: issue_severity_and_description(
                x["check_out"],
                self.check_objects[x["check_name"]]
                ),
            axis=1,
        )
        df_fail = df_fail.merge(new_cols, left_index=True, right_index=True)
        return df_fail

    def __write_report_body(self, failing, group_by):
        """
        Writes the report body.

        Parameters
        ----------
        failing : pandas.DataFrame
            Dataframe with the failed checks.
        group_by : list
            List of columns to group by.

        Returns
        -------
        None

        """
        # Start writing the report contents in the buffer
        self.buffer.write(
            self.__class__.report_messages["FAILING_HEADER"])

        if not failing.empty:
            # Select only the desired output columns, use clean names, and
            # reindex
            failing_simplified = failing[
                self.__class__.default_report_columns_failing
                ].replace(
                    {"check_name": self.__class__.check_names_map}
                    ).rename(
                    columns=self.__class__.column_names_map).set_index(
                        group_by)

            self.__df_to_buffer(failing_simplified)
        else:
            self.buffer.write(
                self.__class__.report_messages["NO_FAILING_CHECKS"])

        self.buffer.write(self.__class__.report_messages["WHITESPACE"])

    def __write_report_summary(self, df, passing, failing, group_by):
        """
        Writes a summary of the results in the buffer.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe containing all the results of the checks.
        passing : pandas.DataFrame
            Dataframe containing the passing results of the checks.
        failing : pandas.DataFrame
            Dataframe containing the failing results of the checks.
        group_by : list
            List of columns to group the results by.

        Returns
        -------
        None

        """

        # calculate the statistics of failing tests, if there are any
        if not failing.empty:

            # Select only the desired output columns, use clean names, and
            # reindex

            # [self.__class__.default_report_columns_failing]
            failing = failing.replace(
                    {"check_name": self.__class__.check_names_map}
                    ).rename(
                    columns=self.__class__.column_names_map).set_index(
                        group_by)

            grouped_by_param_name = (
                failing.groupby(
                    by=self.__class__.column_names_map["original_name"]
                    )[self.__class__.column_names_map["severity"]
                      ].count().to_frame(name="Number")
            )

            grouped_by_check_type = (
                failing.groupby(
                    by=self.__class__.column_names_map["check_name"])[
                    self.__class__.column_names_map["severity"]
                ]
                .count()
                .to_frame(name="Number")
            )
            grouped_by_check_type["Percent of all issues"] = \
                100 * grouped_by_check_type["Number"] / \
                grouped_by_check_type["Number"].sum()
            grouped_by_check_type["Percent of all issues"] = \
                grouped_by_check_type["Percent of all issues"].round(
                    decimals=1)

            grouped_by_var_name_and_severity = (
                failing.groupby([
                    self.__class__.column_names_map["original_name"],
                    self.__class__.column_names_map["severity"]])[
                    self.__class__.column_names_map["severity"]].count(
                    ).to_frame(name="Number")).reset_index(
                    ).set_index(
                        self.__class__.column_names_map["original_name"])

            grouped_by_severity = (
                failing.groupby(self.__class__.column_names_map["severity"])[
                    self.__class__.column_names_map["severity"]].count(
                    ).to_frame(name="Number"))
            grouped_by_severity["Percent of all issues"] = \
                100 * grouped_by_severity["Number"]/grouped_by_severity[
                    "Number"].sum()
            grouped_by_severity["Percent of all issues"] = \
                grouped_by_severity["Percent of all issues"].round(decimals=1)

            # all files from which all checks imported data
            # if data for one variable was loaded from two (or more) separate
            # files (very unlikely), but the issue was only in one of them,
            # the other files will also be counted as having an issue.
            all_imported_files = list(itertools.chain.from_iterable(
                [set(row["File name"]) for _, row in failing.iterrows()]))

            # count number of times each file was imported
            a = {x: all_imported_files.count(x) for x in set(
                all_imported_files)}
            # convert to DataFrame
            group_by_data_origin = pd.DataFrame.from_dict(a,
                                                          orient='index',
                                                          columns=["Number"])
            group_by_data_origin.index.name = "File name"

        #######################################################################

        self.buffer.write(self.__class__.report_messages["WHITESPACE"])
        self.buffer.write(self.__class__.report_messages[
            "SUMMARY_HEADER"])

        # Lines with totals
        self.buffer.write(
            self.__class__.report_messages[
                "NUM_PARAMS_ANALYZED_BOLD"].format(
                    len(df[self.__class__.column_names_map[
                        "original_name"]].unique())
            )
        )
        self.buffer.write(self.__class__.report_messages["WHITESPACE"])
        self.buffer.write(
            self.__class__.report_messages[
                "NUM_CHECKS_EVALUATED_BOLD"].format(df.shape[0])
        )
        self.buffer.write(self.__class__.report_messages["WHITESPACE"])

        if not failing.empty:
            self.buffer.write(
                self.__class__.report_messages[
                    "NUM_FAILING_CHECKS_BOLD"].format(
                    failing.shape[0], 100 * failing.shape[0] / df.shape[0]
                )
            )
        else:
            self.buffer.write(
                self.__class__.report_messages[
                    "NUM_FAILING_CHECKS_BOLD"].format(0, 0)
            )

        if not failing.empty:
            # Number of issues of each severity
            self.buffer.write(self.__class__.report_messages["WHITESPACE"])
            self.buffer.write(self.__class__.report_messages[
                "NUMBER_SEVERITY_ISSUES"])
            self.__df_to_buffer(grouped_by_severity.reset_index(), False)

            # Number of issues of each type
            self.buffer.write(self.__class__.report_messages["WHITESPACE"])
            self.buffer.write(self.__class__.report_messages[
                "NUMBER_TYPE_ISSUES"])
            self.__df_to_buffer(grouped_by_check_type.reset_index(), False)

            # Number of issues in each data file
            self.buffer.write(self.__class__.report_messages["WHITESPACE"])
            self.buffer.write(self.__class__.report_messages[
                "NUMBER_DATA_ORIGIN"])
            self.__df_to_buffer(group_by_data_origin.reset_index(), False)

            # Number of issues of each severity for each parameter
            self.buffer.write(
                self.__class__.report_messages[
                    "NUMBER_ISSUES_PARAMETER_BY_TYPE"]
            )
            self.__df_to_buffer(grouped_by_var_name_and_severity)

            # Number of issues per parameter
            self.buffer.write(self.__class__.report_messages["WHITESPACE"])
            self.buffer.write(
                self.__class__.report_messages["NUMBER_ISSUES_PARAMETER"]
            )
            self.__df_to_buffer(grouped_by_param_name)
            self.buffer.write(self.__class__.report_messages["WHITESPACE"])

        # Passing tests
        self.buffer.write(self.__class__.report_messages["WHITESPACE"])
        self.buffer.write(self.__class__.report_messages["PASSING_HEADER"])

        if not passing.empty:
            passing_simplified = passing[
                self.__class__.default_report_columns_passing].replace(
                    {"check_name": self.__class__.check_names_map}
                    ).rename(
                        columns=self.__class__.column_names_map
                        ).set_index(group_by)

            self.__df_to_buffer(passing_simplified.drop(
                labels="check_pass",
                axis=1))

        else:
            self.buffer.write(self.__class__.report_messages[
                "NO_PASSING_CHECKS"])

    def __df_to_buffer(self, df, index=True):
        """
        Writes DataFrame to buffer.

        Parameters
        -----------
        df: pd.DataFrame
            DataFrame to write to buffer.

        index: bool
            If True, index will be printed.

        Returns
        --------
        None

        """
        self.buffer.write("\n")

        if index:
            df.index.names = [None]*len(df.index.names)
            self.buffer.write(df.to_html(justify="left"))

        else:
            self.buffer.write(df.to_html(justify="left", index=index))

        self.buffer.write("\n\n")
