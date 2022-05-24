import os
import re

from polidoro_argument import Command

from polidoro_cli import CLI
from polidoro_cli.cli.cli import import_dependency

try:
    import github
except ModuleNotFoundError:
    class GitHubMock:
        class Workflow:
            class Workflow:
                pass

        class WorkflowRun:
            class WorkflowRun:
                pass

        class Repository:
            class Repository:
                pass

        class Github:
            pass


    github = GitHubMock


class Base:
    def __init__(self, data):
        if isinstance(data, dict):
            self.data = data
        else:
            self.__dict__.update(data.__dict__)

    def final_status(self):
        return self.conclusion or self.status

    def __getattr__(self, item):
        if 'data' in self.__dict__:
            if item.startswith('get_'):
                def get_():
                    _item = item.replace('get_', '')
                    class_name = _item[:-1] if _item[-1] == 's' else _item
                    clazz = Base._get_subclass(class_name)
                    resp = self.data[_item]
                    if isinstance(resp, list):
                        return [clazz(r) for r in resp]
                    return clazz(resp)

                return get_
            return self.data[item]
        raise AttributeError(self.__name__, item)

    @staticmethod
    def _get_subclass(class_name):
        for cls in Base.__subclasses__():
            if cls.__name__.lower() == class_name.lower():
                return cls


class Step(Base):
    pass


class Job(Base):
    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self._steps = []
        # noinspection PyStatementEffect
        self.steps

    @property
    def steps(self):
        if not self._steps and self.conclusion != 'success':
            self._steps = self.get_steps()
        return self._steps


# noinspection PyUnresolvedReferences
class Run(Base, github.WorkflowRun.WorkflowRun):
    def __init__(self, *args, name=None, **kwargs):
        super(Run, self).__init__(*args, **kwargs)
        self.name = name
        self._jobs = []
        # noinspection PyStatementEffect
        self.jobs

    @property
    def jobs(self):
        if not self._jobs and self.conclusion != 'success':
            self._jobs = self.get_jobs()
        return self._jobs

    def get_jobs(self):
        _, data = self.repository._requester.requestJsonAndCheck("GET", self.jobs_url)
        return [Job(j) for j in data['jobs']]

    def update(self):
        super(Run, self).update()
        self._jobs = []
        # noinspection PyStatementEffect
        [j.steps for j in self.jobs]

    def __str__(self):
        lines = [f'{self.name} -> {self.final_status()}']
        if self.conclusion != 'success':
            for job in self.jobs:
                lines.append(f'- {job.name} -> {job.final_status()}')
                if job.conclusion != 'success':
                    for step in job.steps:
                        lines.append(f'-- {step.name} -> {step.final_status()} '
                                     f'{job.html_url if step.final_status() == "failure" else ""}')
        return '\n'.join(lines)


# noinspection PyUnresolvedReferences
class Workflow(Base, github.Workflow.Workflow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_run = None

    def get_last_run(self):
        if self._last_run is None:
            self._last_run = Run(next(iter(self.get_runs())), name=self.name)
        return self._last_run


# noinspection PyUnresolvedReferences
class Repository(Base, github.Repository.Repository):
    def get_workflows(self):
        return [Workflow(wf) for wf in super(Repository, self).get_workflows()]


class GitHubAPI(github.Github):
    def get_repo(self, *args, **kwargs):
        return Repository(super(GitHubAPI, self).get_repo(*args, **kwargs))


def colorfy(workflow_str):
    lines = []
    polidoro_terminal = import_dependency('polidoro_terminal')
    for line in workflow_str.split('\n'):
        color = ''
        if 'success' in line:
            color = polidoro_terminal.Color.GREEN
        elif 'queued' in line:
            color = polidoro_terminal.Color.YELLOW
        elif 'skipped' in line:
            color = polidoro_terminal.Format.DIM
        elif 'failure' in line:
            color = polidoro_terminal.Color.RED
        elif 'in_progress' in line:
            color = polidoro_terminal.Color.CYAN
        lines.append(str(color) + line + str(polidoro_terminal.Format.NORMAL))
    return '\n'.join(lines)


class GitHub(CLI):
    @staticmethod
    @Command(aliases=['m'], help='Monitor the last branch pipeline')
    def monitor():
        import_dependency('github', 'PyGithub')
        polidoro_terminal = import_dependency('polidoro_terminal')
        polidoro_terminal.cursor.hide()
        try:
            gh = GitHubAPI(os.environ['GITHUB_TOKEN'])
            out, _ = CLI.execute('git config --get remote.origin.url', capture_output=True, show_cmd=False)
            repo_name = re.search(r'github.com[:/](?P<repo>.*)\.git', out).groupdict()['repo']
            repo = gh.get_repo(repo_name)
            workflows = repo.get_workflows()
            return_lines = 0
            finish = False
            workflow_str = ''
            while not finish:
                finish = True
                workflow_list = []
                for workflow in workflows:
                    run = workflow.get_last_run()
                    if not run.conclusion:
                        run.update()
                        finish = False
                    workflow_list.append(str(run))
                new_workflow_str = '\n'.join(workflow_list)
                if new_workflow_str != workflow_str:
                    workflow_str = new_workflow_str
                    polidoro_terminal.erase_lines(return_lines)
                    print(colorfy(workflow_str))
                    return_lines = workflow_str.count('\n') + 1
        finally:
            polidoro_terminal.cursor.show()
