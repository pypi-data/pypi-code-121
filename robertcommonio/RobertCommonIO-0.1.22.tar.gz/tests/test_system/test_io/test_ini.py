from robertcommonio.system.io.ini import INIConfig, INIAccessor

def test_ini():
    config = INIConfig(PATH='test.ini', PARAMS={'HTTP_SERVER': {'HTTP_HOST': '0.0.0.0', 'HTTP_PORT': 5002}})
    accessor = INIAccessor(config)
    assert accessor.get('HTTP_HOST', str) != '0.0.0.0'
    accessor.set('HTTP_HOST', '127.0.0.1')
    assert accessor.get('HTTP_HOST', str) == '127.0.0.1'
    print()

test_ini()