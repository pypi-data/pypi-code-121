import time
from types import SimpleNamespace
import pytz

common = SimpleNamespace(dir_eva=None,
                         elbus_path=None,
                         elbus_name=None,
                         bus=None,
                         rpc=None,
                         cli=None,
                         interactive=False,
                         public_key=None,
                         TZ=pytz.timezone(time.tzname[0]))
current_command = SimpleNamespace(json=False,
                                  debug=False,
                                  timeout=5,
                                  exit_code=0)
