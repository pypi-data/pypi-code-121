import os
import sys
from shlex import quote

from sumoappclient.common.utils import get_normalized_path
from sumoappclient.common.logger import get_logger

CENTRAL_PUBLIC_APPS_REPO = "sumologic-private-partner-apps"
CENTRAL_PRIVATE_APPS_REPO = "sumologic-public-partner-apps"
CENTRAL_REPO_OWNER = "SumoLogic"
BRANCH_TO_SYNC = "master"

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoapputils.common.utils import run_cmd
from sumoapputils.appdev.fifoqueue import FifoQueue

PUBLIC_SUBMODULES_JOB_QUEUE = "pull_public_submodule_jobs"
PRIVATE_SUBMODULES_JOB_QUEUE = "pull_private_submodule_jobs"


def add_submodule(submodule_repo_full_name, submodule_branch_name):
    submodule_repo_name = submodule_repo_full_name.split('/')[1]
    submodule_repo_url = 'git@github.com:%s.git' % submodule_repo_full_name
    run_cmd('git submodule add -b %s -- %s' % (quote(submodule_branch_name), quote(submodule_repo_url)))
    run_cmd('git submodule init -- %s' % quote(submodule_repo_name))


def add_or_update_submodule(submodule_repo_full_name, submodule_branch_name=BRANCH_TO_SYNC):
    submodule_repo_name = submodule_repo_full_name.split('/')[1]
    if not os.path.isdir(submodule_repo_name):
        add_submodule(submodule_repo_full_name, submodule_branch_name)

    # assuming git > v1.8
    run_cmd('git submodule update --remote --merge -- %s' % quote(submodule_repo_name))
    run_cmd('git add %s' % quote(submodule_repo_name))
    run_cmd('git commit -m \"move submodule to latest commit in master\"')
    return_code, _ = run_cmd('git push origin %s' % quote(submodule_branch_name))
    return return_code


def remove_submodule(submodule_repo_full_name):
    submodule_repo_name = submodule_repo_full_name.split('/')[1]
    print("removing submodule %s" % quote(submodule_repo_full_name))
    rc, _ = run_cmd('git submodule deinit -f %s' % quote(submodule_repo_name))
    if rc == 0:
        rc, _ = run_cmd('git rm -f %s' % quote(submodule_repo_name))
    if rc == 0:
        rc, _ = run_cmd('git add -u && git commit -m "Removed submodule"')
    if rc == 0:
        rc, _ = run_cmd('rm -rf .git/modules/%s' % quote(submodule_repo_name))


def pull_parent_repo_with_submodules(parent_dir, owner, apps_repo, parent_repo_branch_name):


    if parent_dir is None:
        all_partner_repo = 'git@github.com:%s/%s.git' % (owner, apps_repo)
        run_cmd('git clone --recursive %s' % quote(all_partner_repo))
        repo_dir = os.path.join(os.getcwd(), apps_repo)
    else:
        if parent_dir.startswith("/"):
            repo_dir = parent_dir
        else:
            repo_dir = get_normalized_path(parent_dir)

    os.chdir(repo_dir)
    run_cmd('git checkout %s' % quote(parent_repo_branch_name))

def update_all_private_submodules(parent_dir=None, num_items=5):
    jobs = FifoQueue(PRIVATE_SUBMODULES_JOB_QUEUE).deque(num_items)

    pull_parent_repo_with_submodules(parent_dir, CENTRAL_PRIVATE_APPS_REPO, CENTRAL_REPO_OWNER, BRANCH_TO_SYNC)
    failed_tests_cnt = 0
    failed_repos = []

    for job in jobs:
        has_failures = add_or_update_submodule(job['repo_full_name'], BRANCH_TO_SYNC)

        if has_failures:
            failed_tests_cnt += 1
            failed_repos.append("%s:%s" % (job['repo_full_name'], BRANCH_TO_SYNC))

    print("Total %d: Failed: %d Failed repos: %s" % (len(jobs), failed_tests_cnt, ",".join(failed_repos)))

    exit_status = 1 if failed_tests_cnt > 0 else 0
    sys.exit(exit_status)


def update_all_public_submodules(parent_dir=None, num_items=5):
    jobs = FifoQueue(PUBLIC_SUBMODULES_JOB_QUEUE).deque(num_items)

    pull_parent_repo_with_submodules(parent_dir, CENTRAL_PUBLIC_APPS_REPO, CENTRAL_REPO_OWNER, BRANCH_TO_SYNC)
    failed_tests_cnt = 0
    failed_repos = []
    for job in jobs:
        has_failures = add_or_update_submodule(job['repo_full_name'], BRANCH_TO_SYNC)

        if has_failures:
            failed_tests_cnt += 1
            failed_repos.append("%s:%s"% (job['repo_full_name'], BRANCH_TO_SYNC))

    print("Total %d: Failed: %d Failed repos: %s" % (len(jobs), failed_tests_cnt, ",".join(failed_repos)))

    exit_status = 1 if failed_tests_cnt > 0 else 0
    sys.exit(exit_status)


if __name__ == '__main__':
    update_all_private_submodules()
    update_all_public_submodules()
