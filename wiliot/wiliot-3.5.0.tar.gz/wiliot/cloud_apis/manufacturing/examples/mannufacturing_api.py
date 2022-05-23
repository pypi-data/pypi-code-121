"""
 The following code snippet shows how to use pyWiliot for Wiliot's Manufacturing API:
 To use, please make sure to define the following environment variables to store your Wiliot API credentials:
 WILIOT_OAUTH_USERNAME
 WILIOT_OAUTH_PASSWORD
"""

# Import the library
from wiliot.cloud_apis.manufacturing.manufacturing import *
import os

# Initialise an Wiliot client object
wiliot_manufacturing = ManufacturingClient(os.environ.get('WILIOT_OAUTH_USERNAME'),
                                           os.environ.get('WILIOT_OAUTH_PASSWORD'))


# Change the owner for a sequence of pixel IDs - useful for changing consecutive IDs - like part of a reel
req = wiliot_manufacturing.change_pixel_owner_by_range("first_pixel_id", "last_pixel_id", "from_owner_id", "to_owner_id")

# Change the owner for a list of pixel IDs - When non-consecutive IDs need changing - up to 3000 pixels
req = wiliot_manufacturing.change_pixel_owner_by_list(["tag_1", "tag_2", "tag_3"], "from_owner_id", "to_owner_id")

# Change the owner of pixels by file - when needing to change more than 3000, non-consecutive IDs
#
# The file should be formatted as follows:
# tagId
# tag_1_id
# tag_2_id
# .....
req = wiliot_manufacturing.change_pixel_owner_by_file("from_owner_id", "to_owner_id", "/path/to/file")

# Each of the functions above returns a string representing a request ID. To check on the status of the request
print(wiliot_manufacturing.get_pixel_change_request_status(req))
