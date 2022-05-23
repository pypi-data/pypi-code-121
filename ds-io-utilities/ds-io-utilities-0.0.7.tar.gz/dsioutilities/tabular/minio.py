import s3fs
from minio import Minio
from ..utils import input_or_output, get_dataset_property

def set_connection(access_key, secret_key, url):

    minio_access_key = access_key
    minio_secret_key = secret_key
    endpoint_url = url

    class S3FileSystemPatched(s3fs.S3FileSystem):
        def __init__(self, *k, **kw):
            
            # Fix for calling set connection as many times as needed. Another fix is to remove kw from init method.
            if "key" in kw:
                kw.pop("key")
                kw.pop("secret")
                kw.pop("client_kwargs")
            
            super(S3FileSystemPatched, self).__init__( *k,
                                                    key = minio_access_key,
                                                    secret = minio_secret_key,
                                                    client_kwargs={'endpoint_url': endpoint_url},
                                                    **kw)
            print('S3FileSystem is patched with url:  ' + endpoint_url)

    s3fs.S3FileSystem = S3FileSystemPatched


def minio_ls(address, access_key, secret_key, bucket_name, folder, extention):

    if folder[-1] != "/":
        folder = folder + "/"

    client = Minio(
        address,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    objects = client.list_objects(bucket_name=bucket_name, prefix=folder)

    return [x._object_name for x in objects if extention in x._object_name[-len(extention):]]



def get_path(name):
    
    # Get credentials
    minio_url = get_dataset_property(name=name, prop="minIO_URL")
    access_key = get_dataset_property(name=name, prop="minIO_ACCESS_KEY")
    secret_key = get_dataset_property(name=name, prop="minIO_SECRET_KEY")
    bucket_name = get_dataset_property(name=name, prop="minio_bucket")
    
    # Set connection for pandas reading
    set_connection(access_key=access_key, secret_key=secret_key, url=minio_url)

    if input_or_output(name) == "input":
        # List all files in dataset folder
        files_list = minio_ls(address=minio_url.replace("http://", ""), access_key=access_key, secret_key=secret_key, bucket_name=bucket_name, 
                                folder=get_dataset_property(name),
                                extention=".csv")
        if len(files_list) > 1:
            return ["s3://" + bucket_name + "/" + x for x in files_list]
        elif len(files_list) == 1:
            return "s3://" + bucket_name + "/" + files_list[0]
        else:
            raise Exception("Dataset is empty!")

    elif input_or_output(name) == "output":
        return "s3://" + bucket_name + "/" + get_dataset_property(name) + "/dataset.csv"
    else:
        raise Exception("Error: cannot establish if dataset is an input or output one! Are you sure the name is right?")
