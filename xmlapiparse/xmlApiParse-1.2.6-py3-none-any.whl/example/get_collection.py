from get_auth import current_request
from xmlApiParse.enums import SpecificCollectionsEnum, AllCollectionsEnum


specific_collection_list = current_request.specific_collections_request(SpecificCollectionsEnum.cashes.value)
all_collection_list = current_request.all_collections_request(AllCollectionsEnum.order_list.value)
print(f'Specific collection: {specific_collection_list}')
print(f'All collection: {all_collection_list}')
