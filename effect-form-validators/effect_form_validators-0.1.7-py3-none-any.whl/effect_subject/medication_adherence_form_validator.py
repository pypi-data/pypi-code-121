from edc_adherence.form_validator_mixin import MedicationAdherenceFormValidatorMixin
from edc_crf.crf_form_validator import CrfFormValidator


class MedicationAdherenceFormValidator(
    MedicationAdherenceFormValidatorMixin, CrfFormValidator
):
    pass
