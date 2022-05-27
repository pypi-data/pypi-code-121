from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikService import AbstractIkologikService


class CustomerService(AbstractIkologikService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer'

    def get_by_name(self, name: str) -> object:
        # Prepare the search
        search = Search()
        search.add_filter("name", "EQ", [name])
        search.add_order("name", "ASC")
        search.set_pagination(0, 1)

        # Query
        result = self.search(search)
        if result and len(result) == 1:
            return result[0]
        else:
            return None
