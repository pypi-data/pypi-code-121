from edc_model.models import BaseUuidModel

from edc_he.model_mixins import HealthEconomicsEducationModelMixin


class HealthEconomics(HealthEconomicsEducationModelMixin, BaseUuidModel):
    class Meta:
        pass
