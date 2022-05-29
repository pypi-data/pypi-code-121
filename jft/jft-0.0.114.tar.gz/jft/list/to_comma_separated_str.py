f = lambda _list: ','.join([f"'{_}'" for _ in _list])
t = lambda: f(['abc', 'def', 'ghi']) == "'abc','def','ghi'"