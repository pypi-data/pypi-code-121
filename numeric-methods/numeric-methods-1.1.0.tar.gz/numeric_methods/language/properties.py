from numeric_methods.language import LANGUAGE_VARIANTS


class LanguageProperties:
    def __init__(self):
        self.current = "ENGLISH"
        self.variants = LANGUAGE_VARIANTS

    def get_acceptable(self, pattern: str) -> str | None:
        for variant in self.variants:
            if pattern.lower() in variant[0]:
                return variant[1]


class TranslateProperties:
    def __init__(self):
        self.documentation_subscribers = []

    def documentation(self, docs: dict[str, str]):
        def decorator(function):
            self.documentation_subscribers.append(function)
            function.__all_docs__ = docs
            function.__doc__ = docs[LANGUAGE.current]
            return function

        return decorator

    def update(self):
        for subscriber in self.documentation_subscribers:
            subscriber.__doc__ = subscriber.__all_docs__.get(
                LANGUAGE.current,
                f"No documentation found for {LANGUAGE.current} language\n" + subscriber.__all_docs__["ENGLISH"]
            )


LANGUAGE = LanguageProperties()
TRANSLATE = TranslateProperties()
