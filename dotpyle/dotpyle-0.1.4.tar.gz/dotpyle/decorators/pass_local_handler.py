from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_local_handler = pass_meta_key(
    constants.LOCAL_FILE_HANDLER_PROVIDER,
    doc_description="the :class:`LocalFileHandler` object",
)
