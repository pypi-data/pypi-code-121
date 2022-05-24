import deepdish as dd
import h5py
import json
import os
import xmltodict
import yaml

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, validate_arguments, Field
from json import dumps
from easyDataverse.core.file import File

from easyDataverse.core.uploader import upload_to_dataverse, update_dataset
from easyDataverse.core.dataverseBase import DataverseBase
from easyDataverse.core.downloader import download_from_dataverse
from easyDataverse.tools.utils import YAMLDumper, get_class


class Dataset(BaseModel):
    class Config:
        extra = "allow"

    metadatablocks: Dict[str, Any] = dict()
    p_id: Optional[str] = None
    files: List[File] = Field(default_factory=list)

    # ! Adders

    def add_metadatablock(self, metadatablock: DataverseBase) -> None:
        """Adds a metadatablock object to the dataset if it is of 'DataverseBase' type and has a metadatablock name"""

        # Check if the metadatablock is of 'DataverseBase' type
        if issubclass(metadatablock.__class__, DataverseBase) is False:
            raise TypeError(
                f"Expected class of type 'DataverseBase', got '{metadatablock.__class__.__name__}'"
            )

        if hasattr(metadatablock, "_metadatablock_name") is False:
            raise TypeError(
                f"The provided class {metadatablock.__class__.__name__} has no metadatablock name and is thus not compatible with this function."
            )

        # Add the metadatablock to the dataset as a dict
        block_name = getattr(metadatablock, "_metadatablock_name")
        self.metadatablocks.update({block_name: metadatablock})

        # ... and to the __dict__
        setattr(self, block_name, metadatablock)

    def add_file(self, dv_path: str, local_path: str, description: str = ""):
        """Adds a file to the dataset based on the provided path.

        Args:
            filename (str): Path to the file to be added.
            description (str, optional): Description of the file. Defaults to "".
        """

        # Create the file
        file = File(filename=dv_path, local_path=local_path, description=description)

        if file not in self.files:
            self.files.append(file)
        else:
            raise Exception(f"File has already been added to the dataset")

    def add_directory(self, dirpath: str) -> None:
        """Adds a complete directory to the dataset.

        Args:
            dirpath (str): Path to the directory
        """

        dirpath = os.path.join(dirpath)

        if not os.path.isdir(dirpath):
            raise FileNotFoundError(
                f"Directory at {dirpath} does not exist or is not a directory. Please provide a valid directory."
            )

        for path, _, files in os.walk(dirpath):

            if "." in path:
                continue

            for file in files:
                if file.startswith("."):
                    continue

                # Get all the metadata
                filepath = os.path.join(path, file)

                path_parts = [
                    p
                    for p in filepath.split(os.path.sep)
                    if not p in dirpath.split(os.path.sep)
                ]
                filename = os.path.join(*path_parts)
                data_file = File(filename=filename, local_path=filepath)

                # Substitute new files with old files
                found = False
                for f in self.files:
                    if f.filename == filename:
                        f.local_path = data_file.local_path
                        found = True
                        break

                if not found:
                    self.files.append(data_file)

    # ! Exporters

    def xml(self) -> str:
        """Returns an XML representation of the dataverse object."""

        # Turn all keys to be camelcase
        fields = self._keys_to_camel({"dataset_version": self.dict()})

        return xmltodict.unparse(fields, pretty=True, indent="    ")

    def dataverse_dict(self) -> dict:
        """Returns a dictionary representation of the dataverse dataset."""

        # Convert all blocks to the appropriate format
        blocks = {}
        for block in self.metadatablocks.values():
            blocks.update(block.dataverse_dict())

        return {"datasetVersion": {"metadataBlocks": blocks}}

    def dataverse_json(self, indent: int = 2) -> str:
        """Returns a JSON representation of the dataverse dataset."""

        return dumps(self.dataverse_dict(), indent=indent)

    def yaml(self) -> str:
        """Exports the dataset as a YAML file that can also be read by the API"""

        # Get the name of the module to ensure
        # that the correct one is used when reading
        # the YAML file later on
        lib_name = os.environ["EASYDATAVERSE_LIB_NAME"]

        # Initialize the data structure that will be dumped
        data = {"lib_name": lib_name}

        if self.p_id:
            data["dataset_id"] = self.p_id

        # Convert each metadatablock to JSON
        data.update(self.dict(include={"metadatablocks"}, exclude_none=True))

        return yaml.dump(
            data, Dumper=YAMLDumper, default_flow_style=False, sort_keys=False
        )

    def json(self) -> str:
        """Exports the dataset as a JSON file that can also be read by the API"""

        # Get the name of the module to ensure
        # that the correct one is used when reading
        # the YAML file later on
        lib_name = os.environ["EASYDATAVERSE_LIB_NAME"]

        # Initialize the data structure that will be dumped
        data = {"lib_name": lib_name}

        if self.p_id:
            data["dataset_id"] = self.p_id

        # Convert each metadatablock to JSON
        data.update(self.dict(include={"metadatablocks"}, exclude_none=True))

        return json.dumps(data, indent=4)

    def hdf5(self, path: str) -> None:
        """Exports the dataset to an HDF5 dataset that can also be read by the API_TOKEN

        Args:
            path (str): Path to the destination HDF5 files.
        """

        # Write metatdat to hdf5
        dd.io.save(path, self.dict(exclude={"files"}, exclude_none=True))

        # Add all files
        with h5py.File(path, "r+") as f:

            # Create Files Tag
            files = f.create_group("Files")

            for file in self.files:
                if not file.local_path:
                    # Skip if there is no actual data
                    continue

                # Create destination file
                destination = file.filename.replace("/", "\\")
                dset = files.create_group(destination)

                if h5py.is_hdf5(file.local_path):
                    # If it is an HDF5 file then copy the content and
                    # not the binary file
                    dset.attrs["is_h5"] = True
                    with h5py.File(file.local_path) as h5:
                        f.copy(h5, f"Files/{destination}/content")

                else:
                    # If its not an HDF5 file add the binary to attrs
                    dset.attrs["is_h5"] = False
                    dset.attrs["content"] = open(file.local_path, "rb").read()

                if file.description:
                    dset.attrs["description"] = file.description

    # ! Dataverse interfaces

    def upload(
        self,
        dataverse_name: str,
        content_loc: Optional[str] = None,
        DATAVERSE_URL: Optional[str] = None,
        API_TOKEN: Optional[str] = None,
    ) -> str:
        """Uploads a given dataset to a Dataverse installation specified in the environment variable.

        Args:
            dataverse_name (str): Name of the target dataverse.
            filenames (List[str], optional): File or directory names which will be uploaded. Defaults to None.
            content_loc (Optional[str], optional): If specified, the ZIP that is used to upload will be stored at the destination provided. Defaults to None.
            DATAVERSE_URL (Optional[str], optional): Alternatively provide base url as argument. Defaults to None.
            API_TOKEN (Optional[str], optional): Alternatively provide the api token as argument. Attention, do not use this for public scripts, otherwise it will expose your API Token. Defaults to None.
        Returns:
            str: [description]
        """

        self.p_id = upload_to_dataverse(
            json_data=self.dataverse_json(),
            dataverse_name=dataverse_name,
            files=self.files,
            p_id=self.p_id,
            DATAVERSE_URL=DATAVERSE_URL,
            API_TOKEN=API_TOKEN,
            content_loc=content_loc,
        )

        return self.p_id

    def update(
        self,
        contact_name: Optional[str] = None,
        contact_mail: Optional[str] = None,
        content_loc: Optional[str] = None,
        DATAVERSE_URL: Optional[str] = None,
        API_TOKEN: Optional[str] = None,
    ):
        """Updates a given dataset if a p_id has been given.

        Use this function in conjunction with 'from_dataverse_doi' to edit and update datasets.
        Due to the Dataverse REST API, downloaded datasets wont include contact mails, but in
        order to update the dataset it is required. For this, provide a name and mail for contact.
        EasyDataverse will search existing contacts and when a name fits, it will add the mail.
        Otherwise a new contact is added to the dataset.

        Args:
            contact_name (str, optional): Name of the contact. Defaults to None.
            contact_mail (str, optional): Mail of the contact. Defaults to None.
            content_loc (Optional[str], optional): If specified, the ZIP that is used to upload will be stored at the destination provided. Defaults to None.
        """

        # Update contact
        if contact_name is None and contact_mail is None:
            # Check if there is already a contact defined
            contact_mails = [
                contact.email for contact in self.citation.contact if contact.email
            ]

            if len(contact_mails) == 0:
                raise ValueError(
                    f"Please provide a contact name and email to update the dataset"
                )

        # Check if there is a contact with the given name already in the dataset
        has_mail = False
        for contact in self.citation.contact:
            if contact.name == contact_name:
                contact.email = contact_mail
                has_mail = True

        if has_mail == False:
            # Assign a completely new contact if the name is new
            self.citation.add_contact(name=contact_name, email=contact_mail)

        update_dataset(
            json_data=self.dataverse_dict()["datasetVersion"],
            p_id=self.p_id,
            files=self.files,
            DATAVERSE_URL=DATAVERSE_URL,
            API_TOKEN=API_TOKEN,
            content_loc=content_loc,
        )

    # ! Initializers

    @classmethod
    @validate_arguments
    def from_dataverse_doi(cls, doi: str, filedir: str = "."):
        """Initializes a Dataset from a given Dataverse dataset.

        Args:
            doi (str): DOI of the dataverse Dataset.
            lib_name (str): Name of the library to fetch the given metadatablocks.

        Returns:
            Dataset: Resulting dataset that has been downloaded from Dataverse.
        """

        lib_name = os.environ["EASYDATAVERSE_LIB_NAME"]

        return download_from_dataverse(cls(), doi, lib_name, filedir)

    @classmethod
    def from_json(cls, path: str, use_id: bool = True):
        """Initializes a dataset based on a given YAML file.

        The specifications for the JSON file include the following:
        {
            lib_name: "Important to infer the metadatablocks. For instance 'pyDaRUS'.",
            dataset_id: "Used to update datasets that are already given. Leave out for new ones.",
            metadatablocks: {
                block1: {
                    field1: Content of the field
                    field2: ...
                },
                block2: {
                    field1: ...
                }
            }
        }

        Args:
            path (str): Path to the YAML file.
            use_id (bool): Whether or not the Dataset ID should be included. Defaults to True.

        Returns:
            Dataset: The resulting Dataset instance.
        """

        # Load JSON file
        with open(path, "r") as file_handle:
            data = json.loads(file_handle.read())

        return cls.from_dict(data, use_id)

    @classmethod
    def from_yaml(cls, path: str, use_id: bool = True):
        """Initializes a dataset based on a given YAML file.

        The specifications for the YAML file include the following:

        lib_name: Important to infer the metadatablocks. For instance 'pyDaRUS'.
        dataset_id: Used to update datasets that are already given. Leave out for new ones.
        metadatablocks:
          block1:
           field1: Content of the field
           field2: ...
          blocks2:
           field1: ...

        Args:
            path (str): Path to the YAML file.
            use_id (bool): Whether or not the Dataset ID should be included. Defaults to True.

        Returns:
            Dataset: The resulting Dataset instance.
        """

        # Load YAML file
        with open(path, "r") as file_handle:
            data = yaml.safe_load(file_handle.read())

        return cls.from_dict(data, use_id)

    @classmethod
    def from_dict(cls, data: dict, use_id: bool = True):

        # Initialize blank dataset
        # and get lib_name for imports
        dataset = cls()
        lib_name = data["lib_name"]
        dataset_id = data.get("dataset_id")

        if dataset_id and use_id:
            # Assign ID if given
            dataset.p_id = dataset_id

        # Iteratively import the modules and add blocks
        for module_name, fields in data["metadatablocks"].items():

            # Adapt module name to the namespace of generated code
            module_name = f".metadatablocks.{module_name}"

            # Retrieve class and initialize using the given
            # YAML data as a dicitonary
            cls = get_class(module_name, lib_name)[-1]
            instance = cls(**fields)

            dataset.add_metadatablock(instance)

        return dataset

    # ! Utilities

    @staticmethod
    def _snake_to_camel(word: str) -> str:
        return "".join(x.capitalize() or "_" for x in word.split("_"))

    def _keys_to_camel(self, dictionary: dict):
        nu_dict = {}
        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):
                nu_dict[self._snake_to_camel(key)] = self._keys_to_camel(
                    dictionary[key]
                )
            else:
                nu_dict[self._snake_to_camel(key)] = dictionary[key]
        return nu_dict
