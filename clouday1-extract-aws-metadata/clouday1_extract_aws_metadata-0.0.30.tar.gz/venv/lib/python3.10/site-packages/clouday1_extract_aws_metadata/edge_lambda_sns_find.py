import os
import json

'''FIND CONNECTION BETWEEN LAMBDA AND SNS'''


def edge_lambda_sns_find(cytoscape_edge_data, region):
    # retrieve sns object
    script_dir = os.path.dirname('.')
    file_path_read_sns = os.path.join(
        script_dir, 'data/sns-list-topic-'+region+'.json')
    with open(file_path_read_sns, 'r') as openfile_sns:
        sns_object = json.load(openfile_sns)
        openfile_sns.close()
    # retrieve lambda object
    file_path_read_lambda = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    with open(file_path_read_lambda, 'r') as openfile_lambda:
        lambda_object = json.load(openfile_lambda)
    # prepare edge for sns and lambda
    for lambdas in lambda_object['Functions']:
        for sns in sns_object['Topics']:
            try:
                if(lambdas['Environment']['Variables']['SNS_TOPIC'] == sns['TopicArn']):
                    print('Found connection between lambda{} and sns{}'.format(
                        lambdas['FunctionName'], sns['TopicArn']))
                    lambda_sns_edge_data = {
                        "data": {
                            "id": lambdas['FunctionArn']+'-'+sns['TopicArn'],
                            "source": lambdas['FunctionArn'],
                            "target": sns['TopicArn'],
                        }
                    }
                    if(cytoscape_edge_data.count(lambda_sns_edge_data) == 0):
                        cytoscape_edge_data.append(lambda_sns_edge_data)
                    cytoscape_edge_data.append(lambda_sns_edge_data)
            except:
                print('No connection between lambda{} and sns{}'.format(
                    lambdas['FunctionName'], sns['TopicArn'])
                )
