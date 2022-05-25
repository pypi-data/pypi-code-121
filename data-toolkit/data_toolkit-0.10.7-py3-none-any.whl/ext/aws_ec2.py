import boto3
import warnings
warnings.simplefilter(action='ignore')
import pandas as pd
import os
import humanize

def parse_keys(x):
    try:
        return [ r['Value'] for r in x if r['Key']=='Name'][0]
    except:
        print("one of the instances does not have a name")

def get_ec2(status: str, profile: str, filter: str):
    possible_filters = dict(
        live=[{"Name":"instance-state-name", "Values":["running"] }],
        all=[]
    )

    filters = possible_filters[filter]

    ec2 = boto3.session.Session(profile_name=profile, region_name='eu-west-1').client('ec2')
    live_inst = ec2.describe_instances(Filters=filters)
    df = pd.DataFrame(live_inst['Reservations'])
    try:
        df_list = [ pd.DataFrame.from_dict(x[0], orient='index') for x in df['Instances'].values ]
    except KeyError as e:
        return f'No instances running for {profile} with filter {filter}'
    full_df = pd.concat(df_list,axis=1, sort=True).T

    full_df['SG'] = [ ','.join([i['GroupName'] for i in f ]) for f in  full_df.SecurityGroups  ] 
    
    # humanize all LaunchTime timestamps
    # full_df['LaunchTime'] = [ humanize.naturaltime(i) for i in full_df.LaunchTime.values]  - pd.Timestamp.now()
    full_df['LaunchTime'] = full_df.LaunchTime.astype('int64').apply(lambda x: humanize.naturaldelta(pd.to_datetime(x)))

    # shorten CPU options
    full_df['CPUs'] = full_df.CpuOptions.apply(lambda x: x['CoreCount'])
    del full_df['CpuOptions']

    target_columns = 'CPUs InstanceId InstanceType LaunchTime SG PublicIpAddress Tags PrivateIpAddress'.split(' ')

    # check if tags present
    if 'Tags' not in full_df.columns:
        full_df.Tags = 'N/A'
    return_df = full_df[target_columns]

    return_df['name'] = return_df.Tags.apply(lambda x: parse_keys(x))

    pd.set_option('display.max_colwidth', 40)

    return return_df

def update_ec2_ssh(profile: str):
    from .sshconf import read_ssh_config

    # get ssh config path and expand user path
    ssh_path = os.path.expanduser(os.path.join('~', '.ssh', 'config'))

    # get ec2 and ssh config to get hosts
    running_instances = get_ec2("running", profile=profile, filter='live').T
    ssh_config_obj = read_ssh_config(ssh_path)
    hosts = ssh_config_obj.hosts()
    changes = {}

    for index, row in running_instances.T.iterrows():
        try:
            target_host = [ t['Value'] for t in row.Tags if t['Key']=='Name'][0]
        except IndexError as e:
            raise IndexError("You probably did not set up the EC2 tags correctly (there are empties)")
        except TypeError as e:
            print(f"Raised TypeError {e}. Likely missing tags for row {row}")
        target_ip = row.PublicIpAddress
        # change and write
        if target_host in ssh_config_obj.hosts_:
            ssh_config_obj.set(target_host, HostName=target_ip)
            changes[target_host] = target_ip
            ssh_config_obj.write(ssh_path)
        else:
            print(f'Could not find {target_host} in SSH config.')

    print(f"Changed {changes.keys()} to {changes.items()} respectively.")


def start_ec2(instance_id: str, profile: str):
    ec2 = boto3.session.Session(profile_name=profile, region_name='eu-west-1').client('ec2')

    resp = ec2.start_instances(InstanceIds=[instance_id])
    print(resp)


def stop_ec2(inst_id: str, profile: str):
    ec2 = boto3.session.Session(profile_name=profile, region_name='eu-west-1').client('ec2')

    resp = ec2.stop_instances(InstanceIds=[instance_id])
    print(resp)

def change_inst_type(inst_id: str, profile: str):
    ec2 = boto3.session.Session(profile_name=profile, region_name='eu-west-1').client('ec2')

    resp = ec2.change