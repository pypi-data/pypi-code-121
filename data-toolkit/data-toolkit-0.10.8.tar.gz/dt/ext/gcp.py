import os
import subprocess as sp
import pandas as pd
import json 

term_wdith = os.get_terminal_size().columns

pd.set_option('display.max_colwidth',term_wdith - 20)

def gcp_ls():
    # TODO: non-preemptible instances have wrong formatting.
    instances_list = sp.check_output('gcloud compute instances list'.split(' '))
    stringified_instances = str(instances_list).split('\\n')
    df = pd.DataFrame([ d.split()  for d in stringified_instances[:-1] ])
    # df.rename(columns=df.iloc[0]).drop(df.index[0])
    df = df.T.set_index(0).T
    return df


def scp(inst_id: int, rpath: str):
    gcp_instances = gcp_ls()
    tar_ip = gcp_instances.iloc[inst_id-1].EXTERNAL_IP
    tar_name = gcp_instances.iloc[inst_id-1].iloc[0]
    sftp = os.path.abspath(__file__).split('/')[:-2] + ['templates', 'sftp.json']

    scp_json = json.load(open('/'.join(sftp)))
    scp_json['host'] = tar_ip
    scp_json['name'] = tar_name
    scp_json['remotePath'] = rpath
    
    if not os.path.exists('.vscode'): os.mkdir('.vscode')
    tar_file = open(f"{os.getcwd()}/.vscode/sftp.json",'w')

    json.dump(scp_json, tar_file)
    print(f'Succesfully written {tar_name} (IP: {tar_ip}) into {str(tar_file)}')
    # import ipdb; ipdb.set_trace()