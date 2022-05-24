import os
import json

'''FIND CONNECTION INSIDE STEP FUNCTION'''


def sfn_find_connection(cytoscape_node_data, cytoscape_edge_data):
    # list of files in the data directory
    list_of_files = os.listdir('./data/sfn')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('sfn-definition-'):
            script_dir = os.path.dirname('./data/sfn/')
            file_path_read = os.path.join(script_dir, each_file)
            with open(file_path_read, 'r') as openfile:
                unfiltered_sfn_arn = each_file[15:]
                filtered_sfn_arn = (unfiltered_sfn_arn.split('.')[0])[0:-7]
                print(filtered_sfn_arn)
                try:
                    sfn_connection_object = json.load(openfile)
                    listOfStates = list(
                        sfn_connection_object['States'].values())
                    totalStates = len(sfn_connection_object['States'].keys())
                    for i in range(totalStates):
                        # sourceId for edge
                        sourceId = ''
                        # if state is lambda
                        if('lambda' in listOfStates[i]['Resource']):
                            print('Lambda Found in SFN')
                            sourceId = (
                                listOfStates[i]['Parameters']['FunctionName'])[:-8]
                            for item in cytoscape_node_data:
                                if item['data']['id'] == sourceId:
                                    item['data'].update(
                                        {"parent": filtered_sfn_arn})
                        # if state is sns
                        if('sns' in listOfStates[i]['Resource']):
                            # give the last state parent node
                            print('SNS Found in SFN')
                            sourceId = (
                                listOfStates[i]['Parameters']['TopicArn'])
                            for item in cytoscape_node_data:
                                if item['data']['id'] == sourceId:
                                    item['data'].update(
                                        {"parent": filtered_sfn_arn})
                        # if this is not end state
                        if(i != totalStates-1):
                            print('this is not end state', i)
                            targetId = ''
                            # if next state is lambda
                            if('lambda' in listOfStates[i+1]['Resource']):
                                targetId = (
                                    listOfStates[i+1]['Parameters']['FunctionName'])[:-8]
                            # if next state is sns
                            if('sns' in listOfStates[i+1]['Resource']):
                                targetId = (
                                    listOfStates[i+1]['Parameters']['TopicArn'])
                            # edge data
                            sfn_edge_data = {
                                "data": {
                                    "id": sourceId+'-'+targetId,
                                    "source": sourceId,
                                    "target": targetId,
                                }
                            }
                            cytoscape_edge_data.append(sfn_edge_data)

                except:
                    print('No connection inside step function')
            openfile.close()