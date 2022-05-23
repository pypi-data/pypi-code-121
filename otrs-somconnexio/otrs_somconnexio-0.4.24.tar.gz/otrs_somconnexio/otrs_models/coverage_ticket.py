class CoverageTicket:
    """
    This ticket type lets us check whether a particular address has broadband coverage or not.
    This entity is for read-only purposes only. These tickets are not created or updated in OTRS.
    For this reason, it only implements a getter and the constructor.
    """
    def __init__(self, ticket):
        self.ticket = ticket

    def __getattr__(self, attr):
        """
        With this method we implement a decorator pattern.
        This reads from the response and hides the details of the dynamic fields.
        """
        dynamic_field = self.ticket.response.dynamic_field_get(attr)
        return dynamic_field.value if dynamic_field else ""
