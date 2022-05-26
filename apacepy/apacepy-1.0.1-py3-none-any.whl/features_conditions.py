from deampy.parameters import _Parameter, Constant

from apacepy.time_series import SumIncidence, SumPrevalence, SumCumulativeIncidence, RatioTimeSeries


class _Feature:

    def __init__(self, name):

        self.name = name
        self.value = None
        self.min = float('-inf')
        self.max = float('inf')

    def _update_min_max(self):

        if self.value is None:
            return

        if self.value > self.max:
            self.max = self.value
        if self.value < self.min:
            self.man = self.value

    def reset(self):
        self.value = None
        self.min = float('-inf')
        self.max = float('inf')

    def update(self, epi_time=None):
        pass


class FeatureEpidemicTime(_Feature):
    """ feature defined as the epidemic time """

    def __init__(self, name):

        _Feature.__init__(self, name=name)

    def update(self, epi_time=None):

        self.value = epi_time
        self._update_min_max()


class FeatureIntervention(_Feature):
    """ feature defined on an intervention """

    def __init__(self, name, intervention, feature_type='switch value'):
        """
        param: type: (string) 'switch value' or 'if ever switched off' or 'if ever switched on'
        """

        _Feature.__init__(self, name=name)
        self.intervention = intervention
        if feature_type == 'switch value':
            self.type = 'v'
        elif feature_type == 'if ever switched off':
            self.type = 'f'
        elif feature_type == 'if ever switched on':
            self.type = 'n'
        else:
            raise ValueError('Invalid feature type.')

    def update(self, epi_time=None):
        if self.type == 'v':
            self.value = self.intervention.switchValue
        elif self.type == 'f':
            self.value = self.intervention.ifEverSwitchedOff
        elif self.type == 'n':
            self.value = self.intervention.ifEverSwitchedOn
        else:
            raise ValueError('Invalid feature type.')

        self._update_min_max()


class FeatureSurveillance(_Feature):
    """ feature defined on a time-series (sum incidence or ratio) with surveillance """

    def __init__(self, name,
                 sum_time_series_with_surveillance=None,
                 ratio_time_series_with_surveillance=None,
                 feature_type='m'):
        """
        :param name: (string) feature name
        :param sum_time_series_with_surveillance: (SumIncidence, SumPrevalence, or SumCumulativeIncidence)
            with surveillance
        :param ratio_time_series_with_surveillance: (RatioTimeSeries) with surveillance
        :param feature_type: 'm' to use the last observation as feature and
                             's' to use the change between the last two observations as feature
        """

        _Feature.__init__(self, name=name)
        self.type = feature_type

        # sum time-series
        if sum_time_series_with_surveillance is not None:
            assert isinstance(sum_time_series_with_surveillance, SumIncidence) or \
                   isinstance(sum_time_series_with_surveillance, SumPrevalence) or \
                   isinstance(sum_time_series_with_surveillance, SumCumulativeIncidence)
            if sum_time_series_with_surveillance.surveillance is None:
                raise AttributeError("To use the sum incidence '{}' to define a feature, "
                                     "it must have surveillance on (if_surveyed=True).".format(self.name))
            self.surveillance = sum_time_series_with_surveillance.surveillance

        # ratio time-series
        if ratio_time_series_with_surveillance is not None:
            assert isinstance(ratio_time_series_with_surveillance, RatioTimeSeries)
            if not ratio_time_series_with_surveillance.ifSurveyed:
                raise AttributeError("To use the ratio time-series '{}' to define a feature, "
                                     "it must have surveillance on (if_surveyed=True).".format(self.name))
            self.surveillance = ratio_time_series_with_surveillance

        if sum_time_series_with_surveillance is not None and ratio_time_series_with_surveillance is not None:
            raise ValueError('Only one surveyed time-series can be provided.')

    def update(self, epi_time=None):
        """ updates feature value """

        try:
            if self.type == 'm':
                self.value = self.surveillance.surveyedTimeSeries[-1]
            elif self.type == 's':
                try:
                    self.value = self.surveillance.surveyedTimeSeries[-1] - self.surveillance.surveyedTimeSeries[-2]
                except:
                    self.value = 0
            else:
                raise ValueError("Invalid feature type for feature '{}'.".format(self.name))
        except IndexError:
            raise IndexError("Make sure the surveyed time-series on which the feature '{}' "
                             "is defined on is included in the list of time-series "
                             "when populating the model.".format(self.name))

        self._update_min_max()


class _Condition:

    def __init__(self, name):

        self.name = name
        self.value = None

    def reset(self):
        self.value = None

    def update(self):
        pass


class ConditionAlwaysTrue(_Condition):

    def __init__(self, name=None):

        _Condition.__init__(self, name=name)
        self.value = True


class ConditionAlwaysFalse(_Condition):

    def __init__(self, name=None):
        _Condition.__init__(self, name=name)
        self.value = False


class ConditionOnFeatures(_Condition):

    def __init__(self, name, features=(), signs=(), thresholds=(), logic='and'):
        _Condition.__init__(self, name=name)

        self.features = features
        self.signs = signs
        self.thresholds = []
        # convert threshold values to parameters
        for t in thresholds:
            if isinstance(t, _Parameter):
                self.thresholds.append(t)
            else:
                if t is None:
                    raise ValueError("Error in condition '{}'. Thresholds for cannot be none.".format(name))
                else:
                    self.thresholds.append(Constant(value=t))
        self.logic = logic

    def update(self):

        # the result is None if no feature has a value
        self.value = None

        if self.logic == 'and':
            # all features need to have a value to make the comparison
            self.value = True
            for f in self.features:
                if f.value is None:
                    self.value = None
                    break

            # return false if one condition is violated
            if self.value:
                for i, f in enumerate(self.features):
                    if not compare(x=f.value, sign=self.signs[i], y=self.thresholds[i].value):
                        self.value = False
                        break

        elif self.logic == 'or':
            # at least one feature needs to have a value to make the comparison
            for f in self.features:
                if f.value is not None:
                    self.value = False
                    break
            # return true if one condition is met
            for i, f in enumerate(self.features):
                if f.value is not None:
                    if f.value is not None and compare(x=f.value, sign=self.signs[i], y=self.thresholds[i].value):
                        self.value = True
                        break
            raise ValueError('Needs to be carefully debugged.')
        else:
            raise ValueError


class ConditionOnConditions(_Condition):

    def __init__(self, name, conditions=[], logic='and'):
        _Condition.__init__(self, name=name)

        self.conditions = conditions
        self.logic = logic

    def update(self):

        # the result is None if no feature has a value
        self.value = None

        if self.logic == 'and':
            # at least one condition needs to have a value to make the comparison
            for c in self.conditions:
                if c.value is not None:
                    self.value = True
                    break
            # return false if one condition is violated
            for c in self.conditions:
                if c.value is not None and not c.value:
                    self.value = False
                    break
        elif self.logic == 'or':
            # at least one condition needs to have a value to make the comparison
            for c in self.conditions:
                if c.value is not None:
                    self.value = False
                    break
            # return true if one condition is met
            for c in self.conditions:
                if c.value is not None and c.value:
                    self.value = True
                    break

        else:
            raise ValueError


def compare(x, sign, y):

    if x is None:
        return None

    if sign == 'e':
        return abs(x-y) < 0.00001
    elif sign == 'l':
        return x < y
    elif sign == 'g':
        return x > y
    elif sign == 'lq':
        return x <= y
    elif sign == 'ge':
        return x >= y
    else:
        raise ValueError('Invalid comparison.')
