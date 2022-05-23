# coding: utf-8
class ADSLTicketConfiguration:
    process_id = "Process-441820b536cb5b9899d12f729e6f5e97"
    activity_id = "Activity-6036295f5d5035663dd7817ab69fdedd"
    type = "Sin Clasificar"
    queue = "Serveis de banda ampla::Provisió ADSL"
    state = "new"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        if otrs_configuration:
            self.process_id = otrs_configuration.adsl_process_id
            self.activity_id = otrs_configuration.adsl_activity_id
            self.type = otrs_configuration.adsl_ticket_type
            self.queue = otrs_configuration.adsl_ticket_queue
            self.state = otrs_configuration.adsl_ticket_state
            # We need to mantain this typo because is in a Tryton model field.
            self.priority = otrs_configuration.adsl_ticket_proprity
