from fluentcheck.assertions_is.base_is import IsBase


class __IsLists(IsBase):
    @property
    def is_list(self) -> "Is":
        self.check.is_list()
        return self

    @property
    def not_list(self) -> "Is":
        self.check.is_not_list()
        return self

    def list_contains(self, char) -> "Is":
        self.check.is_in_list(char)
        return self

    def list_not_contains(self, char) -> "Is":
        self.check.is_not_in_list(char)
        return self
