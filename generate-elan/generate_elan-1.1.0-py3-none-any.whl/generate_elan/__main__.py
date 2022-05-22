import os 
import argparse
from typing import List
from pympi.Elan import Eaf
from tqdm import tqdm

def get_audio_files(directories: str, audio_extension: str) -> list:
    paths = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(audio_extension):
                    paths.append(os.path.join(root, file))
    return paths

def create_elan_files(audio_paths: List[str]):
    for audio_path in tqdm(audio_paths, desc='Creating ELAN files', dynamic_ncols=True):
        elan_path = audio_path.replace('.wav', '.eaf')
        elan_file = Eaf(file_path=None, author='Shahad Mahmud', suppress_version_warning=True)
        
        # relative audio path
        rel_audio_path = os.path.relpath(audio_path, os.path.dirname(elan_path))
        elan_file.add_linked_file(file_path=audio_path, relpath=rel_audio_path)
        
        elan_file.remove_tier('default')
        elan_file.add_tier(tier_id='speaker')
        
        elan_file.to_file(elan_path)
    print('ELAN file creation completed')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ELAN files from a directory of audio files")
    parser.add_argument("-d", "--directory", nargs='+', help="Directory containing audio files", required=True)
    parser.add_argument("-e", "--extension", help="Audio extension", default='.wav')
    
    args = parser.parse_args()
    
    audio_paths = get_audio_files(args.directory, args.extension)
    create_elan_files(audio_paths)