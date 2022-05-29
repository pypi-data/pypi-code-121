from vinca import _cli_objects

def run():
    from fire import Fire
    Fire(component=_cli_objects, name='vinca')
