from . import constants

def debug( message ):
    """Print message in a debug mode."""
    
    get_root().prints.debug( message )


def get_root():
    return constants.ROOT
