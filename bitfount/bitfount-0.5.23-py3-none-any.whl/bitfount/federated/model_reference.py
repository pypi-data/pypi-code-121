"""References to custom models."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Optional, Type, Union, cast

from marshmallow import fields

from bitfount.data.datastructure import DataStructure
from bitfount.data.datastructure import registry as datastructure_registry
from bitfount.data.schema import BitfountSchema
from bitfount.federated.logging import _get_federated_logger
from bitfount.hub.helper import _default_bitfounthub
from bitfount.models.base_models import _BaseModelRegistryMixIn
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _BaseSerializableObjectMixIn,
    _StrAnyDict,
)
from bitfount.utils import _get_non_abstract_classes_from_module

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub
    from bitfount.models.bitfount_model import BitfountModel

logger = _get_federated_logger(__name__)


class BitfountModelReference(_BaseModelRegistryMixIn, _BaseSerializableObjectMixIn):
    """Describes a local or remote reference to a `BitfountModel` class.

    Args:
        model_ref: Either path to model file or name of model on hub.
        datastructure: `DataStructure` to be passed to the model when initialised.
        schema: `BitfountSchema` to be passed to the model when initialised.
        username: The username of the model owner. Defaults to bitfount session username
            if not provided.
        hub: Required for upload/download of model. This attribute is set after
            initialisation on the worker side as the hub is not serialized. Defaults to
            None.
        hyperparameters: Hyperparameters to be passed to the model constructor after it
            has been loaded from file or hub. Defaults to None.

    Raises:
        ValueError: If `username` is not provided and `hub` is not provided.

    :::tip

    To use another user's custom model, simply provide that user's username instead of
    your own (along with the name of the model as the `model_ref` argument).

    :::
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_ref": fields.Method(
            serialize="get_model_ref", deserialize="load_model_ref"
        ),
        # The hub should not be serialized but can be deserialized if provided
        "hub": fields.Raw(allow_none=True, load_only=True),
        "username": fields.Str(allow_none=True),
        "hyperparameters": fields.Dict(keys=fields.Str()),
        "schema": fields.Nested(BitfountSchema._Schema),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"datastructure": datastructure_registry}

    def __init__(
        self,
        model_ref: Union[Path, str],
        datastructure: DataStructure,
        schema: Optional[BitfountSchema] = None,
        username: Optional[str] = None,
        hub: Optional[BitfountHub] = None,
        hyperparameters: Optional[_StrAnyDict] = None,
    ):
        self.class_name = type(self).__name__
        self.model_ref = model_ref
        self.datastructure = datastructure
        self.schema = schema if schema else BitfountSchema()
        self.hub = _default_bitfounthub(hub, username=username)
        self.hyperparameters = hyperparameters if hyperparameters is not None else {}
        self.username = username or self.hub.username

    def _get_model_from_path(self) -> Type[BitfountModel]:
        """Returns model class from path.

        Returns:
            The model class.
        """
        self.model_ref = cast(Path, self.model_ref)
        return _get_non_abstract_classes_from_module(self.model_ref)[
            self.model_ref.stem
        ]

    def _upload_model_to_hub(self) -> None:
        """Uploads model to hub under the logged-in user's account."""
        # model_ref is path to model code file
        self.model_ref = cast(Path, self.model_ref)
        model_sent_status = self.hub.send_model(self.model_ref)
        if not model_sent_status:
            raise ValueError(
                "Could not send model to Hub. Please address issues and try again"
            )

    def _get_model_from_hub(self) -> Type[BitfountModel]:
        """Returns model class from hub from user denoted by `self.username`.

        Returns:
            The model class.
        """
        # model_ref is the name of a model on the hub
        self.model_ref = cast(str, self.model_ref)
        model_cls = self.hub.get_model(self.username, self.model_ref)

        # Check that the model has been retrieved correctly
        if not model_cls:
            raise ValueError(
                "Unable to retrieve model from hub, check logs for details."
            )
        return model_cls

    def get_model(self) -> Type[BitfountModel]:
        """Gets the model referenced.

        If the model is a Path to a `BitfountModel`, it will upload it to BitfountHub
        and return the model class. If it is a name of a model on the hub, it will
        download the model from the hub and return the model class.

        Returns:
            The model class.

        Raises:
            TypeError: If the model is not a Path or a string.
            TypeError: If the model does not implement `DistributedModelProtocol`.
            ValueError: If a `BitfountHub` instance has not been provided or if there
                was a communication error with the hub.
        """
        if isinstance(self.model_ref, Path):
            model_cls = self._get_model_from_path()

            # Check that chosen model is compatible with federation by checking if it
            # implements `DistributedModelProtocol`. The only way to do this is to
            # instantiate the model and perform an `isinstance` check.
            model = model_cls(
                datastructure=self.datastructure,
                schema=self.schema,
                **self.hyperparameters,
            )
            if not isinstance(model, DistributedModelProtocol):
                raise TypeError(
                    f"Model {self.model_ref.stem} does not implement "
                    f"DistributedModelProtocol."
                )

            self._upload_model_to_hub()

            # self.model_ref is set to the name of the model so that the model doesn't
            # get unnecessarily re-uploaded if `get_model` is called multiple times
            self.model_ref = self.model_ref.stem
        elif isinstance(self.model_ref, str):
            model_cls = self._get_model_from_hub()
        else:
            raise TypeError(f"Model of type {type(self.model_ref)} not recognised.")

        return model_cls
