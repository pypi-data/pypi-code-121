from edc_constants.constants import NOT_APPLICABLE, OTHER, PRIMARY, SECONDARY, TERTIARY

EDUCATION_CERTIFICATES_CHOICES = (
    (PRIMARY, "Primary Certificate"),
    (SECONDARY, "Secondary Certificate"),
    (TERTIARY, "post-Secondary/Tertiary/College"),
    (OTHER, "Other, please specify ..."),
    (NOT_APPLICABLE, "Not applicable, never went to school"),
)
