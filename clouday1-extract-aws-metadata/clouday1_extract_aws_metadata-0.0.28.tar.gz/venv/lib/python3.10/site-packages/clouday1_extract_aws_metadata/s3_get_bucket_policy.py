import boto3
import json
import os


def s3_get_bucket_policy(region):
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/s3-list-bucket-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)
        count = 0
        BucketNameList = []

        for item in data['Buckets']:
            count += 1
            BucketNameList.append(item['Name'])

        for i in range(count):
            try:
                client = boto3.client('s3', region_name=region)
                response = client.get_bucket_policy(
                    Bucket=BucketNameList[i]
                )
                json_response = json.dumps(response)
                file_path_write = os.path.join(
                    script_dir, 'data/s3-policy/s3-'+region+'-'+BucketNameList[i]+'-policy.json')
                with open(file_path_write, 'w') as outfile:
                    outfile.write(json_response)
                    outfile.close()

            except:
                print('Error in get S3 Policy')

    except:
        print('File not found for s3-get-bucket-policy')
