from directory_api_client.base import AbstractAPIClient

url_company_by_ch_id = '/testapi/company/{companies_house_number}/'
url_published_companies = '/testapi/companies/published/'


class DirectoryTestAPIClient(AbstractAPIClient):
    def get_company_by_ch_id(self, ch_id, authenticator=None):
        return self.get(
            url=url_company_by_ch_id.format(companies_house_number=ch_id),
            authenticator=authenticator,
        )

    def delete_company_by_ch_id(self, ch_id, authenticator=None):
        return self.delete(
            url=url_company_by_ch_id.format(companies_house_number=ch_id),
            authenticator=authenticator,
        )

    def get_published_companies(self, *, limit=None, minimal_number_of_sectors=None, authenticator=None):
        params = {}
        if limit:
            params['limit'] = limit
        if minimal_number_of_sectors:
            params['minimal_number_of_sectors'] = minimal_number_of_sectors
        return self.get(
            url=url_published_companies,
            params=params,
            authenticator=authenticator,
        )
