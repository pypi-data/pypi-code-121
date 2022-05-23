from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_logger = pass_meta_key(
    constants.LOGGER_PROVIDER,
    doc_description="the :class:`Logger` object",
)
