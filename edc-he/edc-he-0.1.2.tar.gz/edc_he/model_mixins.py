from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_constants.choices import YES_NO_NA
from edc_model.models import OtherCharField

from .choices import EDUCATION_CERTIFICATES_CHOICES


class HealthEconomicsEducationModelMixin(models.Model):
    education_in_years = models.IntegerField(
        verbose_name="How many years of education did you complete?",
        validators=[MinValueValidator(0), MaxValueValidator(30)],
    )

    education_certificate = models.CharField(
        verbose_name="What is your highest education certificate?",
        max_length=50,
        choices=EDUCATION_CERTIFICATES_CHOICES,
        null=True,
        blank=False,
    )

    education_certificate_other = OtherCharField()

    education_certificate_tertiary = models.CharField(
        verbose_name=(
            "If your highest education certificate above is "
            "`Tertiary`, what type of tertiary certificate?"
        ),
        max_length=50,
        null=True,
        blank=True,
    )

    primary_school = models.CharField(
        verbose_name="Did you go to primary/elementary school?",
        max_length=15,
        choices=YES_NO_NA,
    )

    primary_school_in_years = models.IntegerField(
        verbose_name="If YES, for how many years",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
    )

    secondary_school = models.CharField(
        verbose_name="Did you go to secondary school?", max_length=15, choices=YES_NO_NA
    )

    secondary_school_in_years = models.IntegerField(
        verbose_name="If YES, for how many years",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
    )

    higher_education = models.CharField(
        verbose_name="Did you go to higher education?", max_length=15, choices=YES_NO_NA
    )

    higher_education_in_years = models.IntegerField(
        verbose_name="If YES, for how many years",
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
