from edc_constants.constants import YES
from edc_crf.crf_form_validator import CrfFormValidator


class ClinicalNoteFormValidator(CrfFormValidator):
    def clean(self):
        self.required_if(YES, field="has_comment", field_required="comments")
