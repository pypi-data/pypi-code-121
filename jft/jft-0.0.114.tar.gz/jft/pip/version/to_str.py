f = lambda v: f"{v['major']}.{v['minor']}.{v['patch']}"
t = lambda: '1.2.3' == f({'major': 1, 'minor': 2, 'patch': 3})
