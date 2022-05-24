import os
import json

'''FIND CONNECTION BETWEEN LAMBDA AND TRANSCRIBE'''


def edge_lambda_to_transcribe(cytoscape_edge_data, region, account_id):
    # list of files in the data directory
    list_of_files = os.listdir('./data/cloudtrail-start-transcription')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-start-transcription-'):
            script_dir = os.path.dirname(
                './data/cloudtrail-start-transcription/')
            file_path_read_transcribe = os.path.join(script_dir, each_file)
            with open(file_path_read_transcribe, 'r') as openfile_transcribe:
                cloudtrail_transcribe_object = json.load(openfile_transcribe)
                try:
                    if 'AWS_Lambda' in cloudtrail_transcribe_object['userAgent']:
                        lambda_arn = 'arn:aws:lambda:'+region+':'+account_id + \
                            ':function:' + \
                            (cloudtrail_transcribe_object['userIdentity']
                             ['principalId'].split(':')[-1])
                        transcribe_edge_data = {
                            "data": {
                                "id": lambda_arn+'-'+'transcribe',
                                "source": lambda_arn,
                                "target": 'transcribe',
                            }
                        }
                        if(cytoscape_edge_data.count(transcribe_edge_data) == 0):
                            cytoscape_edge_data.append(transcribe_edge_data)
                        print('Found connection between transcribe and lambda:{}'.format(
                            cloudtrail_transcribe_object['userIdentity']['principalId'].split(':')[-1]))
                except:
                    print('No connection between lambda and transcribe')
            openfile_transcribe.close()
