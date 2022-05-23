from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_config_handler = pass_meta_key(
    constants.CONFIG_HANDLER_PROVIDER,
    doc_description="the :class:`ConfigManager` object",
)
