from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_dashboard.url_names import AlreadyRegistered, url_names
from edc_facility import import_holidays
from edc_model_wrapper import ModelWrapper, ModelWrapperModelError
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_subject_model_wrappers import AppointmentModelWrapper, SubjectVisitModelWrapper

from ..models import Appointment, OnScheduleOne, SubjectVisit
from ..visit_schedule import visit_schedule1


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = "edc_subject_model_wrappers.subjectvisit"


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

    def test_knows_appt_model(self):
        model_obj = Appointment(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_schedule_name="visit_schedule1",
            visit_code="1000",
            schedule_name="schedule1",
            timepoint=0,
        )
        wrapper = AppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    def test_with_visit_model_wrapper_cls_bad2(self):
        """Assert raises if subject visit model is not
        in the Appointment configurations.
        """

        class MyAppSubjectVisitModelWrapper(ModelWrapper):
            model = "myapp.subjectvisit"

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MyAppSubjectVisitModelWrapper
            model = "edc_appointment.appointment"

        model_obj = Appointment(visit_schedule_name="visit_schedule1")
        MyAppointmentModelWrapper(model_obj=model_obj)

    def test_with_visit_model_wrapper_cls_bad3(self):
        """Assert raises if the model is speified and does not
        match the appointment relative to the if subject visit model
        from the Appointment configurations.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper
            model = "myapp.appointment"

        model_obj = Appointment(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_schedule_name="visit_schedule1",
            visit_code="1000",
            schedule_name="schedule1",
        )
        self.assertRaises(
            ModelWrapperModelError, MyAppointmentModelWrapper, model_obj=model_obj
        )

    def test_with_visit_model_wrapper_cls_ok(self):
        """Assert determines appointment model from
        visit model wrapper.
        """

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        model_obj = Appointment(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_schedule_name="visit_schedule1",
            visit_code="1000",
            schedule_name="schedule1",
        )
        wrapper = MyAppointmentModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_appointment.appointment")
        self.assertEqual(wrapper.model_cls, Appointment)

    def test_model_wrapper_forced_rewrap(self):
        """Assert visit model wrapper can be referenced more than once."""

        class MyAppointmentModelWrapper(AppointmentModelWrapper):
            visit_model_wrapper_cls = MySubjectVisitModelWrapper

        subject_identifier = "12345"
        report_datetime = get_utcnow()
        appointment = Appointment.objects.get(
            visit_code="1000",
        )
        subject_visit = SubjectVisit.objects.create(
            subject_identifier=subject_identifier,
            appointment=appointment,
            report_datetime=report_datetime,
            visit_schedule_name="visit_schedule1",
            visit_code="1000",
            schedule_name="schedule1",
        )
        wrapper = MyAppointmentModelWrapper(model_obj=appointment)

        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
        # call again, trigger a forced re-wrap
        self.assertEqual(wrapper.wrapped_visit.object, subject_visit)
