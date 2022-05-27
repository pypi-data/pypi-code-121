from typing import Any

from edc_constants.constants import POS, YES
from edc_crf.crf_form_validator import CrfFormValidator


class HistopathologyFormValidatorMixin:
    def validate_histopathology(self: Any):
        self.required_if(
            YES, field="tissue_biopsy_performed", field_required="tissue_biopsy_date"
        )

        self.validate_date_against_report_datetime("tissue_biopsy_date")

        self.applicable_if(
            YES,
            field="tissue_biopsy_performed",
            field_applicable="tissue_biopsy_result",
        )
        self.required_if(
            POS,
            field="tissue_biopsy_result",
            field_required="tissue_biopsy_organism_text",
        )


class HistopathologyFormValidator(
    HistopathologyFormValidatorMixin,
    CrfFormValidator,
):
    def clean(self):
        self.validate_histopathology()
