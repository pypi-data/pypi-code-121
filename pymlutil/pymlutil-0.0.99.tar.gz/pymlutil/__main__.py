import sys
import os

from .s3 import *
from .jsonutil import *
from pymlutil.imutil import ImUtil, ImTransform

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process arguments')

    parser.add_argument('-d', '--debug', action='store_true',help='Wait for debuggee attach')   
    parser.add_argument('-debug_port', type=int, default=3000, help='Debug port')
    parser.add_argument('-debug_address', type=str, default='0.0.0.0', help='Debug port')

    parser.add_argument('-credentials', type=str, default='creds.yaml', help='Credentials file.')

    parser.add_argument('-src', type=str, default=None, help='source path')
    parser.add_argument('-dest', type=str, default=None, help='destindation path')

    parser.add_argument('--PutDir', '-p', action='store_true',help='Put directory in S3') 
    parser.add_argument('-set', type=str, default='dataset', help='set defined in credentials file')

    parser.add_argument('-clone', action='store_true',help='Clone objects from source to destination S3')
    parser.add_argument('-srcS3', type=str, default=None, help='path to source directory')
    parser.add_argument('-srcSet', type=str, default='dataset', help='set defined in credentials file')
    parser.add_argument('-destS3', type=str, default=None, help='path to source directory')
    parser.add_argument('-destSet', type=str, default='dataset', help='set defined in credentials file')

    args = parser.parse_args()
    return args

def main(args):

    if args.PutDir:
        s3, creds, s3def = Connect(args.credentials)
        if args.set not in s3def['sets']:
            print('PutDir failed: args.set {} not found in credentials file'.format(args.set))
        elif args.src is None:
            print('PutDir failed: args.src is None')
        elif args.dest is None:
            print('PutDir failed: args.dest is None')
        else:
            dest = '{}/{}'.format(s3def['sets'][args.set]['prefix'], args.dest)
            s3.PutDir(s3def['sets'][args.set]['bucket'], args.src, dest)

    if args.clone:
        s3Src, _, s3SrcDef = Connect(args.credentials, s3_name=args.srcS3)
        s3Dest, _, s3DestDef = Connect(args.credentials, s3_name=args.destS3)

        srcSet = None
        if args.srcSet in s3SrcDef['sets']:
            srcSet = s3SrcDef['sets'][args.srcSet]
        else:
            raise ValueError('{} {} clone srcSet failure {}'.format(__file__, __name__, args.srcSet))

        destSet = None
        if args.destSet in s3DestDef['sets']:
            destSet = s3DestDef['sets'][args.destSet]
        else:
            raise ValueError('{} {} clone destSet failure {}'.format(__file__, __name__, args.destSet))

        s3Dest.CloneObjects(destSet['bucket'], args.dest , s3Src, srcSet['bucket'], args.src)

    print('pymluitil complete')

    
if __name__ == '__main__':
    import argparse
    args = parse_arguments()

    if args.debug:
        print("Wait for debugger attach on {}:{}".format(args.debug_address, args.debug_port))
        import debugpy

        debugpy.listen(address=(args.debug_address, args.debug_port)) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client()  # Pause the program until a remote debugger is attached
        print("Debugger attached")

    main(args)