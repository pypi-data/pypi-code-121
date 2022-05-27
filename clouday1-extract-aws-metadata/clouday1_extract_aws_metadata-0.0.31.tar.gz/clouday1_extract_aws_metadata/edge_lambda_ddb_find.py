import os
import json

'''FIND CONNECTION BETWEEN DDB AND LAMBDA'''


def edge_lambda_ddb_find(cytoscape_edge_data, region):
    # retrieve lambda object
    script_dir = os.path.dirname('.')
    file_path_read_lambda = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    with open(file_path_read_lambda, 'r') as openfile_lambda:
        lambda_object = json.load(openfile_lambda)
        openfile_lambda.close()
    # retrieve ddb object
    file_path_read_ddb = os.path.join(
        script_dir, 'data/dynamodb-list-table-'+region+'.json')
    with open(file_path_read_ddb, 'r') as openfile_ddb:
        ddb_object = json.load(openfile_ddb)
        openfile_ddb.close()
    # logic to find edge between lambda and ddb
    for lambdas in lambda_object['Functions']:
        for ddb in ddb_object['TableNames']:
            try:
                account_id=lambdas['FunctionArn'].split(':')[4]
                if lambdas['Environment']['Variables']['DB_TABLE_NAME'] == ddb:
                    print('Found connection between {} and {}'.format(
                        lambdas['FunctionName'], ddb))
                    arn_ddb='arn:aws:dynamodb:'+region+':'+account_id+':table/'+ddb
                    cytoscape_edge_data.append({
                        "data": {
                            "id": lambdas['FunctionName'] + '-' + arn_ddb,
                            "source": lambdas["FunctionArn"],
                            "target": arn_ddb,
                        }
                    })
            except:
                print('No connection between {} and {}'.format(
                    lambdas['FunctionName'], ddb))
