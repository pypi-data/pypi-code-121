from django import forms
from edc_constants.constants import (
    HEADACHE,
    IN_PERSON,
    NO,
    NOT_APPLICABLE,
    OTHER,
    PATIENT,
    UNKNOWN,
    VISUAL_LOSS,
    YES,
)
from edc_constants.disease_constants import (
    CN_PALSY_LEFT_OTHER,
    CN_PALSY_RIGHT_OTHER,
    FOCAL_NEUROLOGIC_DEFICIT_OTHER,
)
from edc_constants.utils import get_display
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR, NOT_APPLICABLE_ERROR
from edc_visit_schedule.utils import is_baseline
from edc_visit_tracking.choices import ASSESSMENT_TYPES, ASSESSMENT_WHO_CHOICES


class SignsAndSymptomsFormValidator(CrfFormValidator):

    reportable_fields = ["reportable_as_ae", "patient_admitted"]

    def clean(self) -> None:
        self.validate_any_sx_unknown()

        self.validate_current_sx()

        self.m2m_other_specify(OTHER, m2m_field="current_sx", field_other="current_sx_other")

        self.applicable_if(YES, field="any_sx", field_applicable="cm_sx")

        self.validate_current_sx_gte_g3()

        self.m2m_other_specify(
            OTHER, m2m_field="current_sx_gte_g3", field_other="current_sx_gte_g3_other"
        )

        self.validate_current_sx_other_specify_fields()

        self.validate_investigations_performed()

        self.validate_reporting_fieldset()

    def in_person_visit(self):
        return self.cleaned_data.get("subject_visit").assessment_type == IN_PERSON

    @staticmethod
    def _get_sisx_display_value(key):
        return key

    def validate_any_sx_unknown(self):
        error_msg = ""
        if self.cleaned_data.get("any_sx") == UNKNOWN:
            if self.in_person_visit():
                error_msg = (
                    "Invalid. Cannot be 'Unknown' "
                    f"if this is an '{get_display(ASSESSMENT_TYPES,IN_PERSON)}' visit."
                )
            elif self.cleaned_data.get("subject_visit").assessment_who == PATIENT:
                error_msg = (
                    "Invalid. Cannot be 'Unknown' "
                    f"if spoke to '{get_display(ASSESSMENT_WHO_CHOICES, PATIENT)}'."
                )

            if error_msg:
                raise self.raise_validation_error({"any_sx": error_msg}, INVALID_ERROR)

    def validate_current_sx(self):
        if self.cleaned_data.get("any_sx") == YES:
            self.m2m_selections_not_expected(NOT_APPLICABLE, m2m_field="current_sx")
        elif self.cleaned_data.get("any_sx") in [NO, UNKNOWN]:
            self.m2m_selection_expected(
                NOT_APPLICABLE,
                m2m_field="current_sx",
                error_msg=f"Expected '{self._get_sisx_display_value(NOT_APPLICABLE)}' only.",
            )

        self.m2m_single_selection_if(NOT_APPLICABLE, m2m_field="current_sx")

    def _get_selection_keys(self, field_name):
        if self.cleaned_data.get(field_name):
            return [obj.name for obj in self.cleaned_data.get(field_name)]
        return []

    def validate_current_sx_gte_g3(self):
        if self.cleaned_data.get("any_sx") in [NO, UNKNOWN]:
            self.m2m_selection_expected(
                NOT_APPLICABLE,
                m2m_field="current_sx_gte_g3",
                error_msg=f"Expected '{self._get_sisx_display_value(NOT_APPLICABLE)}' only.",
            )

        self.m2m_single_selection_if(NOT_APPLICABLE, m2m_field="current_sx_gte_g3")

        # G3 selections, if specified, should come from the original symptoms list
        sx_gte_g3_selections = self._get_selection_keys("current_sx_gte_g3")
        sx_selections = self._get_selection_keys("current_sx")

        if sx_gte_g3_selections != [NOT_APPLICABLE] and [
            sx for sx in sx_gte_g3_selections if sx not in sx_selections
        ]:
            raise forms.ValidationError(
                {
                    "current_sx_gte_g3": (
                        "Invalid selection. "
                        "Must be from above list of signs and symptoms, "
                        f"or '{self._get_sisx_display_value(NOT_APPLICABLE)}' if none of the "
                        "symptoms are Grade 3 or above"
                    )
                }
            )

    def validate_current_sx_other_specify_fields(self):
        self.m2m_other_specify(
            HEADACHE, m2m_field="current_sx", field_other="headache_duration"
        )
        self.m2m_other_specify(
            CN_PALSY_LEFT_OTHER,
            m2m_field="current_sx",
            field_other="cn_palsy_left_other",
        )
        self.m2m_other_specify(
            CN_PALSY_RIGHT_OTHER,
            m2m_field="current_sx",
            field_other="cn_palsy_right_other",
        )
        self.m2m_other_specify(
            FOCAL_NEUROLOGIC_DEFICIT_OTHER,
            m2m_field="current_sx",
            field_other="focal_neurologic_deficit_other",
        )
        self.m2m_other_specify(
            VISUAL_LOSS, m2m_field="current_sx", field_other="visual_field_loss"
        )

    def validate_investigations_performed(self):
        for fld in ["xray_performed", "lp_performed", "urinary_lam_performed"]:
            self.applicable_if_true(
                condition=self.in_person_visit(),
                field_applicable=fld,
                not_applicable_msg=(
                    "Invalid. This field is not applicable if this is not "
                    f"an '{get_display(ASSESSMENT_TYPES,IN_PERSON)}' visit."
                ),
            )

    def validate_reporting_fieldset(self):
        # hospitalization not reportable at baseline
        baseline = is_baseline(self.cleaned_data.get("subject_visit"))
        for fld in self.reportable_fields:
            if baseline and self.cleaned_data.get(fld) != NOT_APPLICABLE:
                raise self.raise_validation_error(
                    {fld: "Not applicable at baseline."}, NOT_APPLICABLE_ERROR
                )

        if not baseline:
            self.applicable_if(YES, field="any_sx", field_applicable="reportable_as_ae")

            sx_gte_g3_selections = self._get_selection_keys("current_sx_gte_g3")
            if (
                sx_gte_g3_selections == [NOT_APPLICABLE]
                and self.cleaned_data.get("reportable_as_ae") == YES
            ):
                raise forms.ValidationError(
                    {
                        "reportable_as_ae": (
                            "Invalid selection. "
                            "Expected 'No', if no symptoms at Grade 3 or above were reported."
                        )
                    }
                )
            if (
                sx_gte_g3_selections != [NOT_APPLICABLE]
                and self.cleaned_data.get("reportable_as_ae") == NO
            ):
                raise forms.ValidationError(
                    {
                        "reportable_as_ae": (
                            "Invalid selection. "
                            "Expected 'Yes', if symptoms Grade 3 or above were reported."
                        )
                    }
                )

            self.applicable_if(YES, field="any_sx", field_applicable="patient_admitted")
