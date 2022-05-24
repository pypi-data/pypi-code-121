from dateutil.relativedelta import relativedelta
from django import forms
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
            "cd4_value": self.ELIGIBLE_CD4_VALUE,
            "cd4_date": (get_utcnow_as_date() - relativedelta(days=7)),
            "serum_crag_value": POS,
            "serum_crag_date": (get_utcnow_as_date() - relativedelta(days=6)),
            "lp_done": YES,
            "lp_date": (get_utcnow_as_date() - relativedelta(days=6)),
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
