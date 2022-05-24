import boto3
from json import JSONEncoder
import datetime
import json
import os


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def apigw_get_integration(region):

    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/apigw-get-rest-apis-'+region+'.json')
    f = open(file_path_read, 'r')
    data = json.load(f)
    count_rest_api = 0
    count_resource = 0
    count_method = 0
    # store the rest api
    RestApiIdList = []
    # store the resource
    ResourceIdList = []
    # store the method
    MethodList = []
    for rest_api in data['items']:
        count_rest_api += 1
        RestApiIdList.append(rest_api['id'])

    for i in range(count_rest_api):
        file_path2 = os.path.join(
            script_dir, 'data/apigw-resource/apigw-get-resource-'+region+'-'+RestApiIdList[i]+'.json')
        a = open(file_path2, 'r')
        resources = json.load(a)

        for resource in resources['items']:
            ResourceIdList.append(resource['id'])
            count_resource += 1
        try:
            for j in range(count_resource):
                count_method += 1
                MethodList.append(resource['resourceMethods'])
                new_method = list(MethodList[0].keys())
            try:
                for k in range(count_method):
                    client = boto3.client(
                        'apigateway', region_name=region)
                    response = client.get_integration(
                        restApiId=RestApiIdList[i],
                        resourceId=ResourceIdList[j],
                        httpMethod=new_method[k]
                    )

                    json_list = json.dumps(
                        response, indent=4, cls=DateTimeEncoder)
                    file_path_write = os.path.join(
                        script_dir, 'data/apigw-integration/apigw-get-integration-'+RestApiIdList[i]+'.json')
                    with open(file_path_write, 'w')as outfile:
                        outfile.write(json_list)
                        outfile.close()
            except:
                print('integration not found')
        except:
            print('method not found')
