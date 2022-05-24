import boto3
import json
import os


def waf_list_resource_web_acl(region):
    client = boto3.client('wafv2', region_name=region)

    # list of files in the data directory
    list_of_files = os.listdir('./data/cloudtrail-create-WebACL')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-waf-createWebACL-'):
          # open every file in cloudtrail-create-WebACL folder inside data folder
            script_dir = os.path.dirname('.')
            file_path_read = os.path.join(
                script_dir, 'data/cloudtrail-create-WebACL/'+each_file)
            with open(file_path_read, 'r') as openfile:
                cloudtrail_waf_object = json.load(openfile)
            # get the web arn from the cloudtrail object
            webARN = cloudtrail_waf_object['responseElements']['summary']['aRN']
            response = client.list_resources_for_web_acl(
                WebACLArn=webARN,
            )
            json_list = json.dumps(response)
            script_dir = os.path.dirname('.')
            file_path_write_list_resource = os.path.join(
                script_dir, 'data/waf-list-resource/waf-list-resource-web-acl-' +
                cloudtrail_waf_object['responseElements']['summary']['name']+'-'
                + region+'.json')
            # write the json file to the data/waf-list-resource folder
            with open(file_path_write_list_resource, 'w')as outfile:
                outfile.write(json_list)
                outfile.close()
            # write resource data for every resource inside the webACL
            for items in response["ResourceArns"]:
                response2 = client.get_web_acl_for_resource(
                    ResourceArn=items
                )
                json_list_2 = json.dumps(response2)

                script_dir = os.path.dirname('.')
                file_path_write_get_web_acl = os.path.join(
                    script_dir, 'data/waf-list-resource/get-web-acl-for-resource-' +
                    response2['WebACL']
                    ['Name']+'-'+region+'.json')
                with open(file_path_write_get_web_acl, 'w')as outfile:
                    outfile.write(json_list_2)
                    outfile.close()
