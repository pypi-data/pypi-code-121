import os
import json


def edge_sns_to_lambda_find(cytoscape_edge_data):
    list_of_files = os.listdir('./data/lambda-get-policy')
    # each file read description policy of one lambda
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('lambda-arn'):
            script_dir = os.path.dirname('./data/lambda-get-policy/')
            file_path_read_connection = os.path.join(script_dir, each_file)
            with open(file_path_read_connection, 'r') as openfile:
                sns_lambda_description = json.load(openfile)
                modified_policy = json.loads(sns_lambda_description['Policy'])
                # in this policy there would be stated one or several service that could trigger lambda
                for items in (modified_policy['Statement']):
                    try:
                        lambdaArn = items['Resource']
                        triggerArn = items['Condition']['ArnLike']['AWS:SourceArn']
                        # check if source trigger is sns
                        if('sns.amazonaws.com' in items['Principal']['Service']):
                            print('Found connection between SNS:{} and lambda:{}'.
                                format(triggerArn, lambdaArn))
                            # put data into cytoscape_edge_data
                            data_sns_lambda = {
                                "data": {
                                    "id": "edge_"+triggerArn+'_to_'+lambdaArn,
                                    "source": triggerArn,
                                    "target": lambdaArn
                                }
                            }
                            cytoscape_edge_data.append(data_sns_lambda)
                    except:
                        print('Something error in sns and lambda edge')