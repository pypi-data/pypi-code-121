import os.path
from wiliot.cloud_apis.api_client import Client, WiliotCloudError


class ManufacturingClient(Client):
    def __init__(self, oauth_username, oauth_password, env='', log_file=None):
        self.client_path = "manufacturing/"
        super().__init__(oauth_username, oauth_password, env, log_file)

    # Pixel Ownership Change functions

    def change_pixel_owner_by_range(self, from_owner_id, to_owner_id, from_pixel_id, to_pixel_id):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param from_pixel_id: String - The first pixel ID
        :param to_pixel_id: String - The last pixel ID
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        payload = {
            "fromTo": {
                "from": from_pixel_id,
                "to": to_pixel_id
            }
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e

    def change_pixel_owner_by_list(self, from_owner_id, to_owner_id, pixel_id_list):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_list: List of pixel IDs
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        assert isinstance(pixel_id_list, list), "pixel_id_list must be a list"
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        payload = {
            "tagIds": pixel_id_list
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e

    def change_pixel_owner_by_file(self, from_owner_id, to_owner_id, pixel_id_file_path):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_file_path : full path to a csv file containing one column called tagId
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        with open(pixel_id_file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(pixel_id_file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send, params=parameters)
                return res.get("trackingRequestId", None)
            except WiliotCloudError as e:
                print("Failed to request pixel ownership change")
                raise e

    def get_pixel_change_request_status(self, request_tracking_id):
        """
        Get information about the status of an ownership change request
        :param request_tracking_id: String - The request tracking ID returned from the change pixel owner request call
        :return: A dictionary with information about the details and the progress of the request
        """
        path = "ownerChange"
        res = self._get(path, {'requestId': request_tracking_id})
        return res


