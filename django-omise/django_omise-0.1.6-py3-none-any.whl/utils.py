from __future__ import annotations

import omise

from django.apps import apps
from django.conf import settings

from typing import Optional, Any, TYPE_CHECKING, List

if TYPE_CHECKING:
    from django.db import models
    from django_omise.models.base import OmiseBaseModel


def get_payment_methods_for_form() -> List[str]:
    """
    Get the payment method as per setting for checkout form

    :returns: List of payment methods by setting OMISE_PAYMENT_METHODS or default to credit card only.
    """
    payment_methods = get_payment_methods()
    if "card" in payment_methods:
        payment_methods += ["old_card", "new_card"]

    return payment_methods


def get_payment_methods() -> List[str]:
    """
    Get the payment method as per setting

    :returns: List of payment methods by setting OMISE_PAYMENT_METHODS or default to credit card only.
    """
    payment_methods = setting("OMISE_PAYMENT_METHODS", ["card"])
    return payment_methods


def get_payment_methods_by_country(country: Optional[str] = None) -> List[str]:
    """
    Get the payment methods supported by country

    :param country: 3-digit country code.

    :returns: List of supported payment methods
    """
    payment_methods = [
        "card",
    ]

    if country is None:
        country = setting("OMISE_COUNTRY", "THA")

    if country in ["THA", "JPN"]:
        payment_methods.append("internet_banking")

    return payment_methods


def setting(name: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it will return a default.

    :param name: Name of setting
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return getattr(settings, name, default)


def is_omise_object_instances(value) -> bool:
    """
    Check if a value is an instance of Omise Classes.

    See all the classes here https://github.com/omise/omise-python/blob/master/omise/__init__.py

    :param value: The value to check.

    :returns: True if value is an instance of Omise Classes, False otherwise
    """
    return isinstance(
        value,
        (
            omise.Account,
            omise.Balance,
            omise.BankAccount,
            omise.Capability,
            omise.Card,
            omise.Chain,
            omise.Charge,
            omise.Collection,
            omise.Customer,
            omise.Dispute,
            omise.Document,
            omise.Event,
            omise.Forex,
            omise.Link,
            omise.Occurrence,
            omise.Receipt,
            omise.Recipient,
            omise.Refund,
            omise.Search,
            omise.Schedule,
            omise.Source,
            omise.Token,
            omise.Transaction,
            omise.Transfer,
        ),
    )


def update_or_create_from_omise_object(
    omise_object: omise.Base, raise_if_not_implemented: bool = False
) -> models.Model:
    """
    Update or create a new Django object from Omise object.

    :param omise_object: Any of the Omise object.
    :param raise_if_not_implemented: Whether to raise error if there is no model for Omise object. Default is False.

    :returns: The corresponding model instance.
    """
    model = get_model_from_omise_object(
        omise_object=omise_object, raise_if_not_implemented=raise_if_not_implemented
    )

    if model is None:
        return None

    new_object = model.update_or_create_from_omise_object(omise_object=omise_object)
    return new_object


def get_model_from_omise_object(
    omise_object: omise.Base,
    raise_if_not_implemented: bool = False,
) -> OmiseBaseModel:
    """
    Get the model of the django_omise app with a given Omise object.

    :param omise_object: Any of the Omise object.
    :param raise_if_not_implemented: Whether to raise error if there is no model for Omise object. Default is False.

    :returns: The corresponding model class.
    """
    app_label = "django_omise"
    model_map = {
        omise.Card: get_current_app_model(model_name="Card"),
        omise.Customer: get_current_app_model(model_name="Customer"),
        omise.Charge: get_current_app_model(model_name="Charge"),
        omise.Source: get_current_app_model(model_name="Source"),
        omise.Event: get_current_app_model(model_name="Event"),
        omise.Refund: get_current_app_model(model_name="Refund"),
    }

    if raise_if_not_implemented and type(omise_object) not in model_map:
        raise ValueError(
            f"The object {str(type(omise_object))} has not been implemented"
        )

    return model_map.get(type(omise_object), None)


def get_current_app_model(model_name: str) -> models.Model:
    """
    Get the model of the django_omise app with a given model name.

    :param model_name str: The model name.

    :returns: The corresponding model class.
    """
    app_label = "django_omise"
    return apps.get_model(app_label=app_label, model_name=model_name)
