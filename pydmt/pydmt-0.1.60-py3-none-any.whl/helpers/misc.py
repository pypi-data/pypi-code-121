def get_version_str():
    # pylint: disable=import-outside-toplevel
    import config.version
    return ".".join(str(x) for x in config.version.tup)
