import os
import json

'''FIND CONNECTION BETWEEN TRANSCRIBE AND S3'''


def edge_transcribe_to_s3_find(cytoscape_edge_data, region, account_id):
    list_of_files = os.listdir('./data/cloudtrail-start-transcription')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-start-transcription-job-'):
            # retrieve transcribe object
            script_dir = os.path.dirname(
                './data/cloudtrail-start-transcription/')
            file_path_read_transcribe = os.path.join(script_dir, each_file)
            with open(file_path_read_transcribe, 'r') as openfile_transcribe:
                cloudtrail_transcribe_object = json.load(openfile_transcribe)
                openfile_transcribe.close()
            # retrieve s3 object
            script_dir_s3 = os.path.dirname('.')
            file_path_read = os.path.join(
                script_dir_s3, 'data/s3-list-bucket-'+region+'.json')
            with open(file_path_read, 'r') as openfile:
                s3_object = json.load(openfile)
            # do logic for edge transcribe to s3
            try:
                for s3 in s3_object['Buckets']:
                    if(cloudtrail_transcribe_object['requestParameters']['outputBucketName'] == s3['Name']):
                        transcribe_s3_edge_data = {
                            "data": {
                                "id": 'transcribe-'+"arn:aws:s3:::"+s3["Name"],
                                "source": 'transcribe',
                                "target": "arn:aws:s3:::"+s3["Name"],
                            }
                        }
                        if(cytoscape_edge_data.count(transcribe_s3_edge_data) == 0):
                            cytoscape_edge_data.append(
                                transcribe_s3_edge_data)
                            print('Found connection between transcribe and s3:{}'.format(
                                cloudtrail_transcribe_object['requestParameters']['outputBucketName']))
            except:
                print('No connection between transcribe and s3 bucket:{}'.format(
                    cloudtrail_transcribe_object['requestParameters']['outputBucketName']
                ))
