from datetime import datetime
from pandas import DataFrame

from pricecypher.collections import ScopeCollection, ScopeValueCollection
from pricecypher.endpoints import DatasetsEndpoint, UsersEndpoint


class Datasets(object):
    """
    Datasets API. Exposes all available operations on datasets, like fetching the available datasets, listing
    the scopes within a dataset, retrieving transactions within a dataset, etc.

    :param str bearer_token: Bearer token for PriceCypher (logical) API. Needs 'read:datasets' scope.
    :param str users_base: (optional) Base URL for PriceCypher user tool API. Used to find base URL of dataset service,
        when no dss_base is provided.
        (defaults to https://users.pricecypher.com)
    :param str dss_base: (optional) Base URL for PriceCypher dataset service API.
        (defaults to dss_url property as returned for the dataset by the PriceCypher user tool API)
    :param RestClientOptions rest_options: (optional) Set any additional options for the REST client, e.g. rate-limit.
        (defaults to None)
    """

    def __init__(self, bearer_token, users_base='https://users.pricecypher.com', dss_base=None, rest_options=None):
        self._bearer = bearer_token
        self._users_base = users_base
        self._dss_base = dss_base
        self._rest_options = rest_options
        self._all_meta = None

    def _get_dss_base(self, dataset_id):
        """
        Get dataset service url base for the given dataset ID.
        Will be fetched from dataset META if no dss_base present.

        :param int dataset_id: Dataset ID to get base URL for.
        :return Base domain of the dataset service instance in which the given dataset is contained.
            NB: does not point to the specific dataset endpoint within the dataset service API.
        :rtype Optional[str]
        """
        if self._dss_base is not None:
            return self._dss_base

        return self.get_meta(dataset_id).dss_url

    def index(self):
        """
        List all available datasets the user has access to.
        Response is cached in this instance for as long as this instance lives.

        :return: list of datasets.
        :rtype list[Dataset]
        """
        if self._all_meta is None:
            self._all_meta = UsersEndpoint(self._bearer, self._users_base, self._rest_options).datasets().index()

        return self._all_meta

    def get_meta(self, dataset_id):
        """
        Get metadata like the dataset service url and time of creation of a dataset

        :param dataset_id: Dataset to get metadata for.
        :rtype: Dataset
        """
        return next((d for d in self.index() if d.id == dataset_id), None)

    def get_scopes(self, dataset_id, bc_id='all'):
        """
        Get all scopes for the given dataset.

        :param int dataset_id: Dataset to retrieve scopes for.
        :param str bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: Collection of scopes for the given dataset.
        :rtype: ScopeCollection
        """
        return ScopeCollection(
            DatasetsEndpoint(self._bearer, dataset_id, self._get_dss_base(dataset_id), self._rest_options)
            .business_cell(bc_id)
            .scopes()
            .index()
        )

    def get_scope_values(self, dataset_id, scope_id, bc_id='all'):
        """
        Get all scopes values for the given scope within the given dataset.

        :param int dataset_id: Dataset to retrieve scope values for.
        :param int scope_id: Scope to retrieve scope values for.
        :param str bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: Collection of scope values for the given scope within the given dataset.
        :rtype: ScopeValueCollection
        """
        dss_base = self._get_dss_base(dataset_id)
        return ScopeValueCollection(
            DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._rest_options)
            .business_cell(bc_id)
            .scopes()
            .scope_values(scope_id)
        )

    def get_transaction_summary(self, dataset_id, bc_id='all'):
        """
        Get a summary of the transactions. Contains the first and last date of any transaction in the dataset.

        :param int dataset_id: Dataset to retrieve summary for.
        :param str bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: Summary of the transactions.
        :rtype: TransactionSummary
        """
        dss_base = self._get_dss_base(dataset_id)
        return DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._rest_options) \
            .business_cell(bc_id) \
            .transactions() \
            .summary()

    def get_transactions(self, dataset_id, aggregate, columns, start_date_time=None, end_date_time=None, bc_id='all'):
        """
        Display a listing of transactions as a dataframe. The transactions can be grouped or not, using the aggregate
        parameter. The desired columns, as well as filters and aggregation methods, can be specified.

        :param int dataset_id: Dataset to retrieve transactions for.
        :param bool aggregate: If true, the transactions will be grouped on all categorical columns that have no
            aggregation method specified.
        :param list columns: Desired columns in the resulting dataframe. Each column must be a dict. Each column must
            have either a `representation` or a `name_dataset` specified. The following properties are optional.
                `filter`: value or list of values the resulting transactions should be filtered on.
                `aggregate`: aggregation method that should be used for this column. When aggregating and no
                    aggregation method is specified, the method that is used is determined by the underlying dataset
                    service. See dataset service documentation on how this default is determined.
                `key`: Column name to be used in the resulting dataframe. Defaults to 'scope_' appended with scope id.
        :param datetime start_date_time: When specified, only transactions at or after this date are considered.
        :param datetime end_date_time: When specified, only transactions before this date are considered.
        :param str bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: Dataframe of transactions.
        :rtype: DataFrame
        """
        dss_base = self._get_dss_base(dataset_id)
        # Find scopes for the provided columns.
        columns_with_scopes = self._add_scopes(dataset_id, columns, bc_id)
        # Map each scope to the provided column key.
        scope_keys = self._find_scope_keys(columns_with_scopes)
        # Find the scope IDs that should be selected.
        select_scopes = [c['scope'].id for c in columns_with_scopes]
        # Add scope values to the columns that have a filter set.
        # TODO possible optimization: only fetch scope values that are included in the filters.
        columns_with_values = [
            self._add_scope_values(dataset_id, c, bc_id) for c in columns_with_scopes if dict.get(c, 'filter')
        ]
        # Find all scope value filters to be sent to the dataset service.
        filters = self._find_scope_value_filters(columns_with_values)
        # Find all aggregation methods to be sent to the dataset service.
        aggregation_methods = self._find_aggregation_methods(columns_with_scopes)

        # Build the request data to be sent to the dataset service.
        request_data = {
            'aggregate': aggregate,
            'select_scopes': select_scopes,
        }

        if len(filters) > 0:
            request_data['filter_scope_values'] = filters

        if len(aggregation_methods) > 0:
            request_data['aggregation_methods'] = aggregation_methods

        if isinstance(start_date_time, datetime):
            request_data['start_date_time'] = start_date_time
        elif start_date_time is not None:
            raise ValueError('start_date_time should be an instance of datetime.')

        if isinstance(end_date_time, datetime):
            request_data['end_date_time'] = start_date_time
        elif end_date_time is not None:
            raise ValueError('end_date_time should be an instance of datetime.')

        # Fetch transactions from the dataset service.
        transactions = DatasetsEndpoint(self._bearer, dataset_id, dss_base, self._rest_options) \
            .business_cell(bc_id) \
            .transactions() \
            .index(request_data)

        # Map transactions to dicts based on the provided column keys and convert to pandas dataframe.
        return DataFrame.from_records([t.to_dict(scope_keys) for t in transactions])

    def _add_scopes(self, dataset_id, columns, bc_id='all'):
        """
        Find the scope for each provided column and return new list of columns with scope information stored inside.

        :param int dataset_id: Dataset ID to retrieve scopes for.
        :param list[dict] columns: Each column should be a dict with either a `representation` or `name_dataset`
            property.
        :param str bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: New list of columns, with for each column an added `scope` property.
        :rtype list[dict]
        """
        all_scopes = self.get_scopes(dataset_id, bc_id)

        def add_scope(column: dict):
            if 'representation' in column and 'name_dataset' in column:
                raise ValueError('Both `representation` and `name_dataset` provided for column {0}'.format(str(column)))
            elif 'representation' in column:
                scope = all_scopes.find_by_repr(column['representation'])
            elif 'name_dataset' in column:
                scope = all_scopes.find_by_name_dataset(column['name_dataset'])
            else:
                raise ValueError('No scope could be found for column {0}'.format(str(column)))

            return {**column, 'scope': scope}

        return list(map(add_scope, columns))

    def _add_scope_values(self, dataset_id, column, bc_id='all'):
        """
        Add scope values to the given column.

        :param int dataset_id: Dataset ID to retrieve scope values for.
        :param dict column: Column with `scope` property, for which scope values should be retrieved.
        :param bc_id: (optional) business cell ID.
            (defaults to 'all')
        :return: Copy of the given column with additional `scope_values` property.
        :rtype: dict
        """
        if 'scope' not in column:
            pass

        scope = column['scope']
        scope_values = self.get_scope_values(dataset_id, scope.id, bc_id)

        return {**column, 'scope_values': scope_values}

    def _find_scope_value_filters(self, columns):
        """
        Find all filters that have been defined in the given columns, as a list of scope value IDs.

        :param list[dict] columns: For all columns that have a `filter` and `scope_values` property, the scope values
            to be  filtered will be collected.
        :return: List of all scope value IDs that the columns should be filtered on.
        :rtype: list
        """
        filters = []

        for column in columns:
            filt = dict.get(column, 'filter')
            scope_values = dict.get(column, 'scope_values')

            # If column has no filter or scope_values set, there is nothing to filter.
            if not filt or not scope_values:
                continue

            # Pluck scope value IDs and add to list of all filters.
            filters.extend(scope_values.where_in(filt).pluck('id'))

        return filters

    def _find_aggregation_methods(self, columns):
        """
        Find all aggregation methods that have been defined in the given columns, as a list of dicts where each dict
        contains a `scope_id` and `method`.

        :param list[dict] columns: For all columns that have an `aggregate` and `scope` property, the aggregation
            methods to be applied will be collected.
        :return: List of all aggregation methods that are defined in the columns.
        :rtype list[dict]
        """
        aggregation_methods = []

        for column in columns:
            aggregate = dict.get(column, 'aggregate')
            scope = dict.get(column, 'scope')

            # If column has no aggregate or no scope info set, no aggregation method can be applied for this column.
            if not aggregate or not scope:
                continue

            aggregation_methods.append({
                'scope_id': scope.id,
                'method': aggregate,
            })

        return aggregation_methods

    def _find_scope_keys(self, columns):
        """
        Find the keys that have been defined for all scopes in the given columns. Assumes that all columns have a
        `scope` property set.

        :param list[dict] columns: For all columns, find the scope ID and which key should be used for that scope.
        :return: Dictionary of scope IDs to column keys.
        :rtype: dict
        """
        scope_keys = {}

        for column in columns:
            scope = column['scope']
            key = dict.get(column, 'key', 'scope_{}'.format(scope.id))

            scope_keys[scope.id] = key

        return scope_keys
