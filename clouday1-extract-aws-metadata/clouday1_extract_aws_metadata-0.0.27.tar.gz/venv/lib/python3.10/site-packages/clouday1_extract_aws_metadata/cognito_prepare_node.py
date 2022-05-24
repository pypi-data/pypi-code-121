import os
import json


def cognito_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read_cognito = os.path.join(
        script_dir, 'data/cognito-list-identity-pools-'+region+'.json')
    with open(file_path_read_cognito, 'r') as openfile_cognito:
        cognito_object = json.load(openfile_cognito)
        openfile_cognito.close()
    for cognito in cognito_object['IdentityPools']:
        file_path_read_cognito_description=os.path.join(script_dir,'data/cognito-describe/cognito-describe-'+cognito['IdentityPoolName']+'-'+region+'.json')
        with open(file_path_read_cognito_description,'r') as openfile_describe_cognito:
            cognito_describe_object=json.load(openfile_describe_cognito)
            openfile_describe_cognito.close()
        cognito_node={
            'data': {
                'id': cognito['IdentityPoolId'],
                'arn': cognito['IdentityPoolId'],
                'type': 'Cognito',
                'name': cognito['IdentityPoolName'],
                'account_id': account_id,
                'region': region,
                "cost_for_month": "0.00 USD"
            }
        }
        cognito_node['data'].update(cognito_describe_object)
        cognito_node['data']['tag'] = cognito_node['data']['IdentityPoolTags']
        cognito_node['data'].pop('IdentityPoolTags')
        cytoscape_node_data.append(cognito_node)

