from .argument import Argument

APP = "trans"

EXIT = "exit()"
CLEAR = "clear()"

FIRST_LANG = "cs"
SECOND_LANG = "en"
FIRST_LANG_NAME = "first"
SECOND_LANG_NAME = "second"
LANGUAGE_NAME = "languages"
SETTINGS_FILE = "settings.cfg"

INPUT = ">>> "
LOADING = "..."
LAST_LINE = "\r"

ERROR_MESSAGE = "This a word, not's exist in the google, in a list words."
ARGUMENTS = [

    Argument( 'h', 'help', 'Print this help text and exit' ),
    Argument( 'm', 'message', 'The message is for translation.' ),
    Argument( 'f', 'first', 'Set a first language (example: "cs" or "en" ).' ),
    Argument( 's', 'second', 'Set a second language (example: "en" or "cs" ).' )
]
