from re import findall
from gitlab_ps_utils.api import GitLabApi
from gitlab_ps_utils.misc_utils import safe_json_response
from gitlab_evaluate.lib import human_bytes as hb
from gitlab_evaluate.lib import utils

gl_api = GitLabApi()

# Project only keyset-based pagination - https://docs.gitlab.com/ee/api/#keyset-based-pagination

def get_last_id(link):
    # Get id_after value. If the Link key is missing it's done, with an empty list response
    return findall(r"id_after=(.+?)&", link)[0] if link else None

'''
Generates the URL to get the full project info with statistics
'''
def proj_info_get(i, source):
    '''Trying to create proper api call with project id.'''
    return f"{source}/api/v4/projects/{str(i)}?statistics=true"

def proj_pl_get(i, source):
    '''Trying to create proper api call with project id to get the number of pipelines.'''
    i = str(i)
    pl_inf_url = f"/api/v4/projects/{i}/pipelines"
    gl_proj_pl = source + pl_inf_url
    return gl_proj_pl

def proj_issue_get(i, source):
    '''Trying to create proper api call with project id to get the number of issues.'''
    i = str(i)
    issue_inf_url = f"/api/v4/projects/{i}/issues"
    gl_issue_pl = source + issue_inf_url
    return gl_issue_pl

def proj_branch_get(i, source):
    '''Trying to create proper api call with project id to get the number of branches.'''
    i = str(i)
    branch_inf_url = f"/api/v4/projects/{i}/repository/branches"
    gl_branch_pl = source + branch_inf_url
    return gl_branch_pl

def proj_mr_get(i, source):
    '''Trying to create proper api call with project id to get the number of MR's.'''
    i = str(i)
    mr_inf_url = f"/api/v4/projects/{i}/merge_requests"
    gl_mr_pl = source + mr_inf_url
    return gl_mr_pl

def proj_tag_get(i, source):
    '''Trying to create proper api call with project id to get the number of tags.'''
    i = str(i)
    tag_inf_url = f"/api/v4/projects/{i}/repository/tags"
    gl_tag_pl = source + tag_inf_url
    return gl_tag_pl

def proj_packages_url(i):
    return f"projects/{str(i)}/packages"

def proj_registries_url(i):
    return f"projects/{str(i)}/registry/repositories"

def proj_registries_tags_url(pid, rid):
    return f"projects/{str(pid)}/registry/repositories/{str(rid)}/tags"

def proj_registries_tag_details_url(pid, rid, tid):
    return f"projects/{str(pid)}/registry/repositories/{str(rid)}/tags/{tid}"

def get_registry_details(i):
    return f"registry/repositories/{str(i)}?size=true"

# def proj_commits_get(i, source):
#     '''Trying to create proper api call with project id to get the number of commits.'''
#     i = str(i)
#     commits_url = "/api/v4/projects/{i}/repository?statistics=yes"
#     gl_commits_pl = source + commits_url
#     return gl_commits_pl       
### Functions - Return API Data
# Gets the X-Total from the statistics page with the -I on a curl
def check_x_total_value_update_dict(check_func, p, url="", headers={}, value_column_name="DEFAULT_VALUE", over_column_name="DEFAULT_COLUMN_NAME", results={}):
    flag = False
    if resp := gl_api.generate_get_request(host="", api="", token=headers.get("PRIVATE-TOKEN"), url=url): 
        num = int(resp.headers.get('X-Total', 0))
        num_over = check_func(num)
        if num_over:
            flag = True
        results[value_column_name] = num
        results[over_column_name] = num_over
    else:
        print(f"Could not retrieve {value_column_name} for project: {p.get('id')} - {p.get('name')}")
    return flag
        
# gets the full stats of the project and sorts based on the returned items, passing a few through the HumanReadable utility
def check_full_stats(url, project, my_dict, headers={}):
    if resp := gl_api.generate_get_request(host="", api="", token=headers.get("PRIVATE-TOKEN"), url=url): 
        
        result = resp.json()
        if kind := result.get("namespace"):
            my_dict.update({"kind": kind.get("kind")})
        if stats := result.get("statistics"):
            # storage_size = result.get('storage_size')
            # commit_count = stats.get('commit_count')
            # repository_size = stats.get('repository_size')
            # wiki_size = stats.get['wiki_size']
            # lfs_objects_size = stats.get['lfs_objects_size']
            # job_artifacts_size = stats.get['job_artifacts_size']
            # snippets_size = stats.get['snippets_size']
            # packages_size = stats.get['packages_size']

            for k, v in stats.items():
                my_dict.update({ k: hb.HumanBytes.format(v, True) if k != "commit_count" else v, k + "_over": utils.check_size(k, v)}) 
                # my_dict[k] = {
                #     "value": hb.HumanBytes.format(v, True) if k != 'commit_count' else v,
                #     "over": utils.check_size(k, v)
                # }
        else:
            print(f"Could not extracts stats for project {project.get('name')}.\n")
    else:
        print(f"Could not retrieve project with stats for project id: {project.get('id')}")

def get_registry_size(pid, source, token):
    """
        Iterates over a project's registry data and returns the total size of registry data
    """
    registry_hashes = {}
    for registry_repo in gl_api.list_all(source, token, proj_registries_url(pid)):
        if isinstance(registry_repo, str):
            print(' Container registry inaccessible or disabled. Skipping')
            continue
        rid = registry_repo['id']
        for registry_tags in gl_api.list_all(source, token, proj_registries_tags_url(pid, rid)):
            # print(registry_tags)
            tid = registry_tags['name']
            repo_details = safe_json_response(gl_api.generate_get_request(source, token, proj_registries_tag_details_url(pid, rid, tid)))
            if repo_size := repo_details.get('total_size'):
                registry_hashes['short_revision'] = repo_size

    total_size = sum(registry_hashes.values())

    return utils.sizeof_fmt(total_size), utils.check_storage_size(total_size)

def getApplicationInfo(host,token,api):
    if resp := gl_api.generate_get_request(host=host, token=token, api=api):
        result = resp.json()
        ## error handling - look for 200 
        return result

def getVersion(host,token,api):
    if resp := gl_api.generate_get_request(host=host,token=token,api=api):
        result = resp.json()
        ## error handling - look for 200 
        return result

def getArchivedProjectCount(host,token):
    if resp := gl_api.generate_get_request(host=host,token=token,api='projects?archived=True'):
        result = resp.headers.get('X-Total')
        return result