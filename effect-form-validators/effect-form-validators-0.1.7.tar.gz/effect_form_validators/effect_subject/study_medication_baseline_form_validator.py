from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR
from edc_utils.text import formatted_date
from edc_visit_schedule.utils import is_baseline


class StudyMedicationBaselineFormValidator(CrfFormValidator):
    def clean(self) -> None:
        if not is_baseline(self.subject_visit):
            self.raise_validation_error(
                {"__all__": "This form may only be completed at baseline"}, INVALID_ERROR
            )
        # flucon
        self.required_if(YES, field="flucon_initiated", field_required="flucon_dose")
        self.required_if(
            NO, field="flucon_initiated", field_required="flucon_not_initiated_reason"
        )
        self.required_if(YES, field="flucon_initiated", field_required="flucon_dose_datetime")
        if self.cleaned_data.get("report_datetime") and self.cleaned_data.get(
            "flucon_dose_datetime"
        ):
            if (
                self.cleaned_data.get("report_datetime").date()
                != self.cleaned_data.get("flucon_dose_datetime").date()
            ):
                dte_as_str = formatted_date(self.cleaned_data.get("report_datetime").date())
                self.raise_validation_error(
                    {"flucon_dose_datetime": f"Expected {dte_as_str}"}, INVALID_ERROR
                )

        # flucyt
        self.required_if(YES, field="flucyt_initiated", field_required="flucyt_dose")
        self.required_if(
            NO, field="flucyt_initiated", field_required="flucyt_not_initiated_reason"
        )
        self.required_if(YES, field="flucyt_initiated", field_required="flucyt_dose_datetime")
        if self.cleaned_data.get("report_datetime") and self.cleaned_data.get(
            "flucyt_dose_datetime"
        ):
            if (
                self.cleaned_data.get("report_datetime").date()
                != self.cleaned_data.get("flucyt_dose_datetime").date()
            ):
                dte_as_str = formatted_date(self.cleaned_data.get("report_datetime").date())
                self.raise_validation_error(
                    {"flucyt_dose_datetime": f"Expected {dte_as_str}"}, INVALID_ERROR
                )
