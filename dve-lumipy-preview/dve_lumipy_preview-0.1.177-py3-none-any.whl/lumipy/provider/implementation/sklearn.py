from typing import Optional, Dict, Union, Iterable, List

from ..metadata import TableParam, ColumnMeta
from ..base_provider import BaseProvider
from ...query.expression.sql_value_type import SqlValType
from sklearn.decomposition import PCA


class PcaProjectionProvider(BaseProvider):
    """Provider that computes a Principal Component Analysis (PCA) given some data and then projects them onto
    the first n-many principal components.

    This provider uses the sklearn implementation of a PCA.

    """

    def __init__(self, n_components: int):

        self.n_components = n_components

        cols = [
            ColumnMeta(f'PC{i}', SqlValType.Double, f"Projection onto principal component {i}")
            for i in range(n_components)
        ]

        table_params = [TableParam("InputData", description="Input data to the PCA transformer.")]

        super().__init__(
            f"Sklearn.Pca.Projector{n_components}D",
            columns=cols,
            table_parameters=table_params,
            description=self.__doc__
        )

    def _get_data(
            self,
            data_filter: Optional[Dict[str, object]],
            limit: Union[int, None],
            **params
    ) -> Iterable[Dict[str, Union[str, int, float]]]:

        if 'InputData' not in params.keys():
            raise ValueError()

        input_df = params['InputData']

        pca = PCA(n_components=self.n_components)

        out_array = pca.fit_transform(input_df)

        def row_map(row):
            return {f'PC{i}': v for i, v in enumerate(row)}

        return map(row_map, out_array)
