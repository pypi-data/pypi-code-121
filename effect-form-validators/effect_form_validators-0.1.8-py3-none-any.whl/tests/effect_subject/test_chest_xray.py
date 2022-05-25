from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_mock_queries.query import MockModel, MockSet
from edc_constants.constants import NO, NORMAL, OTHER, YES
from edc_utils import get_utcnow

from effect_form_validators.effect_subject import ChestXrayFormValidator as Base

from ..mixins import FormValidatorTestMixin, TestCaseMixin


class ChestXrayFormValidator(FormValidatorTestMixin, Base):
    @property
    def consent_datetime(self) -> datetime:
        return get_utcnow() - relativedelta(years=1)

    @property
    def previous_chest_xray_date(self):
        return (get_utcnow() - relativedelta(years=1)).date()


class TestChestXrayFormValidation(TestCaseMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        # signs_and_symptoms
        self.signs_and_symptoms = MockModel(
            mock_name="SignsAndSymptoms",
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
            xray_performed=YES,
        )
        self.xray_result_other = MockModel(
            mock_name="XrayResults", name=OTHER, display_name=OTHER
        )
        self.xray_result_normal = MockModel(
            mock_name="XrayResults", name=NORMAL, display_name=NORMAL
        )
        # set for reverse lookup
        self.subject_visit.signsandsymptoms = self.signs_and_symptoms

    def get_cleaned_data(self, **kwargs) -> dict:
        cleaned_data = super().get_cleaned_data(**kwargs)
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=MockSet(self.xray_result_normal),
            chest_xray_results_other=None,
        )
        return cleaned_data

    def test_chest_xray_ok(self):
        self.subject_visit.signsandsymptoms.xray_performed = YES
        form_validator = ChestXrayFormValidator(cleaned_data=self.get_cleaned_data())
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_no_chest_xray_raises(self):
        self.subject_visit.signsandsymptoms.xray_performed = NO
        form_validator = ChestXrayFormValidator(cleaned_data=self.get_cleaned_data())
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray", cm.exception.error_dict)

    def test_no_chest_xray_ok(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = NO
        cleaned_data.update(
            chest_xray=NO,
            chest_xray_date=None,
            chest_xray_results=None,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_chest_xray_other_field_not_expected_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=MockSet(self.xray_result_normal),
            chest_xray_results_other="blah",
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_results_other", cm.exception.error_dict)

    def test_chest_xray_other_field_expected_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=MockSet(self.xray_result_other),
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_results_other", cm.exception.error_dict)

    def test_chest_xray_other_field_expected_ok(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=MockSet(self.xray_result_other),
            chest_xray_results_other="blah",
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_chest_xray_expects_date_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=None,
            chest_xray_results=None,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_date", cm.exception.error_dict)

    def test_chest_xray_expects_chest_xray_results_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=None,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_results", cm.exception.error_dict)

    def test_chest_xray_not_performed_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = NO
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=None,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray", cm.exception.error_dict)

    def test_no_chest_xray_with_date_raises(self):
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = NO
        cleaned_data.update(
            chest_xray=NO,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=None,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_date", cm.exception.error_dict)

    def test_cannot_have_other_results_with_normal(self):
        xray_results = MockSet(self.xray_result_normal, self.xray_result_other)
        cleaned_data = self.get_cleaned_data()
        self.subject_visit.signsandsymptoms.xray_performed = YES
        cleaned_data.update(
            chest_xray=YES,
            chest_xray_date=self.subject_visit.report_datetime.date(),
            chest_xray_results=xray_results,
            chest_xray_results_other=None,
        )
        form_validator = ChestXrayFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("chest_xray_results", cm.exception.error_dict)
        self.assertIn(
            "Invalid combination",
            str(cm.exception.error_dict.get("chest_xray_results")),
        )
