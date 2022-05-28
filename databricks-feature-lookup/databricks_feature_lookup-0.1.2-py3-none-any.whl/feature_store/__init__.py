# This init file must be kept in sync with the init file under `client/python/databricks/feature_store`
# As Python will defer to the later installed init file, any changes to the Feature Store client must be added here
# so that the Feature Store client's imports are still accessible if the lookup client is installed afterwards.

# However, it is also possible that only the lookup client will be installed. For that case, we wrap the imports from
# the Feature Store client in a try/catch and silently ignore the import errors.

try:
    from databricks.feature_store.client import FeatureStoreClient
    from databricks.feature_store.decorators import feature_table
    from databricks.feature_store.entities.feature_lookup import FeatureLookup
    from databricks.feature_store.utils.logging_utils import (
        _configure_feature_store_loggers,
    )

    _configure_feature_store_loggers(root_module_name=__name__)

    __all__ = ["FeatureStoreClient", "feature_table", "FeatureLookup"]
except ImportError as e:
    None
