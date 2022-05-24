from datetime import timedelta

from django import forms
from django.test import TestCase
from edc_constants.constants import NO, NOT_APPLICABLE, UNKNOWN, YES
from edc_form_validators import FormValidatorTestCaseMixin
from edc_utils import get_utcnow, get_utcnow_as_date

from effect_form_validators.effect_prn import HospitalizationFormValidator as Base
from effect_form_validators.tests.mixins import FormValidatorTestMixin, TestCaseMixin


class HospitalizationFormValidator(FormValidatorTestMixin, Base):
    pass


class TestHospitalizationFormValidation(FormValidatorTestCaseMixin, TestCaseMixin, TestCase):

    form_validator_default_form_cls = HospitalizationFormValidator

    def get_cleaned_data(self, **kwargs) -> dict:
        return {
            "report_datetime": get_utcnow(),
            "have_details": YES,
            "admitted_date": get_utcnow_as_date() - timedelta(days=3),
            "admitted_date_estimated": NO,
            "discharged": YES,
            "discharged_date": get_utcnow_as_date() - timedelta(days=1),
            "discharged_date_estimated": NO,
            "lp_performed": YES,
            "lp_count": 2,
            "csf_positive_cm": YES,
            "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=2),
            "narrative": "Details of admission",
        }

    def test_cleaned_data_ok(self):
        cleaned_data = self.get_cleaned_data()
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_minimal_details_ok(self):
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "have_details": NO,
            "admitted_date": get_utcnow_as_date(),
            "admitted_date_estimated": NO,
            "discharged": UNKNOWN,
            "discharged_date": None,
            "discharged_date_estimated": NOT_APPLICABLE,
            "lp_performed": NO,
            "lp_count": None,
            "csf_positive_cm": NOT_APPLICABLE,
            "csf_positive_cm_date": None,
            "narrative": "",
        }
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_required_if_discharged_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date(),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": None,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_not_required_if_discharged_not_yes(self):
        for answer in [NO, UNKNOWN]:
            with self.subTest(answer=answer):
                cleaned_data = self.get_cleaned_data()
                cleaned_data.update(
                    {
                        "have_details": NO,
                        "admitted_date": get_utcnow_as_date(),
                        "admitted_date_estimated": NO,
                        "discharged": answer,
                        "discharged_date": get_utcnow_as_date(),
                    }
                )
                form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn("discharged_date", cm.exception.error_dict)
                self.assertEqual(
                    {"discharged_date": ["This field is not required."]},
                    cm.exception.message_dict,
                )

    def test_discharged_date_after_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=1),
                "discharged_date_estimated": NO,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_same_as_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=3),
                "discharged_date_estimated": NO,
                # CSF date cannot be after date discharged
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=3),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_raises_if_earlier_than_admitted_date(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=4),
                "discharged_date_estimated": NO,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date": ["Invalid. Cannot be before date admitted."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_estimated_applicable_if_discharged_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date(),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date(),
                "discharged_date_estimated": NOT_APPLICABLE,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date_estimated", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date_estimated": ["This field is applicable."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_estimated_applicable_if_discharged_not_yes(self):
        for answer in [NO, UNKNOWN]:
            with self.subTest(answer=answer):
                cleaned_data = self.get_cleaned_data()
                cleaned_data.update(
                    {
                        "have_details": NO,
                        "admitted_date": get_utcnow_as_date(),
                        "admitted_date_estimated": NO,
                        "discharged": answer,
                        "discharged_date": None,
                        "discharged_date_estimated": "D",
                    }
                )
                form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn("discharged_date_estimated", cm.exception.error_dict)
                self.assertEqual(
                    {"discharged_date_estimated": ["This field is not applicable."]},
                    cm.exception.message_dict,
                )

    def test_lp_count_required_if_lp_performed_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "lp_performed": YES,
                "lp_count": None,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("lp_count", cm.exception.error_dict)
        self.assertEqual(
            {"lp_count": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_lp_count_not_required_if_lp_performed_no(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "lp_performed": NO,
                "lp_count": 3,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("lp_count", cm.exception.error_dict)
        self.assertEqual(
            {"lp_count": ["This field is not required."]},
            cm.exception.message_dict,
        )

    def test_csf_positive_cm_applicable_if_lp_performed_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "lp_performed": YES,
                "lp_count": 1,
                "csf_positive_cm": NOT_APPLICABLE,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("csf_positive_cm", cm.exception.error_dict)
        self.assertEqual(
            {"csf_positive_cm": ["This field is applicable."]},
            cm.exception.message_dict,
        )

    def test_csf_positive_cm_not_applicable_if_lp_performed_not_yes(self):
        for lp_answer in [NO, UNKNOWN]:
            for csf_answer in [YES, NO, UNKNOWN]:
                with self.subTest(lp_answer=lp_answer, csf_answer=csf_answer):
                    cleaned_data = self.get_cleaned_data()
                    cleaned_data.update(
                        {
                            "lp_performed": lp_answer,
                            "lp_count": None,
                            "csf_positive_cm": csf_answer,
                        }
                    )
                    form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                    with self.assertRaises(forms.ValidationError) as cm:
                        form_validator.validate()
                    self.assertIn("csf_positive_cm", cm.exception.error_dict)
                    self.assertEqual(
                        {"csf_positive_cm": ["This field is not applicable."]},
                        cm.exception.message_dict,
                    )

    def test_csf_positive_cm_date_required_if_csf_positive_cm_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "lp_performed": YES,
                "lp_count": 1,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": None,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("csf_positive_cm_date", cm.exception.error_dict)
        self.assertEqual(
            {"csf_positive_cm_date": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_csf_positive_cm_date_not_required_if_csf_positive_cm_not_yes(self):
        for answer in [NO, UNKNOWN]:
            with self.subTest(answer=answer):
                cleaned_data = self.get_cleaned_data()
                cleaned_data.update(
                    {
                        "lp_performed": YES,
                        "lp_count": 3,
                        "csf_positive_cm": answer,
                        "csf_positive_cm_date": get_utcnow_as_date(),
                    }
                )
                form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn("csf_positive_cm_date", cm.exception.error_dict)
                self.assertEqual(
                    {"csf_positive_cm_date": ["This field is not required."]},
                    cm.exception.message_dict,
                )

    def test_csf_positive_cm_date_not_required_if_csf_positive_not_applicable(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "lp_performed": NO,
                "lp_count": None,
                "csf_positive_cm": NOT_APPLICABLE,
                "csf_positive_cm_date": get_utcnow_as_date(),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("csf_positive_cm_date", cm.exception.error_dict)
        self.assertEqual(
            {"csf_positive_cm_date": ["This field is not required."]},
            cm.exception.message_dict,
        )

    def test_csf_positive_cm_date_after_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=2),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_csf_positive_cm_date_same_as_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=3),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_csf_positive_cm_date_raises_if_earlier_than_admitted_date(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=4),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("csf_positive_cm_date", cm.exception.error_dict)
        self.assertEqual(
            {"csf_positive_cm_date": ["Invalid. Cannot be before date admitted."]},
            cm.exception.message_dict,
        )

    def test_csf_positive_cm_date_before_discharged_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=5),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=3),
                "discharged_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=4),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_csf_positive_cm_date_same_as_discharged_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=5),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=3),
                "discharged_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=3),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_csf_positive_cm_date_raises_if_after_discharged_date(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=5),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=3),
                "discharged_date_estimated": NO,
                "lp_performed": YES,
                "lp_count": 2,
                "csf_positive_cm": YES,
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=2),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("csf_positive_cm_date", cm.exception.error_dict)
        self.assertEqual(
            {"csf_positive_cm_date": ["Invalid. Cannot be after date discharged."]},
            cm.exception.message_dict,
        )

    def test_narrative_required_if_have_details_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "narrative": "",
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("narrative", cm.exception.error_dict)
        self.assertEqual(
            {"narrative": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_narrative_can_still_be_entered_if_have_details_no(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": NO,
                "narrative": "bbbb",
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")
