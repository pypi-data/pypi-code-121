from collections import namedtuple

from django import forms
from django.test import TestCase, tag
from django_mock_queries.query import MockModel, MockSet
from edc_constants.constants import NO, NOT_APPLICABLE, NOT_ESTIMATED, OTHER, YES
from edc_form_validators import FormValidatorTestCaseMixin
from edc_utils import get_utcnow

from effect_form_validators.effect_subject import PatientTreatmentFormValidator as Base

from ..mixins import FormValidatorTestMixin, TestCaseMixin

MyInstance = namedtuple("MyList", ["name", "display_name"])


class MockList:
    def __init__(self, name=None, display_name=None):
        self.instance = MyInstance(name=name, display_name=display_name)

    @staticmethod
    def count():
        return 1

    def __iter__(self):
        yield self.instance


class PatientTreatmentFormValidator(FormValidatorTestMixin, Base):
    pass


class TestPatientTreatmentFormValidation(FormValidatorTestCaseMixin, TestCaseMixin, TestCase):

    form_validator_default_form_cls = PatientTreatmentFormValidator

    def setUp(self):
        self.antibiotics_obj = MockModel(
            mock_name="amoxicillin", name="amoxicillin", display_name="amoxicillin"
        )
        self.drugs_obj = MockModel(
            mock_name="vitamins", name="vitamins", display_name="vitamins"
        )
        self.tb_treatments_obj = MockModel(mock_name="H", name="H", display_name="H")
        self.antibiotics_qs = MockSet(
            MockModel(mock_name="amoxicillin", name="amoxicillin", display_name="amoxicillin"),
            MockModel(mock_name="other", name=OTHER, display_name=OTHER),
        )
        self.drugs_qs = MockSet(
            MockModel(mock_name="vitamins", name="vitamins", display_name="vitamins"),
            MockModel(mock_name="other", name=OTHER, display_name=OTHER),
        )
        self.tb_treatments_qs = MockSet(
            MockModel(mock_name="H", name="H", display_name="H"),
            MockModel(mock_name="other", name=OTHER, display_name=OTHER),
        )

    @staticmethod
    def get_cleaned_data_patient_no_cm_no_tx():
        return {
            "report_datetime": get_utcnow(),
            "lp_completed": NO,
            "cm_confirmed": NOT_APPLICABLE,
            "on_cm_tx": NOT_APPLICABLE,
            "cm_tx_given": NOT_APPLICABLE,
            "cm_tx_given_other": "",
            "on_tb_tx": NO,
            "tb_tx_date": None,
            "tb_tx_date_estimated": NOT_APPLICABLE,
            "tb_tx_given": None,
            "tb_tx_given_other": "",
            "tb_tx_reason_no": "contraindicated",
            "tb_tx_reason_no_other": "",
            "on_steroids": NO,
            "steroids_date": None,
            "steroids_date_estimated": NOT_APPLICABLE,
            "steroids_given": NOT_APPLICABLE,
            "steroids_given_other": "",
            "steroids_course": None,
            "on_co_trimoxazole": NO,
            "co_trimoxazole_date": None,
            "co_trimoxazole_date_estimated": NOT_APPLICABLE,
            "co_trimoxazole_reason_no": "deferred_local_clinic",
            "co_trimoxazole_reason_no_other": "",
            "on_antibiotics": NO,
            "antibiotics_date": None,
            "antibiotics_date_estimated": NOT_APPLICABLE,
            "antibiotics_given": MockSet(),
            "antibiotics_given_other": "",
            "on_other_drugs": NO,
            "other_drugs_date": None,
            "other_drugs_date_estimated": NOT_APPLICABLE,
            "other_drugs_given": MockSet(),
            "other_drugs_given_other": "",
        }

    @staticmethod
    def get_cleaned_data_patient_with_cm_with_all_tx():
        return {
            "report_datetime": get_utcnow(),
            "lp_completed": YES,
            "cm_confirmed": YES,
            "on_cm_tx": YES,
            "cm_tx_given": "1w_amb_5fc",
            "cm_tx_given_other": "",
            "on_tb_tx": YES,
            "tb_tx_date": get_utcnow().date(),
            "tb_tx_date_estimated": NOT_ESTIMATED,
            "tb_tx_given": MockList(name="H", display_name="H"),
            "tb_tx_given_other": "",
            "tb_tx_reason_no": NOT_APPLICABLE,
            "tb_tx_reason_no_other": "",
            "on_steroids": YES,
            "steroids_date": get_utcnow().date(),
            "steroids_date_estimated": NOT_ESTIMATED,
            "steroids_given": "oral_prednisolone",
            "steroids_given_other": "",
            "steroids_course": 3,
            "on_co_trimoxazole": YES,
            "co_trimoxazole_date": get_utcnow().date(),
            "co_trimoxazole_date_estimated": NOT_ESTIMATED,
            "co_trimoxazole_reason_no": NOT_APPLICABLE,
            "co_trimoxazole_reason_no_other": "",
            "on_antibiotics": YES,
            "antibiotics_date": get_utcnow().date(),
            "antibiotics_date_estimated": NOT_ESTIMATED,
            "antibiotics_given": MockList(name="H", display_name="H"),
            "antibiotics_given_other": "",
            "on_other_drugs": YES,
            "other_drugs_date": get_utcnow().date(),
            "other_drugs_date_estimated": NOT_ESTIMATED,
            "other_drugs_given": MockList(name="H", display_name="H"),
            "other_drugs_given_other": "",
        }

    @tag("1")
    def test_cleaned_data_patient_no_cm_no_tx_ok(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    @tag("1")
    def test_cleaned_data_patient_with_cm_with_all_tx_ok(self):
        cleaned_data = self.get_cleaned_data_patient_with_cm_with_all_tx()

        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    @tag("1")
    def test_cm_confirmed_na_if_lp_not_completed(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": NO,
                "cm_confirmed": NO,
            }
        )
        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cm_confirmed", cm.exception.error_dict)
        self.assertIn(
            "This field is not applicable",
            cm.exception.error_dict.get("cm_confirmed")[0].message,
        )

    @tag("1")
    def test_cm_confirmed_applicable_if_lp_completed(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": NOT_APPLICABLE,
            }
        )
        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cm_confirmed", cm.exception.error_dict)
        self.assertIn(
            "This field is applicable",
            cm.exception.error_dict.get("cm_confirmed")[0].message,
        )

    @tag("1")
    def test_cm_tx_na_if_cm_not_confirmed(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": NO,
                "on_cm_tx": NO,
            }
        )
        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("on_cm_tx", cm.exception.error_dict)
        self.assertIn(
            "This field is not applicable",
            cm.exception.error_dict.get("on_cm_tx")[0].message,
        )

    @tag("1")
    def test_cm_tx_applicable_if_cm_confirmed(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": YES,
                "on_cm_tx": NOT_APPLICABLE,
            }
        )

        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("on_cm_tx", cm.exception.error_dict)
        self.assertIn(
            "This field is applicable",
            cm.exception.error_dict.get("on_cm_tx")[0].message,
        )

    @tag("1")
    def test_cm_tx_given_na_if_cm_tx_no(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": YES,
                "on_cm_tx": NO,
                "cm_tx_given": "1w_amb_5fc",
            }
        )
        form_validator = PatientTreatmentFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cm_tx_given", cm.exception.error_dict)
        self.assertIn(
            "This field is not applicable",
            cm.exception.error_dict.get("cm_tx_given")[0].message,
        )

    @tag("1")
    def test_cm_tx_given_applicable_if_cm_tx(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": YES,
                "on_cm_tx": YES,
                "cm_tx_given": NOT_APPLICABLE,
            }
        )
        self.assertFormValidatorError(
            field="cm_tx_given",
            expected_msg="This field is applicable.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_cm_tx_given_other_required_if_specified(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": YES,
                "on_cm_tx": YES,
                "cm_tx_given": OTHER,
                "cm_tx_given_other": "",
            }
        )
        self.assertFormValidatorError(
            field="cm_tx_given_other",
            expected_msg="This field is required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_cm_tx_given_other_not_required_if_not_specified(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "lp_completed": YES,
                "cm_confirmed": YES,
                "on_cm_tx": YES,
                "cm_tx_given": "1w_amb_5fc",
                "cm_tx_given_other": "some_other_cm_tx_given",
            }
        )
        self.assertFormValidatorError(
            field="cm_tx_given_other",
            expected_msg="This field is not required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    # steroid validation tests
    @tag("1")
    def test_steroids_given_na_if_steroids_no(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": NO,
                "steroids_given": "oral_prednisolone",
                "steroids_given_other": "",
                "steroids_course": 1,
            }
        )
        self.assertFormValidatorError(
            field="steroids_given",
            expected_msg="This field is not applicable.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_steroids_given_applicable_if_steroids(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": YES,
                "steroids_date": get_utcnow().date(),
                "steroids_date_estimated": "MD",
                "steroids_given": NOT_APPLICABLE,
                "steroids_given_other": "",
                "steroids_course": None,
            }
        )
        self.assertFormValidatorError(
            field="steroids_given",
            expected_msg="This field is applicable.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_steroids_given_other_required_if_specified(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": YES,
                "steroids_date": get_utcnow().date(),
                "steroids_date_estimated": "MD",
                "steroids_given": OTHER,
                "steroids_given_other": "",
                "steroids_course": 1,
            }
        )
        self.assertFormValidatorError(
            field="steroids_given_other",
            expected_msg="This field is required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_steroids_given_other_not_required_if_not_specified(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": YES,
                "steroids_date": get_utcnow().date(),
                "steroids_date_estimated": "MD",
                "steroids_given": "oral_prednisolone",
                "steroids_given_other": "xxx",
                "steroids_course": 1,
            }
        )
        self.assertFormValidatorError(
            field="steroids_given_other",
            expected_msg="This field is not required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_steroids_course_not_required_if_steroids_no(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": NO,
                "steroids_given": NOT_APPLICABLE,
                "steroids_given_other": "",
                "steroids_course": 1,
            }
        )
        self.assertFormValidatorError(
            field="steroids_course",
            expected_msg="This field is not required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_steroids_course_required_if_steroids(self):
        cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
        cleaned_data.update(
            {
                "on_steroids": YES,
                "steroids_date": get_utcnow().date(),
                "steroids_date_estimated": "MD",
                "steroids_given": "oral_prednisolone",
                "steroids_given_other": "",
                "steroids_course": None,
            }
        )
        self.assertFormValidatorError(
            field="steroids_course",
            expected_msg="This field is required.",
            form_validator=self.validate_form_validator(cleaned_data),
        )

    @tag("1")
    def test_date_fields_required_if_prescribed_yes(self):
        for field_stub in [
            "tb_tx",
            "steroids",
            "co_trimoxazole",
            "antibiotics",
            "other_drugs",
        ]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": YES,
                        f"{field_stub}_date": None,
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_date",
                    expected_msg="This field is required.",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_date_fields_not_required_if_prescribed_no(self):
        for field_stub in [
            "tb_tx",
            "steroids",
            "co_trimoxazole",
            "antibiotics",
            "other_drugs",
        ]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_date": get_utcnow().date(),
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_date",
                    expected_msg="This field is not required.",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_date_estimated_fields_applicable_if_prescribed_yes(self):
        for field_stub in [
            "tb_tx",
            "steroids",
            "co_trimoxazole",
            "antibiotics",
            "other_drugs",
        ]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": YES,
                        f"{field_stub}_date": get_utcnow().date(),
                        f"{field_stub}_date_estimated": NOT_APPLICABLE,
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_date_estimated",
                    expected_msg="This field is applicable",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_date_estimated_fields_not_applicable_if_prescribed_no(self):
        for field_stub in [
            "tb_tx",
            "steroids",
            "co_trimoxazole",
            "antibiotics",
            "other_drugs",
        ]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_date": None,
                        f"{field_stub}_date_estimated": "YMD",
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_date_estimated",
                    expected_msg="This field is not applicable.",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_m2m_fields_required_if_prescribed_yes(self):
        for field_stub, list_model in [
            ("tb_tx", MockModel),
            ("antibiotics", MockModel),
            ("other_drugs", MockModel),
        ]:
            with self.subTest(field_stub=field_stub, list_model=list_model):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": YES,
                        f"{field_stub}_date": get_utcnow().date(),
                        f"{field_stub}_date_estimated": "YMD",
                        f"{field_stub}_given": None,
                    }
                )
                if field_stub == "tb_tx":
                    cleaned_data.update({"tb_tx_reason_no": NOT_APPLICABLE})
                self.assertFormValidatorError(
                    field=f"{field_stub}_given",
                    expected_msg="This field is required",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_m2m_fields_not_applicable_if_prescribed_no(self):
        for field_stub, list_model in [
            ("tb_tx", MockModel),
            ("antibiotics", MockModel),
            ("other_drugs", MockModel),
        ]:
            with self.subTest(field_stub=field_stub, list_model=list_model):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_date": None,
                        f"{field_stub}_given": MockList(
                            name=NOT_APPLICABLE, display_name=NOT_APPLICABLE
                        ),
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_given",
                    expected_msg="This field is not required",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_m2m_other_fields_required_if_other_specified(self):
        for field_stub, list_model in [
            ("tb_tx", MockModel),
            ("antibiotics", MockModel),
            ("other_drugs", MockModel),
        ]:
            with self.subTest(field_stub=field_stub, list_model=list_model):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": YES,
                        f"{field_stub}_date": get_utcnow().date(),
                        f"{field_stub}_date_estimated": "YMD",
                        f"{field_stub}_given": MockList(name=OTHER, display_name=OTHER),
                        f"{field_stub}_given_other": "",
                    }
                )
                if field_stub == "tb_tx":
                    cleaned_data.update({"tb_tx_reason_no": NOT_APPLICABLE})
                self.assertFormValidatorError(
                    field=f"{field_stub}_given_other",
                    expected_msg="This field is required.",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

                cleaned_data.update({f"{field_stub}_given_other": "Some other value"})
                self.assertFormValidatorNoError(
                    form_validator=self.validate_form_validator(cleaned_data)
                )

    @tag("1")
    def test_m2m_other_fields_not_required_if_not_specified(self):
        for field_stub, list_model in [
            ("tb_tx", MockModel),
            ("antibiotics", MockModel),
            ("other_drugs", MockModel),
        ]:
            with self.subTest(field_stub=field_stub, list_model=list_model):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_date": None,
                        f"{field_stub}_given": None,
                        f"{field_stub}_given_other": "Some other value",
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_given_other",
                    expected_msg="This field is not required.",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

                cleaned_data.update({f"{field_stub}_given_other": ""})
                self.assertFormValidatorNoError(
                    form_validator=self.validate_form_validator(cleaned_data)
                )

    @tag("1")
    def test_reason_no_applicable_if_prescribed_no(self):
        for field_stub in ["tb_tx", "co_trimoxazole"]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update({f"{field_stub}_reason_no": NOT_APPLICABLE})
                self.assertFormValidatorError(
                    field=f"{field_stub}_reason_no",
                    expected_msg="This field is applicable",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_reason_no_not_applicable_if_prescribed_yes(self):
        for field_stub in ["tb_tx", "co_trimoxazole"]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": YES,
                        f"{field_stub}_date": get_utcnow().date(),
                        f"{field_stub}_date_estimated": "YMD",
                        f"{field_stub}_reason_no": "contraindicated",
                    }
                )
                if field_stub == "tb_tx":
                    cleaned_data.update({"tb_tx_given": MockList(name="H", display_name="H")})

                self.assertFormValidatorError(
                    field=f"{field_stub}_reason_no",
                    expected_msg="This field is not applicable",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_reason_no_other_required_if_specified(self):
        for field_stub in ["tb_tx", "co_trimoxazole"]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_reason_no": OTHER,
                        f"{field_stub}_reason_no_other": "",
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_reason_no_other",
                    expected_msg="This field is required",
                    form_validator=self.validate_form_validator(cleaned_data),
                )

    @tag("1")
    def test_reason_no_other_not_required_if_not_specified(self):
        for field_stub in ["tb_tx", "co_trimoxazole"]:
            with self.subTest(field_stub=field_stub):
                cleaned_data = self.get_cleaned_data_patient_no_cm_no_tx()
                cleaned_data.update(
                    {
                        f"on_{field_stub}": NO,
                        f"{field_stub}_reason_no": "contraindicated",
                        f"{field_stub}_reason_no_other": "Some other reason",
                    }
                )
                self.assertFormValidatorError(
                    field=f"{field_stub}_reason_no_other",
                    expected_msg="This field is not required",
                    form_validator=self.validate_form_validator(cleaned_data),
                )
