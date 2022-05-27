import os
import json

def edge_s3_to_cognito_find(cytoscape_edge_data):
    # list of files in the data directory
    list_of_files = os.listdir('./data/cloudwatch-cognito')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudwatch-get-cognito-event-'):
            script_dir = os.path.dirname('./data/cloudwatch-cognito/')
            file_path_read_translate = os.path.join(script_dir, each_file)
            with open(file_path_read_translate,'r') as openfile_cloudwatch_cognito:
                cognito_event=json.load(openfile_cloudwatch_cognito)
                openfile_cloudwatch_cognito.close()
                # get each log in the event and find for the connection between s3 and cognito
                for log in cognito_event['events']:
                    # take a look at every event
                    messageModified=json.loads(log['message'])
                    # ensure that the target is cognito
                    provider=messageModified['userIdentity']['sessionContext']['webIdFederationData']['federatedProvider']
                    cognitoArn=''
                    s3Arn=''
                    if('cognito-identity.amazonaws.com' in provider):
                        cognitoArn=messageModified['userIdentity']['sessionContext']['webIdFederationData']['attributes']['cognito-identity.amazonaws.com:aud']
                
                    # ensure that source is s3
                    if('s3.amazonaws.com' in messageModified['eventSource']):
                        s3Arn="arn:aws:s3:::"+messageModified['requestParameters']['bucketName']
                    
                    # if cognito and s3 exist then add the edge
                    if(cognitoArn and s3Arn):
                        s3_cognito_edge_data = {
                            "data": {
                                "id": "edge_"+cognitoArn+"_"+s3Arn,
                                "source": s3Arn,
                                "target": cognitoArn,
                            }
                        }
                        if(cytoscape_edge_data.count(s3_cognito_edge_data) == 0):
                            cytoscape_edge_data.append(s3_cognito_edge_data)
                            print('Found connection between s3{} and cognito:{}'.format(s3Arn,cognitoArn))
