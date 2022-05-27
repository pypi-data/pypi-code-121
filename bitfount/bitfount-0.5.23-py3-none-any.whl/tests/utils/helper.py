"""Testing helper functions."""
import datetime
import inspect
from io import BytesIO
import logging
import random
import string
from typing import Any, List, Literal, Optional, Protocol, Sequence, Tuple, Union, cast
from unittest.mock import create_autospec

from PIL import Image, ImageOps
from _pytest.logging import LogCaptureFixture
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import numpy as np
import pandas as pd
import pytest

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import SchemaOverrideMapping
from bitfount.federated.aggregators.aggregator import Aggregator
from bitfount.federated.aggregators.base import _BaseAggregatorFactory
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.authorisation_checkers import (
    IdentityVerificationMethod,
    _LocalAuthorisation,
)
from bitfount.federated.early_stopping import FederatedEarlyStopping
from bitfount.federated.modeller import _Modeller
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.secure import SecureShare
from bitfount.federated.transport.worker_transport import (
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.federated.types import AlgorithmType, ProtocolType
from bitfount.federated.utils import _ALGORITHMS, _MODELS, _PROTOCOLS
from bitfount.federated.worker import _Worker
from bitfount.hub.api import BitfountHub
from bitfount.metrics import (
    BINARY_CLASSIFICATION_METRICS,
    MULTICLASS_CLASSIFICATION_METRICS,
    REGRESSION_METRICS,
    MetricCollection,
)
from bitfount.models.base_models import ClassifierMixIn, Optimizer, _BaseModel
from bitfount.types import DistributedModelProtocol, _StrAnyDict
from bitfount.utils import _add_this_to_list, seed_all
from tests.utils.mocks import LocalMessageService, LocalMessageServiceSharedQueues

# PYTEST MARKS
# tests involving a specific backend
backend_test = pytest.mark.backend_test

# tests that run the full end-to-end system in the form of tutorials
tutorial_test = pytest.mark.tutorial_test
# tests that run the full end-to-end system, but mock out web calls
end_to_end_mocks_test = pytest.mark.end_to_end_mocks_test
# tests that run the full end-to-end system, including web calls
end_to_end_test = pytest.mark.end_to_end_test
# slower, integration- or training-like tests
integration_test = pytest.mark.integration_test
# faster, unit-test-like tests
unit_test = pytest.mark.unit_test
# Individual test markers for tutorial tests
tutorial_1_test = pytest.mark.tutorial_1_test
tutorial_2_test = pytest.mark.tutorial_2_test
tutorial_3_test = pytest.mark.tutorial_3_test
tutorial_4_test = pytest.mark.tutorial_4_test
tutorial_5_test = pytest.mark.tutorial_5_test
tutorial_6_test = pytest.mark.tutorial_6_test
tutorial_7_test = pytest.mark.tutorial_7_test
tutorial_8_test = pytest.mark.tutorial_8_test
tutorial_9_test = pytest.mark.tutorial_9_test
tutorial_10_test = pytest.mark.tutorial_10_test

DATASET_ROW_COUNT = 4000
DIMS = (DATASET_ROW_COUNT, 4)
AUC_THRESHOLD = 0.6
MAE_THRESHOLD = 0.2

PRIVATE_KEY = inspect.cleandoc(
    """-----BEGIN RSA PRIVATE KEY-----
    MIIEpQIBAAKCAQEAwA0cNMjzEm+LPFolbdOAcIB6hX7QGqkzVC8L8W5X2qFFDrSb
    TI9CSifQ3/1A+xYfiZrR4Za2cCvCtIzHxVctEAcQSW+IDRjh5vvdGTKgJMtaf3YH
    eXMk9NAN4Px6McuqaBE2llYt6okICha8MEUR9lffa761WkOOWnWAXQFUWxWOxuVn
    KQOOm1OQ0OiGd+6b81TbSmHDL1QeAMN66tscnR0zFuLfaCRz8yZIsKR1bUPTAUnC
    B3gaUXIixxDTeSG6XHItb7c/uHJUPtW4lFLiDF12JX0GwQvkpYCe3I++fBxC0xcd
    GwmncKocOLtsuOPswDHH3waxp5KGVDsdx8Po8QIDAQABAoIBAQCiYvN0lm0hK3u5
    nieDw5AYkCoI8n8X6/Vgux8IF1rlm/L+Siv+Aiv089Gjc0ochEpKWcQZUQwVsIrD
    iz3nWJzbrn1Q+qM5H87zNgdvJOVP9zogCDattHSNI9Z4ZEMWE7WUpOlZGKleZFuN
    3EdnMR/NAeQCAJDrL7AQQMY23cbr88dZ1VJ0zJdt50IdjTHjG5gpX8ifl3egWQSa
    xKh3QJWFQI8oR69lT29ZAGgaPb3mhruyvUCK0ioI++g9kBMVncMeNV0SrsHNTdWH
    mKhjEI1KeNTPBXxZCD43L2/tCp+K+9WZs2LJdsCtN1/bDjc7xMWFQnoJ+8OcpYEX
    tV5k+VgBAoGBAPapKUk7vtaLhCA2+T7dde83QjgvcNwH2hB7Zbs5rEElBJUWDFsf
    Av08jqHY8kTsBbh78uq+CWTY+G/d2pUw6hHoHVWLyTrMbnIl/moRjypCNsKcSRP/
    tmAepWz3smBfpgin5GrSx29LCI6EE1sOOKYj1IsQPwuTObFqnCBa8e4xAoGBAMdS
    oMtTI4eNR7X8jS+id0rM3tvWwxQT5SvyoJA/WzQa1PRCf96r6CXWZ7+0A38tpkdF
    OL3qK2UUzweVqEGZu+ZzrrOBO9d2jfbcZSSZ/Qd3fANpl9SkImYVyyZhGzbkIZce
    5UkH3HauLDvvCnWl2JJDlzgJuqQu+F9AKmxj8TbBAoGBANYHlOaR7Bc4Om7FpOLy
    wZnQBirAp5qVSZfRq0WZVqm0WFSRLCmJMEvS1yUDHb3GW3RoQTGFspsKVhCjnj6k
    kgb1tTZ8tCDMMO3ln+wjzmlpySB3AkZTNcoT7ZEvIV3UwTpzjJVQznL41bTsT+tL
    3MX1A0Gj2EDQAFi9XDoLEDCRAoGBAI69sKMLTfVkCsfcLevACHgL0UlUOm3ldYgM
    gEns5U6iLIEkIlh/eYenTLMvohVwxpRhkSoISb1gsoZ2+YDJLJPzolewo/9ASphP
    6yrUEC1JtwjmlLHWPUAoOUyp3AhqRVfo60BqncpsHwdov2/TLg5I00FxTjUH4hys
    YfUveW3BAoGAEjzWgY8QAURahV9yM+OHmeEwV6bvHw/4ibkK5XirkmmSbQupjJTh
    jW2pOrnXM0xJ4EJ2WnkZLeV3bq0/Bj1OS8HV+fd9Xtk0XxM4takMymSLxO2bwRG1
    HvZly5yJtsfMwz4Sc0N2Sb+DzxsZYQKx1N2ya6ToKyaoyKCroK0jCPk=
    -----END RSA PRIVATE KEY-----"""
)

PUBLIC_KEY = inspect.cleandoc(
    """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwA0cNMjzEm+LPFolbdOA
    cIB6hX7QGqkzVC8L8W5X2qFFDrSbTI9CSifQ3/1A+xYfiZrR4Za2cCvCtIzHxVct
    EAcQSW+IDRjh5vvdGTKgJMtaf3YHeXMk9NAN4Px6McuqaBE2llYt6okICha8MEUR
    9lffa761WkOOWnWAXQFUWxWOxuVnKQOOm1OQ0OiGd+6b81TbSmHDL1QeAMN66tsc
    nR0zFuLfaCRz8yZIsKR1bUPTAUnCB3gaUXIixxDTeSG6XHItb7c/uHJUPtW4lFLi
    DF12JX0GwQvkpYCe3I++fBxC0xcdGwmncKocOLtsuOPswDHH3waxp5KGVDsdx8Po
    8QIDAQAB
    -----END PUBLIC KEY-----"""
)

PRIVATE_SSH_KEY = inspect.cleandoc(
    """-----BEGIN OPENSSH PRIVATE KEY-----
    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
    -----END OPENSSH PRIVATE KEY-----"""
)

PUBLIC_SSH_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDZiKWPoSiWzs+znXBpl3vcq"
    "X41Bxh+usVsKB5yjhj1EPBQDVtH/0BHXxP5DPF8TdnKMNaL51yp33IkNX029o"
    "oJ6fscskKsc7EKRqIddMY/WXkq3fuBdaPVE9+KnAsvHWcXXe9xw5HSmFmZHsa"
    "FBzdcOhyfdHAw3qzJuxdVFQKqIVMm8rGfuCEeT0aydlcTCDfEP5opZY0cxFES"
    "gCCnHEpPG3Tw87jOi0YcmQQVZu0FxTiSuzhETR5AXfq3O6Yw5cy9n958Z54pk"
    "x0n4pCgPps5e7lweXBz3dWOjsqOF64hwaHxKRVe5dDROftsC0TZCLn3vhH+Mb"
    "nN3VxJ6DVEmlHBYOpOC2Xm5J2h1YqSgFTnuYUaRNVpzdP5iJ5p4GngofVUVOq"
    "P+24rUb3dN9twqK6lEENG/0XIY1XQ4H+3c4zPs+Lf7hgJhRaFObw9DHZxJOBI"
    "0BGEQrSsrY//IuEpxy6p+0wDDaoWxWjtTh4iycUpQCVgEl5FR4ewg+tzhTrpW"
    "fqrfNWMvhy9bmbCJ0b3px5cUJ42szQCI7IgCkYBiiJ0iZ+KwYvrGDCtPvIQk0"
    "r3nbV7BTnjjonSUJ8FcLh7AmEQ+oUlIw3d7t4015QboQmXCum2pN71Oy2Y/Je"
    "me6L/3NtAnOYTppgP5wVxFbMYt8N4eLbh2Hf0/m20NpuctT/SDw=="
    " test_open_ssh@example.com"
)
TABLE_NAME: str = "test_table"


def create_dataset(
    classification: bool = True,
    seed: int = 420,
    image: bool = False,
    multiimage: bool = False,
    multihead: bool = False,
    img_size: int = 50,
) -> pd.DataFrame:
    """Creates a random (seeded) dataset for testing."""
    seed_all(seed)

    base_date = datetime.date(2019, 1, 1)
    date_list = [
        base_date - datetime.timedelta(days=x) for x in range(int(DIMS[0] / 3))
    ] * 3
    df_date = pd.DataFrame(date_list, columns=["Date"])
    df_int = pd.DataFrame(np.random.randint(1, 1000, size=DIMS), columns=list("ABCD"))
    df_float = pd.DataFrame(np.random.uniform(0, 1, size=DIMS), columns=list("EFGH"))
    df_str = pd.DataFrame(
        np.random.choice(list(string.ascii_lowercase), size=DIMS).tolist(),
        columns=list("IJKL"),
    )
    df_bool = pd.DataFrame(
        list(np.random.choice([True, False], size=DIMS)), columns=list("MNOP")
    )
    target = pd.DataFrame(list(np.zeros(shape=DIMS[0], dtype=int)), columns=["TARGET"])

    data: pd.DataFrame = pd.concat(
        [df_date, df_int, df_float, df_str, df_bool, target], axis=1
    )

    if classification:
        data.loc[(data.A > 500) & (data.F < 0.5) & (data.D % 2 == 0), "TARGET"] = 1
    else:
        data["TARGET"] = data.E + data.F - (1 / data.B) / np.random.uniform()
    size = img_size if img_size is not None else 50
    if image or multiimage:

        def create_image(x: pd.DataFrame, size: int = size) -> BytesIO:
            def sigmoid(n: pd.Series) -> int:
                return int(255 / (1 + np.exp(-n)))

            # Use column "M" as defining whether the image is grayscale
            R, G, B = sigmoid(x["A"] / 100), sigmoid(x["F"]), sigmoid(x["D"] / 100)
            image = Image.new("RGB", size=(size, size), color=(R, G, B))
            if x["M"]:
                image = ImageOps.grayscale(image)
            temp = BytesIO()
            image.save(temp, format="png")
            return temp

        if image:
            data["image"] = data.apply(create_image, args=[size], axis=1)
        if multiimage:
            data["image1"] = data.apply(create_image, args=[size], axis=1)
            data["image2"] = data.apply(create_image, args=[size], axis=1)
    if multihead:
        data = data.assign(category=list(np.random.choice(["A", "B"], size=len(data))))
    return data


def create_dataset_pii(
    seed: int = 420,
) -> pd.DataFrame:
    """Creates a PII dataset with (seeded) random values for testing."""
    seed_all(seed)

    # Create a list of private identifiers
    df_names = pd.DataFrame(
        np.asarray(range(1, 5001)),
        columns=["name"],
    )
    df_int = pd.DataFrame(
        np.random.randint(1, 1000, size=(5000, 1)), columns=["int_field"]
    ).astype("int")
    df_str = pd.DataFrame(
        np.random.choice(list(string.ascii_lowercase), size=(5000, 1)).tolist(),
        columns=["str_field"],
    ).astype("str")
    df_obj = pd.DataFrame(
        np.random.choice(list(string.ascii_lowercase), size=(5000, 1)).tolist(),
        columns=["obj_field"],
    ).astype("object")

    df_age = pd.DataFrame(np.random.randint(1, 110, size=(5000, 1)), columns=["age"])
    df_height = pd.DataFrame(
        np.random.triangular(left=25, mode=168, right=230, size=(5000, 1)),
        columns=["height"],
    )
    df_weight = pd.DataFrame(
        np.random.triangular(left=1.8, mode=70, right=230, size=(5000, 1)),
        columns=["weight"],
    )

    exercise_choices = [
        "none",
        "run",
        "cycle",
        "swim",
        "row",
        "weights",
        "elliptical",
        "yoga",
        "pilates",
        "sport",
        "other",
    ]
    exercise_priors = [0.2, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
    df_exercise = pd.DataFrame(
        np.random.choice(exercise_choices, size=(5000, 1), p=exercise_priors),
        columns=["exercise"],
    )
    data: pd.DataFrame = pd.concat(
        [df_names, df_age, df_weight, df_height, df_exercise, df_int, df_str, df_obj],
        axis=1,
    )

    return data


def create_datastructure(
    multilabel: bool = False,
    multihead: bool = False,
    multihead_size: int = 1,
    loss_weights: bool = False,
) -> DataStructure:
    """This method creates and returns a DataStructure object."""
    target: Union[str, List[str]] = "TARGET"
    ignore_cols = ["Date"]
    loss_weights_col = None
    multihead_col = None

    if loss_weights:
        loss_weights_col = "weights"

    if multihead:
        multihead_col = "category"

    if multilabel:
        target = [cast(str, target), "TARGET_2"]

    return DataStructure(
        table=TABLE_NAME,
        target=target,
        ignore_cols=ignore_cols,
        multihead_col=multihead_col,
        multihead_size=multihead_size,
        loss_weights_col=loss_weights_col,
    )


def create_query_datastructure(
    multilabel: bool = False,
    multihead: bool = False,
    multihead_size: int = 1,
    loss_weights: bool = False,
) -> DataStructure:
    """This method creates and returns a DataStructure object."""
    target: Union[str, List[str]] = "target"
    loss_weights_col = None
    multihead_col = None
    query = """SELECT dd1."A" as a1, dd1."D" as d1, dd1."M" as m1,
                dd1."N" as n1, dd1."TARGET" as target,
                dd2."A" as a2, dd2."D" as d2, dd2."M" as m2, dd2."N" as n2
                FROM dummy_data dd1, dummy_data_2 dd2
                WHERE dd1."Date" = dd2."Date"
    """
    feature_override: SchemaOverrideMapping = {
        "continuous": ["a1", "d1", "a2", "d2"],
        "categorical": [
            {"m1": {"True": 1, "False": 0}},
            {"n1": {"True": 1, "False": 0}},
            {"m2": {"True": 1, "False": 0}},
            {"n2": {"True": 1, "False": 0}},
            {"target": {"0": 0, "1": 1}},
        ],
    }
    if loss_weights:
        loss_weights_col = "weights"

    if multihead:
        multihead_col = "category"

    if multilabel:
        target = [cast(str, target), "TARGET_2"]

    return DataStructure(
        query=query,
        schema_types_override=feature_override,
        target=target,
        multihead_col=multihead_col,
        multihead_size=multihead_size,
        loss_weights_col=loss_weights_col,
    )


def create_datasource(
    classification: bool,
    multilabel: bool = False,
    multihead: bool = False,
    loss_weights: bool = False,
    image: bool = False,
    multiimage: bool = False,
) -> _BaseSource:
    """This method creates and returns a _BaseSource object."""
    image_col: Optional[List[str]]
    if image:
        data = create_dataset(
            classification=classification, image=image, multihead=multihead
        )
        image_col = ["image"]
    elif multiimage:
        data = create_dataset(
            classification=classification, multiimage=multiimage, multihead=multihead
        )
        image_col = ["image1", "image2"]
    else:
        data = create_dataset(classification=classification, multihead=multihead)
        image_col = None

    if loss_weights:
        data = data.assign(weights=1.0)

    if multihead:
        data = data.assign(category=list(np.random.choice(["A", "B"], size=len(data))))

    if multilabel:
        data = data.assign(TARGET_2=np.zeros(len(data)))
        data.loc[(data.A < 700) & (data.F < 0.5) & (data.D % 2 == 1), "TARGET_2"] = 1

    dataset = DataFrameSource(data, seed=420, image_col=image_col)

    return dataset


def create_datasource_pii() -> _BaseSource:
    """This method creates and returns a PII DataFrameSource dataset."""
    data = create_dataset_pii()

    dataset = DataFrameSource(data, seed=420, image_col=None)

    return dataset


def create_schema(
    classification: bool,
    multilabel: bool = False,
    multihead: bool = False,
    loss_weights: bool = False,
) -> BitfountSchema:
    """Helper function for creating datastructure and datasource."""
    datastructure = create_datastructure(multilabel, multihead, loss_weights)
    datasource = create_datasource(classification, multilabel, multihead, loss_weights)
    schema = BitfountSchema()
    force_stypes = {}
    force_categorical: List[Optional[str]] = []
    if classification:
        force_categorical = _add_this_to_list(datastructure.target, force_categorical)
        if multihead:
            force_categorical = _add_this_to_list(
                datastructure.multihead_col, force_categorical
            )

    if force_categorical:
        force_stypes = {TABLE_NAME: {"categorical": force_categorical}}
    datasource.load_data()
    schema.add_datasource_tables(
        datasource=datasource,
        table_name=TABLE_NAME,
        force_stypes=force_stypes,  # type: ignore[arg-type] # Reason: this will always have the needed type after the ifs. # noqa: B950
    )

    return schema


def create_schema_pii() -> BitfountSchema:
    """Helper function for creating datastructure and datasource for a PII dataset."""
    datasource = create_datasource_pii()
    schema = BitfountSchema()

    datasource.load_data()
    schema.add_datasource_tables(
        datasource=datasource,
        table_name=TABLE_NAME,
        force_stypes=None,
    )

    return schema


def get_datastructure_and_datasource(
    classification: bool,
    multilabel: bool = False,
    multihead: bool = False,
    multihead_size: int = 1,
    loss_weights: bool = False,
) -> Tuple[DataStructure, _BaseSource]:
    """Helper function for creating datastructure and datasource."""
    datastructure = create_datastructure(
        multilabel, multihead, multihead_size, loss_weights
    )
    datasource = create_datasource(classification, multilabel, multihead, loss_weights)
    return datastructure, datasource


def create_local_modeller_and_workers(
    model_name: str,
    protocol_name: str,
    algorithm_name: str,
    secure_aggregation: bool = False,
    early_stopping: bool = False,
    auto_eval: bool = True,
) -> Tuple[_Modeller, List[_Worker]]:
    """Creates a modeller and workers to run in tests."""
    pod_ids = ["Alice/AlicePod", "Bob/BobPod"]
    pod_public_keys = {
        pod_id: create_autospec(RSAPublicKey, instance=True) for pod_id in pod_ids
    }
    results_only: bool = bool(protocol_name == "ResultsOnly")

    # Seed everything for consistency
    seed_all(43)

    # Create default hyperparams
    hyperparams: _StrAnyDict = {
        "epochs": 1,
        "batch_size": 32,
        "optimizer": Optimizer("RAdam", {"lr": 0.001}),
    }

    # Add to hyperparams based on model type
    if "RandomForest" in model_name or "LogisticRegression" in model_name:
        if not results_only:
            raise ValueError(
                "Random Forest and Logistic Regression can only be run with algorithm "
                "ResultsOnly"
            )
        hyperparams = {}

    # Create base data variables
    data = create_dataset(classification=True)
    schema = BitfountSchema()
    pod_datasets = []

    if results_only:
        # ResultsOnly only works with one pod
        pod_ids = ["Alice/AlicePod"]

    # Create datasets for each pod and combine them in the schema
    for _ in pod_ids:
        dataset = DataFrameSource(
            cast(pd.DataFrame, data.sample(n=1000, random_state=random.randint(1, 101)))
        )
        pod_datasets.append(dataset)

        # to make sure modeller schema corresponds to the worker schema
        schema.add_datasource_tables(
            dataset,
            table_name=TABLE_NAME,
            force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
            ignore_cols={TABLE_NAME: ["Date"]},
        )
    data_structure = DataStructure(
        table=TABLE_NAME, target="TARGET", ignore_cols=["Date"]
    )

    # Create local message service object
    mailbox_queues = LocalMessageServiceSharedQueues()
    modeller_name = "modeller-name"
    modeller_mailbox_id = "modeller_mailbox_id"
    # Just use the same key for each as we're running local tests
    aes_encryption_key = b"aes_encryption_key"

    # Handle early stopping
    early_stopping_ = None
    if early_stopping:
        early_stopping_ = FederatedEarlyStopping("validation_loss", 1, 0.01)

    # Create model
    model_class = _MODELS[model_name]
    model = model_class(datastructure=data_structure, schema=schema, **hyperparams)
    # Create algorithm
    algorithm = _ALGORITHMS[AlgorithmType[algorithm_name].name](
        model=model,
        epochs_between_parameter_updates=1,
    )

    # Create protocol
    protocol_kwargs: _StrAnyDict = {}
    if protocol_name == "FederatedAveraging":
        assert isinstance(model, DistributedModelProtocol)
        if secure_aggregation:
            sec_share = SecureShare()
            aggregator: _BaseAggregatorFactory = SecureAggregator(
                secure_share=sec_share
            )
        else:
            aggregator = Aggregator()

        protocol_kwargs = {
            "epochs_between_parameter_updates": 1,
            "aggregator": aggregator,
            "auto_eval": auto_eval,
        }
    protocol = _PROTOCOLS[ProtocolType[protocol_name].name](
        early_stopping=early_stopping_, algorithm=algorithm, **protocol_kwargs
    )

    # Create workers directly
    workers = []
    serialized_protocol = protocol.dump()
    for pod_identifier, dataset in zip(pod_ids, pod_datasets):
        message_service = LocalMessageService(
            username=pod_identifier.split("/")[0],
            shared_queues=mailbox_queues,
            modeller_mailbox_id=modeller_mailbox_id,
            pod_ids=pod_ids,
        )

        worker_mailbox: _WorkerMailbox
        if secure_aggregation:
            worker_mailbox = _InterPodWorkerMailbox(
                pod_identifier=pod_identifier,
                modeller_mailbox_id=modeller_mailbox_id,
                modeller_name=modeller_name,
                aes_encryption_key=aes_encryption_key,
                message_service=message_service,
                pod_mailbox_ids=message_service.worker_mailbox_ids,
                pod_public_keys=pod_public_keys,
                private_key=create_autospec(RSAPrivateKey, instance=True),
            )
        else:
            worker_mailbox = _WorkerMailbox(
                pod_identifier=pod_identifier,
                modeller_mailbox_id=modeller_mailbox_id,
                modeller_name=modeller_name,
                aes_encryption_key=aes_encryption_key,
                message_service=message_service,
                pod_mailbox_ids=message_service.worker_mailbox_ids,
            )

        worker = _Worker(
            datasource=dataset,
            mailbox=worker_mailbox,
            bitfounthub=create_autospec(BitfountHub, instance=True),
            authorisation=_LocalAuthorisation(
                _PodResponseMessage(modeller_name, pod_identifier),
                serialized_protocol,
            ),
            pod_identifier=pod_identifier,
            serialized_protocol=serialized_protocol,
        )
        workers.append(worker)

    # Create modeller
    modeller = _Modeller(
        protocol=protocol,
        message_service=LocalMessageService(
            username=modeller_name,
            shared_queues=mailbox_queues,
            modeller_mailbox_id=modeller_mailbox_id,
            pod_ids=pod_ids,
        ),
        bitfounthub=create_autospec(BitfountHub, instance=True),
        identity_verification_method=IdentityVerificationMethod.KEYS,  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
        private_key=create_autospec(RSAPrivateKey, instance=True),
    )

    return modeller, workers


def assert_results(
    model: _BaseModel,
    test_preds: Optional[np.ndarray] = None,
    test_target: Optional[Union[Sequence[float], Sequence[int]]] = None,
) -> None:
    """Assert results of a fitted model.

    This method takes a fitted model, evaluates it and performs some checks
    on the output.
    """
    if test_preds is None or test_target is None:
        preds, targs = model.evaluate()
        # TODO: [BIT-1604] Remove these assert statements once they become superfluous.
        assert isinstance(preds, np.ndarray)
        assert isinstance(targs, np.ndarray)
    else:
        preds = test_preds
        targs = np.asarray(test_target)
    metrics = MetricCollection.create_from_model(model)
    results = metrics.compute(targs, preds)
    assert results is not None
    assert isinstance(results, dict)
    if isinstance(model, ClassifierMixIn):
        auc = results["AUC"]
        assert auc > AUC_THRESHOLD
        if not model.multilabel and model.n_classes == 2:
            assert len(results) == len(BINARY_CLASSIFICATION_METRICS)
        else:
            assert len(results) == len(MULTICLASS_CLASSIFICATION_METRICS)
    else:
        assert len(results) == len(REGRESSION_METRICS)
        mae = results["MAE"]
        assert mae < MAE_THRESHOLD


class CallArgsLike(Protocol):
    """A protocol that defines a unittest.mock.call_args-like interface."""

    args: List[Any]
    kwargs: _StrAnyDict


def get_arg_from_args_or_kwargs(
    call_args: CallArgsLike, args_idx: int, kwarg_name: str
) -> Any:
    """Retrieves a mock function call argument regardless of how it was passed.

    Will extract a mock function argument regardless of if it was supplied by
    arg or kwarg.

    Args:
        call_args: The result of call_args from a mock call.
        args_idx: The potential position in *args the argument would be, zero-indexed.
        kwarg_name: The potential name in **kwargs of the argument.

    Returns:
        The argument, if found, or None if no argument was found.
    """
    # Check kwargs first as they must be provided after args
    try:
        return call_args.kwargs[kwarg_name]
    except KeyError:
        pass

    # Otherwise check args
    try:
        return call_args.args[args_idx]
    except IndexError:
        pass

    # Otherwise, couldn't be found
    raise ValueError(f'Could not find "{kwarg_name}" argument in call_args')


# caplog helper methods
_LOG_LEVEL_NAMES = Union[
    Literal["DEBUG"],
    Literal["INFO"],
    Literal["WARNING"],
    Literal["ERROR"],
    Literal["CRITICAL"],
]


def get_logs_at_level(
    caplog_fixture: LogCaptureFixture,
    levelname: _LOG_LEVEL_NAMES,
    full_details: bool = False,
) -> str:
    """Returns all logs at a given level as a single string.

    Args:
        caplog_fixture: The caplog fixture to extract from.
        levelname: The name of the log level to retrieve messages of.
        full_details: Whether to extract only the log record message or the full details
                  (timestamp, exception info, etc.). Uses the default formatter
                  to get the full log record output.

    Returns:
         All the log messages at the target level as a newline-joined string.
    """
    level_records = [
        record for record in caplog_fixture.records if record.levelname == levelname
    ]
    # Need to interpolate/format the messages
    if full_details:
        formatter = logging.Formatter()
        level_messages = [formatter.format(r) for r in level_records]
    else:
        level_messages = [r.getMessage() for r in level_records]
    return "\n".join(level_messages)


def get_debug_logs(
    caplog_fixture: LogCaptureFixture, full_details: bool = False
) -> str:
    """Returns all logs at debug level as a single string.

    All the log messages are combined as a newline-joined string.

    See `get_logs_at_level` for more information.
    """
    return get_logs_at_level(caplog_fixture, "DEBUG", full_details)


def get_info_logs(caplog_fixture: LogCaptureFixture, full_details: bool = False) -> str:
    """Returns all logs at info level as a single string.

    All the log messages are combined as a newline-joined string.

    See `get_logs_at_level` for more information.
    """
    return get_logs_at_level(caplog_fixture, "INFO", full_details)


def get_warning_logs(
    caplog_fixture: LogCaptureFixture, full_details: bool = False
) -> str:
    """Returns all logs at warning level as a single string.

    All the log messages are combined as a newline-joined string.

    See `get_logs_at_level` for more information.
    """
    return get_logs_at_level(caplog_fixture, "WARNING", full_details)


def get_error_logs(
    caplog_fixture: LogCaptureFixture, full_details: bool = False
) -> str:
    """Returns all logs at error level as a single string.

    All the log messages are combined as a newline-joined string.

    See `get_logs_at_level` for more information.
    """
    return get_logs_at_level(caplog_fixture, "ERROR", full_details)


def get_critical_logs(
    caplog_fixture: LogCaptureFixture, full_details: bool = False
) -> str:
    """Returns all logs at critical level as a single string.

    All the log messages are combined as a newline-joined string.

    See `get_logs_at_level` for more information.
    """
    return get_logs_at_level(caplog_fixture, "CRITICAL", full_details)
