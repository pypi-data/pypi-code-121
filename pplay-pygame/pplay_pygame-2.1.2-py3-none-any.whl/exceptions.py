class WindowNotInitialized(ValueError):
    def __init__(self, field: str):
        self.field = field

    def __str__(self):
        return (
            f"Could not return field {self.field}, because the window has "
            f"not yet been initialized."
        )
