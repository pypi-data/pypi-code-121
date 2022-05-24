import os
import boto3
import json

def s3_get_bucket_tagging(region):
    client = boto3.client('s3', region_name=region)
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/s3-list-bucket-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        s3_object = json.load(openfile)
        for item in s3_object['Buckets']:
            try:
                #get tags for each s3 bucket
                response = client.get_bucket_tagging(
                    Bucket=item['Name']
                )
                json_list = json.dumps(response, indent=4)
                file_path2 = os.path.join(
                    script_dir, 'data/s3-list-tags/get-bucket-tagging-'+item['Name']+'-'+region+'.json')
                with open(file_path2, 'w')as outfile:
                    outfile.write(json_list)
                    outfile.close()
                
            except:
                print("The TagSet does not exist")
