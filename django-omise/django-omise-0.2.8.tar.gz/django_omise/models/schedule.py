from .base import OmiseBaseModel, OmiseMetadata, OmiseDeletableModel
from .choices import Currency, OccurrenceStatus, ScheduleStatus, SchedulePeriod

from django.utils.translation import gettext_lazy as _

from django.db import models

from django_omise.omise import omise


class Schedule(OmiseBaseModel, OmiseDeletableModel):

    NON_DEFAULT_FIELDS = OmiseBaseModel.NON_DEFAULT_FIELDS + [
        "charges",
    ]

    omise_class = omise.Schedule

    active = models.BooleanField(
        help_text=_("Whether schedule is status running or expiring.")
    )

    charge = models.OneToOneField(
        "django_omise.ChargeSchedule",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    end_on = models.DateField(
        blank=True,
        help_text=_("End date of schedule in ISO 8601 format."),
    )

    ended_at = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Actual end date of schedule in ISO 8601 format."),
    )

    every = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_(
            "How often schedule should run when applied to period. For example, if set to 3 and period is set to week, schedule should run every 3 weeks."
        ),
    )
    in_words = models.TextField(blank=True)
    next_occurrences_on = models.JSONField(blank=True, default=list)

    # Todo # on = models.SomeField
    period = models.CharField(max_length=5, choices=SchedulePeriod.choices, blank=True)

    start_on = models.DateField(
        help_text=_("Start date of schedule in ISO 8601 format.")
    )

    status = models.CharField(
        max_length=50,
        choices=ScheduleStatus.choices,
    )

    # Todo # transfer = models.ForeignKey("django_omise.Transfer")


class Occurrence(OmiseBaseModel):

    message = models.CharField(max_length=255, blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    # Todo # result = models.ForeignKey('django_omise.Result')

    retry_on = models.DateField(blank=True, null=True)

    schedule = models.ForeignKey(
        "django_omise.Schedule", on_delete=models.PROTECT, related_name="occurrences"
    )

    schduled_on = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=OccurrenceStatus.choices)


class ChargeSchedule(OmiseBaseModel, OmiseMetadata):

    amount = models.IntegerField(
        help_text="Refund amount in smallest unit of charge currency.",
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    card = models.ForeignKey(
        "django_omise.Card",
        on_delete=models.PROTECT,
        related_name="charge_schedules",
        blank=True,
        null=True,
    )

    customer = models.ForeignKey(
        "django_omise.Customer",
        on_delete=models.PROTECT,
        related_name="charge_schedules",
    )

    default_card = models.BooleanField()

    description = models.TextField(blank=True)

    @property
    def human_amount(self) -> float:
        if not self.pk:
            return 0
        if self.currency == Currency.JPY:
            return f"{self.amount:,.2f}"
        return f"{self.amount / 100:,.2f}"
