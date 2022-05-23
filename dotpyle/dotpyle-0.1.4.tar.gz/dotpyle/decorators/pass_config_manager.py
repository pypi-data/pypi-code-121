from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_config_manager = pass_meta_key(
    constants.CONFIG_MANAGER_PROVIDER,
    doc_description="the :class:`ConfigHandler` object",
)
