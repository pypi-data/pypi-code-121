'''
Operations to speed up S3 access.
'''
import pandas as pd
from joblib import delayed, Parallel
import boto3
# from profilehooks import profile
import os
try:
    term_width = os.get_terminal_size().columns
except OSError:
    term_width = 70


DONGLES_TO_SKIP = [
    'test',
    '861579032390149', # not entirely sure why 
]


def urlifier(dongle, drive_time):
    """
    Turns any dongle and drive time into a cabana url
    """
    url = f"http://cl-cabana.eba-eez4uaij.eu-west-1.elasticbeanstalk.com/cabana/?route={dongle}%7C{drive_time}"
    return url


def get_lastest_file(dongle_id: str):
    """
    Get the lastest file in the bucket.
    TODO: eventually paratemrize the -1 to get any file
    """

    s3_resource = boto3.resource('s3')
    bucket_name = 'creationlabs-raw-data'
    bucket = s3_resource.Bucket(bucket_name)

    last_segment, last_complete_drive = get_selected_drives(None, s3_resource, bucket_name, dongle_id)
    # 064b1a99381ec054 2021-09-09--16-31-00 
    drive = '--'.join(last_segment.drive.split('--')[:-1])
    return urlifier(last_segment.dongle_id, drive)


def get_drives_df(s3_resource, bucket_name, dongle_id: str, filter=0):
    '''
    TODO: this probably requires a significant refactoring.
    '''
    from dt.ext.aws_s3_list import s3list

    bucket = s3_resource.Bucket(bucket_name)
    bucket_list = list(s3list(bucket, dongle_id, recursive=False, list_dirs=True))
    df = pd.DataFrame(bucket_list) 

    # filter out files with boot crash or swaglog
    df = df[~df.key.str[-5:-1].isin(['glog','boot','rash'])]

    df = df.key.str.split('/', expand=True)
    try:
        df.columns = ['dongle_id', 'drive','ext']
    except ValueError:
        return pd.DataFrame([])

    df['date'] = df.drive.str[:10]
    df['time'] = df.drive.str[12:20]
    df['seg_num'] = df.drive.str.split('--').str[-1]
    df['drive_time'] = df.drive.str.split('--').str[:-1].str.join('--')

    df = df.sort_values(by=['date','time'], ascending=False)
    df.seg_num = pd.to_numeric(df.seg_num, errors='coerce')

    # TODO: make available
    if filter!=0:
        df = df[df.seg_num!=0]
        df = df.reset_index().groupby('drive_time').max()
        df = df[~pd.isna(df.seg_num)].reset_index()
        
        # set display cols according to terminal width
        pd.set_option('display.max_colwidth',term_width)

    return df

def get_selected_drives(s3, s3_resource, bucket_name, dongle_id):
    """
    Get the selected drives for a dongle.
    """
    df = get_drives_df(s3_resource, bucket_name, dongle_id)
    
    if len(df) == 0:
        # return two empty series of dimensions 14
        return pd.Series(), pd.Series()

    # filter out playlist files/folders
    df = df[df.drive_time.str.len() > 16 ]

    try:
        latest_drive = df.iloc[0]
        last_complete_drives = df[df.seg_num!=0]
    except IndexError:
        return pd.Series(), pd.Series()

    if len(last_complete_drives) > 0:
        last_complete_drive = last_complete_drives.iloc[0]
    else:
        last_complete_drive = latest_drive

    return latest_drive, last_complete_drive

def parallel_get_selected_drives(dongle, bucket_name, latest, latest_files):
    """
    Get the selected drives for a dongle.
    """
    # setting up parameters for parallel processing
    s3 = boto3.session.Session(region_name='eu-west-1').client('s3')
    s3_resource = boto3.resource('s3')
    
    latest_drive, last_complete_drive = get_selected_drives(s3, s3_resource, bucket_name, dongle)
    if latest:       latest_files.append(last_complete_drive)
    else:  latest_files.append(latest_drive)
    return latest_files
    

def get_dongle_drives(s3, s3_resource, bucket_name, dongle_id: str, filter: int, latest=False):
    from pqdm.processes import pqdm
    from functools import partial
    # get number of cores in host computer
    num_cores = os.cpu_count()
   
    raw_data_buckets = s3.list_objects_v2(Bucket='creationlabs-raw-data',Delimiter='/')
    dongle_ids = [x['Prefix'].split('/')[0] for x in raw_data_buckets['CommonPrefixes']]
    
    if filter: dongle_ids = [ x for x in dongle_ids if x not in DONGLES_TO_SKIP]
    else: dongle_ids = [ x for x in dongle_ids if x not in DONGLES_TO_SKIP]

    latest_files = []
    
    # create partial for parallel_get_selected_drives
    parallel_get_selected_drives_partial = partial(parallel_get_selected_drives, bucket_name=bucket_name,
                                                   latest=latest, latest_files=latest_files)

    # get the latest file for each dongle
    parallel_results = pqdm(n_jobs=num_cores, function=parallel_get_selected_drives_partial,
                            array=dongle_ids)
    
    # get indexes of files in parallel_results that have len == 0
    no_files = [ (i,x) for i,x in enumerate(parallel_results) if len(x[0])==0]
    
    # map indexes to dongle ids
    missing_dongles = [ dongle_ids[i] for i,x in no_files ]
    
    print(f"Not found any files for dongles: {missing_dongles}")

    df = pd.DataFrame(parallel_results).reset_index()
    # remap a series of rows in df[0] to a dataframe
    df = df[0].apply(pd.Series).reset_index(drop=True)
    
    df = df[~df.ext.isna()]
    return df
    

def get_drives(target, bucket_name: str = 'creationlabs-raw-data', metadata_file: str = '/home/jakub/data/asco/devices.csv',
                        show_n: int = 50, filter=0):
    # TODO: profile
    # get all dongle ids
    import humanize

    pd.set_option('display.max_colwidth',70)
    
    s3 = boto3.session.Session(region_name='eu-west-1').client('s3')
    s3_resource = boto3.resource('s3')

    if target=='-1':
        df = get_dongle_drives(s3, s3_resource, bucket_name, target, filter, latest=True)
    elif target=='0':
        df = get_dongle_drives(s3, s3_resource, bucket_name, target, filter)
    else:
        df = get_drives_df(s3_resource, bucket_name, dongle_id=target, filter=filter)

    df = df[df.drive_time.str.len() > 16 ]

    df['upload_time'] = df.drive.str.split('--').str[:-1].str.join('--')
    df['upload_time'] = pd.to_datetime(df.upload_time, format='%Y-%m-%d--%H-%M-%S')

    # get naturaltime from now to the time of the latest file
    df['time'] = df['upload_time'].apply(lambda x: humanize.naturaldelta(x))
    df = df.sort_values(by='upload_time', ascending=False)

    if target in ['0', '-1']:
        if filter: 
            df = add_metadata(df, metadata_file)
            target_columns = ['dongle_id','drive','time','seg_num','Registration_Number', 'Company']
            print(df[target_columns])
        else: print(df[['dongle_id','drive','time','seg_num']])
    else:
        df['link'] = df.apply(lambda x: urlifier(x.dongle_id, x.drive_time), axis=1)
        df = df[['drive_time','seg_num','link']]
        
        # max display size
        pd.set_option('display.max_colwidth',term_width)
        
        # drop duplicates in link and get max seg_num 
        df = df.drop_duplicates(subset=['link'], keep='last')
        df = df.sort_values(by='drive_time', ascending=False)
        
        # print the latest files
        print(df.head(show_n))

def pull_latest(dongle_id):
    """
    Download the latest file in the bucket.
    """
    bucket = 'creationlabs-raw-data'
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, dongle_id)
    files = obj.meta.client.list_objects(Bucket=bucket, Prefix=dongle_id)
    last_segment = '/'.join(files['Contents'][-1]['Key'].split('/')[:-1])
    last_drive = last_segment.split('--')[1]
    # s3.meta.client.download_file(bucket, last_drive, dongle_id)
    cmd = f'aws s3 sync s3://{bucket}/{dongle_id} .  --exclude="*" --include="{last_drive}*"'
    print(f"Running {cmd}")
    os.system(cmd)

# @profile
def add_metadata(df: pd.DataFrame, metadata_file_path: str):
    """
    Add metadata to the dataframe.
    """

    if not os.path.exists(metadata_file_path):
        print(f"Metadata file {metadata_file_path} not found")
        return df

    meta_data = pd.read_csv(metadata_file_path)
    meta_data.columns = [x.replace(' ', '_') for x in meta_data.columns]
    
    # remove all rows with na in Dongle_ID
    meta_data = meta_data[~meta_data.Dongle_ID.isna()]

    # remove values where Deprecated = True
    meta_data = meta_data[~(meta_data.Deprecated==True)]
    
    # merge the two dataframes
    df = df.merge(meta_data, left_on='dongle_id', right_on="Dongle_ID")
    
    return df