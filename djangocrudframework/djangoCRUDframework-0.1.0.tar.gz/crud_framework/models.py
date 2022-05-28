from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class BaseChoices:
    @classmethod
    def get_choices(cls):
        res = []
        for k, v in cls.__dict__.items():
            if k not in ['__module__', '__dict__', '__weakref__', '__doc__']:
                res.append((v, v))
        return res


class BaseManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.getter_model = kwargs.pop('getter_model', ValueError('model is required'))
        super(BaseManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return self.getter_model.objects.get_queryset()


# TODO handle errors
# TODO Soft delete model
class BaseModel(models.Model):
    class Meta:
        abstract = True


class BaseTrackedModel(BaseModel):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(null=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, auto_now=True)
    is_deleted = models.BooleanField(default=False, null=False, blank=True)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='%(class)s_editor_user')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='%(class)s_creator_user')

    def __init__(self, *args, **kwargs):
        super(BaseTrackedModel, self).__init__(*args, **kwargs)
        # todo update editor


class BaseHistoryModel(BaseTrackedModel):
    class Meta:
        abstract = True

    history = HistoricalRecords(inherit=True, related_name='log')
