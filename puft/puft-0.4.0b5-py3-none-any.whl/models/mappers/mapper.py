from __future__ import annotations
from typing import TYPE_CHECKING

from warepy import log, Singleton, format_message
from flask_sqlalchemy import SQLAlchemy

from ..services.database import native_db


class Mapper(Singleton):
    """Represents database table data manipulations. Abstracted to only contain classmethods.

    Contain class variable `params` which can be assigned during program assembling individually for each children."""
    model = native_db.Model 

    @classmethod
    @log.catch
    def set_orm_model(cls, model: SQLAlchemy.Model) -> None:
        """Set mapper's orm model attribute to work with."""
        cls.model = model

    @classmethod
    @log.catch
    def filter_first(cls, **kwargs) -> SQLAlchemy.Model:
        """Filter first ORM mapped model by given kwargs and return it.
        
        Raise:
            ValueError: if there is no such ORM model in database matched given kwargs."""
        model = cls.model.query.filter_by(**kwargs).first()
        if model is None:
            error_message = format_message("There is no model {} with such parameters: {}", [cls.model, kwargs])            
            raise ValueError(error_message)
        else:
            return model

    @classmethod
    @log.catch
    def filter_all(cls, order_by: str | None = None, descending_order: bool = False, **kwargs) -> list[SQLAlchemy.Model]:
        """Filter all ORM mapped models by given kwargs and return them.

        It's possible to send argument `order_by` to order resulting instance. It should be string referencing to target object attribute.
        For example, if you want to order `Food` by `order` attribute:
        ```
            Food.filter_all(order_by="price", shop_id=12)  # Filter all food for Shop with id 12 and order them.
        ```
        Also you can append `descending_order=True` to apply descending ordering.
        
        Raise:
            ValueError: If there is no such ORM models in database matched given kwargs.
            ValuerError: If there is no such attribute to order by (wrong string given to argument `order_by`)."""
        if order_by is not None:
            # Calculate order target.
            order_target = None
            if order_by not in cls.model.__dict__:
                error_message = format_message("No such attribute in ORM model {}, matched given order argument: {}", [cls.model, order_by])
                raise ValueError(error_message)
            # Also consider asc/desc order.
            if descending_order:
                exec(f"order_target = cls.model.{order_by}.desc()")
            else:
                exec(f"order_target = cls.model.{order_by}")
            models = cls.model.query.filter_by(**kwargs).order_by(order_target).all()
        else:
            models = cls.model.query.filter_by(**kwargs).all()

        if not models:
            error_message = format_message("There is no model {} with such parameters: {}", [cls.model, kwargs])            
            raise ValueError(error_message)
        else:
            return models