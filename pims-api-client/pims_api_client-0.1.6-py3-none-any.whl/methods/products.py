from .base_executor import BaseExecutor
from pims_api_client.schemas.products import ProductFilterItem, ProductList, ProductListFilter, ProductItemList

class ProductsMethodsExecutor(BaseExecutor):

    async def fetch_filters(self):
        response = await self.client.get('pim/api/v1/product/filter')
        return ProductFilterItem.parse_obj(response)

    async def fetch_products(self, data: ProductListFilter):
        response = await self.client.post('pim/api/v1/product/list', data=data.dict())
        return ProductList.parse_obj(response)