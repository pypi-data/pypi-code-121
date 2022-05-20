try:
    import requests
    import functools
    from requests.adapters import HTTPAdapter, Retry

    USER_AGENT = lambda: "checker"

    def requests_with_retries(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(400, 404, 500, 502),
        default_timeout=5,
        session=None,
    ):
        requests.adapters.DEFAULT_POOL_TIMEOUT = default_timeout
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.headers.update({"User-Agent": USER_AGENT()})
        session.mount('http://', adapter)

        patch_methods_with_default_timeout(session, default_timeout)

        return session

    # why should I do that?...
    def patch_methods_with_default_timeout(session, timeout):
        for method in ('get', 'options', 'head', 'post', 'put', 'patch', 'delete'):
            setattr(session, method, functools.partial(getattr(session, method), timeout=timeout))

except ImportError:
    pass
