from django import forms
from edc_constants.constants import TERTIARY, YES


class HeEducationFormValidatorMixin:
    """A mixin to be declared with `CrfFormValidatorMixin` and `FormValidator`."""

    def clean_education(self):
        """Works with fields from the HealthEconomicsEducationModeMixin"""
        has_education_in_years = (
            self.cleaned_data.get("education_in_years") is not None
            and self.cleaned_data.get("education_in_years") > 0
        )
        education_in_years = self.cleaned_data.get("education_in_years")
        if (
            has_education_in_years
            and self.age_in_years
            and education_in_years > self.age_in_years
        ):
            raise forms.ValidationError(
                {
                    "education_in_years": (
                        "Cannot exceed subject's age. "
                        f"Got subject is {self.age_in_years} years old."
                    )
                }
            )
        self.applicable_if_true(
            has_education_in_years, field_applicable="education_certificate"
        )
        self.validate_other_specify(
            field="education_certificate", other_specify_field="education_certificate_other"
        )
        self.required_if(
            TERTIARY,
            field="education_certificate",
            field_required="education_certificate_tertiary",
        )

        self.applicable_if_true(has_education_in_years, field_applicable="primary_school")
        self.required_if(
            YES,
            field="primary_school",
            field_required="primary_school_in_years",
            field_required_evaluate_as_int=True,
        )
        self.applicable_if_true(has_education_in_years, field_applicable="secondary_school")
        self.required_if(
            YES,
            field="secondary_school",
            field_required="secondary_school_in_years",
            field_required_evaluate_as_int=True,
        )
        self.applicable_if_true(has_education_in_years, field_applicable="higher_education")
        self.required_if(
            YES,
            field="higher_education",
            field_required="higher_education_in_years",
            field_required_evaluate_as_int=True,
        )
