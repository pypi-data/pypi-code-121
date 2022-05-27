from jira import JIRA
from config import jira_url, jira_username, jira_password


class jira:

    def __init__(self, username=None, password=None, url=None):
        try:
            self.jira = JIRA(basic_auth=(jira_username, jira_password),
                             options={'server': jira_url})
            self.enabled = True
            print('jira: enabled')
        except:
            print('jira: disabled (could not connect)')
            self.enabled = False

    def raise_ticket(self, system, message):

        print('RAISING A TICKET')

        issue_dict = {
            'project': {'id': 10001},
            'summary': f'PSS Alert: {system}',
            'description': message,
            'issuetype': {'name': 'Incident'},
            "customfield_12200":  [{"key": "SC-21303"}],
            "customfield_14503":  [{"key": "SC-21669"}]
        }

        if self.enabled:
            ticket_number = self.jira.create_issue(fields=issue_dict)
        else:
            print('Unable to connect to Jira.')
            ticket_number = ''
        return ticket_number
