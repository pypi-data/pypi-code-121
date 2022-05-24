import json


def to_camelcase(text):
    return ''.join(word.title() if i else word for i, word in enumerate(text.split('_')))


class Margins(dict):
    top: int = 0
    bottom: int = 0
    left: int = 0
    right:  int = 0

    def __init__(self):
        dict.__init__(self, top=0, bottom=0, left=0, right=0)

    def items(self):
        return [('top', self.top),
                ('bottom', self.bottom),
                ('left', self.left),
                ('right', self.right)]


class Clip(dict):
    x: float = 0
    y: float = 0
    width: float = 0
    height:  float = 0
    scale:  float = 0

    def __init__(self):
        dict.__init__(self, x=0, y=0, width=0, height=0, scale=0)

    def items(self):
        return [('x', self.x),
                ('y', self.y),
                ('width', self.width),
                ('height', self.height),
                ('scale', self.scale)]


class KeyValue(dict):
    name: str = None
    value: str = None

    def __init__(self):
        dict.__init__(self, name=None, value=None)

    def items(self):
        vals = []
        if not self.name or not self.value:
            return vals
        return [
            ('name', self.name),
            ('value', self.value)
        ]


class Flow(dict):
    def __init__(self, action: str,
                 selector: str = None,
                 name: str = None,
                 value: str = None,
                 timeout: int = None,
                 eval_selector: bool = None,
                 eval_value: bool = None):
        dict.__init__(self, action=action)

        self.action: str = action
        self.selector: str = selector
        self.name: str = name
        self.value: str = value
        self.timeout: int = timeout
        self.eval_selector: bool = eval_selector
        self.eval_value: bool = eval_value

    def items(self):
        vals = []
        if not self.action:
            return []

        vals.append(('action', self.action))
        if self.name:
            vals.append(('name', self.name))
        if self.selector:
            vals.append(('selector', self.selector))
        if self.value:
            vals.append(('value', self.value))
        if self.timeout:
            vals.append(('timeout', self.timeout))
        if self.eval_selector:
            vals.append(('evalSelector', self.eval_selector))
        if self.eval_value:
            vals.append(('evalValue', self.eval_value))
        return vals


class Option:
    """Option for `api.browserlify.com`
    https://browserlify.com/docs/apis/token.html    
    """

    def __init__(self, token: str) -> None:
        self._token: str = token

        self.url: str = ''
        self.paper: str = ''
        self.region: str = ''
        self.page_limit: int = 0
        self.wait_load: int = 0
        self.delay: int = 0
        self.device: str = ''
        self.headers: list[KeyValue] = []
        self.cookies: list[KeyValue] = []
        self.proxy: str = ''
        self.disabled_image: bool = False
        self.enabled_adblock: bool = False
        self.asurl: bool = False

        self.flows: list[Flow] = []
        self.context: dict = None
        self.userdata: dict = None
        self.callback: str = ''

        # PDF option
        self.full_page: bool = False
        self.print_background: bool = False
        self.landscape: bool = False
        self.width: int = None
        self.height: int = None
        self.margins: Margins = None
        self.header: str = ''
        self.footer: str = ''

        # PDF Protection
        self.author: str = ''
        self.user_password: str = ''
        self.owner_password: str = ''
        self.no_print: bool = False
        self.no_copy: bool = False
        self.no_modify: bool = False

        # screenshot
        self.format: str = ''
        self.clip: Clip = None
        self.flip: bool = False
        self.flop: bool = False
        self.rotate: int = 0
        self.quality: int = 0

    def omitempty(self, k):
        v = getattr(self, k)

        if 'method' in type(v).__name__:
            return True

        if v:
            return False
        return True

    @property
    def payload(self) -> dict:
        vals = {
            'token': self._token,
        }
        for k in dir(self):
            if k.startswith('_') or k == 'payload':
                continue

            if not self.omitempty(k):
                vals[to_camelcase(k)] = getattr(self, k)
        return vals
