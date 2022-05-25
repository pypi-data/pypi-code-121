from django.db import models
from django.db.models.deletion import CASCADE
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow

from edc_reportable.choices import REPORTABLE
from edc_reportable.units import GRAMS_PER_DECILITER


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)


class SpecimenResult(BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=CASCADE)

    report_datetime = models.DateTimeField(default=get_utcnow)

    haemoglobin = models.DecimalField(decimal_places=1, max_digits=6, null=True, blank=True)

    haemoglobin_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    haemoglobin_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    haemoglobin_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade III " "or above?",
        max_length=25,
        choices=YES_NO_NA,
    )

    @property
    def abnormal(self):
        return self.results_abnormal

    @property
    def reportable(self):
        return self.results_reportable
