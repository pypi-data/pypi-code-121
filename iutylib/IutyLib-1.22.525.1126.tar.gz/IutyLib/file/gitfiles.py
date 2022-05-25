import os
import git
from git.repo import Repo
from git.repo.fun import is_git_dir


class GitRepository(object):
    """
    git仓库管理
    """

    def __init__(self, local_path, branch='master'):
        self.local_path = local_path
        
        self.repo = Repo(self.local_path)
        

    def setRemote(self,repo_url):
        name = os.path.split(self.local_path)[-1]
        
        remote = self.repo.create_remote(name="origin", url=repo_url)
        pass
    
    def existsRemote(self,name = "origin"):
        exists = self.repo.remote(name).exists()
        return exists
    
    def init(local_path):
        
        print(git.Repo.init(path=local_path))
        repo = GitRepository(local_path)
        return repo
        pass

    def clone(local_path, repo_url, branch = 'master'):
        """
        初始化git仓库
        :param repo_url:
        :param branch:
        :return:
        """
        
        git_local_path = os.path.join(local_path, '.git')
        if not is_git_dir(git_local_path):
            Repo.clone_from(repo_url, to_path=local_path, branch=branch)
            repo = GitRepository(local_path)
            return repo
        else:
            repo = Repo(local_path)
            return repo
        pass

    def isDirty(self):
        return self.repo.is_dirty()

    def add(self,path):
        self.repo.git.add(path)
        pass

    def commit(self,msg = "regular commit"):
        if self.isDirty():
            self.repo.git.commit("-am",msg,author="iuty")
        pass

    def pull(self):
        """
        从线上拉最新代码
        :return:
        """
        self.repo.git.pull()
    
    def push(self,name="origin",branch="master"):
        if self.existsRemote():
            self.repo.git.push(name,branch)
        pass
    
    def commitAndPush(self,msg = "regular commit",name = "origin",branch = "master"):
        self.commit(msg = msg)
        self.push(name = name,branch = branch)
        pass
    
    def branches(self):
        """
        获取所有分支
        :return:
        """
        branches = self.repo.remote().refs
        return [item.remote_head for item in branches if item.remote_head not in ['HEAD', ]]

    def commits(self):
        """
        获取所有提交记录
        :return:
        """
        commit_log = self.repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                       max_count=50,
                                       date='format:%Y-%m-%d %H:%M')
        log_list = commit_log.split("\n")
        return [eval(item) for item in log_list]

    def tags(self):
        """
        获取所有tag
        :return:
        """
        return [tag.name for tag in self.repo.tags]

    def changeToBranch(self, branch):
        """
        切换分值
        :param branch:
        :return:
        """
        self.repo.git.checkout(branch)

    def changeToCommit(self, branch, commit):
        """
        切换commit
        :param branch:
        :param commit:
        :return:
        """
        self.change_to_branch(branch=branch)
        self.repo.git.reset('--hard', commit)

    def createBranch(branch):
        self.repo.create_head(branch)
        pass

    def changeToTag(self, tag):
        """
        切换tag
        :param tag:
        :return:
        """
        self.repo.git.checkout(tag)


if __name__ == '__main__':
    local_path = os.path.join(r"D:\PythonSolution","py.lib")
    #GitRepository.clone(local_path,r"https://github.com/Iuty/py.lib.git")
    #GitRepository.clone(local_path,r"https://github.com/Iuty/cnn.data.lightning.git")
    #repo = GitRepository.init(local_path)
    repo = GitRepository(local_path)
    
    #repo.add("IutyLib/file/gitfiles.py")
    print(repo.isDirty())
    #repo.remote("https://github.com/Iuty/cnn.data.lightning.git")
    #repo.commit()
    #print(repo.existsRemote())
    #repo.push()
    #repo.commit()
    #branch_list = repo.branches()
    print(branch_list)
    
    #repo.pull()