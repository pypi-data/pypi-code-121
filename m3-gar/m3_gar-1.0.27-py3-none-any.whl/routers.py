from m3_gar.config import (
    DATABASE_ALIAS,
)


class GARRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'm3_gar':
            return DATABASE_ALIAS

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'm3_gar':
            return DATABASE_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        """
        Разрешить связи из других бд к таблицам ГАР
        но запретить ссылаться из бд ГАР в другие БД
        """

        if obj1._meta.app_label == 'm3_gar' and obj2._meta.app_label == 'm3_gar':
            return True

    def allow_migrate(self, db, app_label, **hints):
        """Разрешить синхронизацию моделей в базе ГАР"""
        if app_label == 'm3_gar':
            return db == DATABASE_ALIAS
        elif db == DATABASE_ALIAS:
            return False
