import boto3
import json
import os
# describe all available state machine


def sfn_describe(region):
    try:
        client = boto3.client('stepfunctions', region_name=region)
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/step-function-list-state-machine-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)

        count = 0
        stateARN = []
        for items in data['stateMachines']:
            count += 1
            stateARN.append(items['stateMachineArn'])

        for i in range(count):
            response2 = client.describe_state_machine(
                stateMachineArn=stateARN[i])
            definition = response2['definition']
            response2.pop('definition')
            serializeDate = json.dumps(response2['creationDate'], default=str)
            response2['creationDate'] = serializeDate
            json_string = json.dumps(response2)

            # use os path
            file_path_write_state = os.path.join(
                script_dir, 'data/sfn/sfn-describe-'+stateARN[i]+'-policy.json')
            file_path_write_definition = os.path.join(
                script_dir, 'data/sfn/sfn-definition-'+stateARN[i]+'-policy.json')

            with open(file_path_write_state, 'w') as outfile:
                outfile.write(json_string)
                outfile.close()

            with open(file_path_write_definition, 'w') as outfile2:
                outfile2.write(definition)
                outfile2.close()
    except:
        print('File not found for sfn-describe')
