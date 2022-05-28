"""
Slack handler.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

from logging import Handler, getLevelName

try:
    import requests
except ImportError:
    requests = None

# SlackLogifireHandler

class SlackLogifireHandler(Handler):
    """
    Send log records to a Slack.
    """

    def __init__(self,
                 token,
                 channel='#general',
                 mention_users='',
                 icon_emoji=':fire:',
                 bot_name='CRIT',
                 ):
        """
        Init.
        Args:
            token (str): Slack API token
            channel (str): channel name like '#channel' or '@private'
            mention_users (str): users for mention '@user1 @user2 @userN'
            icon_emoji (str):
            bot_name (str):
        """
        assert requests is not None, "module \"requests\" is required"

        Handler.__init__(self)

        self.token = token
        self.channel = channel
        self.mention_users = mention_users
        self.icon_emoji = icon_emoji
        self.bot_name = bot_name

    def emit(self, record):
        """
        Emit a record.
        """
        try:
            msg = self.format(record)

            text = '```{}```'.format(msg.replace('```', '???'))
            text = '{} {}'.format(self.mention_users, text).lstrip()

            data = dict(
                token=self.token,
                channel=self.channel,
                icon_emoji=self.icon_emoji,
                username=self.bot_name,
                parse='full',
                text=text,
            )

            requests.post('https://slack.com/api/chat.postMessage', data=data)

        except RecursionError:  # refs https://bugs.python.org/issue36272
            raise
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = getLevelName(self.level)
        return '<%s %s[bot=%s, mention=%s](%s)>' % \
               (self.__class__.__name__, self.channel, self.bot_name, self.mention_users, level)
