class Commit:
    def __init__(self, sha: str, message: str) -> None:
        self.__sha = sha
        self.__message = message

    @property
    def sha(self) -> str:
        return self.__sha

    @property
    def message(self) -> str:
        return self.__message

    def __repr__(self) -> str:
        return f"Commit [sha={self.__sha}, message={self.__message}]"
