def exception_handler(client_name: str):
    def client_wrapper(func):
        def inner_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise Exception(
                    f"Client '{client_name}' failed to fetch with error:\n{e}"
                )

        return inner_function

    return client_wrapper
