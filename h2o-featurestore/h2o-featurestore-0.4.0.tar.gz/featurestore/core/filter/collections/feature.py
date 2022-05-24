from ..base import ArrayField, NumericField, StringField


class FeatureProfile(object):
    feature_type = StringField("features.profile.featureType")


class Feature(object):
    name = StringField("features.fullyQualifiedFeatureNames")
    description = StringField("features.description")
    importance = NumericField("features.importance")
    data_type = StringField("features.dataType")
    profile = FeatureProfile
