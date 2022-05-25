from typing import Any

from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_csf.form_validators import (
    LpFormValidatorMixin,
    QuantitativeCsfFormValidatorMixin,
)
from edc_lab import CrfRequisitionFormValidatorMixin


class LpCsfFormValidator(
    CrfRequisitionFormValidatorMixin,
    LpFormValidatorMixin,
    QuantitativeCsfFormValidatorMixin,
    CrfFormValidator,
):
    csf_culture_panel = None

    def clean(self):
        self.validate_lp()
        self.validate_csf_assessment()
        self.validate_csf_culture("csf_requisition")

    def validate_csf_assessment(self: Any):
        for fld in [
            "india_ink",
            "csf_crag_lfa",
            "sq_crag",
            "sq_crag_pos",
            "crf_crag_titre_done",
        ]:
            self.applicable_if(YES, NO, field="csf_positive", field_applicable=fld)

        self.required_if(YES, field="crf_crag_titre_done", field_required="crf_crag_titre")

    def validate_csf_culture(self: Any, requisition: str):
        self.require_together(
            field=requisition,
            field_required="csf_culture_assay_datetime",
        )
        self.validate_requisition(
            requisition, "csf_culture_assay_datetime", self.csf_culture_panel
        )
        self.required_if_true(
            self.cleaned_data.get("quantitative_culture") is not None,
            field_required=requisition,
        )
