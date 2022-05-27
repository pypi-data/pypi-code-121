from django import forms
from edc_appointment.constants import MISSED_APPT
from edc_constants.choices import ALIVE_DEAD_UNKNOWN_NA_MISSED
from edc_constants.constants import (
    ALIVE,
    HOSPITAL_NOTES,
    IN_PERSON,
    NEXT_OF_KIN,
    NOT_APPLICABLE,
    OTHER,
    OUTPATIENT_CARDS,
    PATIENT,
    PATIENT_REPRESENTATIVE,
    TELEPHONE,
    UNKNOWN,
    YES,
)
from edc_constants.utils import get_display
from edc_form_validators import INVALID_ERROR
from edc_visit_tracking.choices import (
    ASSESSMENT_TYPES,
    ASSESSMENT_WHO_CHOICES,
    VISIT_INFO_SOURCE2,
)
from edc_visit_tracking.constants import MISSED_VISIT
from edc_visit_tracking.form_validators import VisitFormValidator


class SubjectVisitFormValidator(VisitFormValidator):

    validate_missed_visit_reason = False

    def clean(self):

        self.not_applicable_if(
            MISSED_VISIT,
            field="reason",
            field_applicable="assessment_type",
            not_applicable_msg="This field is not applicable. See Appointment",
        )

        if self.cleaned_data.get("reason") != MISSED_VISIT:
            self.validate_assessment_type()

        self.not_applicable_if(
            MISSED_VISIT,
            field="reason",
            field_applicable="assessment_who",
            not_applicable_msg="This field is not applicable. See Appointment",
        )

        if self.cleaned_data.get("reason") != MISSED_VISIT:
            self.validate_assessment_who()

        self.not_applicable_if(
            MISSED_VISIT,
            field="reason",
            field_applicable="info_source",
            not_applicable_msg="This field is not applicable. See Appointment",
        )

        if self.cleaned_data.get("reason") != MISSED_VISIT:
            self.validate_info_source_against_assessment_type_who()

        self.not_applicable_if(
            MISSED_VISIT,
            field="reason",
            field_applicable="survival_status",
            not_applicable_msg="This field is not applicable. See Appointment",
        )

        if self.cleaned_data.get("reason") != MISSED_VISIT:
            self.validate_survival_status()

        self.not_applicable_if(
            MISSED_VISIT,
            field="reason",
            field_applicable="hospitalized",
            not_applicable_msg="This field is not applicable. See Appointment",
        )

        if self.cleaned_data.get("reason") != MISSED_VISIT:
            self.validate_hospitalized()

    def applicable_if_not_missed(self, field_applicable: str) -> bool:
        if (
            self.cleaned_data.get("appointment").appt_timing == MISSED_APPT
            and self.cleaned_data.get("assessment_type") != NOT_APPLICABLE
        ):
            self.raise_validation_error(
                {field_applicable: "This field is not applicable. See Appointment"},
                INVALID_ERROR,
            )
        return True

    def validate_assessment_type(self):
        if (
            self.cleaned_data.get("appointment").is_baseline_appt
            and self.cleaned_data.get("assessment_type") != IN_PERSON
        ):
            raise forms.ValidationError(
                {"assessment_type": "Invalid. Expected 'In person' at baseline"}
            )

        self.validate_other_specify(field="assessment_type")

    def validate_assessment_who(self):
        self.not_applicable(
            MISSED_APPT, field="appt_status", field_applicable="assessment_type"
        )
        if self.cleaned_data.get("appt_status") != MISSED_APPT:
            if (
                self.cleaned_data.get("assessment_type") == IN_PERSON
                and self.cleaned_data.get("assessment_who") != PATIENT
            ):
                raise forms.ValidationError(
                    {"assessment_who": "Invalid. Expected 'Patient' if 'In person' visit"}
                )

        self.validate_other_specify(field="assessment_who")

    @staticmethod
    def info_source_reconciles_with_assessment_type_who(
        info_source: str,
        assessment_type: str,
        assessment_who: str,
    ) -> bool:
        """Returns True, if 'info_source' answer reconciles with
        'assessment_type' and 'assessment_who' answers.
        """
        return (
            info_source == PATIENT
            and any(
                (
                    assessment_type == IN_PERSON and assessment_who == PATIENT,
                    assessment_type == TELEPHONE and assessment_who == PATIENT,
                )
            )
            or info_source == PATIENT_REPRESENTATIVE
            and any(
                (
                    assessment_type == TELEPHONE and assessment_who == NEXT_OF_KIN,
                    assessment_type == TELEPHONE and assessment_who == OTHER,
                    assessment_type == OTHER,
                )
            )
            or info_source in [HOSPITAL_NOTES, OUTPATIENT_CARDS, OTHER]
        )

    @staticmethod
    def get_info_source_mismatch_error_msg(
        info_source: str,
        assessment_type: str,
        assessment_who: str,
    ) -> str:
        return (
            "Invalid. Did not expect information source: "
            f"'{get_display(VISIT_INFO_SOURCE2, info_source)}' for "
            f"'{get_display(ASSESSMENT_TYPES, assessment_type)}' "
            "assessment with "
            f"'{get_display(ASSESSMENT_WHO_CHOICES, assessment_who)}.'"
        )

    def validate_info_source_against_assessment_type_who(self):
        if not self.info_source_reconciles_with_assessment_type_who(
            info_source=self.cleaned_data.get("info_source"),
            assessment_type=self.cleaned_data.get("assessment_type"),
            assessment_who=self.cleaned_data.get("assessment_who"),
        ):
            error_msg = self.get_info_source_mismatch_error_msg(
                info_source=self.cleaned_data.get("info_source"),
                assessment_type=self.cleaned_data.get("assessment_type"),
                assessment_who=self.cleaned_data.get("assessment_who"),
            )
            raise forms.ValidationError({"info_source": error_msg})

    def validate_survival_status(self):
        if self.cleaned_data.get("survival_status") != ALIVE:
            error_msg = None

            if self.cleaned_data.get("appointment").is_baseline_appt:
                survival_status = self.cleaned_data.get("survival_status")
                error_msg = (
                    "Invalid: Cannot be "
                    f"'{get_display(ALIVE_DEAD_UNKNOWN_NA_MISSED, survival_status)}' "
                    "at baseline"
                )

            elif self.cleaned_data.get("assessment_type") == IN_PERSON:
                error_msg = "Invalid: Expected 'Alive' if this is an 'In person' visit"

            elif self.cleaned_data.get("assessment_who") == PATIENT:
                error_msg = "Invalid: Expected 'Alive' if spoke to 'Patient'"

            if error_msg:
                raise forms.ValidationError({"survival_status": error_msg})

    def validate_hospitalized(self):
        if (
            self.cleaned_data.get("appointment").is_baseline_appt
            and self.cleaned_data.get("hospitalized") == YES
        ):
            raise forms.ValidationError({"hospitalized": "Invalid. Expected NO at baseline"})

        if self.cleaned_data.get("hospitalized") == UNKNOWN and (
            self.cleaned_data.get("assessment_who") == PATIENT
            or self.cleaned_data.get("info_source") == PATIENT
        ):
            raise forms.ValidationError(
                {
                    "hospitalized": (
                        "Invalid. Cannot be 'Unknown' if spoke to 'Patient' "
                        "or 'Patient' was MAIN source of information"
                    )
                }
            )
