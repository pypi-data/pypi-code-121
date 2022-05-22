from django.db import models


class DeletedStatusQueryset(models.QuerySet):
    def live(self):
        return self.filter(deleted=False)

    def deleted(self):
        return self.filter(deleted=True)

    def not_deleted(self):
        return self.filter(deleted=False)


class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return DeletedStatusQueryset(self.model, using=self._db)

    def live(self):
        return self.get_queryset().live()

    def deleted(self):
        return self.get_queryset().deleted()


class DeletableManager(models.Manager):
    def get_queryset(self):
        return DeletedStatusQueryset(self.model, using=self._db)

    def live(self):
        return self.get_queryset().not_deleted()

    def not_deleted(self):
        return self.get_queryset().not_deleted()

    def deleted(self):
        return self.get_queryset().deleted()
