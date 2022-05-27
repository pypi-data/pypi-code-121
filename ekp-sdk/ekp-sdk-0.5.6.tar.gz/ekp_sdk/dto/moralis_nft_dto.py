from typing import TypedDict


class MoralisNftDto(TypedDict, total=False):
    '''
    :example
    {
      "token_address": "0x05f0d89931eb06d4596af209de4a9779cef73cde",
      "token_id": "20300",
      "owner_of": "0x553a463f365c74eda00b7e5aaf080b066d4ca03c",
      "block_number": "17996141",
      "block_number_minted": "17996141",
      "token_hash": "ebe82b4820e228db95660090c8572adc",
      "amount": "1",
      "contract_type": "ERC721",
      "name": "MetaBombHero",
      "symbol": "MBH",
      "token_uri": "https://metabomb.io/v1/hero/20300",
      "metadata": null,
      "synced_at": "2022-05-21T13:50:01.211Z",
      "last_token_uri_sync": "2022-05-21T13:50:00.360Z",
      "last_metadata_sync": "2022-05-21T13:50:01.211Z"
    }
    '''

    token_address: str
    token_id: str
    owner_of: str
    block_number: str
    block_number_minted: str
    token_hash: str
    amount: str
    contract_type: str
    name: str
    symbol: str
    token_uri: str
    metadata: str
    synced_at: str
    last_token_uri_sync: str
    last_metadata_sync: str