"""Examples of API call for Twins operations"""

from trustedtwin import RestService

client = RestService(auth='$my_private_token')

twin_description = {
    "description": {
        "example_param": "example_value"
    }    
}
# creation of a new Twin
twin = client.twins.create(twin_description)

twin_uuid = twin['creation_certificate']['uuid']            # uuid4
twin_creator = twin['creation_certificate']['creator']      # uuid4 of account creating twin
twin_status = twin['status']                                # alive | terminated
twin_description = twin['description']                      # in this case equals to set twin_description

# get Twin:
twin = client.twins.get(twin_uuid)                          # response the same as during creation

# update of a Twin (only description can be updated)
new_description = {
    "description": {
        "new_param": "new_param"
    }    
}
# important: previous description will be replaced with new one
response = client.twins.update(new_description, twin_uuid)
twin_description = twin['description']                      # equals to new_description

# termination of a Twin
terminated_twin = client.twins.terminate(twin_uuid)
who_terminated = terminated_twin['termination_certificate']['issuer']            # uuid4 of account terminating Twin
when_terminated = terminated_twin['termination_certificate']['terminated_ts']    # epoch timestamp of termination

# get terminated twin:
terminated_twin = client.twins.get(twin_uuid, show_terminated=True)
