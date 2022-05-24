import cv2
import numpy as np

import pyzbar.pyzbar as pyzbar

import cloudmersive_barcode_api_client
from cloudmersive_barcode_api_client.rest import ApiException

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects

def get_barcode(filepath):
    im              = cv2.imread(filepath)

    decodedObjects = None
    try:
        decodedObjects  = decode(im)
    except Exception as ex:
        print(ex)

    if decodedObjects is None:
        return None

    if len(decodedObjects) != 0:
        code        = str(decodedObjects[0].data)
        return code
    return None
    

# Display barcode and QR code location  
def display(im, decodedObjects):

    # Loop over all decoded objects
    for decodedObject in decodedObjects: 
        points = decodedObject.polygon

        # If the points do not form a quad, find convex hull
        if len(points) > 4 : 
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else : 
            hull = points;

        # Number of points in the convex hull
        n = len(hull)

def decode_code(value):
    configuration = cloudmersive_barcode_api_client.Configuration()
    configuration.api_key['Apikey'] = '5f46158c-c65f-4199-bae4-df2b83b8c739'

    # create an instance of the API class
    api_instance = cloudmersive_barcode_api_client.BarcodeLookupApi(cloudmersive_barcode_api_client.ApiClient(configuration))
    #value = '5449000232250' # str | Barcode value

    api_response = None
    try:
        # Lookup a barcode value and return product data
        api_response = api_instance.barcode_lookup_ean_lookup(value)
    except ApiException as e:
        #print("Exception when calling BarcodeLookupApi->barcode_lookup_ean_lookup: %s\n" % e)
        pass
    return api_response