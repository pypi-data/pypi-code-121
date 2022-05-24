from ..base import ArrayField, BooleanField, NumericField, StringField


class FeatureSet(object):
    name = StringField("featureSetName")
    description = StringField("description")
    deprecated = BooleanField("deprecated")
    application_name = StringField("applicationName")
    application_id = StringField("applicationId")
    tags = ArrayField("tags")
    data_source_domains = ArrayField("dataSourceDomains")
    owner = StringField("owner.name")
    author = StringField("author.name")
    features = ArrayField("features")
