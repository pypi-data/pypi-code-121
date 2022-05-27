import os
import boto3
import json


def sns_list_tags(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    try:
        client = boto3.client('sns', region_name=region,
        aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)

        # open file for searching all kind of sns topic
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/sns-list-topic-'+region+'.json')
        with open(file_path_read, 'r')as openfile:
            json_object = json.load(openfile)
        # get all the sns topic in specified region
        for item in json_object['Topics']:
        # get the topic attribute for each sns and write into json file
            try:
                response = client.list_tags_for_resource(
                    ResourceArn=item['TopicArn'])
                json_list = json.dumps(response)
                with open('./data/sns-list-tags/sns-list-tags-'+item['TopicArn']+'.json', 'w') as outfile:
                    outfile.write(json_list)
                    outfile.close()
            except:
                print('Something is Error')
    except:
        print('File not found for sns-list-tags')

