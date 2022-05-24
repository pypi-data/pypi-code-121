from django.core.exceptions import ValidationError
from django.test import TestCase
from django_mock_queries.query import MockModel, MockSet
from edc_constants.constants import (
    IN_PERSON,
    NEXT_OF_KIN,
    NO,
    NOT_APPLICABLE,
    OTHER,
    PATIENT,
    TELEPHONE,
    UNKNOWN,
    YES,
)

from effect_form_validators.effect_subject import SignsAndSymptomsFormValidator as Base

from ..mixins import FormValidatorTestMixin, TestCaseMixin


class SignsAndSymptomsFormValidator(FormValidatorTestMixin, Base):
    pass


class TestSignsAndSymptomsFormValidation(TestCaseMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.sisx_choice_na = MockModel(
            mock_name="SiSx", name=NOT_APPLICABLE, display_name=NOT_APPLICABLE
        )
        self.investigations_performed_fields = [
            "xray_performed",
            "lp_performed",
            "urinary_lam_performed",
        ]

    def get_cleaned_data(self, **kwargs) -> dict:
        cleaned_data = super().get_cleaned_data(**kwargs)
        cleaned_data.update(
            any_sx=NO,
            current_sx=MockSet(self.sisx_choice_na),
            current_sx_other="",
            cm_sx=NOT_APPLICABLE,
            current_sx_gte_g3=MockSet(self.sisx_choice_na),
            current_sx_gte_g3_other="",
            headache_duration="",
            cn_palsy_left_other="",
            cn_palsy_right_other="",
            focal_neurologic_deficit_other="",
            visual_field_loss="",
            xray_performed=NO,
            lp_performed=NO,
            urinary_lam_performed=NO,
            reportable_as_ae=NOT_APPLICABLE,
            patient_admitted=NOT_APPLICABLE,
        )
        return cleaned_data

    def test_cleaned_data_ok(self):
        self.subject_visit.assessment_type = IN_PERSON
        form_validator = SignsAndSymptomsFormValidator(cleaned_data=self.get_cleaned_data())
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_any_sx_unknown_ok(self):
        self.subject_visit.assessment_type = TELEPHONE
        self.subject_visit.assessment_who = NEXT_OF_KIN
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            any_sx=UNKNOWN,
            current_sx=MockSet(self.sisx_choice_na),
            current_sx_other="",
            cm_sx=NOT_APPLICABLE,
            current_sx_gte_g3=MockSet(self.sisx_choice_na),
            current_sx_gte_g3_other="",
            headache_duration="",
            cn_palsy_left_other="",
            cn_palsy_right_other="",
            focal_neurologic_deficit_other="",
            visual_field_loss="",
            xray_performed=NOT_APPLICABLE,
            lp_performed=NOT_APPLICABLE,
            urinary_lam_performed=NOT_APPLICABLE,
            reportable_as_ae=NOT_APPLICABLE,
            patient_admitted=NOT_APPLICABLE,
        )

        form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_any_sx_unknown_raises_if_in_person_visit(self):
        self.subject_visit.assessment_type = IN_PERSON
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(any_sx=UNKNOWN)

        form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("any_sx", cm.exception.error_dict)
        self.assertEqual(
            {"any_sx": ["Invalid. Cannot be 'Unknown' if this is an 'In person' visit."]},
            cm.exception.message_dict,
        )

    def test_unknown_raises_if_telephone_visit_with_patient(self):
        self.subject_visit.assessment_type = TELEPHONE
        self.subject_visit.assessment_who = PATIENT
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(any_sx=UNKNOWN)

        form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("any_sx", cm.exception.error_dict)
        self.assertEqual(
            {"any_sx": ["Invalid. Cannot be 'Unknown' if spoke to 'Patient'."]},
            cm.exception.message_dict,
        )

    def test_any_sx_unknown_ok_if_did_not_speak_to_patient(self):
        self.subject_visit.assessment_type = TELEPHONE
        self.subject_visit.assessment_who = NEXT_OF_KIN
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            any_sx=UNKNOWN,
        )

        form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertNotIn("any_sx", cm.exception.error_dict)

        self.subject_visit.assessment_type = OTHER
        self.subject_visit.assessment_who = OTHER
        form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertNotIn("any_sx", cm.exception.error_dict)

    def test_investigations_performed_applicable_if_in_person_visit(self):
        self.subject_visit.assessment_type = IN_PERSON

        for fld in self.investigations_performed_fields:
            for answer in [YES, NO]:
                with self.subTest(fld=fld, answer=answer):
                    # Reset values, and test form is valid
                    cleaned_data = self.get_cleaned_data()
                    cleaned_data.update(
                        any_sx=NO,
                        current_sx=MockSet(self.sisx_choice_na),
                        cm_sx=NOT_APPLICABLE,
                        current_sx_gte_g3=MockSet(self.sisx_choice_na),
                        xray_performed=NO,
                        lp_performed=NO,
                        urinary_lam_performed=NO,
                    )
                    form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
                    try:
                        form_validator.validate()
                    except ValidationError as e:
                        self.fail(f"ValidationError unexpectedly raised. Got {e}")

                    # Try with NA, where form validator expects answer
                    cleaned_data.update({fld: NOT_APPLICABLE})
                    form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
                    with self.assertRaises(ValidationError) as cm:
                        form_validator.validate()
                    self.assertIn(fld, cm.exception.error_dict)
                    self.assertEqual(
                        {fld: ["This field is applicable."]},
                        cm.exception.message_dict,
                    )

                    cleaned_data.update({fld: answer})
                    form_validator = SignsAndSymptomsFormValidator(cleaned_data=cleaned_data)
                    try:
                        form_validator.validate()
                    except ValidationError as e:
                        self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_investigations_performed_not_applicable_if_not_in_person_visit(self):
        for fld in self.investigations_performed_fields:
            for assess_type, assess_who in [(TELEPHONE, NEXT_OF_KIN), (OTHER, OTHER)]:
                for answer in [YES, NO]:
                    with self.subTest(
                        assess_type=assess_type,
                        assess_who=assess_who,
                        answer=answer,
                    ):
                        # Reset values, and test form is valid
                        self.subject_visit.assessment_type = assess_type
                        self.subject_visit.assessment_who = assess_who
                        cleaned_data = self.get_cleaned_data()
                        cleaned_data.update(
                            any_sx=NO,
                            current_sx=MockSet(self.sisx_choice_na),
                            cm_sx=NOT_APPLICABLE,
                            current_sx_gte_g3=MockSet(self.sisx_choice_na),
                            xray_performed=NOT_APPLICABLE,
                            lp_performed=NOT_APPLICABLE,
                            urinary_lam_performed=NOT_APPLICABLE,
                        )
                        form_validator = SignsAndSymptomsFormValidator(
                            cleaned_data=cleaned_data
                        )
                        try:
                            form_validator.validate()
                        except ValidationError as e:
                            self.fail(f"ValidationError unexpectedly raised. Got {e}")

                        # Try with answer, where form validator expects NA
                        cleaned_data.update({fld: answer})
                        form_validator = SignsAndSymptomsFormValidator(
                            cleaned_data=cleaned_data
                        )
                        with self.assertRaises(ValidationError) as cm:
                            form_validator.validate()
                        self.assertIn(fld, cm.exception.error_dict)
                        self.assertEqual(
                            {
                                fld: [
                                    "Invalid. This field is not applicable if this is not "
                                    "an 'In person' visit."
                                ]
                            },
                            cm.exception.message_dict,
                        )
