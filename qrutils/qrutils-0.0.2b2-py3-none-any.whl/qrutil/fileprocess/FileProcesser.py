import os

def find_file_in_dir(dir: str, spacial_key=''):
    file_names = []
    for root, dirs ,files in os.walk(dir, topdown=False):
        if spacial_key == '':
            file_names += files
        else:
            for name in files:
                if spacial_key in name:
                    file_names.append(name)
    return file_names


if __name__ == '__main__':
    result = find_file_in_dir('dist', 'whl')
    print(result)
