from edc_constants.constants import NO, OTHER, YES
from edc_form_validators.form_validator import FormValidator


class PatientTreatmentFormValidator(FormValidator):
    def clean(self):
        self.validate_on_cm_tx()
        self.validate_tb_tx()
        self.validate_steroids()
        self.validate_co_trimoxazole()
        self.validate_antibiotics()
        self.validate_other_drugs()

    def validate_on_cm_tx(self):
        self.applicable_if(YES, field="lp_completed", field_applicable="cm_confirmed")
        self.applicable_if(YES, field="cm_confirmed", field_applicable="on_cm_tx")
        self.applicable_if(YES, field="on_cm_tx", field_applicable="cm_tx_given")
        self.validate_other_specify("cm_tx_given")

    def validate_tb_tx(self):
        self.required_if(YES, field="on_tb_tx", field_required="tb_tx_date")
        self.applicable_if(YES, field="on_tb_tx", field_applicable="tb_tx_date_estimated")
        self.m2m_required_if(YES, field="on_tb_tx", m2m_field="tb_tx_given")
        self.m2m_other_specify(OTHER, m2m_field="tb_tx_given", field_other="tb_tx_given_other")
        self.applicable_if(NO, field="on_tb_tx", field_applicable="tb_tx_reason_no")
        self.validate_other_specify("tb_tx_reason_no")

    def validate_steroids(self):
        self.required_if(YES, field="on_steroids", field_required="steroids_date")
        self.applicable_if(
            YES, field="on_steroids", field_applicable="steroids_date_estimated"
        )
        self.applicable_if(YES, field="on_steroids", field_applicable="steroids_given")
        self.validate_other_specify("steroids_given")
        self.required_if(YES, field="on_steroids", field_required="steroids_course")

    def validate_co_trimoxazole(self):
        self.required_if(YES, field="on_co_trimoxazole", field_required="co_trimoxazole_date")
        self.applicable_if(
            YES,
            field="on_co_trimoxazole",
            field_applicable="co_trimoxazole_date_estimated",
        )

        self.applicable_if(
            NO, field="on_co_trimoxazole", field_applicable="co_trimoxazole_reason_no"
        )
        self.validate_other_specify("co_trimoxazole_reason_no")

    def validate_antibiotics(self):
        self.required_if(YES, field="on_antibiotics", field_required="antibiotics_date")
        self.applicable_if(
            YES, field="on_antibiotics", field_applicable="antibiotics_date_estimated"
        )
        self.m2m_required_if(YES, field="on_antibiotics", m2m_field="antibiotics_given")
        self.m2m_other_specify(
            OTHER, m2m_field="antibiotics_given", field_other="antibiotics_given_other"
        )

    def validate_other_drugs(self):
        self.required_if(YES, field="on_other_drugs", field_required="other_drugs_date")
        self.applicable_if(
            YES, field="on_other_drugs", field_applicable="other_drugs_date_estimated"
        )
        self.m2m_required_if(YES, field="on_other_drugs", m2m_field="other_drugs_given")
        self.m2m_other_specify(
            OTHER, m2m_field="other_drugs_given", field_other="other_drugs_given_other"
        )
