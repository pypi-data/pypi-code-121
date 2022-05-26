__all__ = ["ExperimentIterableDataset"]

import os
import pandas as pd

from typing import Union, Optional
from warnings import warn
from ibm_watson_machine_learning.helpers.connections.flight_service import (
    FlightConnection,
)
from ibm_watson_machine_learning.helpers.connections.local import LocalBatchReader
from ibm_watson_machine_learning.utils.autoai.enums import SamplingTypes

# Note: try to import torch lib if available, this fallback is done based on
# torch dependency removal request
try:
    from torch.utils.data import IterableDataset

except ImportError:
    IterableDataset = object
# --- end note


class ExperimentIterableDataset(IterableDataset):
    """
        This dataset is intended to be an Iterable stream from Flight Service.
        It should iterate over flight logical batches and menages by Connection class
        how batches are downloaded and created. It should take into consideration only 2 batches at a time.
        If we have 2 batches already downloaded, it should block further download
        and wait for first batch to be consumed.

        Example
        -------
        >>> experiment_metadata = {
        >>>     "prediction_column": 'species',
        >>>     "prediction_type": "classification",
        >>>     "project_id": os.environ.get('PROJECT_ID'),
        >>>     'wml_credentials': wml_credentials
        >>> }

        >>> connection = DataConnection(data_asset_id='5d99c11a-2060-4ef6-83d5-dc593c6455e2')


        >>># default sampling - read first 1GB of data
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=True,
        >>>                                              sampling_type='first_n_records',
        >>>                                              sample_size_limit = 1GB,
        >>>                                              experiment_metadata=experiment_metadata)

        >>># read all data records in batches / no subsampling
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=False,
        >>>                                               experiment_metadata=experiment_metadata)

        >>># stratified/random sampling
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=True,
        >>>                                              sampling_type='stratified',
        >>>                                              sample_size_limit = 1GB,
        >>>                                              experiment_metadata=experiment_metadata)

    """

    connection: Union[FlightConnection, LocalBatchReader] = None

    def __init__(
        self,
        connection: "DataConnection",
        experiment_metadata: dict = None,
        enable_sampling: bool = True,
        sample_size_limit: int = 1073741824 if "32" in os.environ.get("MEM", "32") else 104857600,  # 1GB in Bytes,
        sampling_type: str = SamplingTypes.FIRST_N_RECORDS,
        binary_data: bool = False,
        number_of_batch_rows: int = None,
        stop_after_first_batch: bool = False,
        **kwargs,
    ):
        super().__init__()
        self.experiment_metadata = experiment_metadata
        self.enable_sampling = enable_sampling
        self._wml_client = getattr(connection, "_wml_client", None)
        if self._wml_client is None:
            self._wml_client = kwargs.get("_wml_client", None)
        self.binary_data = binary_data
        self.sampling_type = sampling_type
        self.read_to_file = kwargs.get('read_to_file')
        self.authorized = self._wml_check_authorization()

        # Note: convert to dictionary if we have object from WML client
        if not isinstance(connection, dict):
            dict_connection = connection._to_dict()

        else:
            dict_connection = connection
        # --- end note

        # Note: backward compatibility after sampling refactoring #27255
        if kwargs.get('with_sampling') or kwargs.get('normal_read'):
            warn("The parameters with_sampling and normal_read in ExperimentIterableDataset are deprecated. "
                 "Use enable_sampling and sampling_type instead.")
            if kwargs.get('normal_read'):
                self.enable_sampling = False
            if kwargs.get('with_sampling'):
                from ibm_watson_machine_learning.utils.autoai.enums import PredictionType
                self.enable_sampling = True
                if self.experiment_metadata.get("prediction_type") in [PredictionType.REGRESSION]:
                    self.sampling_type = SamplingTypes.RANDOM
                elif self.experiment_metadata.get("prediction_type") in [PredictionType.CLASSIFICATION,
                                                                         PredictionType.BINARY,
                                                                         PredictionType.MULTICLASS]:
                    self.sampling_type = SamplingTypes.STRATIFIED
        # --- end note

        # if number_of_batch_rows is provided, batch_size does not matter anymore

        if self.authorized:
            # first used headers from experiment metadata if they were set.
            headers_ = None
            if self.experiment_metadata.get("headers"):
                headers_ = self.experiment_metadata.get("headers")
            elif self._wml_client is not None:
                headers_ = self._wml_client._get_headers()

            self.connection = FlightConnection(
                headers=headers_,
                sampling_type=self.sampling_type,
                label=self.experiment_metadata.get("prediction_column"),
                learning_type=self.experiment_metadata.get("prediction_type"),
                params=self.experiment_metadata,
                project_id=self.experiment_metadata.get("project_id"),
                space_id=self.experiment_metadata.get("space_id"),
                asset_id=dict_connection.get("location", {}).get("id"),
                connection_id=dict_connection.get("connection", {}).get("id"),
                data_location=dict_connection,
                data_size_limit=sample_size_limit,
                flight_parameters=kwargs.get("flight_parameters", {}),
                extra_interaction_properties=kwargs.get("extra_interaction_properties",{}),
                fallback_to_one_connection=kwargs.get(
                    "fallback_to_one_connection", True
                ),
                number_of_batch_rows=number_of_batch_rows,
                stop_after_first_batch=stop_after_first_batch,
                _wml_client=kwargs.get('_wml_client')
            )

        else:
            if (
                dict_connection.get("type") == "fs"
                and "location" in dict_connection
                and "path" in dict_connection["location"]
            ):
                self.connection = LocalBatchReader(
                    file_path=dict_connection["location"]["path"], batch_size=sample_size_limit
                )

            else:
                raise NotImplementedError(
                    "For local data read please use 'fs' (file system) connection type."
                    "To use remote data read please provide 'experiment_metadata'."
                )

    def _wml_check_authorization(self) -> bool:
        """
        Check if we can authorize with WML.
        If the connection have wml_client initialized use it as an attribute.
        Otherwise credentials should be provided in the experiment_metadata dictionary.
        If they the client is properly initialized True will be returned.
        """
        if self._wml_client is not None:
            return True

        if self.experiment_metadata is None:
            return False

        if self.experiment_metadata.get("wml_credentials") is not None:
            from ibm_watson_machine_learning import APIClient

            self._wml_client = APIClient(
                wml_credentials=self.experiment_metadata["wml_credentials"]
            )
            return True

        elif self.experiment_metadata.get("headers") is not None:
            return True

        else:
            return False

    def write(
        self, data: Optional[pd.DataFrame] = None, file_path: Optional[str] = None
    ) -> None:
        """
        Writes data into data source connection.

        Parameters
        ----------
        data: pandas DataFrame, optional
            Structured data to be saved in dat source connection. (Either 'data' or 'file_path' need to be provided)

        file_path: str, optional
            Path to the local file to be saved in source data connection (binary transfer).
            (Either 'data' or 'file_path' need to be provided)
        """
        if (data is None and file_path is None) or (
            data is not None and file_path is not None
        ):
            raise ValueError("Either 'data' or 'file_path' need to be provided.")

        if data is not None and not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"'data' need to be a pandas DataFrame, you provided: '{type(data)}'."
            )

        if file_path is not None and not isinstance(file_path, str):
            raise TypeError(
                f"'file_path' need to be a string, you provided: '{type(file_path)}'."
            )

        if data is not None:
            self.connection.write_data(data)

        else:
            self.connection.write_binary_data(file_path)

    def __iter__(self):
        """Iterate over Flight Dataset."""
        if self.authorized:
            if self.enable_sampling:
                if self.sampling_type == SamplingTypes.FIRST_N_RECORDS:
                    return self.connection.iterable_read()
                else:
                    self.connection.enable_subsampling = True
                    return self.connection.iterable_read()
            else:
                if self.binary_data:
                    return self.connection.read_binary_data(read_to_file=self.read_to_file)

                else:
                    return self.connection.read()
        else:
            return (batch for batch in self.connection)
