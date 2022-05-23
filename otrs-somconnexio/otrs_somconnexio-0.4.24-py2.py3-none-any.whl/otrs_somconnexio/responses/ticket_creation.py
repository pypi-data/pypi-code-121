class OTRSCreationTicketResponse():
    """
    This class is to map in object interface the response of Ticket creation call to the OTRS web
    service using the library PyOTRS.
    Transform the dict returned by the PyOTRS client in a object with a friendly interface.
    Dict returned:
        {'TicketNumber': '2018121900000025', 'TicketID': '1135', 'ArticleID': '3200'}
    """
    def __init__(self, otrs_response):
        self.response = otrs_response

    @property
    def id(self):
        return self.response.get('TicketID')

    @property
    def number(self):
        return self.response.get('TicketNumber')

    # Unused property.
    @property
    def article_id(self):
        return self.response.get('ArticleID')
