# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
import base64
from enum import Enum

import dill
import numpy as np
import os
import pandas as pd
import time
import typing
import urllib.parse

from shapelets.dsl import (
    DataApp,
    NodeReturnType,
    SupportedTypes
)
from shapelets.model import (
    Collection,
    CollectionType,
    Dataframe,
    FunctionDescription,
    Model,
    NDArray,
    Permission,
    Sequence,
    SequenceMetadata
)
from shapelets.services import (
    CollectionsService,
    DataAppService,
    DataframeService,
    ExecutionService,
    FunctionsService,
    LoginService,
    MetadataService,
    ModelsService,
    NDArraysService,
    read_user_from_login_file,
    ShapeletsLoginException,
    SequencesService,
    TestService,
    UsersService
)


class Services(Enum):
    COLLECTIONS = "collections_service"
    DATA_APP = "data_app_service"
    DATAFRAMES = "dataframe_service"
    EXECUTION = "execution_service"
    FUNCTIONS = "functions_service"
    MODELS = "models_service"
    METADATA = "metadata_service"
    NDARRAYS = "ndarrays_service"
    SEQUENCES = "sequences_service"
    TEST = "test_service"
    USERS = "users_service"


class Shapelets:
    """
    This class acts as a client for the Shapelets platform, it holds the user session.
    """

    def __init__(self, login_service: LoginService):
        base_url = login_service.base_url
        cookies = login_service.cookies
        self.services = {
            Services.COLLECTIONS: CollectionsService(base_url, cookies),
            Services.DATA_APP: DataAppService(base_url, cookies),
            Services.DATAFRAMES: DataframeService(base_url, cookies),
            Services.EXECUTION: ExecutionService(base_url, cookies),
            Services.FUNCTIONS: FunctionsService(base_url, cookies),
            Services.METADATA: MetadataService(base_url, cookies),
            Services.MODELS: ModelsService(base_url, cookies),
            Services.NDARRAYS: NDArraysService(base_url, cookies),
            Services.SEQUENCES: SequencesService(base_url, cookies),
            Services.TEST: TestService(base_url, cookies),
            Services.USERS: UsersService(base_url, cookies)
        }
        self.services[Services.FUNCTIONS].download_dsl()

    # ########################### #
    # CollectionsService methods: #
    # ########################### #

    def create_collection(self,
                          name: str = "",
                          description: str = "",
                          tags: typing.List[str] = None,
                          collection_type: CollectionType = CollectionType.GENERAL) -> Collection:
        """
        This function creates a new collection in Shapelets.

        :param name: A String with the name of the collection.
        :param description: A String which describes the purpose of this collection.
        :param tags: A list of String, that represent the features of this collection.
        :param collection_type: A String to represent the type of this collection.
        :return: A new Shapelets Collection.
        """
        return self.services[Services.COLLECTIONS].create_collection(
            name=name,
            description=description,
            tags=tags,
            collection_type=collection_type)

    def create_default_collections(self, collection_name: str = "ENERNOC") -> None:
        """
        This function creates a default collection in the Shapelets instance.

        It is a collection with some sequences extracted from the Dataset passed
        as argument, by default ENERNOC.
        :param collection_name: The collection name, ENERNOC as example.
        :return: The default collection of interest.
        """
        self.services[Services.COLLECTIONS].create_default_collections(collection_name)

    def get_collections(self) -> typing.List[Collection]:
        """
        This function returns a list containing all the user's collections.

        :return: A list of Shapelets Collections.
        """
        return self.services[Services.COLLECTIONS].get_collections()

    def get_collection(self, collection_id):
        """
        This functions returns the collection with the id passed as argument.

        :param collection_id: The collection id.
        :return: A Shapelets Collection.
        """
        return self.services[Services.COLLECTIONS].get_collection(collection_id)

    def update_collection(self,
                          collection,
                          name=None,
                          favorite=None,
                          description=None,
                          tags=None,
                          collection_type=None):
        """
        This function updates a collection with the arguments passed to this function.

        :param collection: The Shapelets Collection.
        :param name: A String with the name of the Collection.
        :param favorite: Boolean to indicate if it is favourite or not.
        :param description: A String with the description of this collection.
        :param tags: A list of Strings with containing the tags f the collection.
        :param collection_type: The collection type.
        :return: The update collection.
        """
        return self.services[Services.COLLECTIONS].update_collection(
            collection,
            name=name,
            favorite=favorite,
            description=description,
            tags=tags,
            collection_type=collection_type)

    def delete_collection(self, collection):
        """
        This function deletes a collection.

        :param collection: The Shapelets Collection.
        :return: Returns True if the operation was successful False otherwise.
        """
        return self.services[Services.COLLECTIONS].delete_collection(collection)

    def get_collection_sequences(self, collection: Collection) -> typing.List[Sequence]:
        """
        This function gets all Shapelets Sequences from the given Collection.

        :param collection: The Collection.
        :return: List of Shapelets Sequences.
        """
        return self.services[Services.COLLECTIONS].get_collection_sequences(collection)

    def get_collection_types(self):
        """
        This function returns a list with all types of Collections.

        :return: A list of strings with all collection types.
        """
        return self.services[Services.COLLECTIONS].get_collection_types()

    def share_collection(self, collection: Collection,
                         subject: typing.Any,
                         grant: Permission):
        """
        This function shares a collection with the given sid, which can be an user or group.

        :param collection: Collection of sequences.
        :param subject: Subject can be an user or group.
        :param grant: The Permission of access.
        """
        self.services[Services.COLLECTIONS].share_collection(collection, subject, grant)

    def unshare_collection(self, collection, subject):
        """
        This function unshares a collection with the given sid, which can be either an User or Group.

        :param collection: Collection of sequences.
        :param subject: Subject, can be an User or Group.
        """
        self.services[Services.COLLECTIONS].unshare_collection(collection, subject)

    def get_collection_sharing(self, collection):
        """
        This function returns a List containing the users with access to the given collection.

        :param collection: The Collection.
        :return: List of Users with access Permission.
        """
        self.services[Services.COLLECTIONS].get_collection_sharing(collection)

    def get_collection_privileges(self, collection):
        """
        This function returns the List of Permissions that the calling user has on the Collection.

        :param collection: The Collection.
        :return: List of Users with access Permission.
        """
        self.services[Services.COLLECTIONS].get_collection_privileges(collection)

    # ######################### #
    # NDArraysService methods: #
    # ######################### #

    def create_nd_array(self,
                        array: np.ndarray,
                        name: str = None,
                        description: str = None) -> NDArray:
        """
        This function registers a new NDArray into Shapelets.

        :param array: The numpy ndarray to be stored.
        :param name: The name of the NDArrray.
        :param description: The description of the NDArray.
        :return: The registered NDArray.
        """
        return self.services[Services.NDARRAYS].create_nd_array(array, name, description)

    def get_nd_array_data(self, ndarray: NDArray) -> np.ndarray:
        """
        This function returns an existing NDArray in Shapelets.

        :param ndarray: The ndarray to be returned.
        :return: A numpy ndarray.
        """
        return self.services[Services.NDARRAYS].get_nd_array_data(ndarray)

    def update_nd_array(self, nd_array: NDArray, array: np.ndarray = None) -> NDArray:
        """
        This function updates a NDArray. This function checks dimensionality to ensure integrity between
        array's data and array's metadata.

        :param nd_array: The NDArray to be updated.
        :param array: This parameter is optional, if present the array's data is updated as well.
        :return: The registered NDArray.
        """
        return self.services[Services.NDARRAYS].update_nd_array(nd_array, array)

    def delete_nd_array(self, nd_array: NDArray) -> bool:
        """
        This function deletes the given NDArray.

        :param nd_array: The NDArray to be deleted.
        returns A bool indicating if the NDArray was deleted or not.
        """
        return self.services[Services.NDARRAYS].delete_nd_array(nd_array)

        # ######################### #
        # ModelsService methods: #
        # ######################### #

    def create_model(self,
                     model,
                     name: str = None,
                     description: str = None,
                     metadata: typing.Dict[str, str] = None) -> Model:
        """
        This function registers a new Model into Shapelets.

        :param model: The data model to be stored.
        :param name: The name of the Model.
        :param description: The description of the Model.
        :param metadata: The metadata of the Model.
        :return: The registered Model.
        """
        return self.services[Services.MODELS].create_model(model, name, description, metadata)

    def get_model_data(self, model: Model) -> str:
        """
        This function returns the Model data of an existing Model in Shapelets.

        :param model: The Model to be returned.
        :return: A string with the Model.
        """

        date_encode = bytes(model.data, encoding='utf-8')
        data_bytes = base64.b64decode(date_encode)
        return dill.loads(data_bytes)
        # return self.services[Services.MODELS].get_model_data(model)

    def update_model(self, model: Model, new_model: str = None) -> Model:
        """
        This function updates a Model.

        :param model: The Model to be updated.
        :param new_model: This parameter is optional, if present the new model is updated as well.
        :return: The registered Model.
        """
        return self.services[Services.MODELS].update_model(model, new_model)

    def delete_model(self, model: Model) -> bool:
        """
        This function deletes the given Model.

        :param model: The Model to be deleted.
        returns A bool indicating if the Model was deleted or not.
        """
        return self.services[Services.MODELS].delete_model(model)

    # ######################### #
    # DataframesService methods: #
    # ######################### #

    def create_dataframe(self,
                         dataframe: pd.DataFrame,
                         name: str = None,
                         description: str = None) -> Dataframe:
        """
        This function registers a new Dataframe into Shapelets.

        :param dataframe: The dataframe from pandas to be stored.
        :param name: The name of the Dataframe.
        :param description: The description of the Dataframe.
        :return: The registered Dataframe.
        """
        return self.services[Services.DATAFRAMES].create_dataframe(dataframe, name, description)

    def get_dataframe_data(self, dataframe: Dataframe) -> pd.DataFrame:
        """
        This function returns an existing Dataframe in Shapelets.

        :param dataframe: The Dataframe to be returned.
        :return: A pandas dataframe.
        """
        return self.services[Services.DATAFRAMES].get_dataframe_data(dataframe)

    def update_dataframe(self, dataframe: Dataframe, new_data: pd.DataFrame = None) -> Dataframe:
        """
        This function updates a Dataframe.

        :param dataframe: The Dataframe to be updated.
        :param new_data: This parameter is optional, if present the data of the given Dataframe is updated with the new
        pandas dataframe.
        :return: The registered Dataframe.
        """
        return self.services[Services.DATAFRAMES].update_dataframe(dataframe, new_data)

    def delete_dataframe(self, dataframe: Dataframe) -> bool:
        """
        This function deletes the given Dataframe.

        :param dataframe: The Dataframe to be deleted.
        returns A bool indicating if the given Dataframe was deleted or not.
        """
        return self.services[Services.DATAFRAMES].delete_dataframe(dataframe)

    # ######################### #
    # SequencesService methods: #
    # ######################### #

    def create_sequence(self,
                        dataframe: pd.DataFrame,
                        name: str = "",
                        starts: np.datetime64 = None,
                        every=None,
                        collection=None) -> Sequence:
        """
        This function creates a sequence from a dataframe and stores it into Shapelets.

        NOTE: Only regular (evenly spaced) series are allowed.
        :param dataframe: A pandas dataframe. If it has a datetime64 index it will be used.
        :param name: name of the sequence.
        :param every: Time in milliseconds for regular series. The parameter is mandatory
        if the dataframe has not a datetime64 index.
        :param starts: Start is the timestamp of the beginning of the sequence. The
        parameter is mandatory if the dataframe has not a datetime64 index.
        :param collection: The Collection that sets if the sequence should be add to
        a Collection. None if it is not required.
        :return: The Sequence.
        """

        if collection is None:
            collections = self.services[Services.COLLECTIONS].get_collections()
            collection = next(
                col for col in collections if col.name == "Default Collection")
        return self.services[Services.SEQUENCES].create_sequence(
            dataframe,
            name,
            starts,
            every,
            collection)

    def update_sequence(self, sequence, dataframe):
        """
        This function updates a Sequence.

        :param sequence: The sequence to be updated.
        :param dataframe: A pandas dataframe containing the new information to be
        stored in the sequence.
        """
        self.services[Services.SEQUENCES].update_sequence(sequence, dataframe)

    def get_sequence_data(self, sequence):
        return self.services[Services.SEQUENCES].get_sequence_data(sequence)

        # ######################## #
        # MetadataService methods: #
        # ######################## #

    def get_metadata(self, collection: Collection) -> pd.DataFrame:
        """
        This function returns all the metadata for the given Collection.

        :param collection: The given Collection.
        :return: A dataframe with all de metadata with sequence names as index and each column
        name as the metadata field.
        """
        return self.services[Services.METADATA].get_metadata(collection)

    def add_metadata(self, collection: Collection, sequence: Sequence, metadata: SequenceMetadata):
        """
        This function adds MetaData to a Sequence in a Collection.

        :param collection: The Collection which the sequence belongs to.
        :param sequence: The Sequence.
        :param metadata: the metadata to be added.
        """
        self.services[Services.METADATA].add_metadata(collection, sequence, metadata)

    def add_metadata_from_pandas(self, collection: Collection, dataframe: pd.DataFrame):
        """
        This function adds a pandas dataframe containing metadata to sequences in a Collection.

        The dataframe has to be of the following shape:
            - It must have an index with the name of the sequences.
            - Each column name will be the metadata name and the value of each
              row will be the value of this metadata for the sequence in the
              index of the row.
        The supported types are:
            - float
            - str
            - datetime.datetime
            - np.datetime64
            - Shapelets.MetadataCoordinates
        :param collection: The target Collection.
        :param dataframe: The dataframe containing the metadata.
        """
        self.services[Services.METADATA].add_metadata_from_pandas(
            collection,
            self.get_collection_sequences(collection),
            dataframe)

    # ##################### #
    # UsersService methods: #
    # ##################### #

    def get_users(self):
        """
        This function returns the list of Users in Shapelets.

        :return: List of Users.
        """
        return self.services[Services.USERS].get_users()

    def get_groups(self):
        """
        This function returns the list of Groups in Shapelets.

        :return: List of Groups.
        """
        return self.services[Services.USERS].get_groups()

    def get_my_user_details(self):
        """
        This function returns the calling User's details.

        :return: UserDetails
        """
        return self.services[Services.USERS].get_my_user_details()

    def get_user_details(self, subject_id):
        """
        Returns the user details for the given subject_id.

        :param subject_id: The User.
        :return: An instance of User.
        """
        return self.services[Services.USERS].get_user_details(subject_id)

    # ######################### #
    # DataAppService methods: #
    # ######################### #

    def get_data_apps(self) -> typing.List[DataApp]:
        """
        This function returns the list of DataApps that the calling User has read permissions.

        :return: A list of DataApps.
        """
        return self.services[Services.DATA_APP].get_data_apps()

    def register_data_app(self, app: DataApp):
        """
        This function registers the given DataApp into Shapelets.
        """
        dataapp = self.services[Services.DATA_APP].register_data_app(app)
        print(
            f"Registered data-app: {self.services[Services.DATA_APP].base_url}/app/data-apps/{urllib.parse.quote(dataapp.name)}")
        return dataapp

    def delete_data_app(self, data_app_id: str) -> bool:
        """
        This function removes the given DataApp.
        """
        return self.services[Services.DATA_APP].delete_data_app(data_app_id)

    # ######################### #
    # ExecutionService methods: #
    # ######################### #

    def run(self, output_nodes: NodeReturnType) -> SupportedTypes:
        """
        This function executes and wait for the completion of the given computing graph.

        :param output_nodes: The output nodes of the graph to be executed.
        :return: The list of computed output_nodes.
        """
        return self.services[Services.EXECUTION].run_and_wait_for_all(output_nodes)

    def run_async(self, output_nodes: NodeReturnType) -> int:
        """
        This function executes asynchronously the given computing graph.

        :param output_nodes: The output nodes of the graph to be executed.
        :return: The number of the computing job that represents the enqueued computation.
        """
        return self.services[Services.EXECUTION].run_async(output_nodes)

    def wait_for_result(self, job_id) -> SupportedTypes:
        """
        This function waits until the computation of the given job_id is finished.

        :param job_id: The number of a previously enqueued Job.
        :return: The list of computed output_nodes.
        """
        return self.services[Services.EXECUTION].wait_for_result(job_id)

    def get_all_analysis(self) -> typing.List[str]:
        """
        This function returns a list of all Analysis registers in the system.
        """
        return self.services[Services.EXECUTION].get_all_analysis()

    # ######################### #
    # FunctionsService methods: #
    # ######################### #

    def register_custom_function(self,
                                 custom_function: typing.Callable,
                                 description: FunctionDescription = None,
                                 force: bool = True,
                                 persist_results: bool = True):
        """
        This function registers a new User function in the system.

        :param custom_function: The function to be registered.
        :param description: The description of tee function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: This parameter activates the result caching mechanism.
        """
        self.services[Services.FUNCTIONS].register_custom_function(custom_function, description, force, persist_results)

    def register_custom_splitter(self,
                                 custom_function: typing.Callable,
                                 description: FunctionDescription = None,
                                 force: bool = True,
                                 persist_results: bool = True):
        """
        This function registers a new Splitter user function in the system.

        :param custom_function: The function to be registered.
        :param description: The description of the function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: This parameter activates the result caching mechanism.
        """
        self.services[Services.FUNCTIONS].register_custom_splitter(custom_function, description, force, persist_results)

    def register_custom_reducer(self,
                                custom_function: typing.Callable,
                                description: FunctionDescription = None,
                                force: bool = True,
                                persist_results: bool = True):
        """
        This function registers a new Reducer function in the system.

        :param custom_function: The function to be registered.
        :param description: The description of the function.
        :param force: Force overwriting the function if there is one function with this name already registered.
        :param persist_results: This parameter activates the result caching mechanism.
        """
        self.services[Services.FUNCTIONS].register_custom_reducer(custom_function, description, force, persist_results)

    def register_flow(self,
                      name: str,
                      output_nodes: NodeReturnType,
                      output_names: typing.Optional[typing.List[str]] = None,
                      persist_results: bool = True,
                      documentation: str = "No documentation provided for this function."):
        """
        This function registers a new User flow in the system.

        :param name: The name of the flow.
        :param output_nodes: The output nodes of the flow.
        :param output_names: List of names for the outputs of the flow.
        :param persist_results: This parameter activates the result caching mechanism.
        :param documentation: The doc string of the function.
        """
        self.services[Services.FUNCTIONS].register_flow(name, documentation, output_nodes, output_names,
                                                        persist_results)

    def register_analysis(self,
                          name: str,
                          output_nodes: NodeReturnType,
                          output_names: typing.Optional[typing.List[str]] = None,
                          persist_results: bool = True,
                          documentation: str = "No documentation provided for this function."
                          ):
        """
        This function registers a new User analysis in the system.

        :param name: The name of the flow.
        :param output_nodes: List of output nodes.
        :param output_names: List of names for the outputs of the flow.
        :param persist_results: This parameter activates the result caching mechanism.
        :param documentation: The doc string of the function.
        """
        self.services[Services.FUNCTIONS].register_analysis(name, documentation, output_nodes, output_names,
                                                            persist_results)

    def delete_analysis(self, name: str):
        """
        This function deletes the analysis with the names passed as argument.

        :param name: The name of hte analysis to be deleted.
        """
        self.services[Services.FUNCTIONS].delete_analysis(name)

    def delete_all_analysis(self):
        """
        This function deletes all analysis registered in Shapelets.
        """
        self.services[Services.FUNCTIONS].delete_all_analysis()

    def get_function_parameters(self, name: str = None):
        """
        This function return a FunctionParametersDescription or List[FunctionParametersDescription] depending on the
        name parameter. If it is not given, this function will return a list of all functions within the system,
        otherwise it will return the FunctionParametersDescription of the requested function.

        :param name: The function name to be returned.
        """
        return self.services[Services.FUNCTIONS].get_function_parameters(name)

    # #################### #
    # TestService methods: #
    # #################### #

    def ping(self):
        """
        This function performs a ping action.

        :return True if it receives the pong message.
        """
        return self.services[Services.TEST].ping()

    def test_get(self, api_path):
        """
        This function allows to perform a get action against Shapelets.

        :param api_path: The path of the API to be tested.
        """
        return self.services[Services.TEST].test_get(api_path)

    def test_get_raw(self, api_path):
        """
        This function allows to perform a get action against Shapelets and returns the raw response.

        :param api_path: The path of the API to be tested.
        :return: The raw response of the get action.
        """
        return self.services[Services.TEST].test_get_raw(api_path)

    def test_delete(self, api_path):
        """
        This function allows to perform a delete action against Shapelets.

        :param api_path: The path of the API to be tested.
        """
        return self.services[Services.TEST].test_delete(api_path)

    def test_post(self, api_path, data):
        """
        This function allows to perform a post action against Shapelets.

        :param api_path: The path of the API to be tested.
        """
        return self.services[Services.TEST].test_post(api_path, data)

    def test_put(self, api_path, data):
        """
        This function allows to perform a put action against Shapelets.

        :param api_path: The path of the API to be tested.
        """
        return self.services[Services.TEST].test_put(api_path, data)


def start_shapelet_processes():
    """
    This function launches Shapelets processes in background.
    """
    from shapelets.__main__ import start_all_command
    start_all_command()
    login_service = LoginService('https://localhost', 443)
    while True:
        try:
            login_service.check_server_is_up()
            print(f"server is up...")
            break
        except:
            print(f"server is starting, takes a few seconds...")
            time.sleep(5)


def stop_shapelet_processes():
    """
    This function stops Shapelets processes running in background.
    """
    from shapelets.__main__ import stop_command
    stop_command()


def close_session():
    """
    This function closes the Shapelets processes running in background.
    """
    stop_shapelet_processes()


def init_session(username: str = None,
                 password: str = None,
                 address: str = "https://localhost",
                 port: int = None,
                 start_shapelets_processes: bool = True) -> Shapelets:
    """
    This function initializes the session in Shapelets with the given user, password and address.

    :param username: The username of the user to be logged in.
    :param password: The password of the user.
    :param address: The address of the Shapelets instance to be hit, default to localhost.
    :param port: The number of the port, default to None.
    :param start_shapelets_processes: Launches Shapelets processes in background , default to True.

    :return: The Shapelets object to access all the system API.
    """
    if start_shapelets_processes:
        start_shapelet_processes()

    if username and password and address:
        print(f"Login as {username} for address {address}{':' + str(port) if port else ''}")
        login_service = LoginService(address, port)
        login_service.login_user(username, password)
        return Shapelets(login_service)

    if username and address:
        user_info = read_user_from_login_file(address, username)
        if user_info:
            print(f"Found {username} info in login file for address {address}")
            return init_session(
                user_info["user"],
                user_info["password"],
                user_info["server"],
                port)
        elif os.environ.get("SHAPELETS_PWD"):
            print(f"Found {username} info in Env Variable")
            return init_session(
                username,
                os.environ.get("SHAPELETS_PWD"),
                address,
                port)
        else:
            raise ShapeletsLoginException(f"{username} information not found for address {address}")

    if address:
        user_info = read_user_from_login_file(address)
        if user_info:
            print(f"Found default user info in login file for {address}")
            return init_session(
                user_info["user"],
                user_info["password"],
                user_info["server"],
                port)
        elif os.environ.get("SHAPELETS_USER"):
            print("Found user name in Env Variable")
            return init_session(
                os.environ.get("SHAPELETS_USER"),
                None,
                address,
                port)
        else:
            raise ShapeletsLoginException(f"Login information not found for address {address}")
    else:
        raise ShapeletsLoginException("Login information not found")


def update_password(user: str, password: str, new_password: str, address: str, port: int = None):
    """
    This function updates the password for an User.

    :param user: The user for which the password is going to be updated.
    :param password: The old password.
    :param new_password: The new password.
    :param address: The address of the Shapelets instance.
    :param port: The port.

    :return: True if the password was successfully updated.
    """
    login_service = LoginService(address, port)
    login_service.update_password(user, password, new_password)
    return Shapelets(login_service)
