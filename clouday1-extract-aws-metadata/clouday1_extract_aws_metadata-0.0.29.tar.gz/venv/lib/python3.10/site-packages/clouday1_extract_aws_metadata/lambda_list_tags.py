import os
import boto3
import json


def lambda_list_tags(region):
    client = boto3.client('lambda', region_name=region)

    # open file for searching all kind of lambda function
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/lambda-list-functions-'+region+'.json')
        with open(file_path_read, 'r')as openfile:
            json_object = json.load(openfile)
        # get all the lambda function name in specified region
            for item in json_object['Functions']:
            # get the tags for each lambda and write into json file
                try:
                    response = client.list_tags(
                        Resource=item["FunctionArn"]
                    )
                    json_list = json.dumps(response)
                    with open('./data/lambda-list-tags/lambda-list-tags-'+item["FunctionName"]+'.json', 'w') as outfile:
                        outfile.write(json_list)
                        outfile.close()
                except:
                    print('Error in list lambda tags')

    except:
        print('File not found for lambda-list-tags')
