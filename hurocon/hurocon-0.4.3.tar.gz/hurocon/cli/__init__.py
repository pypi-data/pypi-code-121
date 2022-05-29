def run_cli():
    from .root import cli

    # Initialize CLI modules
    from . import auth, config, device, sms, lte

    cli()
