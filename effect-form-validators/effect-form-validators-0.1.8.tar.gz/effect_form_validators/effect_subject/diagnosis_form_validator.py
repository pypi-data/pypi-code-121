from typing import Any

from edc_constants.constants import NO, NOT_APPLICABLE, OTHER, YES
from edc_crf.crf_form_validator import CrfFormValidator


class DiagnosesFormValidator(CrfFormValidator):

    reportable_fields = ["reportable_as_ae", "patient_admitted"]

    def clean(self) -> None:

        self.validate_diagnoses()

        self.validate_reporting_fieldset()

    def validate_diagnoses(self: Any) -> Any:
        if self.cleaned_data.get("has_diagnoses") == NO:
            self.m2m_selection_expected(
                NOT_APPLICABLE,
                m2m_field="diagnoses",
                error_msg="Expected N/A only if NO significant diagnoses to report.",
            )
        elif self.cleaned_data.get("has_diagnoses") == YES:
            self.m2m_selections_not_expected(
                NOT_APPLICABLE,
                m2m_field="diagnoses",
                error_msg=(
                    "Invalid selection. "
                    "Cannot be N/A if there are significant diagnoses to report."
                ),
            )
        self.m2m_other_specify(OTHER, m2m_field="diagnoses", field_other="diagnoses_other")

    def validate_reporting_fieldset(self: Any) -> None:
        for reportable_field in self.reportable_fields:
            self.applicable_if(YES, field="has_diagnoses", field_applicable=reportable_field)
