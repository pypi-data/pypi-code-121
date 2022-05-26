from openpyxl import Workbook
from pathlib import Path

from .mi_models import MiTransactionMetadata
from .mi_endpoints import mi_endpoint_list

def _dtyp(fieldtype: str) -> str:
    if fieldtype == 'Alpha':
        return 'A'
    elif fieldtype in ('Numeric', 'Number', 'Integer'):
        return 'N'
    else:
        raise LookupError(f'Fieldtype {fieldtype} is not defined')


def mi_output_generate_template(data: MiTransactionMetadata, path: str) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = f'API_{data.program}_{data.transaction}'

    ws.append(['MESSAGE'] + [field.name for field in data.inputs])
    ws.append(['MESSAGE'] + [field.description for field in data.inputs])
    for _ in range(4): ws.append([''])
    ws.append([''] + [f'{_dtyp(field.fieldtype)}.{field.length}' for field in data.inputs])

    wb.create_sheet('MWS')
    ws = wb['MWS']

    ws.append(
        [
            "Application/Environment Name",
            "Web Services Homepage or REST Server Address(<Server>:<Port>)",
            "Service Context/ and/or 'm3api-rest'",
            "optional: Customer Domain or Server",
            "optional: Customer Domain Key"
        ]
    )
    for endpoint in mi_endpoint_list():
        ws.append(
            [
                endpoint.name,
                f'http://{endpoint.host}:{endpoint.port}/mws/',
                'services|m3api-rest'
            ]
        )

    wb.save(path.absolute().joinpath(Path(f'Template_M3_{data.program}_{data.transaction}.xlsx')))
