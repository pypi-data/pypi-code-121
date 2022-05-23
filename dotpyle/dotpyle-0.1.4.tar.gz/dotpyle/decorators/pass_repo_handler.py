from click.decorators import pass_meta_key

from dotpyle.utils import constants

pass_repo_handler = pass_meta_key(
    constants.REPO_HANDLER_PROVIDER,
    doc_description="the :class:`RepoHandler` object",
)
