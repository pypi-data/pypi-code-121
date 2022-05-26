import csv
import sys
from gitlab_evaluate.lib import limits


def write_to_csv(file_path, headers, data, append=False):
    '''
        Writes dictionary data to CSV file

        :param file_path: (str) path to where the CSV will be created
        :param headers: (list[str]) list of strings containing the headers for the CSV
        :param data: (dict) the data to be written to the CSV
        :param append: (bool) If set to True, headers will not be written and an existing file will get appended
    '''
    try:
        file_action = 'w' if not append else 'a'
        with open(file_path, file_action) as cf:
            writer = csv.DictWriter(cf, fieldnames=headers)
            if not append:
                writer.writeheader()
            for entry in data:
                writer.writerow(entry)
    except IOError:
          print(f"\nI/O error. Cannot create {file_path}")
          print(f"Ensure you have the proper permissions to create {file_path}.\n")
          sys.exit()

def check_size(k, v):
    # TODO: Dictionary of function pointers
    if k == "storage_size":
        return check_storage_size(v)
    elif k == "commit_count":
        return check_num_commits(v)
    elif k == "repository_size":
        return check_file_size(v)

def check_num_pl(i):
    return i > limits.PIPELINES_COUNT

def check_num_br(i):
    return i > limits.BRANCHES_COUNT

def check_num_commits(i):
    return i > limits.COMMITS_COUNT

def check_storage_size(i):
    '''Checking storage size against 20 GB'''
    return i > limits.STORAGE_SIZE

def check_registry_size(i):
    '''Checking registry size against 20 GB'''
    return i > limits.CONTAINERS_SIZE

### File size limit is 5GB
def check_file_size(i):
    return i > limits.FILE_SIZE

def check_num_issues(i):
    return i > limits.ISSUES_COUNT

def check_num_mr(i):
    return i > limits.MERGE_REQUESTS_COUNT

def check_num_tags(i):
    return i > limits.TAGS_COUNT

def check_proj_type(i):
    return i 

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
