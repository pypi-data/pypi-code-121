import requests
import json


class InstanceAPIClient:
    BASE_PROD_URL = "https://h5y8burhuk.execute-api.ap-south-1.amazonaws.com/prod"

    def __init__(self):
        pass

    def launch_machine(self, access_token, lease_time):
        x = requests.post(
            InstanceAPIClient.BASE_PROD_URL + "/launch_instance",
            data=json.dumps(
                {
                    "access_token": str(access_token),
                    "lease_time": str(lease_time)
                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response