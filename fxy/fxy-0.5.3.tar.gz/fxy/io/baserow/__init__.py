import pandas
import itertools
from tqdm import tqdm

from baserow.client import BaserowClient


class BaserowIO(BaserowClient):

    def get_table(self, table_id, get_values=True, progress=True):
        """
        :table_id: database table id
        :get_values: set to False to leave listed JSON 'values' as is
        :progress: set to False to not use tqdm
        """

        records = lambda table_id: itertools.chain.from_iterable(
          [[row for row in page.results]
            for page in (progress and tqdm(self.paginated_database_table_rows(table_id))
                         or self.paginated_database_table_rows(table_id))]
        )

        fields = lambda table_id: self._request('GET', path=f'/api/database/fields/table/{table_id}/').json()

        columns = {'field_'+str(field['id']): field['name'] for field in fields(table_id)}

        df = pandas.DataFrame.from_records(records(table_id)).rename(columns=columns)
        if get_values:
            get_val = lambda x: x[0].get('value') if x and isinstance(x, list) and isinstance(x[0], dict) else x
            return df.applymap(get_val)

        return df

