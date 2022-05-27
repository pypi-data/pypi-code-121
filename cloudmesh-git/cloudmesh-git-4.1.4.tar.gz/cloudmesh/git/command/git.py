import glob
import json
import os
import re
import subprocess
from pprint import pprint

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import str_bool
from cloudmesh.common.util import writefile
from cloudmesh.git.api.manager import Manager
from cloudmesh.git.copy import copy_dir
from cloudmesh.git.gh import Gh
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


class GitCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_git(self, args, arguments):
        """
        ::

          Usage:
                git create issue --repo=REPO --file=FILE [--title=TITLE] [--org=ORG]
                git create repository FIRSTNAME LASTNAME GITHUBID [--org=ORG]
                git create repository --file=FILE [--org=ORG]
                git list all [--exclude=ORG]
                git list --org=ORG [MATCH]
                git copy FROM TO DIRS... [--move=TMP]
                git set ssh [DIRS]
                git --refresh
                git clone all [--force=no]
                git pull all
                git issues [--repo=REPO] [--assignee=ASSIGNEE] [--format=HTML] [--out=a.html] [--refresh]

          This command does some useful things.

          Arguments:
              FILE   a file name
              ORG    [default: cloudmesh-community]
              MATCH  is a string that must occur in the repo name or description
              --file=FILE   specify the file
              --repo=REPO   a parameterized list of repo links. If cloudmesh- is the prefix it will be
                            automatically replaced by the repo url. REPO is a parameterized list with
                            comma separated so that multiple repos can be used.
                            If REPO is a filename, each line specifies a repo. the cloudmesh prefix
                            replacement is applied on each line
                            If repo is . or the parameter is ommitted, all directories in the current
                            directory are used to list their issues
             --assignee=ASSIGNEE  a list of assignees so only issues for these users are displayed
                                  if it is ommitted all issues for assignees are displayed.
             --refresh  only downnload the GitHub issue list if --refersh is uses, otherwise it uses a local cache in
                        ~/.cloudmesh/issuelist.json

          Options:
              --force=no    pull the repository if it already exists in current working directory [default: no]

          Description:

                The organization is set by default to
                cloudmesh-community

                git --refresh
                    finds all organizations and repositories the current user belongs to
                    redirects automatically to ~/cloudmesh/git/repo-list.txt

                git clone all [--force=no]
                    uses all organizations and repositories of the user and
                    clones them into the current directory, while making each
                    organization in its own subdirectory
                    uses automatically ~/cloudmesh/git/repo-list.txt
                    which can be created with cms git list all.
                    if force is yes then it pulls preexisting directories

                git set ssh
                    switches the repository to use ssh

                git list --org=ORG
                    lists the repos of the organization

                git list all [--exclude=ORG]
                    gets info of all repos of the current logged in user to github
                    put the result in ~/.cloudmesh/gitcache.txt
                    to exclude an organization, add it to the end of exclude
                    parameter

                git create issue --repo=REPO FILE
                   Create an issue in the given repos.
                   Note that the repos is a string defined as
                   cloudmesh.Parameter, E.g. fa19-516-[100-103,105]
                   effects the repos ending with 100, 101, 102,
                   103, and 105

                   The bundle is defined in cloudmesh-installer

                git create repo NAME FIRSTNAME LASTNAME GITHUBID
                    creates the repo

                git create repo --file=repos.csv
                    creates repos from a file in csv format
                    the format in th csv file is

                    reponame,lastname,firstname,githubid

                git copy FROM TO
                    copies a directory from one repo to the other

                git pull all
                    git pulls all directories and subdirectories of
                    current working directory

                git issuelist
                    creates html file of all issues assigned to logged-in
                    user. assumes that the user is standing in cm
                    directory

          Examples:

               git copy FROM TO

                    git copy cloudmesh/cloudmesh-cloud cloudmesh/cloudmesh-db admin

                    creates a script move.sh that copies the directory admin
                    with history to the cloudmesh-db repo into a folder move

                    from there you can use git mv to place the content where you
                    like. The reason we put it in move is that there may be another
                    dir already in it with tha name.

               git list Park
                  Lists all repos with the name Park in it or its description

               git list fa19-523
                    Lists all repos with the string  fa19-523 in its name


        """
        # arguments.FILE = arguments['--file'] or None

        map_parameters(arguments,
                       'fetch',
                       'move',
                       'repo',
                       'file',
                       'title',
                       'assignee'
                       )
        move = arguments.move or "move"

        VERBOSE(arguments)

        # if arguments.FILE:
        #    print("option a")
        #    m.list(path_expand(arguments.FILE))
        #

        if arguments.list and arguments.all:

            command = "gh api  /user/memberships/orgs"
            r = Shell.run(command)
            # print(r)

            result = json.loads(r)

            result2 = json.dumps(result, indent=2)
            # pprint(result2)
            exclude = Parameter.expand(arguments["--exclude"]) or []
            organizations = []

            for entry in result:
                url = entry["organization_url"]
                name = os.path.basename(url)
                if name not in exclude:
                    organizations.append(name)

            # pprint(organizations)
            repos = []
            for org in organizations:
                command = f"gh repo list {org} -L 1000"
                r = Shell.run(command)
                count = len(r.splitlines())
                Console.msg(f"List repos for {org}. Found {count}")
                lines = [x.split()[0] for x in r.splitlines()]
                repos = repos + lines

            pprint(repos)

            filename = path_expand("~/.cloudmesh/git_cache.txt")
            writefile(filename, "\n".join(repos))
            Console.ok(f'\nWritten list of repos to {filename}')

        # elif arguments["list"]:

        #    '''m = Manager()

        #    m.list(arguments.MATCH)'''

        elif arguments.list and arguments["--org"]:
            command = f'gh api  /orgs/{arguments["--org"]}/repos'
            r = Shell.run(command)
            # print(r)

            result = json.loads(r)

            result2 = json.dumps(result, indent=2)
            # pprint(result2)

            repos = []

            result2 = json.dumps(result, indent=2)
            pprint(result2)

            for entry in result:
                name = entry["full_name"]
                repos.append(name)

            # pprint(organizations)

            pprint(repos)
            filename = path_expand("~/.cloudmesh/git_cache.txt")
            writefile(filename, "\n".join(repos))
            Console.ok(f'\nWritten list of repos to {filename}')

        elif arguments.issues:

            github = Gh()

            # currently only allowing one user
            #if arguments.assignee is not None:
            #    assignee = Parameter.expand(arguments.assignee)[0]
            # TODO: assignee = Parameter.expand(arguments.assignee)
            assignee = arguments.assignee
            if arguments.repo in ['.', "cwd", None]:
                repos = github.repos_in_dir()
            elif arguments.repo in ["pi"]:
                repos = ["cloudmesh-pi-burn", "cloudmesh-pi-cluster", "cloudmesh-git"]

            refresh = arguments["--refresh"] or not github.cache_esists()
            if refresh:
                github.cache_delete()
                github.issues_from_repos(path=repos, assignee=assignee)
                # TODO: github.issues_find(path=repos, assignee=assignee)
                github.cache_save()
            else:
                github.cache_load()

            tables = ""
            total = 0
            for d in github.issue_list:
                print(len(d))
                total = total + len(d)
                table = github.issues_to_table(d)
                if not table:
                    continue
                tables = tables + table + "\n"
            tables = f"Total Issues: {total}<br>" + tables
            html = path_expand("~/.cloudmesh/issuelist.html")
            print("Total Issues", total)
            writefile(html, tables)
            Shell.browser(html)

        elif arguments.clone and arguments["all"]:
            filename = path_expand("~/.cloudmesh/git_cache.txt")
            repos = readfile(filename).splitlines()
            failed_repos = []
            forcing_pull = str_bool(arguments["--force"])
            for repo in repos:
                url = f"git@github.com:{repo}.git"
                org = os.path.dirname(repo)
                name = os.path.basename(repo)
                command = f"mkdir -p {org}; cd {org}; git clone {url}"
                banner(command)
                try:
                    r = Shell.run(command)
                    Console.ok(f"Successfully cloned {repo}.")
                except subprocess.CalledProcessError as e:
                    if forcing_pull:
                        if "already exists and is not an empty directory" in str(e.output):
                            pull_command = f"cd {org}; cd {name}; git pull"
                            banner(pull_command)
                            try:
                                r2 = Shell.run(pull_command)
                                Console.ok(f"Pulled {repo} since it already exists.")
                            except subprocess.CalledProcessError as e2:
                                Console.error(f"Failed to pull {repo}. Continuing...")
                                failed_repos.append(repo)
                                continue
                    else:
                        if "already exists and is not an empty directory" in str(e.output):
                            Console.ok(f"Skipping {repo} because it already exists.")
                        else:
                            Console.error(f"Failed to clone {repo}. Continuing...")
                            failed_repos.append(repo)
                    continue
            if failed_repos:
                Console.error(f"These repos failed to clone:\n")
                for failed_repo in failed_repos:
                    print(f'{failed_repo}\n')

        elif arguments.create and arguments.repo is not None:
            """
            git create issue --repo=REPO --title=TITLE --file=FILE [--org=ORG]
            """
            m = Manager()

            file = arguments.file
            title = arguments.title
            repo = arguments.repo
            repos = Parameter.expand(repo)
            m.issue(repos=repos, title=title, file=file)

        elif arguments.repository and arguments.file and not arguments.issue:

            m = Manager()
            filename = arguments.file
            m.create_repos(filename=filename)

        elif arguments.ssh and arguments.set:

            dirs = arguments["DIRS"] or "."
            org = "get the org from the current dir in .git"
            repo = "get the repo from the current dir in .git"

            for d in dirs:
                if d == ".":
                    location = ""
                else:
                    location = "cd {d}; "
            os.system(f"{location} git remote set-url origin git@github.com:{org}/{repo}.git")

        elif arguments.pull and arguments.all:
            for path in glob.glob(f'./**/', recursive=True):
                command = f"git -C {path} pull"
                banner(command)
                os.system(command)

        elif arguments.copy:
            dirs = arguments.DIRS
            original = arguments.FROM
            destination = arguments.TO
            move = arguments.move

            copy_dir(original=original,
                     destination=destination,
                     directories=dirs,
                     move=move)

        return ""
