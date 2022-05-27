import os
'''Prepare for translate'''


def translate_prepare_node(region, account_id, cytoscape_node_data):
    # list of files in the data directory
    list_of_files = os.listdir('./data/cloudtrail-translate-text')
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-start-translate-text-'):
            print('Found a cloudtrail translate file')
            cytoscape_node_data.append({
                "data": {
                    "type": "Translate",
                    "id": "translate",
                    "region": region,
                    "account_id": account_id,
                    "name": "translate",
                    "cost_for_month": "15.00 USD"
                }
            })
            break
