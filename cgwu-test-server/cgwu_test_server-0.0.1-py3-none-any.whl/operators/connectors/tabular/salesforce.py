from typing import List

import pandas as pd
from simple_salesforce import Salesforce

from aqueduct_executor.operators.connectors.tabular import common, config, connector, extract, load


class SalesforceConnector(connector.TabularConnector):
    def __init__(self, config: config.SalesforceConfig):
        self.client = Salesforce(
            instance_url=config.instance_url,
            session_id=config.access_token,
        )

    def authenticate(self) -> None:
        pass

    def discover(self) -> List[str]:
        raise Exception("Discover is not supported for Salesforce.")

    def extract(self, params: extract.SalesforceParams) -> pd.DataFrame:
        if params.type == common.SalesforceExtractType.QUERY:
            data = self.client.query(params.query)
            # Drop `attributes` column, which contains metadata
            df = pd.DataFrame(data["records"]).drop(["attributes"], axis=1)
        elif params.type == common.SalesforceExtractType.SEARCH:
            data = self.client.search(params.query)
            # Drop `attributes` column, which contains metadata
            df = pd.DataFrame(data["searchRecords"]).drop(["attributes"], axis=1)
        else:
            raise Exception("Unknown Salesforce extract type: %s" % params.type)

        return df

    def load(self, params: load.SalesforceParams, df: pd.DataFrame) -> None:
        # NaN values have to be replaced to avoid a "ValueError: Out of range float values are not JSON compliant"
        # See: https://stackoverflow.com/a/41213102
        df = df.fillna("")
        data = df.to_dict("records")

        obj = getattr(self.client.bulk, params.object)
        obj.update(data, use_serial=True)
