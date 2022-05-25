from datetime import date

from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_crf.crf_model_mixin import CrfModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelManager, OffstudyModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import (
    OffScheduleModelMixin,
    OnScheduleModelMixin,
    VisitCodeFieldsModelMixin,
)
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)
from edc_visit_tracking.models import SubjectVisitMissedReasons

from edc_appointment.models import Appointment


class Panel(ListModelMixin):
    class Meta:
        pass


class SubjectVisit(
    VisitModelMixin,
    ReferenceModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    RequiresConsentFieldsModelMixin,
    BaseUuidModel,
):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=PROTECT,  # related_name="test_visit_schedule_appointment"
    )

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)


class SubjectRequisition(
    NonUniqueSubjectIdentifierFieldMixin, VisitCodeFieldsModelMixin, BaseUuidModel
):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT, related_name="+")

    panel = models.ForeignKey(Panel, on_delete=PROTECT)

    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisitMissed(SubjectVisitMissedModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="missed_reasons"
    )

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"


class SubjectConsent(
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class SubjectOffstudy2(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class SubjectOffstudyFive(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class SubjectOffstudySix(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class SubjectOffstudySeven(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class DeathReport(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


# visit_schedule


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleOne(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleTwo(OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleThree(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleThree(OffScheduleModelMixin, BaseUuidModel):
    pass


class CrfOne(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfTwo(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfThree(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfFour(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfFive(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)
