class URLRegistrar:
    def __init__(self):
        self._urls = dict()

    def register(self, url: str, func):
        self._urls[url] = func

    def get_urls(self):
        return self._urls

    def route(self, url: str):
        def inner(func):
            print(f"Binding {func.__name__} to url '{url}'")
            self.register(url, func)

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        return inner
