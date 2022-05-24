from edc_crf.crf_form_validator import CrfFormValidator
from edc_visit_schedule.utils import is_baseline


class VitalSignsFormValidator(CrfFormValidator):
    def clean(self) -> None:
        self.required_if_true(True, field_required="sys_blood_pressure")

        self.required_if_true(True, field_required="dia_blood_pressure")

        condition = not is_baseline(self.cleaned_data.get("subject_visit"))

        for fld in ["reportable_as_ae", "patient_admitted"]:
            self.applicable_if_true(
                condition=condition,
                field_applicable=fld,
                not_applicable_msg="Not applicable at baseline",
            )
