class BDRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read bydesign models go to bd.
        """
        if model._meta.app_label == 'bydesign':
            return 'bd'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write bydesign models go to 'bd'.
        """
        if model._meta.app_label == 'bydesign':
            return 'bd'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both are in the bydesign app, but not if only one is.
        """
        if obj1._meta.app_label == 'bydesign' and obj2._meta.app_label == 'bydesign':
            return True
        if obj1._meta.app_label == 'bydesign' or obj2._meta.app_label == 'bydesign':
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        No migrations on the bd database.
        """
        if db == 'bd':
            return False
        return None
