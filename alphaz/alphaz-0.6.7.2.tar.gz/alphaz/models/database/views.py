import inspect

from flask_admin.contrib.sqla import ModelView

from core import core

db = core.db

from . import main_definitions as defs
from . import users_definitions as users_defs

for definitions in [defs, users_defs]:
    db_classes_names = [
        m[0]
        for m in inspect.getmembers(definitions, inspect.isclass)
        if m[1].__module__ == definitions.__name__
    ]

    view_config = {}

    views = []
    for db_classe_name in db_classes_names:
        if not db_classe_name in view_config:
            class_object = getattr(definitions, db_classe_name)
            if "__tablename__" in class_object.__dict__:
                base_name = "ALPHA"
                name = "%s:%s" % (base_name, class_object.__tablename__)
                views.append(
                    ModelView(
                        class_object,
                        db.session,
                        name=class_object.__tablename__,
                        category=base_name,
                        endpoint=name,
                    )
                )

