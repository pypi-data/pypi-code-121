from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class BatchService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer, installation) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/batch'

    def get_by_code(self, customer: str, installation: str, batch_type: str, code: str) -> object:
        # Prepare the search
        search = Search()
        search.add_filters([("batchType", "EQ", [batch_type]), ("code", "EQ", [code])])
        search.add_order("batchType", "ASC")
        search.set_pagination(0, 1)

        # Query
        result = self.search(customer, installation, search)
        if result and len(result) == 1:
            return result[0]
        else:
            return None
