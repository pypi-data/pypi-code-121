from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_dashboard.url_names import AlreadyRegistered, url_names
from edc_facility import import_holidays
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules

from edc_subject_model_wrappers import SubjectVisitModelWrapper

from ..models import Appointment, OnScheduleOne, SubjectVisit
from ..visit_schedule import visit_schedule1


class TestModelWrapper(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        try:
            url_names.register(
                "subject_dashboard_url",
                "subject_dashboard_url",
                "edc_subject_model_wrapper",
            )
        except AlreadyRegistered:
            pass

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

        self.subject_identifier = "12345"

        onschedule_datetime = get_utcnow() - relativedelta(years=1)

        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            registration_datetime=onschedule_datetime,
        )

        OnScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )

    def test_(self):
        model_obj = SubjectVisit(report_datetime=get_utcnow())
        wrapper = SubjectVisitModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_subject_model_wrappers.subjectvisit")
        self.assertEqual(wrapper.model_cls, SubjectVisit)

    def test_knows_appointment(self):
        appointment = Appointment.objects.get(visit_code="1000")
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow()
        )
        wrapper = SubjectVisitModelWrapper(model_obj=subject_visit)
        self.assertEqual(str(appointment.id), wrapper.appointment)
