import pandas as pd
import numpy as np
from tqdm import tqdm
import itertools
import argparse
import pickle
import time
import PIconnect as PI

try:
    import OSIsoft
except:
    print("Check queryMultipleTimeFrames function if exists -- Might not be able to find OSIsoft.")

tz = "Etc/GMT-10" if time.localtime().tm_isdst == 0  else "Etc/GMT-11"
PI.PIConfig.DEFAULT_TIMEZONE = tz

SERVER = PI.PIServer()


# <editor-fold desc="Helper Funcitons">
def rollbackTagNames(tag_names, accept_single_name=False):
    if accept_single_name:
        return tag_names.upper().replace("_", ".")
    return [tag_name.upper().replace("_", ".") for tag_name in tag_names]

# Save the object
def savePickle(obj, file_name):
    """
    Save a python object as a .pkl file
    """
    with open(file_name, mode="wb") as file:
        pickle.dump(obj, file)
        file.close()
        print(f"Saved the object to {file_name} successfully!")

# </editor-fold>


# <editor-fold desc="Global Querry Functions">
def getOneInterpolatedTag(tag_name, dates, step_size, periods):
    try:
        tag = SERVER.search(rollbackTagNames(tag_name, True))[0]
    except IndexError as indx_err:
        print(f"{tag_name} couldn't found. Skipping to other tags for Interpolated Values")
        return None, indx_err.__class__.__name__

    one_tag_series = getMultipleInterpolatedDateRanges(tag, dates, step_size, periods)

    return one_tag_series, tag


def getMultipleInterpolatedDateRanges(tag, dates, step_size, periods):
    multiple_range_series = pd.Series(dtype=str)

    for idx, (start_date, end_date) in enumerate(dates):
        single_range_series = getOneInterpolatedDateRange(tag, start_date, end_date, step_size, periods)
        multiple_range_series = pd.concat([multiple_range_series,single_range_series], axis=0)

    return multiple_range_series


def getOneInterpolatedDateRange(tag, start_date, end_date, step_size, periods):
    """by = ["y", "m", "d", "min", "s"] """

    start_date = pd.to_datetime(start_date, infer_datetime_format=True, dayfirst=True, exact=False)
    end_date = pd.to_datetime(end_date, infer_datetime_format=True, dayfirst=True, exact=False)
    dates = pd.date_range(start_date, end_date, periods=periods, tz=tz)

    single_range_series = pd.Series(dtype=str)

    for i in range(len(dates) - 1):
        data = tag.interpolated_values(dates[i], dates[i + 1], step_size)
        single_range_series = pd.concat([single_range_series, pd.Series(data.values.astype(str), index=data.index)], axis=0)
        print(f"Finished period {i}!")

    # Remove duplicate dates
    return single_range_series


def getOneRecordedTag(tag_name, dates, periods):
    """ Difference between interpolated and recorded: Recorded sends tag_name to all the way down to  getOneRange """
    try:
        tag = SERVER.search(rollbackTagNames(tag_name, True))[0]
    except IndexError:
        print(f"{tag_name} couldn't found. Skipping to other tags for Recorded values")
        return None

    one_tag_df = getMultipleRecordedDateRanges(tag, tag_name, dates, periods)

    return one_tag_df


def getMultipleRecordedDateRanges(tag, tag_name, dates, periods=4):
    multiple_range_df = pd.DataFrame(columns=["g", "DateTime", "tag_name", "record"])
    for (start_date, end_date) in dates:
        single_range_df = getOneRecordedDateRange(tag, tag_name, start_date, end_date, periods=periods)
        multiple_range_df = pd.concat([multiple_range_df,single_range_df], axis=0, ignore_index=True)

    return multiple_range_df


def getOneRecordedDateRange(tag, tag_name, start_date, end_date, periods=4):
    start_date = pd.to_datetime(start_date, infer_datetime_format=True, dayfirst=True, exact=False)
    end_date = pd.to_datetime(end_date, infer_datetime_format=True, dayfirst=True, exact=False)
    dates = pd.date_range(start_date, end_date, periods=periods, tz=tz)

    single_range_df = pd.DataFrame(columns=["g", "DateTime", "tag_name", "record"])

    for i in range(len(dates) - 1):
        data = tag.recorded_values(dates[i], dates[i + 1])
        single_range_df = pd.concat([single_range_df, pd.DataFrame({"g"     : "-1", "DateTime": data.index, "tag_name": tag_name,"record": data.values.astype(str)})], axis=0, ignore_index=True)

    return single_range_df
# </editor-fold>




class Querry():
    def __init__(self, **kwargs):
        """ Tags can be added and subtracted though doesn't let adding new date ranges.
            Create a new instance for that. """
        self.df = pd.DataFrame(columns=["g", "DateTime"])
        self.recording_df = pd.DataFrame(columns=["g", "DateTime", "tag_name", "record"])

        # Expected via kwargs
        self.controllers = []
        self.other_tags = []
        self.dates = []
        self.date_names = []
        self.step_size = None
        self.periods = None
        self.recorded_values = False
        self.interpolated_values = False

        # Gets calculated during operations
        self.continuous = []
        self.categorical = []
        self.all_found_tags = []

        self.found_tag_descriptions = {}
        self.found_tag_dtypes = {}

        self.n_tags = 0
        self.n_records = {}

        for (k, v) in kwargs.items():
            self.__setattr__(k, v)

        self.controllers = [m[0] + "_" + m[1] for m in itertools.product(self.controllers, ["pv", "sv", "mv", "mode"])
                            if m[0] != ""]
        if self.periods == 1:
            self.periods = 2

        self.all_searched_tags = self.controllers + self.other_tags

        # Get the recorded and interpolated values
        if self.recorded_values:
            self.queryRecordings()

        if self.interpolated_values:
            self.querryInterpolatedTags()

    # self.df.reset_index(drop=True, inplace=True)

    def querryInterpolatedTags(self):
        self._querryInterpolatedTags(self.all_searched_tags, self.dates, self.step_size, self.periods)

    def _querryInterpolatedTags(self, tag_names, dates, step_size, periods):
        found_one_tag = False

        tag_idx = 0
        pbar = tqdm(total=len(tag_names))
        # For all tag_names...
        while tag_idx < len(tag_names):
            # ...Try querrying all relavant data
            try:
                one_tag_series, tag = getOneInterpolatedTag(tag_names[tag_idx], dates, step_size, periods)
                one_tag_series = one_tag_series[~one_tag_series.index._duplicated()]

            except AttributeError as attr_err:
                # If tag couldn't found in PI then move to the next one
                if one_tag_series is None and tag == "IndexError":
                    tag_idx +=1
                    pbar.update(1)
                    continue
            # .... If error (Targeting Time out error) -- Then go back and try again the same tag
            # TODO: If Timeout error then catch it here
            except Exception as any_exp:
                print(f"Current exceptions e.__class__.__name__ is {any_exp.__class__.__name__} and below is the actual message:")
                print(any_exp)
                continue

            # If found then add to df and into found tags
            found_one_tag = True
            self._addDataToDF(tag_names[tag_idx], one_tag_series)
            self.df.DateTime = one_tag_series.index
            self.all_found_tags += [tag_names[tag_idx]]
            self.found_tag_descriptions[tag_names[tag_idx]] = tag.description
            self.found_tag_dtypes[tag_names[tag_idx]] = tag.pi_point.PointType
            tag_idx += 1
            pbar.update(1)

        pbar.close()

        if found_one_tag:
            self._setGroupsOfDateTime(interpolated=True)
            self.n_tags = len(self.all_found_tags)


    def queryRecordings(self):
        self._querryRecordings(self.all_searched_tags, self.dates, self.periods)

    def _querryRecordings(self, tag_names, dates, periods):

        # For all tags...
        for tag_name in tqdm(tag_names):
            one_tag_df = getOneRecordedTag(tag_name, dates, periods)
            if one_tag_df is None: continue
            self.recording_df = pd.concat([self.recording_df, one_tag_df], axis=0, ignore_index=True)

        self._setGroupsOfDateTime(interpolated=False)

        self.n_records = dict(self.recording_df.tag_name.value_counts())

    def _addDataToDF(self, tag_name, one_tag_series):
        if self.df.shape[1] != 2:
            assert self.df.shape[0] == one_tag_series.shape[0], "Series and DF doesn't have same number of rows"

        try:
            self.df[tag_name] = one_tag_series.astype("float64")
            self.continuous.append(tag_name)
        except ValueError as err:
            try:
                self.df[tag_name] = one_tag_series.astype(str)
            except:
                one_tag_series.name = tag_name
                self.df = pd.merge(self.df, one_tag_series, how="left", left_index=True, right_index=True)

            self.categorical.append(tag_name)
            print(
                f"While trying to convert {tag_name} to float, BELOW exception is captured and {tag_name} stored as a string")
            print(err)

    def _setGroupsOfDateTime(self, interpolated):
        if interpolated:
            if self.df.shape[0] == 0:
                print("No interpolated data found!")
            else:
                # --> Depending on pandas version it might have already converted or not to datetime before this step
                if self.df.DateTime.dtype == "object": # Check recroded version for detailed explanation
                    self.df["DateTime"] = pd.to_datetime(self.df.DateTime)
                self.df.g = "-1"
                tz = self.df.DateTime.dt.tz
                for idx, (start, end) in enumerate(self.dates):
                    self.df.loc[((self.df.DateTime >= pd.to_datetime(start,infer_datetime_format=True, dayfirst=True, exact=False).tz_localize(tz)) & (
                            self.df.DateTime <= pd.to_datetime(end,infer_datetime_format=True, dayfirst=True, exact=False).tz_localize(tz))),"g"] = \
                        self.date_names[idx]
        else:
            if self.recording_df.shape[0]==0:
                print("No recorded data found!")
            else:
                if self.recording_df.DateTime.dtype == "object":
                    # recording_df directly create by appending tag.recorded_values which has a fixed datetime&tz style which is compatible with pd.to_datetime
                    # Hence, we can directly apply it on the recording_df to make sure datetime column is not object--> recording_df initiated seperately and has defulat object columns
                    # --> Depending on pandas version it might have already converted or not to datetime before this step
                    self.recording_df["DateTime"] = pd.to_datetime(self.recording_df.DateTime)

                tz = self.recording_df.DateTime.dt.tz
                for idx, (start, end) in enumerate(self.dates):
                    self.recording_df.loc[
                        ((self.recording_df.DateTime >= pd.to_datetime(start, infer_datetime_format=True, dayfirst=True, exact=False).tz_localize(tz)) & (
                                self.recording_df.DateTime <= pd.to_datetime(end, infer_datetime_format=True, dayfirst=True, exact=False).tz_localize(tz))),"g"] = \
                        self.date_names[idx]

    def addNewTags(self, new_tags):
        if self.interpolated_values:
            assert type(self.df.index[
                            0]) == pd.Timestamp, "To add new tags, indexes should be Timestamp to find matching entries of this new tags"
            if self.periods == 1:
                self.periods = 2

            self._querryInterpolatedTags(new_tags, self.dates, self.step_size, self.periods)

        if self.recorded_values:
            self._querryRecordings(new_tags, self.dates, self.periods)

    # TODO: Convert Querry method to PreProcessor OR find a way to produce processed format of the data
    def addNewDates(self, dates, date_names, step_size, periods):
        d = {"controllers"   : [cont.split("_")[0] for cont in self.controllers],
             "other_tags"    : self.other_tags,
             "dates"         : dates,
             "date_names"    : date_names,
             "step_size"     : step_size,
             "periods"       : periods,
             "recorded_values"  : self.recorded_values,
             }

        q_tmp = Querry(**d)
        new_dates_cols = q_tmp.df.columns.to_list()
        existing_cols = self.df.columns.to_list()

        if step_size != self.step_size:
            print(f"INFO: Initial step size was {self.step_size} and step size for newly added dates is {step_size}")

        if not all([col in new_dates_cols for col in existing_cols]):
            print(
                "Columns are not matching for existing and new dates. Returning Querry object without attaching the queried df to existing one")
            return q_tmp

        self.df = self.df.append(q_tmp.df, ignore_index=True)
        self.df.shape[0]
        print("Appended newly queried dates! Returned Querry object.")
        return q_tmp

    def removeTags(self, tags_to_remove):
        # Remove each tag from list of tags
        for tag in tags_to_remove:
            self.continuous = [cont for cont in self.continuous if cont != tag]
            self.categorical = [cat for cat in self.categorical if cat != tag]

            self.all_found_tags = self.continuous + self.categorical

            if self.n_tags == len(self.all_found_tags):
                print(f"{tag} couldn't found in the tag list")

        # Remove tags from the dataframes
        self.df = self.df[["g", "DateTime"] + self.all_found_tags]
        self.recording_df = self.recording_df.loc[self.recording_df.tag_name.isin(self.all_found_tags),]

    def getNRecordsInTimeRange(self, start_date, end_date):
        """If using string input for dates. Can use following Format 2020-10-20 14:00:00"""
        filtered_df = self.getDateRange(start_date, end_date, interpolated=False, inplace=False)
        n_records = dict(filtered_df.tag_name.value_counts)
        print(n_records)
        return n_records

    def getTags(self, tags: list, interpolated=True):
        # Can only get tags that are found
        tags = [tag for tag in tags if tag in self.all_found_tags]
        if interpolated:
            return self.df[["g", "DateTime"] + tags]
        else:
            return self.recording_df.loc[self.recording_df.tag_name.isin(tags),]

    def getControllers(self, interpolated=True):
        # Can only get tags that are found
        controllers = [tag for tag in self.all_found_tags if tag in self.controllers]
        if interpolated:
            return self.df[controllers]
        else:
            return self.recording_df.loc[self.recording_df.tag_name.isin(controllers),]

    def getOtherTags(self, interpolated=True):
        self.getTags(self.other_tags, interpolated)

    def getContinuous(self, interpolated=True):
        self.getTags(self.continuous, interpolated)

    def getCategorical(self, interpolated=True):
        self.getTags(self.categorical, interpolated)

    def getDateRange(self, start_date, end_date, interpolated=True, inplace=False):
        """If using string input for dates. Can use following Format 2020-10-20 14:00:00"""
        tz = self.df["DateTime"].dt.tz

        if type(start_date) == str:
            start_date = pd.Timestamp(start_date, tz=tz)
        if type(end_date) == str:
            end_date = pd.Timestamp(end_date, tz=tz)

        if interpolated:
            if inplace:
                self.df = self.df.loc[(self.df["DateTime"] > start_date) & (self.df["DateTime"] < end_date),]
                return self.df
            else:
                return self.df.loc[(self.df["DateTime"] > start_date) & (self.df["DateTime"] < end_date),]
        else:
            if inplace:
                self.recording_df = self.recording_df.loc[
                    (self.recording_df["DateTime"] > start_date) & (self.recording_df["DateTime"] < end_date),]
                self.n_records = self.recording_df.shape[0]
            else:
                return self.recording_df.loc[
                    (self.recording_df["DateTime"] > start_date) & (self.recording_df["DateTime"] < end_date),]



# tags = ['3313FIC040.MODE', '3313AIC096A.MODE', '3313AIC095A.MODE', '3313AIC094A.MODE', '3313FIC1124B.MODE', '3313AC095ASP.SV', '3313AC094ASP.SV', '3313FIC030.MODE', '3313LIC032.MODE', '3313AIC093A.MODE', '3313AI546A.PV', '3313FIC040.SV', '3313LIC1049.SV', '3313AI546C.PV', '3313AI547C.PV', '3313AI547A.PV', '3313AIC093A.SV', '3313AI550A.PV', '3313AI550C.PV', '3313FIC070.SV', '3313AC097ASP.SV', '3313AC096ASP.SV', '3313FIC1124B.SV', '3313AI552C.PV', '3313AI553A.PV', '3313FIC060.SV', '3313FIC050.SV', '3313LIC240A.SV', '3313FIC030.SV', '3313LIC1049.MODE', '3313FIC1124.MODE', '3313LIC240A.MODE', '3313FIC2223.MODE', '3313LIC072.MODE', '3313LIC052.SV', '3313AIC097A.MODE', '3313AIC097A.SV', '3313AIC096A.SV', '3313AIC095A.SV', '3313AIC094A.SV', '3313FIC1124.SV', '3313FIC070.MODE', '3313LIC042.SV', '3313FIC2223.SV', '3313FIC2223.MV', '3313LIC032.PV', '3313LIC042.PV', '3313AI551A.PV', '3313FIC060.MODE', '3313LIC062.MODE', '3313FIC050.MODE', '3313LIC052.MODE', '3313LIC042.MODE', '3313LIC032.SV', '3311WIC151.PV', '3313FIC070.MV', '3313LIC072.MV', '3313LIC072.PV', '3313LIC072.SV', '3313LIC062.MV', '3313FIC050.MV', '3313FIC1124.MV', '3313LIC240A.MV', '3313FIC030.MV', '3313LIC032.MV', '3313AI551C.PV', '3313FIC060.MV', '3313LIC062.PV', '3313LIC062.SV', '3313FIC040.MV', '3313LIC042.MV', '3313FIC1124B.MV', '3313AI553C.PV', '3313LIC1049.PV', '3313LIC1049.MV', '3313FIC2223.PV', '3313FIC070.PV', '3313AIC097A.PV', '3313FIC060.PV', '3313AIC096A.PV', '3313FIC050.PV', '3313LIC052.MV', '3313LIC052.PV', '3313AIC095A.PV', '3313FIC040.PV', '3313AIC094A.PV', '3313PI1116.PV', '3313FIC1124B.PV', '3313FIC1124.PV', '3313LIC240A.PV', '3313FIC030.PV','3313AIC093A.PV']
# start_date = "01/01/2021"
# # end_date = "02/06/2021"
# end_date = "01/06/2021"
# start_date2 = "01/12/2021"
# # end_date2 = "02/12/2022"
# end_date2 = "24/05/2022"
# step_size = "1m"
# d = {"controllers"        : [],
#      "other_tags"         : tags[50:],
#      "dates"              : list(zip([start_date,start_date2], [end_date,end_date2])),
#      "date_names"         : ["before", "after"],
#      "step_size"          : step_size,
#      "periods"            : 1,
#      "alias_mapper"       : {},
#      "interpolated_values": True,
#      "recorded_values"    : False
#      }
#
# q = Querry(**d)
# savePickle(q,"t3_q_obj_p2.pkl")
