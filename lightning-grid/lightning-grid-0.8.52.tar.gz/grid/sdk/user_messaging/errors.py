def user_not_authenticated() -> str:
    """Technically this catches either un-authenticated, or blocked users.

     This is used for both cases since we don't want users to know they have been blocked.
    """
    return (
        "You are either not logged into grid, or are not authorized to check "
        "the requested resource. Please login via the `grid login` command."
    )


def datastore_invalid_source(source: str) -> str:
    return (
        f'Unknown Source type for {source}. We accept local file paths, '
        f'HTTP/HTTPS URLs or Amazon S3 Buckets (s3://foo/bar/). Please '
        f'check your input and try again'
    )


def datastore_invalid_no_copy_option(source: str) -> str:
    return (
        f"The no-copy option was passed when creating a datastore from {source}. "
        "This option is only valid for s3 buckets. Please consider removing the "
        "flag or ensuring that your path starts with `s3://`"
    )


def datastore_local_source_dir_is_empty(source) -> str:
    return f"The directory {source} is empty. To create a datastore, atleast one file must exist."


def datastore_upload_process_cancelled() -> str:
    return (
        "You've cancelled your upload, but your progress has been saved. You can run: \n"
        "\n"
        "$ grid datastore resume\n"
        "\n"
        "to resume your upload."
    )


def datastore_s3_source_does_not_end_in_slash(source: str) -> str:
    return (
        f"The {source} S3 URL must end in a '/' in order to specify a directory. "
        f"Single-file S3 datastores are not currently supported. Please rerun your "
        f"last commandand add a '/' to the end of {source} so that it looks like: "
        f"{source}/"
    )
