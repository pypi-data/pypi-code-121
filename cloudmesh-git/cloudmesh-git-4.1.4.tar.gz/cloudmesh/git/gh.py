from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.console import Console
import json
import os

class Gh:

    def __init__(self):
        self.cache = path_expand("~/.cloudmesh/issuelist.json")
        self.issue_list = None

    def cache_delete(self):
        if self.cache_esists():
            os.remove(self.cache)

    def cache_esists(self):
        return os.path.isfile(self.cache)

    def cache_load(self):
        content = readfile(self.cache)
        # do something with the content and load it into _issue_list
        self.issue_list = eval(content)

    def cache_save(self):
        # safe json as string  with json.dumps
        content = json.dumps(self.issue_list, indent=2)
        writefile(filename=self.cache, content=content)

    def repos_in_dir(self, directory="."):
        _directory = path_expand(directory)
        repos = [name for name in os.listdir(_directory) if os.path.isdir(name) and os.path.isdir(f"{name}/.git")]
        return repos

    def run(self, command, path="."):
        directory = path_expand(path)
        command = f'cd {directory} && {command}'
        try:
            r = Shell.run(command)
        except Exception as e:
            print(e)

    def issues_find(self, assignee, path=["."]):
        _issues = []
        for p in path:
            for a in assignee:
                r = self.issues_from_repos(assignee=a, path=[p])
                _issues.append(r)
        return _issues

    def issues_from_repos(self, assignee=None, path=["."]):
        _issues = []
        for p in path:
            r = self.issues(assignee=assignee, path=p)
            _issues.append(r)
        self.issue_list = _issues
        return _issues

    def issues(self, assignee=None, path="."):
        r = None
        directory = path_expand(path)
        if assignee is None:
            parameter = ""
        else:
            parameter = f'--assignee "{assignee}"'
        command = f'cd {directory} && gh issue list {parameter} --json=title,assignees,url,labels'
        print (command)

        try:
            r = Shell.run(command)
            r = json.loads(r)
        except Exception as e:
            print(e)
        return r

    def issues_to_table(self, entries):

        try:
            entry = entries[0]
            repo = os.path.dirname(entry['url'])
            repo_url = os.path.dirname(repo)
            repo_name = repo_url.replace("https://github.com/", "")
            name = repo_name
        except:
            name = "???"

        result = [
            f'<br><b>{name}</b><br><br>',
            '<table frame="border" rules="all" border-spacing="30px";>']
        line = f'<tr><th> repo </th><th> url </th><th> title </th><th> assignees</th><th> labels</th></tr>'
        result.append(line)


        if entries:
            for entry in entries:
                url = entry['url']
                title = entry['title']
                assignees = entry['assignees']
                labels = entry['labels']
                n = os.path.basename(url)
                repo = os.path.dirname(url)
                repo_url = os.path.dirname(repo)
                repo_name = repo_url.replace("https://github.com/", "")
                entry['repo'] = f'<a href="{repo_url}"> {repo_name} </a>'
                entry['url'] = f'<a href="{url}"> {n} </a>'
                entry['title'] = f'<a href="{url}"> {title} </a>'
                entry['assignees'] = ",".join(
                    [f'<a href="https://github.com/{assignee["login"]}"> {assignee["name"] or assignee["login"]} </a>'
                     for assignee in assignees])
                if len(labels) > 0:
                    entry['labels'] = ",".join([label['name'].replace("PRIORITY ", "") for label in labels])
                else:
                    entry['labels'] = ""
                line = f'<tr>'\
                       f'<td> {entry["repo"]} </td>'\
                       f'<td> {entry["url"]} </td>'\
                       f'<td> {entry["assignees"]}</td>' \
                       f'<td> {entry["title"]} </td>' \
                       f'<td>{entry["labels"]}<td>'\
                       '</tr>'
                result.append(line)
            result.append("</table>")
            result = "\n".join(result)
        else:
            result = None
        return result