from edc_constants.constants import YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR
from edc_visit_schedule.utils import is_baseline


class MentalStatusFormValidator(CrfFormValidator):

    reportable_fields = ["reportable_as_ae", "patient_admitted"]

    def clean(self) -> None:

        baseline = is_baseline(self.cleaned_data.get("subject_visit"))

        # Cannot have had a recent seizure at baseline
        if baseline and self.cleaned_data.get("recent_seizure") == YES:
            self.raise_validation_error(
                {"recent_seizure": "Invalid. Cannot have had a recent seizure at baseline"},
                INVALID_ERROR,
            )

        #  GCS cannot be less than 15 at baseline
        if (
            baseline
            and self.cleaned_data.get("glasgow_coma_score")
            and self.cleaned_data.get("glasgow_coma_score") < 15
        ):
            self.raise_validation_error(
                {"glasgow_coma_score": "Invalid. GCS cannot be less than 15 at baseline"},
                INVALID_ERROR,
            )

        # ae and hodspitalization not reportable at baseline
        for fld in ["reportable_as_ae", "patient_admitted"]:
            self.applicable_if_true(
                not baseline,
                field_applicable=fld,
                not_applicable_msg="Not applicable at baseline.",
            )
