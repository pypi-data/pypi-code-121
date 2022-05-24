from datetime import date
from typing import Optional

from edc_constants.constants import NO, NORMAL, OTHER, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR
from edc_utils.text import formatted_date


class ChestXrayFormValidator(CrfFormValidator):
    def clean(self):
        super().clean()

        self.validate_against_ssx()

        self.required_if(YES, field="chest_xray", field_required="chest_xray_date")

        self.validate_date_against_report_datetime("chest_xray_date")

        self.validate_chest_xray_date()

        self.m2m_required_if(YES, field="chest_xray", m2m_field="chest_xray_results")

        self.m2m_single_selection_if(NORMAL, m2m_field="chest_xray_results")

        self.m2m_other_specify(
            OTHER,
            m2m_field="chest_xray_results",
            field_other="chest_xray_results_other",
        )

    def validate_against_ssx(self):
        try:
            xray_performed = self.cleaned_data.get(
                "subject_visit"
            ).signsandsymptoms.xray_performed
        except AttributeError:
            xray_performed = None

        if xray_performed and self.cleaned_data.get("chest_xray"):
            if xray_performed == YES and self.cleaned_data.get("chest_xray") != YES:
                raise self.raise_validation_error(
                    {
                        "chest_xray": (
                            "Invalid. X-ray performed. Expected YES. See `Signs and Symptoms`"
                        )
                    },
                    INVALID_ERROR,
                )
            elif xray_performed == NO and self.cleaned_data.get("chest_xray") != NO:
                raise self.raise_validation_error(
                    {
                        "chest_xray": (
                            "Invalid. X-ray not performed. Expected NO. "
                            "See `Signs and Symptoms`"
                        )
                    },
                    INVALID_ERROR,
                )

    def validate_chest_xray_date(self):
        if self.cleaned_data.get("report_datetime") and self.cleaned_data.get(
            "chest_xray_date"
        ):
            if self.cleaned_data.get("chest_xray_date") < self.consent_datetime.date():
                self.raise_validation_error(
                    {"chest_xray_date": "Invalid. Cannot be before consent date"},
                    INVALID_ERROR,
                )
            elif (
                self.previous_chest_xray_date
                and self.cleaned_data.get("chest_xray_date") < self.previous_chest_xray_date
            ):
                self.raise_validation_error(
                    {
                        "chest_xray_date": (
                            "Invalid. Previous chest x-ray was reported "
                            f"on {formatted_date(self.previous_chest_xray_date)}."
                        )
                    },
                    INVALID_ERROR,
                )

    @property
    def previous_chest_xray_date(self) -> Optional[date]:
        """Returns the date of a previous chest xray, if it exists."""
        try:
            exclude_opts = dict(id=self.instance.id)
        except AttributeError:
            exclude_opts = {}
        qs = (
            self.instance.__class__.objects.filter(subject_visit=self.subject_visit)
            .exclude(
                subject_visit__appointment__timepoint__lt=self.subject_visit.appointment.timepoint,  # noqa
                **exclude_opts,
            )
            .order_by("subject_visit__visit_code", "subject_visit__visit_code_sequence")
        )
        try:
            return qs.last().chest_xray_date
        except AttributeError:
            return None
