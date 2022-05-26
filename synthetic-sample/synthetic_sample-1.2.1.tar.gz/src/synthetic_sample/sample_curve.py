# ====
# beverageBI.synthetic_sample_curve.py
# Class that defines a synthetic curve and methods to apply it over a time period
# ====


import holidays
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
from typing import Union
from isoweek import Week


class AnchorType(Enum):
    """
    Enumeration of the available anchor types
    """
    holiday = "holiday"
    week_of_year = "week_of_year"
    month_of_year = "month_of_year"
    day_of_year = "day_of_year"


class PeriodType(Enum):
    """
    Enumeration of the available period types
    """
    week = "week"
    month = "month"


class SeasonDefinition(Enum):
    """
    Enumeration of the available seasons and the months they include
    """
    Q1 = [1, 2, 3]
    Q2 = [4, 5, 6]
    Q3 = [7, 8, 9]
    Q4 = [10, 11, 12]


class SampleCurveFeature:
    """Defines a single feature of an annual sales curve

    Attributes:
        anchor_type: What type of annual anchor is used to define the feature
            Possible values: "holiday", "week_of_year", "month_of_year", "day_of_year"
        anchor_point: Annual point to define the feature
            Possible values: (string) - holiday name, (int) - week or day of year
        anchor_value: Cumulative percent of total sales (0.0-1.0) completed by the end of the period of the anchor_point
        relative_start: Number of periods before anchor_point to define a relative cumulative percent value
        start_value: Cumulative percent of total sales (0.0-1.0) completed by the end of the period indicated by relative_start
        relative_end: Number of periods before anchor_point to define a relative cumulative percent value
        end_value: Cumulative percent of total sales (0.0-1.0) completed by the end of the period indicated by relative_end
    """

    def __init__(self, anchor_type: AnchorType, anchor_point: Union[str, int], anchor_value: Union[str, int],
                 period_type: PeriodType, relative_start: int = None, start_value: float = None,
                 relative_end: int = None,
                 end_value: float = None) -> None:
        """ Initializes the SampleCurveFeature
        """

        anchor_type = AnchorType(anchor_type)
        if anchor_type not in AnchorType:
            raise NotImplementedError

        self.anchor_type = anchor_type
        self.anchor_point = anchor_point
        self.anchor_value = anchor_value
        self.period_type = period_type
        self.relative_start = relative_start
        self.start_value = start_value
        self.relative_end = relative_end
        self.end_value = end_value

    def add_to_curve(self, year: int, year_df: pd.DataFrame) -> None:
        """ Add this feature to a dataframe for a specified year

        Args:
            year: Calendar year to add the feature for
            year_df: Dataframe to add the feature to, by modifying the percentages in value_column_name
        """
        self.__create_feature_for_year(year, year_df)
        if self.anchor_period is not None:
            self.__add_change_point(year_df, self.anchor_period, self.anchor_value)

            if self.start_value:
                self.__add_change_point(year_df, self.start_period, self.start_value)

            if self.end_value:
                self.__add_change_point(year_df, self.end_period, self.end_value)

    def __create_feature_for_year(self, year: int, year_df: pd.DataFrame) -> None:
        """  Identifies the dates to modify for the feature based on the specific calendar year

        Args:
            year: Calendar year to create the feature for
            year_df: Dataframe of rows for each period, to determine relative dates
        """
        if self.anchor_type == AnchorType.holiday:
            # Get Holiday Period
            holiday_date = holidays.UnitedStates(years=year).get_named(self.anchor_point)[0]
            holiday_date = pd.to_datetime(holiday_date)
            if self.period_type == PeriodType.week:
                self.anchor_period = holiday_date - timedelta(days=(holiday_date.weekday() + 1))
            if self.period_type == PeriodType.month:
                self.anchor_period = pd.Timestamp(holiday_date.year, holiday_date.month, 1)

        elif self.anchor_type == AnchorType.week_of_year:
            if self.period_type == PeriodType.month:
                raise ValueError("Cannot apply week_of_year feature to monthly curve")
            try:
                # If year has 53 weeks, adjust for extra week (First week of Q4)
                if Week(year, 53).week == 53:
                    if self.anchor_point >= 42:
                        self.anchor_point += 1

                date = year_df.loc[self.anchor_point - 1][SampleCurve.period_column_name]
                self.anchor_period = date
            except KeyError:
                self.anchor_period = None

        elif self.anchor_type == AnchorType.month_of_year:
            if self.period_type == PeriodType.week:
                raise ValueError("Cannot apply month_of_year feature to weekly curve")
            try:
                date = year_df.loc[self.anchor_point - 1][SampleCurve.period_column_name]
                self.anchor_period = date
            except KeyError:
                self.anchor_period = None

        elif self.anchor_type == AnchorType.day_of_year:
            date_string = f"{year}-{self.anchor_point}"
            date = pd.to_datetime(date_string, format="%Y-%j")
            # TODO add monthly handling capabilities
            if self.period_type == PeriodType.week:
                self.anchor_period = date - timedelta(days=(date.weekday() + 1))
            else:
                raise NotImplementedError("day_of_year features not implemented for monthly curves")

        if self.relative_start:
            if (self.relative_start >= 0) | (type(self.relative_start) != int):
                raise ValueError("relative_start must be a negative integer")
            if self.period_type == PeriodType.week:
                self.start_period = self.anchor_period + timedelta(days=self.relative_start * 7)
            elif self.period_type == PeriodType.month:
                self.start_month = self.anchor_period + timedelta(months=self.relative_start)

        if self.relative_end:
            if (self.relative_end <= 0) | (type(self.relative_end) != int):
                raise ValueError("relative_end must be a positive integer")
            if self.period_type == PeriodType.week:
                self.end_period = self.anchor_period + timedelta(days=self.relative_end * 7)
            elif self.period_type == PeriodType.month:
                self.start_month = self.anchor_period + timedelta(months=self.relative_end)

    @staticmethod
    def __add_change_point(year_df: pd.DataFrame, period: datetime, value: float) -> None:
        """ Updates the percentage of the value_column_name column in year_df for the record where the period_column_name column equals period

        Args:
            year_df: Dataframe to modify, by changing the percentage in value_column_name
            period: value in the period_column_name column for the record to modify
            value: percentage to update the value_column_name to
        """
        if value:
            period_mask = year_df[SampleCurve.period_column_name] == period
            year_df.loc[period_mask, SampleCurve.value_column_name] = value


class SampleCurve:
    """ Defines an annual sales curve to generate synthetic data

    Args:
        period_type: name of the column to designate the period
        features_list: list of SampleCurveFeature objects to make up the curve
    """
    value_column_name = "value"
    period_column_name = "period"

    def __init__(self, period_type: PeriodType, features_list=None):
        """ Initializes a SampleCurve for the period_type with the specific features
        """
        self.period_type = period_type
        if features_list is not None:
            self.curve_features = features_list

    def create_year(self, year: int) -> pd.DataFrame:
        """ Creates a dataframe for each period_type period for the year with null values for each row

        Args:
            year: Calendar year to create a dataframe for

        Returns:
            Dataframe with each period in the year as a row
        """
        start_date = pd.Timestamp(year, 1, 1)
        end_date = pd.Timestamp(year + 1, 1, 1) + timedelta(days=-1)

        # Create dataframe with a row for each period in the year
        year_df = pd.DataFrame()
        if self.period_type == PeriodType.week:
            # First week has the first Thursday of the year
            # If first day of year comes after Thursday, roll the start date back to include that Monday in the date range
            if start_date.dayofweek in [1, 2, 3]:
                start_date -= timedelta(days=7)

            # Last week is the week before the first Thursday of the next year
            # If the last day of the year comes before
            if end_date.dayofweek < 3:
                end_date += timedelta(days=-7)

            year_df[self.period_column_name] = pd.date_range(start=start_date, end=end_date, freq="W-MON")
            year_df = year_df.reset_index()
            year_df = year_df.rename(columns={"index": "week_number"})
            year_df["week_number"] += 1

        elif self.period_type == PeriodType.month:
            year_df[self.period_column_name] = pd.date_range(start=start_date, end=end_date, freq="MS")

        # Add the value column with nulls for each row
        year_df[self.value_column_name] = np.NaN

        return year_df

    def apply(self, yearly_metadata_dict: dict, seasonal_distribution: dict, modifiers_list: list) -> pd.DataFrame:
        """ Applies the curve to each year specified in yearly_metadata_dict with the associated parameters

        Args:
            yearly_metadata_dict: dictionary with each year to compute as a key and a dictionary with the following as values
                - start_date: date to include in the first period
                - end_date: date to include in the last period
                - sales: total number of sales to distribute
            seasonal_distribution: dictionary with the percentage of sales in each quarter

        Returns:
            dataframe with sales by period for the entire span covered by yearly_metadata_dict
        """
        # Create each yearly curve separately and append as a dataframe to annual_curves
        annual_curves = {}
        for year in yearly_metadata_dict:
            # Create the empty dataframe for the year
            year_dict = yearly_metadata_dict.get(year)
            year_df = self.create_year(year)

            # Add each feature to the curve
            for feature in self.curve_features:
                feature.add_to_curve(year, year_df)

            # Reduce cumulative sum to individual period values
            year_df["temp"] = year_df[self.value_column_name].diff().fillna(
                year_df[self.value_column_name])

            # Fill in intermediary values with average of the values between them
            missing_mask = year_df.value.isnull()
            if sum(missing_mask) > 0:
                average_mask = year_df.week_number.isin([41, 44])
                fill_in_value = year_df[average_mask].temp.mean()
                fill_mask = year_df.week_number.isin([42, 43])
                year_df.loc[fill_mask, "temp"] = fill_in_value
                year_df["pct_of_total"] = year_df["temp"] / year_df["temp"].sum()

                overshoot = year_df.temp.sum() - 100
                year_df["adjustment"] = overshoot * year_df["pct_of_total"]
                year_df["temp"] = year_df["temp"] - year_df["adjustment"]
                year_df["value"] = year_df.temp.cumsum()
                year_df = year_df.drop(columns=["temp", "pct_of_total", "adjustment"])

            # Reduce cumulative sum to individual period values
            year_df[self.value_column_name] = year_df[self.value_column_name].diff().fillna(
                year_df[self.value_column_name])

            # Redistribute percentages according to seasonal_distribution
            for quarter in seasonal_distribution:
                mask = year_df[self.period_column_name].dt.month.isin(SeasonDefinition[quarter].value)
                unscaled_percent = year_df.loc[mask, self.value_column_name].sum()
                scaling_factor = seasonal_distribution[quarter] / unscaled_percent
                year_df.loc[mask, self.value_column_name] = year_df.loc[mask, self.value_column_name] * scaling_factor

            # Filter out all periods that were not included
            for date_cutoff in ["start_date", "end_date"]:
                if year_dict.get(date_cutoff) is not None:
                    if self.period_type == PeriodType.week:
                        cutoff_period = year_dict[date_cutoff] - timedelta(days=(year_dict[date_cutoff].weekday()))
                    elif self.period_type == PeriodType.month:
                        cutoff_period = pd.Timestamp(year_dict[date_cutoff].year, year_dict[date_cutoff].month, 1)
                    else:
                        raise NotImplementedError(f"Only week and month PeriodTypes are implemented")
                    if date_cutoff == "start_date":
                        cutoff_mask = year_df[self.period_column_name] >= cutoff_period
                    else:
                        cutoff_mask = year_df[self.period_column_name] <= cutoff_period
                    year_df = year_df[cutoff_mask]

            # If covid modifier is requested, apply that scaling
            if "covid" in modifiers_list:
                year_df = self.apply_covid_distribution(year_df)

            # Distribute total sales amount
            normalize_sum = year_df[self.value_column_name].sum()
            year_df["value"] = (year_df["value"] / normalize_sum) * year_dict["sales"]

            # Apply smoothing
            year_df[self.value_column_name] = year_df[self.value_column_name].ewm(span=2).mean()
            year_df[self.value_column_name] = year_df[self.value_column_name].astype(int)

            annual_curves[year] = year_df
            
        # Combine all of the dataframes and return
        annual_sales_curve = pd.concat(annual_curves)

        return annual_sales_curve

    def apply_covid_distribution(self, year_df):
        start_date = datetime(2020, 3, 26)
        end_date = datetime(2021, 9, 1)
        covid_scaling_factor = 1.333
        mask_covid = (year_df[self.period_column_name] >= start_date) & (year_df[self.period_column_name] < end_date)
        year_df.loc[mask_covid, self.value_column_name] = year_df.loc[mask_covid, self.value_column_name] * covid_scaling_factor

        return year_df


class CustomSampleCurve(SampleCurve):
    """ Enables creation of creating a custom sales curve by passing in a list of metadata describing SalesCurveFeatures
    """

    def __init__(self, period_type, def_dict_list):
        """ Initializes a CustomSampleCurve using a list of dictionaries

        Args:
            period_type: type of periods to make up the curve
            def_dict_list: list of dictionaries defining each feature, where each must have keys corresponding
                           to the SampleCurveFeature attributes:
                Required: anchor_type, anchor_point, anchor_value, period_type
                Optional: relative_start, start_value, relative_end, end_value
        """
        # Compile the full list of SampleCurveFeatures from the provided dictionary
        features = []
        for def_dict in def_dict_list:
            features.append(
                SampleCurveFeature(anchor_type=def_dict.get("anchor_type"),
                                   anchor_point=def_dict.get("anchor_point"),
                                   anchor_value=def_dict.get("anchor_value"),
                                   period_type=def_dict.get("period_type"),
                                   relative_start=def_dict.get("relative_start"),
                                   start_value=def_dict.get("start_value"),
                                   relative_end=def_dict.get("relative_end"),
                                   end_value=def_dict.get("end_value"))
            )
        # Initialize the curve with full list of features
        SampleCurve.__init__(self, period_type, features)
