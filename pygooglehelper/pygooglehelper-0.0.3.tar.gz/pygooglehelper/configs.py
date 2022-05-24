from pytconf import Config, ParamCreator


class ConfigAuth(Config):
    """
    Configuration parameters for doing the authentication to google
    """
    force = ParamCreator.create_bool(
        help_string="Should we force creation of a new auth token",
        default=False,
    )
    host = ParamCreator.create_str(
        help_string="The hostname for local redirect. This is http, not https. Passed to run_local_server",
        default="localhost",
    )
    port = ParamCreator.create_int(
        help_string="The port for the local redirect server, passed to run_local_server",
        # default=8080,
        default=0,
    )
    # noinspection PyProtectedMember
    authorization_prompt_message = ParamCreator.create_str(
        help_string="The message to display to tell the user to navigate to the authorization URL",
        # default=InstalledAppFlow._DEFAULT_AUTH_PROMPT_MESSAGE,
        default="",
    )
