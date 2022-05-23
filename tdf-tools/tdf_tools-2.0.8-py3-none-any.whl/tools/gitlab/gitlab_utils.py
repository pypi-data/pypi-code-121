#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from tdf_tools.tools.cmd import Cmd
from tdf_tools.tools.gitlab.python_gitlab_api import GitlabAPI
from tdf_tools.tools.print import Print


class GitlabUtils(object):
    def __init__(self):
        Print.stage("gitlab管理")

    def diff(self, targetBranch="master"):
        res = Cmd.run(
            "git diff --name-only {0}..{1}".format(self._getCurBranch(), targetBranch)
        ).splitlines()
        if len(res) > 0:
            Print.str("{0} files diff".format(len(res)))

    def commit(self, message):
        Cmd.runAndPrint("git add .")
        Cmd.runAndPrint("git commit -m {0}".format(message))

    def status(self):
        res = Cmd.run("git status -s")
        if len(res.splitlines()) > 0:
            Print.str(res)
        else:
            Print.str("无文件要提交，干净的工作区")

    def unChangeValidate(self):
        res = Cmd.run("git status -s")
        if len(res.splitlines()) > 0:
            Print.str("本地仍有修改，请先提交代码")
            Print.str(res)
        else:
            exit(1)

    def clone(self, module, gitUrl):
        # 这边给clone下的项目重命名一下，避免仓库名和模块名不一致
        res = Cmd.runAndPrint("git clone {0} {1}".format(gitUrl, module))
        Print.str(res)

    def merge(self, source_branch):
        cmd = "git merge {0}".format(source_branch)
        state = Cmd.system(cmd)
        GitlabUtils.checkStateWithMsg(state, cmd)

    # 一个模块创建MR
    # def mergeRequestCreateForOneModule(self, module):
    # api = GitlabAPI()
    # printStr("模块{0}创建MR：from <{1}> into <{2}>".format(
    #     module, self.initJsonData['featureBranch'], self.initJsonData['testBranch']))
    # api.createMR(
    #     self.moduleJsonData[module]['id'], self.initJsonData['featureBranch'],
    # self.initJsonData['testBranch'])

    # 为所有模块创建MR

    def mergeRequestCreate(self, module, sourceBranch, targetBranch):
        api = GitlabAPI()
        GitlabUtils.unChangeValidate()
        Print.str(
            "模块{0}创建MR：from <{1}> into <{2}>".format(module, sourceBranch, targetBranch)
        )
        api.createMR(self.moduleJsonData[module]["id"], sourceBranch, targetBranch)
        # 命令形式提交mr
        # for module in moduleNameList:
        #     moduleDir = os.path.join(projectModuleDir, module)
        #     os.chdir(moduleDir)
        #     printTitle(module)

        #     # 确保本地代码都应提交了，以免出现代码有忘记提交的，导致提测代码不是最新的
        #     GitlabUtils.unChangeValidate()

        #     cmd = 'git push -o merge_request.create -o merge_request.source={0} -o
        #     merge_request.target={1} -o merge_request.assignee_id={2}'.format(
        #         initJsonData['featureBranch'], initJsonData['testBranch'], "819")
        #     state = os.system(cmd)
        #     GitlabUtils.checkStateWithMsg(state, cmd)
        # print()

    def _getCurBranch(self):
        return GitlabUtils._runCmd("git rev-parse --abbrev-ref HEAD").replace("\n", "")

    def fetch(self):
        cmd = "git fetch"
        state = Cmd.system(cmd)
        GitlabUtils.checkStateWithMsg(state, cmd)

    def pull(self):
        cmd = "git pull"
        state = Cmd.system(cmd)
        GitlabUtils.checkStateWithMsg(state, cmd)

    def checkout(self, featureBranch):
        cmd = "git checkout {0}".format(featureBranch)
        state = Cmd.system(cmd)
        GitlabUtils.checkStateWithMsg(state, cmd)

    def createAndCheckout(self, featureBranch, shouldPush=False):
        cmd = "git checkout -b {0}".format(featureBranch)
        state = Cmd.system(cmd)
        GitlabUtils.checkStateWithMsg(state, cmd)

        if shouldPush:
            cmd = "git push --set-upstream origin {0}".format(featureBranch)
            state = Cmd.system(cmd)
            GitlabUtils.checkStateWithMsg(state, cmd)

    # def _branchJudge(self):
    #     isSame = True
    #     curBranch = ''
    #     for module in self.moduleNameList:
    #         moduleDir = os.path.join(projectModuleDir, module)
    #         os.chdir(moduleDir)
    #         cmd = f'git branch'
    #         branchList = GitlabUtils._runCmd(cmd).splitlines()
    #         for branch in branchList:
    #             if branch.startswith('*'):
    #                 if curBranch == '':
    #                     curBranch = branch.split(' ')[1]
    #                 elif curBranch != branch.split(' ')[1]:
    #                     isSame = False
    #     return isSame

    def push(self):
        pushCmd = "git push"
        state = Cmd.system(pushCmd)
        GitlabUtils.checkStateWithMsg(state, pushCmd)

    def checkStateWithMsg(state, cmd):
        if state != 0:
            Print.error(f"execute '{cmd}' failed")

    def executeRawCommand(self, rawCmd):
        Print.str(Cmd.run(rawCmd))
