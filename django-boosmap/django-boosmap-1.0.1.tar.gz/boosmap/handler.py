# -*- coding: utf-8 -*-
import logging

from requests import api

from boosmap.connector import Connector, ConnectorException
from boosmap.settings import api_settings

logger = logging.getLogger(__name__)


class BoosmapHandler:
    """
        Handler to send shipping payload to Boosmap
    """

    def __init__(self, base_url=api_settings.BOOSMAP['BASE_URL'],
                 token=api_settings.BOOSMAP['TOKEN'],
                 verify=True):

        self.base_url = base_url
        self.token = token
        self.verify = verify
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Boosmap.
        """
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

    def get_shipping_label(self):
        raise NotImplementedError(
            'get_shipping_label is not a method implemented for BoosmapHandler')

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Boosmap courier.
        """

        payload = {
            'order_number': instance.reference,
            'delivery_date': instance.delivery_date,
            'delivery_service': api_settings.BOOSMAP['SERVICE'],
            'delivery_start_time': api_settings.BOOSMAP['START_TIME'],
            'delivery_end_time': api_settings.BOOSMAP['END_TIME'],
            'pickup': {
                'location': {
                    'name': api_settings.SENDER['CD_NAME'],
                    'address': api_settings.SENDER['CD_ADDRESS'],
                    'district': api_settings.SENDER['CD_COMMUNE']
                }
            },
            'dropoff': {
                'contact': {
                    'fullname': instance.customer.full_name,
                    'email': instance.customer.email,
                    'phone': instance.customer.phone,
                },
                'location': {
                    'address': instance.address.full_address,
                    'district': instance.commune.name,
                }
            },
            'packages': [
                {
                    'code': item.sku,
                    'name': item.name,
                    'price': item.price,
                    'qty': item.quantity
                } for item in instance.items
            ],
        }

        if api_settings.SENDER['CD_LOCATION_ID']:
            payload['pickup']['location'] = {'id': api_settings.SENDER['CD_LOCATION_ID']}

        logger.debug(payload)
        return payload

    def create_shipping(self, data):
        """
            This method generate a Boosmap shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.
        """

        url = f'{self.base_url}order'
        logger.debug(data)

        try:
            response = self.connector.post(url, data)
            response[0].update({
                'tracking_number': response[0]['orderNumber'],
            })
            return response[0]

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

    def get_tracking(self, identifier):
        raise NotImplementedError(
            'get_tracking is not a method implemented for BoosmapHandler')

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                'tracking_number': 999999,
                'status': 'Entregado',
                'events': [{
                    'city': 'Santiago',
                    'state': 'RM',
                    'description': 'Llego al almacén',
                    'date': '12/12/2021'
                }]
            }
            return [{
                'city': 'Santiago',
                'state': 'RM',
                'description': 'Llego al almacén',
                'date': '12/12/2021'
            }]
        """
        return raw_data.get('events')

    def get_status(self, raw_data):
        """
            This method returns the status of the order and "is_delivered".
            structure:
            {
                'tracking_number': 999999,
                'status': 'Entregado',
                'events': [{
                    'city': 'Santiago'
                    'state': 'RM',
                    'description': 'Llego al almacén',
                    'date': '12/12/2021'
                }]
            }

            status: [
                'entregado', 'en camino entrega', 'en despacho', 
                'error dirección', 'rechazado por cliente', 'devolución exitosa',
                'sin moradores', 'retiro cd cliente', 'recepción en bodega',
                'fuera de tiempo', 'extraviado en ruta',
            ]

            response: ('Entregado', True)
        """

        status = raw_data.get('status')
        is_delivered = False

        if status.capitalize() == 'Entregado':
            is_delivered = True

        return status, is_delivered
