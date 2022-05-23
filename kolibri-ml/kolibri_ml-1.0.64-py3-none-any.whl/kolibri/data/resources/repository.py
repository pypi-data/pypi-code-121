from kolibri.settings import DIRS,GITHUB_TOKEN, GITHUB_REPO_NAME
from os import path, mkdir
from pathlib import Path
from github import Github
import os

for d in DIRS:
    if not path.exists(d):
        mkdir(d)



try:
    Resources_sha
except NameError:
    Resources_sha={}
path_i=Path(".")
path=path_i
try:
    _repo=Github(GITHUB_TOKEN).get_repo(GITHUB_REPO_NAME)
    __branch=_repo.get_branch("main").commit
    can_reach_repository = True
except Exception as e:
    print("could not reach server "+e)
    can_reach_repository=False
    _repo=None
    __branch=None
    pass





def traverse(node, path = [], paths = []):

    if hasattr(node, "path"):
        path.append(node.path)
    if hasattr(node, "type") and node.type == "blob":
        data=dict(node.raw_data)
        data['path']='/'.join(path)
        if os.path.splitext(data["path"])[1] in ['.gz', '.tgz', '.json']:
            data['url'] = "https://raw.githubusercontent.com/mbenhaddou/kolibri-data/main/{}".format(data['path'])
        else:
            data['url']="https://media.githubusercontent.com/media/mbenhaddou/kolibri-data/main/{}".format(data['path'])
#        data['url']="https://media.githubusercontent.com/media/mbenhaddou/kolibri-data/main/{}".format(data['path'])
#        data['raw_url']="https://raw.githubusercontent.com/mbenhaddou/kolibri-data/main/{}".format(data['path'])
        data['url'] = "https://raw.githubusercontent.com/mbenhaddou/kolibri-data/main/{}".format(data['path'])
        Resources_sha['/'.join(path[1:])]=data

        path.pop()
    else:
        for child in _repo.get_git_tree(node.sha).tree:
            traverse(child, path, paths)
        if path:
            path.pop()

p=[]
if __branch is not None and Resources_sha=={}:
        print('checking resources')
        try:
            for child in _repo.get_git_tree(__branch.sha).tree:
                if child.path=="data":
                    traverse(child, p, Resources_sha)
        except:
            pass

