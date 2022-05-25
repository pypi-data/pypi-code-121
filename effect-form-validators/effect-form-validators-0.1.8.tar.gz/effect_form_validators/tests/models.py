from django.db import models
from edc_list_data.model_mixins import ListModelMixin


class MyList(ListModelMixin, models.Model):
    class Meta:
        pass
