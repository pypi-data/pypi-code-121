from typing import List, TypedDict


class Web3LogDto(TypedDict, total=False):
    '''
    :example
    {
        'address': '0x2076626437c3Bb9273998A5E4F96438aBE467F1C',
        'topics': ['0xe04eefd2590e9186abb360fc0848592add67dcef57f68a4110a6922c4793f7e0',
                    '0x00000000000000000000000000000000000000000000000000000000000000a4',
                    '0x000000000000000000000000553a463f365c74eda00b7e5aaf080b066d4ca03c'
                    ],
        'data':
        '0x00000000000000000000000000000000000000000000003c33c1937564800000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000084d5442482d505245000000000000000000000000000000000000000000000000',
        'blockNumber': 17937471,
        'transactionHash': '0xe4896e51f2508f1b817ea1e5a179e3cee61bdc2104f469443822db8cd75cb1ec',
        'transactionIndex': 45,
        'blockHash': '0x2b6d3df7b0e0ce5d46814a684ad3a54a2bbf719cca6f2e272ae88ab3143aabf9',
        'logIndex': 203,
        'removed': False
    }
    '''
    blockNumber: int
    blockHash: str
    removed: bool
    transactionLogIndex: int
    address: str
    data: str
    topics: List[str]
    transactionHash: str
    transactionIndex: int
    logIndex: int
