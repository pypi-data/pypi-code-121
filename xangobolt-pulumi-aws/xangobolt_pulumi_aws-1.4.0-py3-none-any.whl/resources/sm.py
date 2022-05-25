from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import jsons
import pulumi_aws.secretsmanager as sm
import pulumi_aws_native.secretsmanager as sm_native

def Secret(stem, props, name=None, description=None, provider=None, parent=None, depends_on=None):
    sm_secret = sm.Secret(
        f'secret-{stem}',
        name=name,
        description=description,
        recovery_window_in_days=0,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sm_secret


def SecretVersion(stem, props, sec_id=None, secrets=None, provider=None, parent=None, depends_on=None):
    # string = jsonify(username, password, server, tls)
    sm_secret_version = sm.SecretVersion(
        f'secretversion-{stem}',
        secret_id=sec_id,
        secret_string=secrets,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sm_secret_version


def mqJsonify(username,password,server,tls):
    string = {
        'Username': username,
        'Password': password,
        'Server': server, 
        'Ssl': tls}
    ss = jsons.dumps(string)
    return ss

def rdsJsonify(username,password,engine,host,port,db_id,db):
    string = {
        'username': username,
        'password': password,
        'engine': engine,
        'host': host,
        'port': port,
        'dbInstanceIdentifier': db_id,
        'database': db
    }
    ss = jsons.dumps(string)
    return ss

def redshiftJsonify(username,password,engine,host,port,db_id,db):
    string = {
        'username': username,
        'password': password,
        'engine': engine,
        'host': host,
        'port': port,
        'dbInstanceIdentifier': db_id,
        'database': db
    }
    ss = jsons.dumps(string)
    return ss

def redisJsonify(username,password,server,port):
    string = {
        'username': username,
        'password': password,
        'server': server,
        'port': port,
    }
    ss = jsons.dumps(string)
    return ss

def s3Jsonify(keyname,bucket, UseBabelFish, AllowAllQueueNotification):
    string = {
        keyname: bucket,
        'UseBabelFish': UseBabelFish,
        'AllowAllQueueNotification': AllowAllQueueNotification
    }
    ss = jsons.dumps(string)
    return ss

def urlJsonify(api,portal,dash,cp):
    string = {
        'api': api,
        'dashboard': dash,
        'portal': portal,
        'cp': cp
    }
    ss = jsons.dumps(string)
    return ss