import os
import json

# "arn:aws:execute-api:us-west-2:758325631830:9z24ydgzs2/*/GET/\" ==> example of apigw arn


def api_gw_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read_apigw = os.path.join(
        script_dir, 'data/apigw-get-rest-apis-'+region+'.json')
    with open(file_path_read_apigw, 'r') as openfile_apigw:
        apigw_object = json.load(openfile_apigw)
        openfile_apigw.close()
    for apigw in apigw_object["items"]:
        apiName = apigw['name']
        apiId = apigw['id']
        #get tags for each apigw 
        if "tags" in apigw.keys():
            apiTag = apigw['tags'] 

        file_path_read_resourceapigw = os.path.join(
            script_dir, 'data/apigw-resource/apigw-get-resource-'+region+'-'+apiId+'.json')
        with open(file_path_read_resourceapigw, 'r') as openfile_resourceAPI:
            apigw_resource = json.load(openfile_resourceAPI)
            openfile_resourceAPI.close()
        cytoscape_node_data.append({
            "data": {
                "id": "arn:aws:execute-api:"+region+":"+account_id+":"+apiId,
                "arn": "arn:aws:execute-api:"+region+":"+account_id+":"+apiId,
                "type": "API Gateway",
                "name": apiName,
                "account_id": account_id,
                "region": region,
                "resource": apigw_resource['items'],
                "tag": apiTag,
                "cost_for_month": "3.50 USD"
            }
        })
