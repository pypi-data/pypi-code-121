from datetime import datetime
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django_mock_queries.query import MockModel
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY01


class FormValidatorTestMixin:

    consent_model = None

    def get_consent_for_period_or_raise(self, *args) -> Any:
        pass

    def validate_crf_report_datetime(self):
        pass

    def validate_appt_datetime_in_window_period(self: Any, appointment, *args) -> None:
        pass

    def validate_visit_datetime_in_window_period(self: Any, *args) -> None:
        pass

    def validate_crf_datetime_in_window_period(self: Any, *args) -> None:
        pass

    def datetime_in_window_or_raise(self, *args):
        pass


class TestCaseMixin(TestCase):
    def setUp(self) -> None:
        """Setup appointment and subject_visit Mock models"""
        self.consent_datetime = get_utcnow() - relativedelta(years=1)
        # appointment
        self.appointment = MockModel(
            mock_name="Appointment",
            appt_datetime=self.consent_datetime,
            visit_code=DAY01,
            visit_code_sequence=0,
        )

        # subject_visit
        self.subject_visit = MockModel(
            mock_name="SubjectVisit",
            report_datetime=self.consent_datetime,
            visit_code=DAY01,
            visit_code_sequence=0,
            appointment=self.appointment,
            signsandsymptoms=None,
        )

    def get_cleaned_data(
        self,
        visit_code: Optional[str] = None,
        report_datetime: Optional[datetime] = None,
        visit_code_sequence: Optional[int] = None,
    ) -> dict:
        """Returns dict of subject_visit and report_datetime.

        Updates visit_code and report_datetime if provided.
        """
        visit_code = visit_code or DAY01
        visit_code_sequence = visit_code_sequence or 0
        report_datetime = report_datetime or self.consent_datetime
        self.appointment.visit_code = visit_code
        self.appointment.visit_code_sequence = visit_code_sequence
        self.appointment.report_datetime = report_datetime
        self.subject_visit.appointment = self.appointment
        self.subject_visit.visit_code = visit_code
        self.subject_visit.visit_code_sequence = visit_code_sequence
        self.subject_visit.report_datetime = report_datetime
        return dict(
            subject_visit=self.subject_visit,
            report_datetime=report_datetime,
        )
