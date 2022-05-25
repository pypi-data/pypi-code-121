from edc_crf.crf_form_validator import CrfFormValidator
from edc_microbiology.form_validators import BloodCultureSimpleFormValidatorMixin


class BloodCultureFormValidator(
    BloodCultureSimpleFormValidatorMixin,
    CrfFormValidator,
):
    def clean(self):
        self.validate_blood_culture()
