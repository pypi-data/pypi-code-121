from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.services.AbstractIkologikService import AbstractIkologikService


class DomainService(AbstractIkologikService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/domain'
