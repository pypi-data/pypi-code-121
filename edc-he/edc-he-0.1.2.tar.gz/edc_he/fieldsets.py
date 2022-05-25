from django.contrib import admin

education_fieldset = (
    "Education",
    {
        "fields": (
            "education_in_years",
            "education_certificate",
            "education_certificate_other",
            "education_certificate_tertiary",
            "primary_school",
            "primary_school_in_years",
            "secondary_school",
            "secondary_school_in_years",
            "higher_education",
            "higher_education_in_years",
        )
    },
)

education_radio_fields = {
    "higher_education": admin.VERTICAL,
    "marital_status": admin.VERTICAL,
    "primary_school": admin.VERTICAL,
    "secondary_school": admin.VERTICAL,
    "education_certificate": admin.VERTICAL,
}
