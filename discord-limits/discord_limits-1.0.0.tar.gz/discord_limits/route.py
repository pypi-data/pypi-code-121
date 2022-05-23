from urllib.parse import quote as _uriquote
class Route:
    BASE = 'https://discord.com/api/v9'

    def __init__(self, method, path, **parameters):
        self.path = path
        self.method = method
        url = path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url = url

        # major parameters:
        self.channel_id = parameters.get('channel_id')
        self.guild_id = parameters.get('guild_id')
        self.webhook_id = parameters.get('webhook_id')
        self.webhook_token = parameters.get('webhook_token')