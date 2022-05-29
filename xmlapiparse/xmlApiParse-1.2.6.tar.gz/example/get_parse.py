from get_auth import current_request


parse_list = current_request.parse('<?xml version="1.0" encoding="utf-8"?><RK7Query>'
                                '<RK7CMD CMD="GetRefData" RefName="CATEGLIST" WithMacroProp="1"/></RK7Query>')
print(f'Parse content: {parse_list}')
