import os
import boto3
import json


def sns_get_topic_attribute(region):
    client = boto3.client('sns', region_name=region)

    # open file for searching all kind of sns topic
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/sns-list-topic-'+region+'.json')
        with open(file_path_read, 'r')as openfile:
            json_object = json.load(openfile)
        # get all the sns topic in specified region
        for item in json_object['Topics']:
            # get the topic attribute for each sns and write into json file
            try:
                response = client.get_topic_attributes(
                    TopicArn=item['TopicArn'])
                json_list = json.dumps(response)
                with open('./data/sns-get-topic-attr/sns-get-topic-attribute-'+item['TopicArn']+'.json', 'w') as outfile:
                    outfile.write(json_list)
                    outfile.close()
            except:
                print('Something is Error')

    except:
        print('File not found for sns-get-topic-attr')
