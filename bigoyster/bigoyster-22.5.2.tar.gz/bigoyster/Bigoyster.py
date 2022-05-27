import requests
import logging
import json
import random
import string

_logger = logging.getLogger(__name__)


class Bigoyster:
    token = False
    username = False
    password = False
    base_url = False

    def __init__(self, base_url='https://api.dealsmedia.com/', token=False, username=False, password=False):
        self.base_url = base_url
        self.username = username
        self.password = password

        if token:
            self.token = token
        else:
            self.token = self.get_token(username, password)

    def get_token(self, username, password):
        url = self.base_url + "api-token-auth/"

        payload = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return json.loads(response.text)['token']
        else:
            print('GET TOKEN FAILED')
            return False

    def get_headers(self):
        headers = {
            'Authorization': "Token " + self.token,
        }
        return headers

    def call_create_api(self, object, values):
        baseurl = self.base_url
        url = baseurl + object + '/create/'

        response = requests.post(
            url, json=values, headers=self.get_headers(), timeout=5)

        if response.status_code == 201:
            result = json.loads(response.text)
            return True, result
        elif response.status_code == 401:
            print('NOT AUTHORIZED')
            if self.get_token(username=self.username, password=self.password):
                print('RETRY')
                return self.call_create_api(object, values)
        elif response.status_code >= 400:
            print('400s BAD REQUEST')
            print(response.text)

        else:
            print('UNHANDLED STATUS CODE')
            print(response.text)
        return False, response

    def call_action_api(self, object, action, values):
        baseurl = self.base_url
        url = baseurl + object + '/' + action + '/'

        response = requests.post(
            url, json=values, headers=self.get_headers(), timeout=5)
        print(response.elapsed)
        if response.status_code == 200:
            result = json.loads(response.text)
            return True, result
        elif response.status_code == 401:
            print('NOT AUTHORIZED')
            if self.get_token(username=self.username, password=self.password):
                print('RETRY')
                return self.call_action_api(object, action, values)
        elif response.status_code >= 400:
            print('400s BAD REQUEST')
            print(response.text)

        else:
            print('UNHANDLED STATUS CODE')
            print(response.text)
        return False, response

    def call_get_api(self, object, params):
        baseurl = self.base_url
        url = baseurl + object + '/get/'

        response = requests.get(
            url, params=params, headers=self.get_headers(), timeout=5)
        print(response.elapsed)
        if response.status_code == 200:
            result = json.loads(response.text)
            return result
        elif response.status_code == 401:
            print('NOT AUTHORIZED')
            if self.get_token(username=self.username, password=self.password):
                print('RETRY')
                return self.call_get_api(object, params)
        elif response.status_code == 404:
            print('NOT FOUND')
            return False
        elif response.status_code >= 400:
            print('400s BAD REQUEST')

        else:
            print('UNHANDLED STATUS CODE')
        return response

    def call_list_api(self, object, params):
        baseurl = self.base_url
        url = baseurl + object + '/list/'

        response = requests.get(
            url, params=params, headers=self.get_headers(), timeout=5)

        if response.status_code == 200:
            result = json.loads(response.text)
            return result
        elif response.status_code == 401:
            print('NOT AUTHORIZED')
            if self.get_token(username=self.username, password=self.password):
                print('RETRY')
                return self.call_get_api(object, params)
        elif response.status_code == 404:
            print('NOT FOUND')
            return False
        elif response.status_code >= 400:
            print('400s BAD REQUEST')

        else:
            print('UNHANDLED STATUS CODE')
        return response

    # HELPER FUNCTIONS BELOW
    def get_consumer_by_phone(self, device_id, phone):
        if not device_id:
            raise Exception('NO DEVICE')
        import re
        clean_phone = re.sub("\D", "", phone)
        if len(clean_phone) not in [10, 11]:
            return False
        if clean_phone[0] != "1":
            clean_phone = "1" + clean_phone
        return self.call_get_api('consumer', {'phone': clean_phone, 'device_id': device_id})

    def get_consumer_by_id(self, device_id, consumer_id):
        if not device_id:
            raise Exception('NO DEVICE')
        return self.call_get_api('consumer', {'id': consumer_id, 'device_id': device_id})

    def get_location_coupons(self, location_id='all'):
        params = {
            "location": location_id,
            "status": "active"
        }
        result = self.call_list_api('campaign', params)
        return result.get('results')

    def get_consumer_coupons(
        self, device_id, consumer_id, upcs='', qtys='', prices='', txn_line_refs='', txn_ref='',
        txn_type='sale', sale_auth='', sale_txn_ref='', sale_txn_ref_lines='', taxes=[], labels=[]
    ):
        if txn_type == 'return' and not sale_auth:
            raise Exception('No auth code on refund')
        if not device_id:
            raise Exception('NO DEVICE')
        """
        Get all consumer coupons with optional parameters
        :param consumer_id: UUID
        :param upcs: comma separated string
        :param qtys: comma separated string
        :param prices: comma separated string
        :param txn_line_refs: comma separated string
        :param txn_ref: string
        :param txn_type: string options: sale, return
        :param sale_auth: string only for returns, original sale auth_code
        :param taxes: list of json of taxes summed for order total
        :return:
        """
        # authorization code
        auth_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=16))
        params = {
            "consumer": consumer_id,
            "status": "active",
            "upcs": upcs,
            "qtys": qtys,
            "prices": prices,
            "txn_line_refs": txn_line_refs,
            'auth_code': auth_code,
            'device_id': device_id,
            'txn_ref': txn_ref,
            'txn_type': txn_type,
            'sale_auth': sale_auth,
            'sale_txn_ref': sale_txn_ref,
            'sale_txn_ref_lines': sale_txn_ref_lines,
            'taxes': taxes,
            'labels': labels
        }
        # check if preprocessing required
        x = upcs.split(',')
        if len(x) > len(set(x)):
            params['preprocess'] = True
        # result = self.call_list_api('coupon', params=params)
        success, result = self.call_action_api('coupon', 'auth', params)
        return result

    def start_consumer_order(self, device_id, consumer_id):
        if not device_id:
            raise Exception('NO DEVICE')
        values = {
            'event_type': 'POS006',
            'device': device_id,
            'consumer': consumer_id
        }
        success, result = self.call_create_api('event', values)
        if success:
            return result
        else:
            return {'success': False, 'addl_info': result.text}

    def create_consumer(self, device_id, phone):
        if not device_id:
            raise Exception('NO DEVICE')
        import re
        clean_phone = re.sub("\D", "", phone)
        if len(clean_phone) not in [10, 11]:
            return False
        if clean_phone[0] != "1":
            clean_phone = "1" + clean_phone
        # add to petzmobile
        success, result = self.call_create_api(
            'consumer', {'phone': clean_phone, 'device_id': device_id})
        if success:
            return result
        else:
            return {'success': False, 'addl_info': result.text}

    def capture_coupons(self, device_id, consumer_id, auth_code):
        if not device_id or not consumer_id or not auth_code:
            return {'success': False, 'addl_info': 'Invalid parameters'}
        values = {
            'event_type': 'POS003',
            'device': device_id,
            'consumer': consumer_id,
            'addl_info': {'auth_code': auth_code}
        }
        success, result = self.call_create_api('event', values)
        success = result.get('is_valid')
        todays_savings = '${:,.2f}'.format(result.get('todays_savings'))
        total_savings = '${:,.2f}'.format(result.get('total_savings'))
        receipt_lines = []
        # receipt_lines.append("Today's savings: %s " % todays_savings)
        receipt_lines.append("Petzmobile Lifetime Savings: %s" % total_savings)
        return {'success': success.lower() == 'true', 'receipt_lines': receipt_lines}

    def get_campaign_upcs(self, device_id):
        if not device_id:
            raise Exception('NO DEVICE')
        params = {
            "view": "criteria",
            "status": "active"
        }
        result = self.call_list_api('campaign', params=params).get('results')
        upcs = []
        for c in result:
            for upc in c.get('criteria', {}).get('valid_products', []):
                if upc and upc not in upcs:
                    upcs.append(upc)
        return upcs

    def get_categories(self, channel_name):
        params = {
            "available_retail": True,
            "parent_name": channel_name
        }
        result = self.call_list_api('tag', params=params).get('results')
        return result

    def get_periods(self):
        params = {
            "available_retail": True
        }
        return self.call_list_api('period', params=params).get('results')

    def create_store_coupon(self, device_id, headline, description, image_b64, customer_ref, categories, callback='', selected_periods=[]):
        if not device_id:
            raise Exception('NO DEVICE')
        values = {
            'event_type': 'RET004',
            'device': device_id,
            'addl_info': {
                'headline': headline,
                'description': description,
                'image_b64': image_b64,
                'customer_ref': customer_ref,
                'categories': categories,
                'selected_periods': selected_periods,
                'callback': callback
            }
        }
        success, result = self.call_create_api('event', values)
        return {'success': success, 'result': result}

    def redeem_store_coupon(self, device_id, consumer_id, customer_ref, value, qty):
        if not device_id:
            raise Exception('NO DEVICE')
        values = {
            'event_type': 'POS008',
            'device': device_id,
            'consumer_id': consumer_id,
            'addl_info': {
                'customer_ref': customer_ref,
                'value': value,
                'qty': qty
            }
        }
        success, result = self.call_create_api('event', values)
        return {'success': success}

    def end_campaign(self, device_id, customer_ref):
        if not device_id:
            raise Exception('NO DEVICE')
        values = {
            'event_type': 'POS007',
            'device': device_id,
            'addl_info': {'customer_ref': customer_ref}
        }
        success, result = self.call_create_api('event', values)
        return {'success': success}

    def refund_coupon(self, device_id, coupon_id, qty, amount):
        if not device_id:
            raise Exception('NO DEVICE')
        values = {
            'event_type': 'CPN005',
            'device': device_id,
            'coupon': coupon_id,
            'addl_info': {'qty': qty, 'amount': amount}
        }
        success, result = self.call_create_api('event', values)
        return {'success': success}

    def retail_enrollment(self, enrollment_data):
        reg_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=6))
        enrollment_data['reg_code'] = reg_code
        values = {
            'event_type': 'RET002',
            'addl_info': enrollment_data
        }
        success, result = self.call_create_api('event', values)
        return {'success': success, 'reg_code': reg_code}

    def create_retail_settlement(self, device_id):
        if not device_id:
            raise Exception('NO DEVICE')
        return {'success': 'True'}

    def get_pos_device(self, device_type, device_ref, friendly_name=''):
        if not friendly_name:
            friendly_name = device_ref
        values = {
            'name': friendly_name,
            'pos_ref': device_ref,
            'device_type': device_type
        }
        success, result = self.call_action_api('device', 'get', values=values)
        if success:
            return result
        else:
            return {'success': False, 'addl_info': result.text}
