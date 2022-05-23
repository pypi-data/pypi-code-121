import requests
import logging
import json

from .constants import NETBOX_NSO_NEDS

logger = logging.getLogger()

def _format_error_response(response):
    try:
        message = response.json()['errors']['error'][0]['error-message']
    except KeyError:
        message = 'Failed to make request or error not returned as expected'
    return 'Error code %s: %s' % (response.status_code,
                                  message)



class UMnetnso:

    def __init__(self, host='localhost', port='8080', 
            user='admin', password='admin', ssl=False, verify_ssl=False):
       
        self.s = requests.Session()
        self.s.auth = (user, password)
        self.s.headers.update({
                'Accept': 'application/yang-data+json',
                'Content-Type':'application/yang-data+json',
                })
        self.host = host
        self.port = port
        self.ssl = ssl
        self.verify_ssl = verify_ssl
        self.protocol = 'https' if self.ssl else 'http'

    def _get_restconf(self, path=None, fields=None):
        '''
        does a 'get' of the restconf data resource and returns the results
        '''

        # build url. First we need the base url
        url = f'{self.protocol}://{self.host}:{self.port}/restconf/'
        params = {}

        # Now add our path
        if path:
            path.lstrip('/')
            url += path

        # If were restricting the query by fields,
        # add those to the path as well
        parsed_fields = []
        if(fields):

            for f in fields:

                # User can specify a field expression
                # as a dict with the filtered node as a single key
                # with the value a list of things to filter for
                if(isinstance(f, dict) and len(f.keys()) == 1):
                    key = list(f.keys())[0]
                    if(isinstance(f[key], list)):
                        parsed_fields.append(f'{key}({";".join(f[key])})')
                    else:
                        logger.error(f'Invalid field expression {f}')
                        raise

                elif(isinstance(f, str)):
                    parsed_fields.append(f)

                else:
                    logger.error(f'Invalid field expression {f}')
                    raise

        # Add parsed fields to params
        params['fields'] = ';'.join(parsed_fields)

        logger.debug(f'Built url: {url}, params {params}')

        # send request
        response = self.s.get(
            url,
            verify=self.verify_ssl,
            params=params
        )

        # if we get a 200-ok, we got results. Return those.
        if response.status_code == 200:
            return response.json()

        # if we got a 204, there was no data to return. We'll return
        # True so we know there wasn't an error
        if response.status_code == 204:
            return True

        # Anything else is a failure
        logger.error(_format_error_response(response))
        return False
            

    def _restconf_put(self, path, node, data):
        '''
        Does a PUT and returns the HTTP status code.
        Per RFC8040 4.5, a PUT creates or replaces a
        node. The client provides the name of the node,
        the path to the node, and the data tied to the node.

        The server returns HTTP status code 201 if the node is created,
        204 if the node is replaced. This function returns
        the status code.
        '''
        
        url = f'{self.protocol}://{self.host}:{self.port}/restconf/{path}={node}'
        response = self.s.put(url=url, data=json.dumps(data))

        # if we got a 201 (updated) or 204 (created), return the code
        # so the caller knows which one
        if response.status_code in [201, 204]:
            return response.status_code

        # otherwise return false
        logger.error(_format_error_response(response))
        return False

    def put_device(self, name, address, platform, authgroup='local'):
        '''
        Creates or over-writes a device in NSO. Note that devices are keyed
        on name, not IP.
        '''
        path = 'data/tailf-ncs:devices/device'

        try:
            ned = NETBOX_NSO_NEDS[platform]
        except:
            logger.error(f'No platform to NED mapping for {platform}')
            return False

        data = { 'ncs:device': [ {
                    'name': name,
                    'address':address,
                    'device-type' : { ned["device-type"] : { 'ned-id': ned['ned-id'] }},
                    'port':22,
                    'authgroup': authgroup,
                    'state': {'admin-state':'unlocked' },
                    }
                 ]
               }

        result = self._restconf_put(path, name, data)

        return result.status_code

    def get_all_devices(self):
        '''
        Gets basic info related to devices in ncs
        '''

        path = 'data/tailf-ncs:devices'
        fields = [
            {'device-group': ['name', 'member'] },
            'device/name',
            'device/address',
            'device/state',
            {'device/device-type': ['netconf', 'cli'] },
            ]

        results = self._get_restconf(path=path, fields=fields)
        if results == None:
            return None

        # flattening the results into something a bit more readable.
        # first lets build a nice device name -> device group mapping
        device_groups = {}
        for g in results['tailf-ncs:devices']['device-group']:
            name = g['name']
            for d in g['member']:
                if d in device_groups.keys():
                    logger.error('Device {d} in more than one group!')
                    raise
                device_groups[d] = name

        # now lets build a list of devices with their basic attributes:
        # name, address, operational state, ned, and group
        devices = [ {
                    'name': nso_d['name'],
                    'address': nso_d['address'],
                    'status': nso_d['state']['oper-state'],
                    'ned':nso_d['device-type'][list(nso_d['device-type'].keys())[0]]['ned-id'],
                    'group': device_groups.get(nso_d['name'],None),
                }
                    for nso_d in results['tailf-ncs:devices']['device']
                ]

        return devices

    def get_all_device_groups(self):
        '''
        Pulls a list of all the device groups in nso
        '''
        path = 'data/tailf-ncs:devices/device-group'
        fields = ['name'] 
        results = self._get_restconf(path=path, fields=fields)
        print(results)

        if results == None:
            return None

        # result is a list of key/value pairs {'name':group_name}
        groups = [list(group.values())[0] for group in results['tailf-ncs:device-group']]

        return groups
