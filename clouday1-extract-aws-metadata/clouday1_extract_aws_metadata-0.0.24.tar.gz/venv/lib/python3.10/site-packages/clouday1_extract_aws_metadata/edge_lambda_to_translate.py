import os
import json

'''FIND CONNECTION BETWEEN LAMBDA AND TRANSLATE'''


def edge_lambda_to_translate_find(cytoscape_edge_data, region, account_id):
    # list of files in the data directory
    list_of_files = os.listdir('./data/cloudtrail-translate-text')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-start-translate-text-'):
            script_dir = os.path.dirname('./data/cloudtrail-translate-text/')
            file_path_read_translate = os.path.join(script_dir, each_file)
            with open(file_path_read_translate, 'r') as openfile_translate:
                cloudtrail_translate_object = json.load(openfile_translate)
                openfile_translate.close()
                try:
                    if 'AWS_Lambda' in cloudtrail_translate_object['userAgent']:
                        lambda_arn = 'arn:aws:lambda:'+region+':'+account_id + \
                            ':function:' + \
                            (cloudtrail_translate_object['userIdentity']
                             ['principalId'].split(':')[-1])
                        translate_edge_data = {
                            "data": {
                                "id": lambda_arn+'-'+'translate',
                                "source": lambda_arn,
                                "target": 'translate',
                            }
                        }
                        if(cytoscape_edge_data.count(translate_edge_data) == 0):
                            cytoscape_edge_data.append(translate_edge_data)
                        print('Found connection between translate and lambda:{}'.format(
                            cloudtrail_translate_object['userIdentity']['principalId'].split(':')[-1]))
                except:
                    print('No connection between lambda and translate')
