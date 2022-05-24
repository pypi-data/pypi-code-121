import os
import json

def edge_lambda_to_sfn_find(region,cytoscape_edge_data):
    script_dir=os.path.dirname('.')
    file_path_read_lambda=os.path.join(script_dir,'data/lambda-list-functions-'+region+'.json')
    # read for lambda object
    with open(file_path_read_lambda,'r') as openfile_lambda:
        lambda_object=json.load(openfile_lambda)
        openfile_lambda.close()
    file_path_read_sfn=os.path.join(script_dir,'data/step-function-list-state-machine-'+region+'.json')
    # read for sfn object
    with open(file_path_read_sfn,'r') as openfile_sfn:
        sfn_object=json.load(openfile_sfn)
        openfile_sfn.close()

    for lambdas in lambda_object['Functions']:
        for sfn in sfn_object['stateMachines']:
            # find matching SFN_ARN environment variable in lambda and match to each sfn
            try:
                if lambdas['Environment']['Variables']['SFN_ARN']==sfn['stateMachineArn']:
                    print('Found connection between Lambda{} and SFN{}'.format(lambdas['Environment']['Variables']['SFN_ARN'],
                    sfn['stateMachineArn']))
                    data_lambda_to_sfn={
                        "data":{
                            "id":"edge_"+lambdas['FunctionArn']+'_'+sfn['stateMachineArn'],
                            "source":lambdas['FunctionArn'],
                            "target":sfn['stateMachineArn']
                        }
                    }
                    cytoscape_edge_data.append(data_lambda_to_sfn)
            except:
                print('No SFN is found')

