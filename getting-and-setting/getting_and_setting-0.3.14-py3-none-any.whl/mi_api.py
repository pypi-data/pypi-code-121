''' mi_api.py
The mi_api file, part of the getting-and-setting package contains functions
combines functions from parser.py and request.py to provide abstract tools to
work with the MI Api.

Author: Kim Timothy Engh
Email: kim.timothy.engh@epiroc.com
Licence: GPLv3. See ../LICENCE '''

from typing import Union
from typing import Optional

from functools import lru_cache

from . mi_models import MiRecords
from . mi_models import MiPrograms
from . mi_models import MiProgramMetadata
from . mi_models import MiTransactionMetadata
from . mi_models import MiError

from . mi_parser import mi_parse_execute
from . mi_parser import mi_parse_metadata
from . mi_parser import mi_parse_programs

from . mi_request import mi_request_metadata
from . mi_request import mi_request_execute
from . mi_request import mi_request_programs

from . mi_models import Endpoint

from . mi_endpoints import mi_endpoint_get

class ArgumentError(Exception):
    '''Argument are not aligned with expectations'''




class MiApi:
    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd

    def execute(self, program: str, transaction: str, **kwargs) -> Union[MiRecords, MiError]:
        return mi_parse_execute(
            mi_request_execute(
                self.host,
                self.port,
                self.usr,
                self.pwd,
                program,
                transaction,
                **kwargs
            ).content
        )

    def program_list(self) -> Union[MiPrograms, MiError]:
        return mi_parse_programs(
            mi_request_programs(
                self.host,
                self.port,
                self.usr,
                self.pwd
            ).content
        )

    def program_meta(self, program: str) -> Union[MiProgramMetadata, MiError]:
        return mi_parse_metadata(
            mi_request_metadata(
                self.host,
                self.port,
                self.usr,
                self.pwd,
                program
            ).content
        )

    def transaction_meta(self, program: Optional[str], transaction: Optional[str]) -> Union[MiTransactionMetadata, MiError, None]:
        program_meta = self.program_meta(program)

        if isinstance(program_meta, MiError):
            return program_meta

        for record in program_meta.transactions:
            if record.transaction == transaction:
                return record
        else:
            return None


@lru_cache(10)
def mi_meta(endpoint: str, program: Optional[str] = None, transaction: Optional[str] = None) -> Union[MiPrograms, MiProgramMetadata, MiTransactionMetadata, MiError]:
    ''' Fetch metatdata from the API. Wrapper function for the following functions:
    - mi_meta_list
    - mi_meta_program
    - mi_meta_transactions

    :param endpoint - the name of the enpoint
    :param program - M3 program name
    :param transaction - Program transaction

    Valid combinations of arguments are:
    
    case1: endpoint and not program and not transaction -> MiPrograms
    case2: endpoint and program and not transaction -> MiProgramMetadata
    case3: endpoint and program and transaction -> MiTransactionMetadata

    Other combinations will result in error.'''

    if not program and not transaction:
        return mi_parse_programs(
            mi_request_programs(
                mi_endpoint_get(endpoint).host,
                mi_endpoint_get(endpoint).port,
                mi_endpoint_get(endpoint).usr,
                mi_endpoint_get(endpoint).pwd
            ).content
        )

    elif program and not transaction:
        return  mi_parse_metadata(
                    mi_request_metadata(
                        mi_endpoint_get(endpoint).host,
                        mi_endpoint_get(endpoint).port,
                        mi_endpoint_get(endpoint).usr,
                        mi_endpoint_get(endpoint).pwd,
                        program
                    ).content
                )

    elif program and transaction:
        try:
            return [
                row for row in mi_parse_metadata(
                    mi_request_metadata(
                        mi_endpoint_get(endpoint).host,
                        mi_endpoint_get(endpoint).port,
                        mi_endpoint_get(endpoint).usr,
                        mi_endpoint_get(endpoint).pwd,
                        program
                    ).content
                ).transactions
                if row.transaction == transaction
            ][0]
        except IndexError as error:
            return MiError('No Results', f'{program}_{transaction} does not exist')

    else:
        raise ArgumentError('No case defined for program={program} and transaction={transaction}')


def mi_api_execute(endpoint: str, program: str, transaction: str, **kwargs) -> Union[MiRecords, MiError]:
    ''' Executes API calls, either read or write depending on the transaction.
    The **kwargs represents the input values. The key word "maxrecs" is treated as a special case
    and represents the maximum number of return records. Default is 100. Transactions that write data
    usually don't return any value at all, so the records attribute in MiRecords will usually be
    empty.
    
    :param endpoint - The name of the endpoint
    :param program - The M3 program
    :param metadata - The program transactions
    :param **kwargs - The input for the transaction '''

    return mi_parse_execute(
        mi_request_execute(
            mi_endpoint_get(endpoint).host,
            mi_endpoint_get(endpoint).port,
            mi_endpoint_get(endpoint).usr,
            mi_endpoint_get(endpoint).pwd,
            program,
            transaction,
            **kwargs
        ).content
    )




def get_api_for_endpoint(name: str) -> MiApi:
    ''' Creates a MiApi object for a stored endpoint'''
    print('get_api_for_endpoint will be depreciated in future release.')
    endpoint = mi_endpoint_get(name)
    return MiApi(
        endpoint.host,
        endpoint.port,
        endpoint.usr,
        endpoint.pwd
        )
