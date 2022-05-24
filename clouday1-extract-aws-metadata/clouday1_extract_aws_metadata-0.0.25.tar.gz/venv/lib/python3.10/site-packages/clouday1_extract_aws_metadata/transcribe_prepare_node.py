import os


def transcribe_prepare_node(region, account_id, cytoscape_node_data):
    '''Prepare for transcribe'''
    list_of_files = os.listdir(
        './data/cloudtrail-start-transcription')  # list of files in the data directory
    for each_file in list_of_files:
        # since its all type str you can simply use startswith
        if each_file.startswith('cloudtrail-start-transcription'):
            print('Found a cloudtrail transcribe file')
            cytoscape_node_data.append({
                "data": {
                    "type": "Transcribe",
                    "id": "transcribe",
                    "region": region,
                    "account_id": account_id,
                    "name": "transcribe",
                    "cost_for_month": "24.04 USD"
                }
            })
            break
