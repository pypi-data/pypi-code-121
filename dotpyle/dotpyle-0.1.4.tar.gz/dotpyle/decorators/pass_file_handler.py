from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_file_handler = pass_meta_key(
    constants.FILE_HANDLER_PROVIDER,
    doc_description="the :class:`FileHandler` object",
)
