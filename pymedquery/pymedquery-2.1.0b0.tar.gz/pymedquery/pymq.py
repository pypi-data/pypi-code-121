from pymedquery.pg_crud_handler import CRUD
from pymedquery.minio_data_handler import MinioHandler
from pymedquery.config.logger_object import Logger
from pymedquery.config import config
from pymedquery.src.helpers import batch_maker, encode_payload

import psycopg2
import numpy as np
from minio.error import S3Error
from time import sleep
from typing import (
        Optional, Union, Dict, List, Generator, Any, Tuple, NoReturn
        )


class PyMedQuery:
    """The MedQuery class is the python client that connects the user
    to MedQuery via global env variables. The connection to the database
    happens during python runtime which enables the user to integrate data
    transaction directly into their code and thus project.

    The aim with publishing the method is to let the users extract and upload data in a simple and
    fast way. Data should be centralized, maintained and offered up by the data engineers such that
    the scientist and analysts dont have to think about it.

    Fast, easy and intuitive is the goal.
    """

    def __init__(self) -> NoReturn:
        self.crud: Any = CRUD(
                    user=config.USER,
                    password=config.PASSWORD,
                    database=config.DATABASE
                    )

        self.mh: Any = MinioHandler(
                    access_key=config.USER,
                    secret_key=config.PASSWORD
                            )
        self.log: Any = Logger(__name__)

    def __set_extract_params(
                        self, get_all: bool, format_params: Dict[str, Union[str, int, float, bool]],
                        sql_file_path: str, project_id: str, include_mask: bool,
                        limit: Union[int, str] = None
                        ) -> Union[Dict[str, Union[str, int]], str]:
        """_set_extract_params is a private method that initializes the parameters
        subsequent methods will use for data extraction and upload.

        Parameters
        ----------
        get_all : bool
            Set `get_all` to True if you want to use a default SQL script that extracts
            images and masks from a given project id for you.
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        project_id : str
            Specify the `project_id` for the data that you want. Be sure it is exactly the
            project id that is used in the database
        limit : Union[int, str]
            Use `limit` to set a limit on how many rows (patientIDs) to return
        """
        if get_all:
            if not project_id:
                raise ValueError('please specify the project id that corresponds to the requested data')
            if include_mask is None:
                raise ValueError('please specify `include_mask` to true or false')
            sub = 'subq3' if include_mask else 'subq2'

        format_params: Union[Dict[str, str], Dict[any, any]] = {'project_id': str(project_id), 'limit': limit, 'sub': sub} if get_all else format_params
        sql_file_path: str = config.SERIES_MASK_QUERY_DEFAULT if get_all else sql_file_path

        assert sql_file_path, 'please specify the file path to your SQL script'
        return format_params, sql_file_path

    def __pg_extract(
                    self, sql_file_path: str,
                    format_params: Dict[str, Union[str, int, float, bool]]
                    ) -> Union[List[str], Dict[str, List[Union[str, int, float]]]]:
        """_pg_extract is the private method that extracts structrual and relational data
        from the RDBMS.

        Parameters
        ----------
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script
        """

        # Extract the image and given records
        pg_payload: Dict[Tuple[Any]] = self.crud.read(sql_file_path=sql_file_path, format_params=format_params)

        # NOTE! This is poor design and should be more generic
        # This would be too specific if pyMedQuery is also to handle
        # other kinds of data

        # Sort the results for better code
        series_uids: List[str] = pg_payload['series_uid']
        mask_uids: List[str] = pg_payload['mask_uid']
        all_uids: List[str] = series_uids + mask_uids if mask_uids else series_uids

        return all_uids, pg_payload

    def __fetch_uids(
                self, get_all: bool, format_params: dict,
                sql_file_path: str, project_id: str, limit: str,
                include_mask: bool
                ) -> List[str]:
        """_fetch_uids is the private method that executes the `_set_extract_params`
        and `_pg_extract`.

        Parameters
        ----------
        get_all : bool
             Set `get_all` to True if you want to use a default SQL script that extracts
            images and masks from a given project id for you.
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        project_id : str
            Specify the `project_id` for the data that you want. Be sure it is exactly the
        include_mask : bool
            Use include_mask if to specify whether or not you want corresponding masks to your data. The uses should know that the masks exitst,
            or else the return will be empty. This parameter is needed if and only if the get_all is True.
 project id that is used in the database
        """

        format_params, sql_file_path = self.__set_extract_params(
                            get_all=get_all, format_params=format_params,
                            sql_file_path=sql_file_path, project_id=project_id,
                            limit=limit, include_mask=include_mask
                            )
        all_uids = self.__pg_extract(sql_file_path=sql_file_path, format_params=format_params)
        if not all_uids:
            self.log.warning('Nothing was returned')

        return all_uids

    def __fetch_columns(self, table_name: str, verbose: bool) -> List[str]:
        """__fetch_columns will, yes, fetch the column names and return them in list.

        Parameters
        ----------
        table_name : str
            table_name is the, yes, the name of the table you want to know the column names from.

        Returns
        -------
        List[str] e.g. ['series_uid', 'time' ..., 'cancer_type']

        """
        format_params = {'table_name': table_name}
        colnames = self.crud.read(
                                sql_file_path=config.COL_QUERY_DEFAULT, 
                                format_params=format_params, full_query=False,
                                verbose=verbose
                                )
        if colnames:
            return colnames
        else:
            self.log.error('I tried to fetch column names but got an empty result. Lordy lord!')
            raise psycopg2.OperationalError()

    def extract(
            self, get_all: bool,  project_id: Optional[str] = None, limit: Optional[Union[int, str]] = 'NULL',
            include_mask: Optional[bool] = None, format_params: Optional[dict] = None, sql_file_path: Optional[str] = None,
            bucket_name: Optional[str] = 'multimodal-images'
                ) -> Union[Dict[str, List[np.ndarray]], Dict[str, List[any]]]:
        """extract is the public method that is exposed to the user for data extraction of small image quantites. The method is
        not suitable for large extractions as it will likely end in a memory allocation error. Extract utilizes the private methods
        for its functionality. The user is expected to use the method after instantiating the class.

        Functionality:
            1. Fetch UIDs from RDBMS
            2. Use the UIDs to extract the images(blobs) in the data lake
            3. return the structured and unstructured data in dict format

        Parameters
        ----------
        get_all : bool
            A default SQL query script will be used if `get_all` is set True. The default SQL query will depend on project id if it is
            set to True. All data belonging to the project id will be extracted.
        project_id : Optional[str]
            The `project_id` must be set in the case where `get_all` is set to True. It is not necessary to set this parameter if the user
            is writing a user-customised SQL qeury.
        limit: Optional[Union[int, str]]
            The `limit` is a LIMIT parameter on the SQL query governing how many rows. The default is NULL which is to fetching all rows.
        include_mask : Optional[bool]
            Use include_mask if to specify whether or not you want corresponding masks to your data. The uses should know that the masks exitst,
            or else the return will be empty. This parameter is needed if and only if the get_all is True.
        format_params : Optional[dict]
            The use can include parameters for the SQL query in the dict `format_params`. This can be very helpful in the case of writing pipelines.
        sql_file_path : Optional[str]
            The `sql_file_path` is expected to be set if the user has written a custom SQL query. A standard filepath will be used in the case where
            the user wants to use the default SQL query.
        bucket_name : Optional[str]
            The standard `bucket_name` for the medical images are already given as default although other specific buckets are likely to be in other
            cases than the very standard one.
        """
        try:
            # Get the UIDs from the RDBMS
            all_uids, data_info = self.__fetch_uids(
                                get_all=get_all, sql_file_path=sql_file_path,
                                format_params=format_params, project_id=project_id,
                                limit=limit, include_mask=include_mask
                                )

            if len(all_uids) > 30:
                self.log.warning(f"""
                    Top of the morning! This is just a heads up my good man or woman; you are about to
                    extract {len(all_uids)} 3D images in one go and you might run into a memory
                    allocation error. Consider setting batch to True and specify a batch size if you want.
                    """)
                sleep(5)
            elif not all_uids:
                raise ValueError('Your query returned an empty result. Please check your query or projectID')

            # extract the images by using the MinioHandler class method
            images: Dict[str, List[np.ndarray]] = self.mh.get_blobs(bucket_name=bucket_name, blob_list=all_uids)
            return images, data_info
        except (AttributeError, S3Error, psycopg2.Error) as e:
            self.log.error(f'failed to extract data: {e}')

    def batch_extract(
            self, get_all: bool, sql_file_path: Optional[str] = None,
            project_id: Optional[str] = None, limit: Optional[Union[int, str]] = 'NULL',
            include_mask: Optional[bool] = None, format_params: Optional[dict] = None, batch_size: Optional[int] = 14,
            bucket_name: Optional[str] = 'multimodal-images'
            ) -> Generator[np.ndarray, None, None]:
        """batch_extract is a method that is very much alike `extract` although you can use it for batch extraction
        and by that avoid the memory allocation error.

        Functionality:
            1. Fetch UIDs from the RDBMS
            2. Yield blobs from the data lake by batching UIDs from the list of all UIDs
            3. Return the blobs in a dict and let the user have access to the structrual data
            through the class (self.data_info)

        Parameters
        ----------
        get_all : bool
            see `extract` doctstring
        sql_file_path : Optional[str]
            see `extract` doctstring
        project_id : Optional[str]
            see `extract` doctstring
        limit : Optional[Union[int, str]
            see `extract` doctstring
        include_mask : Optinal[bool]
            see `extract` doctstring
        format_params : Optional[dict]
            see `extract` doctstring
        batch_size : Optional[int]
            The user can specify themselves how large the `batch_size` in the extraction iteration should be. The defualt
            is 14 and is estimated to take ca. 6-8GiB memory.
        bucket_name : Optional[str]
            see `extract` doctstring
        """
        try:
            # get the UIDs from the RDBMS
            all_uids, self.data_info = self.__fetch_uids(
                                get_all=get_all, sql_file_path=sql_file_path,
                                format_params=format_params, project_id=project_id,
                                limit=limit, include_mask=include_mask
                                )

            # create the sample to batch from
            sample: Generator[List[str], None, None] = batch_maker(iterable=all_uids, batch_size=batch_size)

            # run bathes out of the sample and yield them one at the time
            for _batch in sample:
                # extract the images by using the MinioHandler class method
                images: Dict[str, List[np.ndarray]] = self.mh.get_blobs(bucket_name=bucket_name, blob_list=_batch)
                yield images
        except(AttributeError, psycopg2.Error, S3Error) as e:
            self.log.error(f'failed to extract data: {e}')

    def upload(
            self, records: Dict[Union[str, int, float], Any], table_name: str,
            verbose: bool = False, meta: Union[Dict[str, str], None] = None,
            bucket_name: str = config.BUCKET_NAME,
            ignore_conflict: bool = False) -> NoReturn:
        """upload is the method that allows users to upload data to MedQuery without having to deal with
        two wrappers. You simply specify the name of the table you are writing to and include the data as
        records in a dict. You can decide which bucket to store the blobs in, if you have blobs.

        Example of a dictionary with records
        >>>>
        {
        'series_213fds#323': np.ndarray,
        'mask_213fds#323': np.ndarray,
        'model_dmksf3322': None,
        datetime.datetime(0, 1900, 1): None
        }

        The structure is such that the keys are the records values to insert into a table and
        the values are records blobs that you insert into the object storage. The sorting of the keys
        need to follow the sorting in the table.

        Parameters
        ----------
        records : Dict[Union[str, int, float], Any]
            records is the dictionary containing the records you want to insert into MedQuery. The structure of the dict
            matters so please see the example if you are unsure.
        table_name : str
            table_name is simply the name of the table you are inserting into
        verbose : bool
            set verbose to true if you want to have some additional information about your upload
        meta : Union[Dict[str, str], None]
            The meta data will automatically be filled out if your data is np.ndarray
        bucket_name : str
            the bucke name specifies which bucket in the obejct storage you want to use for your data. (mulitmodal_images is the default)
        ignore_conflict : bool
            set ignore conflict to True if you just want to update the table

        Returns
        -------
        NoReturn

        """
        # Fetch the column names from the given table
        col_names = self.__fetch_columns(table_name=table_name, verbose=verbose)

        # The tuple for the records values
        record_values_lst = list(records.keys())
        record_values = tuple(record_values_lst)

        if verbose:
            self.log.info(f"""
            Top of the morning! Here is friendly reminder:

            please make sure that the order of your dictionary keys follows the talbe structure:
            
            Your structure: {record_values}
            {table_name} structure: {col_names}
            """)

        
        self.log.info(f'Uploading records to {table_name} in MedQuery')
        try:
            self.crud.insert(columns=col_names, records=[record_values], table=table_name, ignore_conflict=ignore_conflict)
            self.crud.commit()

            for record_value, record_blob in records.items():
                if record_blob:
                    if isinstance(record_blob, np.ndarray):
                        meta: Dict[str, str] = {
                                'img_shape': str(record_blob.shape),
                                'dtpye': str(record_blob.dtype)
                                }
                    payload, payload_size = encode_payload(payload=record_blob)
                    # Make sure that the bytes reading starts from the beginning
                    if hasattr(payload, 'getbuffer'):
                        payload.seek(0)
                    else:
                        raise ValueError('payload is not a memoryview')

                    # NOTE! we need to make sure that the multimodal bucket dose not get cluttered with
                    # processed data, modelfiles and such. The mask from the models are fine.
                    self.mh.blob_upload(
                            bucket_name=config.BUCKET_NAME,
                            blob_name=record_value,
                            blob_file=payload,
                            size=payload_size,
                            meta=meta
                            )
            self.log.success('Yay! Your upload is completed. Have an awesome ass day!')
            self.crud.close_connection()

        except (ValueError, psycopg2.Error, S3Error) as e:
            self.log.error(f'I tried to connect to the MedQuery but failed to insert the record values {record_values} with the traceback: {e}')
