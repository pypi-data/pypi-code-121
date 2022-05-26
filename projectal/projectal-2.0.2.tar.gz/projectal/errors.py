from requests import HTTPError

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError


class LoginException(Exception):
    """Failed to log in with the credentials provided."""
    pass

class UnsupportedException(Exception):
    """The API endpoint is not available for this entity."""
    pass

class ProjectalException(Exception):
    """
    The API request failed. This exception will extract the specific
    error from the Projectal response if it can find one. To assist
    in debugging, the response object is attached to the exception
    which you may inspect for more precise details.

    In case of failure of a bulk operation, only the error clue for
    the first failure is shown. A counter is included to show how
    many failed (i.e.: 1 of 25).
    """
    def __init__(self, response, reason_message=None):
        """
        `response`: the response object

        `reason_message`: if provided, will use this message as the cause
        of failure instead of assuming it was a misuse of the API.
        """
        self.response = response
        self.url = response.url
        self.body = response.request.body
        self.json = None
        self.message = None
        code = response.status_code

        try:
            self.json = response.json()
        except JSONDecodeError:
            pass

        # Did we get a 200 response but (manually) raised anyway? The consumer
        # method considered this an error. If it did, it MUST tell us why in
        # the message parameter. We pass this message on to the user.
        if code != 207:
            try:
                response.raise_for_status()
                if reason_message:
                    self.message = reason_message
                else:
                    self.message = 'Unexpected response (API client error)'
            except HTTPError:
                pass

        if code == 400 and not self.json:
            self.message = 'Client request error'
        if code == 500:
            self.message = 'Internal server error'
        if self.json and (code == 400 or code == 422 or code == 207):
            if self.json.get('feedbackList', False):
                self.feedback = [f for f in self.json.get('feedbackList', [])] or None
                clue = [f['clue'] for f in self.json['feedbackList'] if f['clue'] not in ['OK', 'Created']]
                hint = [f['hint'].replace('\'', '\"') for f in self.json['feedbackList'] if f['clue'] not in ['OK', 'Created']]
                if len(clue) == 1:
                    clue_part = " - Clue: {} ({})".format(clue[0], hint[0])
                else:
                    clue_part = " - Clue 1 of {}: {} ({})".format(len(clue), clue[0], hint[0])
            else:
                # No feedback list, but clue in top-leel of dict
                clue = self.json['jobClue']['clue']
                hint = self.json['jobClue']['hint'].replace('\'', '\"')
                clue_part = ' - Clue: {} ({})'.format(clue, hint)
            self.message = self.json['status'] + clue_part

        if not self.message:
            self.message = "Request error: {}".format(code)
        super().__init__(self.message)


class ProjectalVersionException(Exception):
    """
    The Projectal server version is incompatible with the version
    of this library.
    """
    pass

