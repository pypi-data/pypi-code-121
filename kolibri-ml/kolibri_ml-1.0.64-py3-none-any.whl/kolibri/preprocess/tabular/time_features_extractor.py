from kolibri.core.component import Component
import calendar
from collections import defaultdict

class TimeFeatures(Component):
    """
    -Given a time feature , it extracts more features
    - Only accepts / works where feature / data type is datetime64[ns]
    - full list of features is:
      ['month','weekday',is_month_end','is_month_start','hour']
    - all extracted features are defined as string / object
    -it is recommended to run Define_dataTypes first
      Args:
        time_features: list of feature names as datetime64[ns] , default empty/none , if empty/None , it will try to pickup dates automatically where data type is datetime64[ns]
        list_of_features: list of required features , default value ['month','weekday','is_month_end','is_month_start','hour']

  """

    defaults = {
        "fixed":{
            "time-features": None,
            "features-list" : ["year", "month", "yearweek", "weekday", "is_month_end", "is_month_start", "hour", "minutes"],
            "drop_source_column": True
        }
    }

    def __init__(self, params):
        super().__init__(parameters=params)
        self.time_features = self.get_parameter("time-features")
        self.list_of_features_o = set(self.get_parameter("features-list"))

    def fit(self, data, y=None):
        if self.time_features is None:
            self.time_features = data.select_dtypes(include=["datetime64[ns]"]).columns
            self.has_hour_ = set()
            for i in self.time_features:
                if "hour" in self.list_of_features_o:
                    if any(x.hour for x in data[i]):
                        self.has_hour_.add(i)
        return self

    def transform(self, dataset, y=None):
        data = dataset.copy()
        # run fit transform first

        def get_time_features(r):
            features = []
            if "year" in self.list_of_features_o:
                features.append(("_year", int(r.year)))
            if "month" in self.list_of_features_o:
                features.append(("_month", int(r.month)))
            if "weekday" in self.list_of_features_o:
                features.append(("_weekday", int(r.weekday())))
            if "is_month_end" in self.list_of_features_o:
                features.append(
                    (
                        "_is_month_end",
                        "1"
                        if calendar.monthrange(r.year, r.month)[1] == r.day
                        else "0",
                    )
                )
            if "is_month_start" in self.list_of_features_o:
                features.append(("_is_month_start", "1" if r.day == 1 else "0"))

            if "minutes" in self.list_of_features_o:
                features.append(("_minutes", str(r.minute)))
            if "yearweek" in self.list_of_features_o:
                features.append(("_week", r.weekofyear))
            return tuple(features)

        # start making features for every column in the time list
        for i in self.time_features:
            assert data.dtypes[i] in ["datetime64[ns]", "datetime64", "datetime64[ns, UTC]"]
            list_of_features = [get_time_features(r) for r in data[i]]

            fd = defaultdict(list)
            for x in list_of_features:
                for k, v in x:
                    fd[k].append(v)

            for k, v in fd.items():
                data[i + k] = v

            # make hour column if choosen
            if "hour" in self.list_of_features_o:
                h = [r.hour for r in data[i]]
                data[f"{i}_hour"] = h
                data[f"{i}_hour"] = data[f"{i}_hour"].apply(str)

        # we dont need time columns any more
        if self.get_parameter("drop_source_column"):
            data.drop(self.time_features, axis=1, inplace=True)

        return data

    def fit_transform(self, dataset, y=None):
        # if no columns names are given , then pick datetime columns
        self.fit(dataset, y=y)

        return self.transform(dataset, y=y)