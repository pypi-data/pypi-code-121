from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator


class ArvHistoryFormValidator(CrfFormValidator):
    def clean(self) -> None:

        condition = (
            self.cleaned_data.get("on_art_at_crag")
            and self.cleaned_data.get("ever_on_art")
            and (
                self.cleaned_data.get("on_art_at_crag") == YES
                or self.cleaned_data.get("ever_on_art") == YES
            )
        )
        # TODO: if YES, on ART prior to CrAg, compare to CrAg date??
        self.required_if_true(condition, field_required="initial_art_date")

        self.validate_date_against_report_datetime("initial_art_date")

        self.applicable_if_true(
            self.cleaned_data.get("initial_art_date"),
            field_applicable="initial_art_date_estimated",
        )

        self.m2m_applicable_if_true(
            self.cleaned_data.get("initial_art_date"), m2m_field="initial_art_regimen"
        )

        self.m2m_other_specify(
            m2m_field="initial_art_regimen", field_other="initial_art_regimen_other"
        )

        self.applicable_if_true(
            self.cleaned_data.get("initial_art_date"),
            field_applicable="has_switched_art_regimen",
        )

        self.required_if(
            YES, field="has_switched_art_regimen", field_required="current_art_date"
        )
        self.date_not_before(
            "initial_art_date",
            "current_art_date",
            "Invalid. Cannot be before ART start date",
            message_on_field="current_art_date",
        )

        self.date_not_equal(
            "current_art_date",
            "initial_art_date",
            "Invalid. Cannot be equal to the ART start date",
            message_on_field="current_art_date",
        )

        self.validate_date_against_report_datetime("current_art_date")

        self.applicable_if(
            YES,
            field="has_switched_art_regimen",
            field_applicable="current_art_date_estimated",
        )

        self.m2m_applicable_if_true(
            self.cleaned_data.get("current_art_date"), m2m_field="current_art_regimen"
        )

        self.m2m_other_specify(
            m2m_field="current_art_regimen", field_other="current_art_regimen_other"
        )

        # defaulted
        self.date_not_before(
            "current_art_date",
            "defaulted_date",
            "Invalid. Cannot be before current ART start date",
            message_on_field="defaulted_date",
        )

        self.date_not_equal(
            "current_art_date",
            "defaulted_date",
            "Invalid. Cannot be equal to the current ART start date",
            message_on_field="defaulted_date",
        )

        # adherent
        self.applicable_if(
            YES, field="has_switched_art_regimen", field_applicable="is_adherent"
        )
        self.required_if(NO, field="is_adherent", field_required="art_doses_missed")

        # vl
        self.required_if(YES, field="has_viral_load", field_required="viral_load_result")
        self.required_if(YES, field="has_viral_load", field_required="viral_load_date")
        self.applicable_if(
            YES, field="has_viral_load", field_applicable="viral_load_date_estimated"
        )
        self.validate_date_against_report_datetime("viral_load_date")

        # self.date_not_before(
        #     "hiv_diagnosis_date",
        #     "viral_load_date",
        #     "Invalid. Cannot be before HIV diagnosis date.",
        # )

        # cd4
        self.required_if(YES, field="has_cd4", field_required="cd4_result")
        self.required_if(YES, field="has_cd4", field_required="cd4_date")
        self.applicable_if(YES, field="has_cd4", field_applicable="cd4_date_estimated")
        self.validate_date_against_report_datetime("cd4_date")

        # self.date_not_before(
        #     "hiv_diagnosis_date",
        #     "cd4_date",
        #     "Invalid. Cannot be before HIV diagnosis date.",
        # )

        # self.required_if(
        #     YES, field="has_previous_arv_regimen", field_required="previous_arv_regimen"
        # )
        #
        # if self.cleaned_data.get("has_previous_arv_regimen") == NO:
        #     self.date_equal(
        #         "initial_art_date",
        #         "current_art_regimen_start_date",
        #         "Invalid. Expected current regimen date to equal initiation date.",
        #     )
        #
        # self.required_if(
        #     YES, field="has_previous_arv_regimen", field_required="previous_arv_regimen"
        # )
        #
        # self.required_if(
        #     OTHER,
        #     field="previous_arv_regimen",
        #     field_required="other_previous_arv_regimen",
        # )
        #
        # self.required_if(YES, field="on_oi_prophylaxis", field_required="oi_prophylaxis")
        #
        # self.m2m_other_specify(
        #     OTHER, m2m_field="oi_prophylaxis", field_other="other_oi_prophylaxis"
        # )
