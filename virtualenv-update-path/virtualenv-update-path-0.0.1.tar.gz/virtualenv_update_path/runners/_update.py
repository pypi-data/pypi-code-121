import argparse
import os
from .._update import update_path_in_base_file, update_path_in_bat_file, _verify_folders

def update_path():
    argument_parser = argparse.ArgumentParser(description="Add a path update to a virualenv")

    argument_parser.add_argument("EnvPath", metavar='env-path', type=str, help='The path to the environment')
    argument_parser.add_argument("PathAddition", metavar='path', type=str, help='The path to add to the environment variables')

    args = argument_parser.parse_args()

    env_path = args.EnvPath
    path_addition = args.PathAddition

    if os.path.isdir(env_path):
        # Get the files
        batch_file = os.path.join(env_path, 'activate.bat')
        base_file = os.path.join(env_path, 'activate')

        # Update the file
        _verify_folders(base_file, path_addition)
        _verify_folders(batch_file, path_addition)
        update_path_in_base_file(base_file, path_addition)
        update_path_in_bat_file(batch_file, path_addition)

    # Deal with the various file types
    elif env_path.endswith('.bat'):
        update_path_in_bat_file(env_path, path_addition)
    
    elif env_path.endswith('activate'):
        update_path_in_base_file(env_path, path_addition)
    
    else:
        raise NotImplementedError('File type not supported')




