class Error(Exception):
    """Main error class to be inherited in all app's custom errors."""
    def expose(self) -> dict:
        return {"error": {
            "name": self.__class__.__name__,
            "message": "; ".join(self.args)
        }}
