import requests, operator, time
from requests import Session, get
import os
from zeep import Client
from zeep.transports import Transport

proxies = {
    'http': '165.225.76.32:80',
    'https': '165.225.76.32:80'
}

cert_path = 'merged-CA.pem'

def get_wsdl_response(base,wsdl,method,parameters,use_cert=False,use_proxy=False,log=None):
    wsdl_url = f'{base}/{wsdl}'
    
    if log is not None:
        log.info(f'Request url {wsdl_url=}, {method=} with parameters {parameters=}')
    if use_cert:
        session         = Session()
        session.verify  = cert_path
        transport       = Transport(session=session)

        client          = Client(wsdl_url,transport=transport)
    else:
        client          = Client(wsdl_url)
    
    if use_proxy:
        client.transport.session.proxies = proxies

    # methods
    services_names = []
    methods = {}
    for service in client.wsdl.services.values():
        services_names.append(service.name)
        
        for port in service.ports.values():
            operations = sorted(
                port.binding._operations.values(),
                key=operator.attrgetter('name'))

            for operation in operations:
                methods[operation.name] = {}
                # operation.input.signature()
                if type(operation.input.body) != list:
                    methods[operation.name] = [operation.input.body.__dict__]

    client.service._binding_options["address"] = f'{base}/{method}/' 
    
    m = [x['name'] for x in methods[method]]
    
    values = []
    for parameter in [x['name'] for x in methods[method]]:
        if parameter in parameters:
            values.append(parameters[parameter])
    
    for i in range(4):
        try:
            r = client.service._operations[method](*values)
            break
        except Exception as ex:
            log.error(ex=ex)
            time.sleep(10)
            r = None
    return r