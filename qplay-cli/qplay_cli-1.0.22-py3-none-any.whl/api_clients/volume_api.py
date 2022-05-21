import requests
import json
from retrying import retry
from ec2_metadata import ec2_metadata

class VolumeAPIClient:
    """Api Client of the Volume API
    """
    
    BASE_PROD_URL = "https://3sv4wcd21a.execute-api.ap-south-1.amazonaws.com/prod"
    
    def __init__(self):
        pass
    
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=8)
    def get_volume_info(self, volume_id='', device_name=''):
        """Returns volume info (tag, assigned sd_device) for the ebs volume 
        identified either through volume_id or (user_name, device_name)
        
        :param: volume_id: str
        :param: user_name: str, e.g. MLModel
        :param: device_name: str, e.g. xvdf
        :returns: dictionary
        """
        url = VolumeAPIClient.BASE_PROD_URL
        
        if volume_id:
            url += "?volume_id={}".format(volume_id)
        elif device_name:
            url += "?dns_name={}&device_name={}".format(ec2_metadata.public_hostname, device_name)
        else:
            raise Exception("Invalid input. Must provide one among a) volume_id, or b) user_name and device_name")
        
        print("Querying url {}".format(url))
        
        response = requests.get(url)
        resp_json = response.json()
        
        vol_info = {"DatasetType": None}
        
        if resp_json["tags"]:
            vol_info = {a['Key']: a['Value'] for a in resp_json["tags"]}
            
        vol_info["SD_DEVICE"] = resp_json["sd"]
        return vol_info