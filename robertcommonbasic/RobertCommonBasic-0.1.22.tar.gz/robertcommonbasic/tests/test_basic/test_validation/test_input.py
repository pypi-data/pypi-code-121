from robertcommonbasic.basic.validation.input import *

config = {'interval': '0.3', 'reg': ''}
reg = ensure_not_none_of('reg', config, str)
interval = ensure_not_none_of('interval', config, float)
print(interval)