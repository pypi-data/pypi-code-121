from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import FEMALE, NEG, NO, NOT_APPLICABLE, POS, YES
from edc_form_validators import FormValidatorTestCaseMixin
from edc_utils import get_utcnow, get_utcnow_as_date

from effect_form_validators.effect_screening import (
    SubjectScreeningFormValidator as Base,
)
from effect_form_validators.tests.mixins import FormValidatorTestMixin, TestCaseMixin


class SubjectScreeningFormValidator(FormValidatorTestMixin, Base):
    pass


class TestSubjectScreeningForm(FormValidatorTestCaseMixin, TestCaseMixin, TestCase):

    form_validator_default_form_cls = SubjectScreeningFormValidator
    ELIGIBLE_CD4_VALUE = 99

    def get_cleaned_data(self, **kwargs) -> dict:
        return {
            "report_datetime": get_utcnow(),
            "initials": "EW",
            "gender": FEMALE,
            "age_in_years": 25,
            "hiv_pos": YES,
            "hiv_dx_ago": "",
            "hiv_dx_date": get_utcnow_as_date() - relativedelta(days=30),
            "cd4_value": self.ELIGIBLE_CD4_VALUE,
            "cd4_date": get_utcnow_as_date() - relativedelta(days=7),
            "serum_crag_value": POS,
            "serum_crag_date": get_utcnow_as_date() - relativedelta(days=6),
            "lp_done": YES,
            "lp_date": get_utcnow_as_date() - relativedelta(days=6),
            "lp_declined": NOT_APPLICABLE,
            "csf_crag_value": NEG,
            "cm_in_csf": NO,
            "cm_in_csf_date": None,
            "cm_in_csf_method:": NOT_APPLICABLE,
            "cm_in_csf_method_other": "",
            "prior_cm_episode": NO,
            "reaction_to_study_drugs": NO,
            "on_flucon": NO,
            "contraindicated_meds": NO,
            "mg_severe_headache": NO,
            "mg_headache_nuchal_rigidity": NO,
            "mg_headache_vomiting": NO,
            "mg_seizures": NO,
            "mg_gcs_lt_15": NO,
            "any_other_mg_ssx": NO,
            "any_other_mg_ssx_other": "",
            "jaundice": NO,
            "pregnant": NOT_APPLICABLE,
            "preg_test_date": None,
            "breast_feeding": NO,
            "willing_to_participate": YES,
            "consent_ability": YES,
            "unsuitable_for_study": NO,
            "reasons_unsuitable": "",
            "unsuitable_agreed": NOT_APPLICABLE,
        }

    def test_cleaned_data_ok(self):
        cleaned_data = self.get_cleaned_data()
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_date_or_date_ago_required_if_hiv_pos_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "",
                "hiv_dx_date": None,
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("hiv_dx_date", cm.exception.error_dict)
        self.assertEqual(
            {"hiv_dx_date": ["This field is required (or the above)."]},
            cm.exception.message_dict,
        )

    def test_hiv_dx_date_ok_if_hiv_pos_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "",
                "hiv_dx_date": cleaned_data.get("cd4_date"),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_hiv_dx_ago_ok_if_hiv_pos_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "1y3m",
                "hiv_dx_date": None,
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_hiv_dx_date_not_required_if_hiv_pos_no(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": NO,
                "hiv_dx_ago": "",
                "hiv_dx_date": get_utcnow_as_date(),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("hiv_dx_date", cm.exception.error_dict)
        self.assertEqual(
            {"hiv_dx_date": ["This field is not required."]},
            cm.exception.message_dict,
        )

    def test_hiv_dx_ago_not_required_if_hiv_pos_no(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": NO,
                "hiv_dx_ago": "1y",
                "hiv_dx_date": None,
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("hiv_dx_ago", cm.exception.error_dict)
        self.assertEqual(
            {"hiv_dx_ago": ["This field is not required."]},
            cm.exception.message_dict,
        )

    def test_both_hiv_dx_ago_and_hiv_dx_date_raises(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "1y",
                "hiv_dx_date": get_utcnow_as_date() - relativedelta(days=30),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("hiv_dx_ago", cm.exception.error_dict)
        self.assertEqual(
            {
                "hiv_dx_ago": [
                    "Date conflict. Do not provide a response "
                    "here if the exact HIV diagnosis date is available."
                ]
            },
            cm.exception.message_dict,
        )

    def test_cd4_date_after_hiv_dx_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "",
                "hiv_dx_date": get_utcnow_as_date() - relativedelta(days=30),
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=7),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cd4_date_after_hiv_dx_ago_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "1m",
                "hiv_dx_date": None,
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=7),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cd4_date_on_hiv_dx_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "",
                "hiv_dx_date": get_utcnow_as_date() - relativedelta(days=7),
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=7),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cd4_date_on_hiv_dx_ago_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "7d",
                "hiv_dx_date": None,
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=7),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cd4_date_before_hiv_dx_date_raises(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "",
                "hiv_dx_date": get_utcnow_as_date() - relativedelta(days=7),
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=8),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cd4_date", cm.exception.error_dict)
        self.assertEqual(
            {
                "cd4_date": [
                    "Invalid. Most recent CD4 count date cannot be before HIV diagnosis."
                ]
            },
            cm.exception.message_dict,
        )

    def test_cd4_date_before_hiv_ago_raises(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "hiv_pos": YES,
                "hiv_dx_ago": "7d",
                "hiv_dx_date": None,
                "cd4_value": self.ELIGIBLE_CD4_VALUE,
                "cd4_date": get_utcnow_as_date() - relativedelta(days=8),
            }
        )
        form_validator = SubjectScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cd4_date", cm.exception.error_dict)
        self.assertEqual(
            {
                "cd4_date": [
                    "Invalid. Most recent CD4 count date cannot be before HIV diagnosis."
                ]
            },
            cm.exception.message_dict,
        )
