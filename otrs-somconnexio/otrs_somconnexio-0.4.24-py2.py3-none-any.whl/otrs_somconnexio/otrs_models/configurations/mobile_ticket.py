# coding: utf-8
class MobileTicketConfiguration:
    process_id = "Process-325351399237c1e69144b17e471b1b51"
    activity_id = "Activity-90f09a366cd9426695ef0e21faeb4ed2"
    type = "Petición"
    queue = "Serveis mòbil::Provisió mòbil"
    state = "new"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        if otrs_configuration:
            self.process_id = otrs_configuration.mobile_process_id
            self.activity_id = otrs_configuration.mobile_activity_id
            self.type = otrs_configuration.mobile_ticket_type
            self.queue = otrs_configuration.mobile_ticket_queue
            self.state = otrs_configuration.mobile_ticket_state
            self.priority = otrs_configuration.mobile_ticket_priority
