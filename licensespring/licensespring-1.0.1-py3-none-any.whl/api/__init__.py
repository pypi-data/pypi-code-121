import base64
import io
import json

import requests

import licensespring
from licensespring.api.authorization import (
    autorization_headers,
    date_header_value,
    offline_signature,
)
from licensespring.api.error import ClientError
from licensespring.api.hardware import HardwareIdProvider
from licensespring.api.signature import SignatureVerifier


class APIClient:
    def __init__(
        self,
        api_key,
        shared_key,
        hardware_id_provider=HardwareIdProvider,
        verify_license_signature=True,
        signature_verifier=SignatureVerifier,
        api_domain="api.licensespring.com",
        api_version="v4",
    ):
        self.api_key = api_key
        self.shared_key = shared_key

        self.hardware_id_provider = hardware_id_provider()

        self.verify_license_signature = verify_license_signature
        self.signature_verifier = signature_verifier()

        self.api_base = "https://{}/api/{}".format(api_domain, api_version)

    def api_url(self, endpoint):
        return "{}{}".format(self.api_base, endpoint)

    def request_headers(self, custom_headers={}):
        headers = {"Content-Type": "application/json"}
        authorization_headers = autorization_headers(self.api_key, self.shared_key)
        return {**headers, **authorization_headers, **custom_headers}

    def request_generic_data(
        self,
        data,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
    ):
        data["product"] = product
        data["hardware_id"] = (
            hardware_id if hardware_id else self.hardware_id_provider.get_id()
        )

        if license_key:
            data["license_key"] = license_key
        if username:
            data["username"] = username
        if password:
            data["password"] = password

        return data

    def request_additional_data(self, data, additional_data):
        for key, value in additional_data.items():
            if value is not None:
                data[key] = value
        return data

    def request_hardware_data(
        self,
        data,
        os_ver=None,
        hostname=None,
        ip=None,
        mac_address=None,
    ):

        data["os_ver"] = (
            os_ver if os_ver is not None else self.hardware_id_provider.get_os_ver()
        )
        data["hostname"] = (
            hostname
            if hostname is not None
            else self.hardware_id_provider.get_hostname()
        )
        data["ip"] = ip if ip is not None else self.hardware_id_provider.get_ip()
        data["mac_address"] = (
            mac_address
            if mac_address is not None
            else self.hardware_id_provider.get_mac_address()
        )

        return data

    def request_vm_data(self, data, is_vm=None, vm_info=None):
        data["is_vm"] = (
            is_vm if is_vm is not None else self.hardware_id_provider.get_is_vm()
        )
        data["vm_info"] = (
            vm_info if vm_info is not None else self.hardware_id_provider.get_vm_info()
        )

        return data

    def request_version_data(self, data, app_ver=None):
        data["sdk_ver"] = "PythonSDK {}".format(licensespring.version)

        if app_ver:
            data["app_ver"] = app_ver
        elif licensespring.app_version:
            data["app_ver"] = licensespring.app_version

        return data

    def send_request(
        self,
        method,
        endpoint,
        custom_headers={},
        params=None,
        data=None,
        json_data=None,
    ):
        response = requests.request(
            method=method,
            url=self.api_url(endpoint),
            headers=self.request_headers(custom_headers=custom_headers),
            params=params,
            data=data,
            json=json_data,
        )
        if 400 <= response.status_code < 500:
            raise ClientError(response)
        else:
            response.raise_for_status()
        return response

    def activate_license(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        app_ver=None,
        os_ver=None,
        hostname=None,
        ip=None,
        is_vm=None,
        vm_info=None,
        mac_address=None,
    ):
        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, password
        )
        data = self.request_hardware_data(
            data=data,
            os_ver=os_ver,
            hostname=hostname,
            ip=ip,
            mac_address=mac_address,
        )
        data = self.request_vm_data(data, is_vm=is_vm, vm_info=vm_info)
        data = self.request_version_data(data, app_ver=app_ver)

        response = self.send_request(
            method="post",
            endpoint="/activate_license",
            json_data=data,
        )
        response_json = response.json()

        if self.verify_license_signature:
            self.signature_verifier.verify_license_signature(
                hardware_id if hardware_id else self.hardware_id_provider.get_id(),
                license_key if license_key else username,
                response_json.get("validity_period"),
                response_json.get("license_signature"),
            )

        return response_json

    def deactivate_license(
        self, product, hardware_id=None, license_key=None, username=None, password=None
    ):
        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, password
        )

        response = self.send_request(
            method="post",
            endpoint="/deactivate_license",
            json_data=data,
        )
        return True if response.status_code == 200 else False

    def check_license(self, product, hardware_id=None, license_key=None, username=None):
        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )
        response = self.send_request(
            method="get",
            endpoint="/check_license",
            params=data,
        )
        response_json = response.json()

        if self.verify_license_signature:
            self.signature_verifier.verify_license_signature(
                hardware_id if hardware_id else self.hardware_id_provider.get_id(),
                license_key if license_key else username,
                response_json.get("validity_period"),
                response_json.get("license_signature"),
            )

        return response_json

    def activate_offline_dump(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        app_ver=None,
        os_ver=None,
        hostname=None,
        ip=None,
        is_vm=None,
        vm_info=None,
        mac_address=None,
    ):
        data = {"request": "activation"}
        data = self.request_generic_data(
            data, product, hardware_id, license_key, username, password
        )
        data = self.request_hardware_data(
            data=data,
            os_ver=os_ver,
            hostname=hostname,
            ip=ip,
            mac_address=mac_address,
        )
        data = self.request_vm_data(data, is_vm=is_vm, vm_info=vm_info)
        data = self.request_version_data(data, app_ver=app_ver)

        data["api_key"] = self.api_key
        data["date"] = date_header_value()
        data["signature"] = offline_signature(
            self.api_key, self.shared_key, data["hardware_id"], license_key, username
        )
        data["request_id"] = self.hardware_id_provider.get_request_id()

        return base64.b64encode(json.dumps(data).encode()).decode()

    def activate_offline_load(self, data, hardware_id=None):
        decoded_data = base64.b64decode(data).decode()
        response_json = json.loads(decoded_data)

        if self.verify_license_signature:
            self.signature_verifier.verify_license_signature(
                hardware_id if hardware_id else self.hardware_id_provider.get_id(),
                response_json.get("license_key")
                if response_json.get("license_key")
                else response_json.get("username"),
                response_json.get("validity_period"),
                response_json.get("license_signature"),
            )

        return response_json

    def activate_offline(self, data):
        decoded_data = base64.b64decode(data).decode()
        license_data = json.loads(decoded_data)

        response = self.send_request(
            method="post",
            endpoint="/activate_offline",
            custom_headers={"Content-type": "text/plain"},
            data=data,
        )
        response_json = response.json()

        if self.verify_license_signature:
            self.signature_verifier.verify_license_signature(
                license_data.get("hardware_id")
                if license_data.get("hardware_id")
                else self.hardware_id_provider.get_id(),
                license_data.get("license_key")
                if license_data.get("license_key")
                else license_data.get("username"),
                response_json.get("validity_period"),
                response_json.get("license_signature"),
            )

        return response_json

    def deactivate_offline_dump(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        app_ver=None,
        os_ver=None,
        hostname=None,
        ip=None,
        mac_address=None,
        consumptions=None,
        product_features=None,
    ):
        data = {"request": "deactivation"}
        data = self.request_generic_data(
            data, product, hardware_id, license_key, username, password
        )
        data = self.request_hardware_data(
            data=data,
            os_ver=os_ver,
            hostname=hostname,
            ip=ip,
            mac_address=mac_address,
        )
        data = self.request_version_data(data, app_ver=app_ver)

        data["api_key"] = self.api_key
        data["date"] = date_header_value()
        data["signature"] = offline_signature(
            self.api_key, self.shared_key, data["hardware_id"], license_key, username
        )
        data["request_id"] = self.hardware_id_provider.get_request_id()
        data = self.request_additional_data(
            data=data,
            additional_data={
                "consumptions": consumptions,
                "product_features": product_features,
            },
        )

        return base64.b64encode(json.dumps(data).encode()).decode()

    def deactivate_offline(self, data):
        response = self.send_request(
            method="post",
            endpoint="/deactivate_offline",
            custom_headers={"Content-type": "text/plain"},
            data=data,
        )

        return True if response.status_code == 200 else False

    def add_consumption(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        consumptions=None,
        max_overages=None,
        allow_overages=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, password
        )
        data = self.request_additional_data(
            data=data,
            additional_data={
                "consumptions": consumptions,
                "max_overages": max_overages,
                "allow_overages": allow_overages,
            },
        )

        response = self.send_request(
            method="post",
            endpoint="/add_consumption",
            json_data=data,
        )

        return response.json()

    def add_feature_consumption(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        feature=None,
        consumptions=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, password
        )
        data["feature"] = feature
        data = self.request_additional_data(
            data=data,
            additional_data={
                "consumptions": consumptions,
            },
        )

        response = self.send_request(
            method="post",
            endpoint="/add_feature_consumption",
            json_data=data,
        )

        return response.json()

    def trial_key(
        self,
        product,
        hardware_id=None,
        email=None,
        license_policy=None,
        first_name=None,
        last_name=None,
        phone=None,
        address=None,
        postcode=None,
        state=None,
        country=None,
        city=None,
        reference=None,
    ):

        data = self.request_generic_data({}, product, hardware_id, None, None, None)
        data = self.request_additional_data(
            data=data,
            additional_data={
                "email": email,
                "license_policy": license_policy,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "address": address,
                "postcode": postcode,
                "state": state,
                "country": country,
                "city": city,
                "reference": reference,
            },
        )

        response = self.send_request(
            method="get",
            endpoint="/trial_key",
            params=data,
        )

        return response.json()

    def product_details(
        self,
        product,
    ):
        data = {"product": product}

        response = self.send_request(
            method="get",
            endpoint="/product_details",
            params=data,
        )

        return response.json()

    def track_device_variables(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        variables=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )
        data["variables"] = variables

        response = self.send_request(
            method="post",
            endpoint="/track_device_variables",
            json_data=data,
        )

        return True if response.status_code == 200 else False

    def floating_release(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )

        response = self.send_request(
            method="post",
            endpoint="/floating/release",
            json_data=data,
        )

        return True if response.status_code == 200 else False

    def floating_borrow(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        password=None,
        borrowed_until=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, password
        )
        data["borrowed_until"] = borrowed_until

        response = self.send_request(
            method="post",
            endpoint="/floating/borrow",
            json_data=data,
        )

        return response.json()

    def change_password(self, username, password, new_password):
        data = {
            "username": username,
            "password": password,
            "new_password": new_password,
        }

        response = self.send_request(
            method="post",
            endpoint="/change_password",
            json_data=data,
        )

        return True if response.status_code == 200 else False

    def versions(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        env=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )
        data = self.request_additional_data(
            data=data,
            additional_data={
                "env": env,
            },
        )

        response = self.send_request(
            method="get",
            endpoint="/versions",
            params=data,
        )

        return response.json()

    def installation_file(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
        env=None,
        version=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )
        data = self.request_additional_data(
            data=data,
            additional_data={
                "env": env,
                "version": version,
            },
        )

        response = self.send_request(
            method="get",
            endpoint="/installation_file",
            params=data,
        )

        return response.json()

    def customer_license_users(self, product, customer):
        data = {
            "product": product,
            "customer": customer,
        }

        response = self.send_request(
            method="get",
            endpoint="/customer_license_users",
            params=data,
        )

        return response.json()

    def sso_url(self, product, customer_account_code):
        data = {
            "product": product,
            "customer_account_code": customer_account_code,
        }

        response = self.send_request(
            method="get",
            endpoint="/sso_url",
            params=data,
        )

        return response.json()

    def get_device_variables(
        self,
        product,
        hardware_id=None,
        license_key=None,
        username=None,
    ):

        data = self.request_generic_data(
            {}, product, hardware_id, license_key, username, None
        )

        response = self.send_request(
            method="get",
            endpoint="/get_device_variables",
            params=data,
        )

        return response.json()
