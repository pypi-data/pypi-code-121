import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

import pygit2
from pathvalidate import sanitize_filepath
from pygit2 import RemoteCallbacks

from ..Exceptions import ChangesNotCommitedError
from ..Exceptions import MergeConflict
from ..Exceptions import NoChangesToCommitError
from ..Exceptions import NoRemoteDefined
from ..Exceptions import ProjectValidationError
from ..migration import getLatestRevision
from ..tuples.git_commit_tuple import GitCommitTuple


logger = logging.getLogger(__name__)

ATTUNE_BRANCH = "attune"
ATTUNE_WORKING_BRANCH = "__working__"

_gitignore = """
# Ignore files in directories named unversioned
**/unversioned/**
**/.DS_Store
"""


def makeRef(branch: str) -> str:
    return "refs/heads/%s" % branch


class PathNameInvalidException(Exception):
    pass


class GitLibMixin:
    defaultCommitter = pygit2.Signature(
        "ServerTribe Attune", "attune@servertribe.com"
    )

    def __init__(self, projectPath: Path):
        self.projectPath = projectPath
        self.__committer = self.defaultCommitter
        self.__repo = None
        self.__indexInitialised = False
        # TODO: What if the class was loaded before a raw commit was made?
        self.__isIndexDirty = False

        try:
            self.loadGitRepo()
        except pygit2.GitError:
            self.initGitRepo()
            self.loadGitRepo()

    @property
    def _repoPath(self) -> Path:
        return self.projectPath / "git_storage"

    @property
    def __checkedOutBranchRef(self) -> str:
        return self.__repo.head.raw_name

    def loadGitRepo(self):
        self.__repo = pygit2.Repository(self._repoPath.as_posix())
        if self.__repo.is_bare:
            raise ValueError(f"{self._repoPath} points to a Git Bare Repo")

    def initGitRepo(self):
        # Create target repo
        self.__repo = pygit2.init_repository(self._repoPath.as_posix())
        self.__indexInitialised = True
        logger.info(f"Create Git repository at {self._repoPath}")
        self.__createInitialCommit()

    def __createInitialCommit(self):
        # We cannot use the public `writeMetadata` method here because the
        # branches and references to have not been set up yet
        self.__writeProjectMetadata()
        self.__writeGitIgnore()
        self.__createCommit(
            "HEAD", "Create default metadata.json", [], self.__index
        )

    def __writeProjectMetadata(self):
        # Create default metadata.json
        data = json.dumps(
            {"revision": getLatestRevision()},
            indent=4,
            sort_keys=True,
            separators=(", ", ": "),
        ).encode()
        path = "metadata.json"
        # Write the file, *without* preparing the working branch
        self.__index.add(
            pygit2.IndexEntry(
                path, self.__repo.create_blob(data), pygit2.GIT_FILEMODE_BLOB
            )
        )
        self.__isIndexDirty = True

    def __writeGitIgnore(self):
        data = _gitignore.encode()
        path = ".gitignore"
        # Write the file, with out preparing the working branch
        self.__index.add(
            pygit2.IndexEntry(
                path, self.__repo.create_blob(data), pygit2.GIT_FILEMODE_BLOB
            )
        )
        self.__isIndexDirty = True

    @property
    def metadata(self):
        tree = self.__workingTree
        data = (tree / "metadata.json").data
        metadataStr = data.decode()
        metadata = json.loads(metadataStr)
        return metadata

    def writeMetadata(self, metadata):
        oid = self.__repo.create_blob(
            json.dumps(
                metadata,
                indent=4,
                sort_keys=True,
                separators=(", ", ": "),
            ).encode()
        )
        self.__prepareWorkingBranch()
        self.__index.add(
            pygit2.IndexEntry("metadata.json", oid, pygit2.GIT_FILEMODE_BLOB)
        )
        self.__isIndexDirty = True

    @classmethod
    def cloneGitRepo(
        cls,
        projectPath: Path,
        url: str,
        username: str = None,
        password: str = None,
    ):
        if username is None and password is None:
            cred = None
        elif password is None:
            cred = pygit2.Username(username)
        else:
            cred = pygit2.UserPass(username, password)

        pygit2.clone_repository(
            url,
            projectPath.as_posix(),
            bare=False,
            callbacks=RemoteCallbacks(credentials=cred),
        )

    def _writeFile(self, path: str, data: bytes, mode=pygit2.GIT_FILEMODE_BLOB):
        if path != sanitize_filepath(path):
            raise PathNameInvalidException(
                "Path %s is not valid, please " "sanitize it first" % path
            )

        oid = self.__repo.create_blob(data)
        self.__prepareWorkingBranch()
        self.__index.add(pygit2.IndexEntry(path, oid, mode))
        self.__isIndexDirty = True

    def _moveDirectory(self, fromPath: Path, toPath: Path):
        if fromPath == toPath:
            raise Exception("The source and destination paths are the same")

        fromTree = self._getTree(fromPath)

        self.__prepareWorkingBranch()

        def recurse(fromParentPath, toParentPath, tree):
            for item in tree:
                fromItemPath = fromParentPath / item.name
                toItemPath = toParentPath / item.name
                # A child tree is a directory
                if isinstance(item, pygit2.Tree):
                    recurse(fromItemPath, toItemPath, item)
                    continue

                # Otherwise it's a blob, move it
                assert isinstance(
                    item, pygit2.Object
                ), "item is not a pygit2.Object"
                self.__index.add(
                    pygit2.IndexEntry(
                        toItemPath.as_posix(), item.oid, item.filemode
                    )
                )
                self.__index.remove(fromItemPath.as_posix())

        recurse(fromPath, toPath, fromTree)
        self.__isIndexDirty = True

    def _moveFile(self, fromPath: Path, toPath: Path):
        if fromPath == toPath:
            raise Exception("The source and destination paths are the same")

        fromTree = self._getTree(fromPath.parent)

        self.__prepareWorkingBranch()

        blob = fromTree / fromPath.name
        assert isinstance(blob, pygit2.Object), "blob is not a pygit2.Object"

        self.__index.add(
            pygit2.IndexEntry(toPath.as_posix(), blob.oid, blob.filemode)
        )
        self.__index.remove(fromPath.as_posix())
        self.__isIndexDirty = True

    def _deleteDirectory(self, path: Path):
        try:
            startTree = self._getTree(path)
        except FileNotFoundError:
            # It's already done.
            return

        self.__prepareWorkingBranch()

        def recurse(parentPath, tree):
            for item in tree:
                itemPath = parentPath / item.name
                # A child tree is a directory
                if isinstance(item, pygit2.Tree):
                    recurse(itemPath, item)
                    continue

                # Otherwise, it's a blob, move it
                assert isinstance(
                    item, pygit2.Object
                ), "item is not a pygit2.Object"
                self.__index.remove(itemPath.as_posix())

        recurse(path, startTree)
        self.__isIndexDirty = True

    def _deleteFile(self, path: Path):
        tree = self._getTree(path.parent)
        self.__prepareWorkingBranch()

        blob = tree / path.name
        assert isinstance(blob, pygit2.Object), "blob is not a pygit2.Object"

        self.__index.remove(path.as_posix())
        self.__isIndexDirty = True

    def _readFile(self, path: Path) -> bytes:
        tree = self._getTree(path.parent)

        if path.name in tree:
            fileObject = tree / path.name
            return fileObject.data
        else:
            raise FileNotFoundError()

    @property
    def isDirty(self) -> bool:
        return self.__isIndexDirty

    def commit(self, msg: str):
        descendentCommit = next(
            self.__repo.walk(self.__workingBranch.target), None
        )
        if descendentCommit is not None:
            descendents = [descendentCommit.id]
        else:
            descendents = []
        self.__createCommit(
            self.__workingBranch.name, msg, descendents, self.__index
        )

    def __createCommit(
        self, targetName: str, msg: str, descendents: list[str], index
    ) -> str:

        tree = index.write_tree()
        author = self.__committer if self.__committer else self.defaultCommitter

        self.__isIndexDirty = False

        return self.__repo.create_commit(
            targetName,
            author,
            author,
            msg,
            tree,
            descendents,
        )

    @property
    def __index(self) -> pygit2.Index:
        if self.__indexInitialised:
            return self.__repo.index

        # Else, initialise the index
        if ATTUNE_WORKING_BRANCH in list(self.__repo.branches):
            self.__repo.index.read_tree(
                tree=self.__repo.revparse_single(
                    makeRef(ATTUNE_WORKING_BRANCH)
                ).tree
            )
        else:
            self.__repo.index.read_tree(
                tree=self.__repo.revparse_single(
                    self.__checkedOutBranchRef
                ).tree
            )
        self.__indexInitialised = True

        return self.__repo.index

    def __prepareWorkingBranch(self):
        if ATTUNE_WORKING_BRANCH not in list(self.__repo.branches):
            commit = next(
                self.__repo.walk(self.__checkedOutBranch.target), None
            )
            self.__repo.create_branch(ATTUNE_WORKING_BRANCH, commit)
            self.__indexInitialised = False

    @property
    def __workingBranch(self) -> pygit2.Branch:
        """Working Branch

        Accessing the working branch causes creation of __working__ branch if
        it does not already exist.

        """
        if ATTUNE_WORKING_BRANCH in list(self.__repo.branches):
            return self.__repo.references[makeRef(ATTUNE_WORKING_BRANCH)]
        return self.__checkedOutBranch

    @property
    def __checkedOutBranch(self) -> pygit2.Branch:
        return self.__repo.references[self.__checkedOutBranchRef]

    @property
    def __workingTree(self):
        branch = self.__checkedOutBranchRef
        if ATTUNE_WORKING_BRANCH in list(self.__repo.branches):
            branch = makeRef(ATTUNE_WORKING_BRANCH)

        return self.__repo.revparse_single(branch).tree

    def _getTree(self, path: Path) -> pygit2.Tree:
        # We will read objects as they are at the working branch
        tree = self.__workingTree
        climbedPath = ""
        for pathComponent in path.as_posix().split("/"):
            climbedPath += f"/{pathComponent}"
            if pathComponent in tree:
                tree = tree / pathComponent
            else:
                raise FileNotFoundError(f"Path {pathComponent} does not exist")
        return tree

    def setCommitterSignature(self, name: str, email: str) -> None:
        self.__committer = pygit2.Signature(name, email)

    def allLocalBranches(self) -> List[str]:
        return [
            str(branch)
            for branch in self.__repo.branches.local
            if not str(branch) == ATTUNE_WORKING_BRANCH
        ]

    def allRemoteBranches(self) -> List[str]:
        return [str(branch) for branch in self.__repo.branches.remote]

    def allBranches(self) -> List[str]:
        return [str(branch) for branch in self.__repo.branches]

    def allRemotes(self) -> List[tuple[str, str]]:
        return [(remote.name, remote.url) for remote in self.__repo.remotes]

    def checkoutBranch(self, branchName: str) -> None:
        if branchName == ATTUNE_WORKING_BRANCH:
            raise ValueError(
                "Cannot checkout the reserved Attune branch %s"
                % ATTUNE_WORKING_BRANCH
            )

        if self.isDirty:
            raise ChangesNotCommitedError()

        # Check if there are changes waiting to be squashed and merged
        if ATTUNE_WORKING_BRANCH in list(self.__repo.branches):
            workingBranch = self.__workingBranch
            checkedOutBranch = self.__checkedOutBranch
            if workingBranch.target != checkedOutBranch.target:
                raise ChangesNotCommitedError()

            # Delete the working branch
            workingBranch.delete()

        if branchName in self.allLocalBranches():
            # Checkout existing branch
            self.__repo.checkout(makeRef(branchName))
        else:
            # Create and checkout new branch
            checkedBranch = self.__checkedOutBranch
            commit = next(self.__repo.walk(checkedBranch.target), None)
            self.__repo.create_branch(branchName, commit)
            self.__repo.checkout(makeRef(branchName))

    def squashAndMergeWorking(self, mergeCommitMessage: str) -> None:
        working = self.__workingBranch
        checkedOut = self.__checkedOutBranch
        checkedOutBranchRef = checkedOut.name

        if self.isDirty:
            raise ChangesNotCommitedError()

        if working.target == checkedOut.target:
            raise NoChangesToCommitError("There are no changes to commit")

        checkedLastCommit = next(self.__repo.walk(checkedOut.target), None)

        # Walk the commits till we find the previous common point
        commitsOnWorking = 0
        for c in self.__repo.walk(working.target):
            if c.id == checkedLastCommit.id:
                break
            commitsOnWorking += 1

        self.__repo.checkout(makeRef(ATTUNE_WORKING_BRANCH))
        # Create squash commit
        # Do a soft reset to the beginning of working branch
        self.__repo.reset(checkedLastCommit.id, pygit2.GIT_RESET_SOFT)
        # Create a commit. This will squash the previous `commitsOnChecked`
        # into one

        squashCommitOid = self.__createCommit(
            makeRef(ATTUNE_WORKING_BRANCH),
            mergeCommitMessage,
            [checkedLastCommit.id],
            self.__index,
        )

        """
        Because we write files directly to the Git object database and
        never to the working directory, running a git status at this point
        will show that the files were deleted because they are not present
        in the working directory. This does not allow us to merge later as
        the repo is in a dirty state. Doing a hard reset, resets the index
        and restores the state of the working directory (in our case,
        it recreates the files that it things were deleted). This is done
        in C code and should be faster than writing files to the working
        directory in Python and then `add commit`ing them.
        """
        self.__repo.reset(squashCommitOid, pygit2.GIT_RESET_HARD)

        # Reload the reference to the working branch
        working = self.__workingBranch

        self.__repo.checkout(checkedOutBranchRef)
        checkedOut.set_target(working.target)
        self.__repo.reset(checkedOut.target, pygit2.GIT_RESET_HARD)

        # Delete the working branch. It will be recreated if there is a new
        # commit
        working.delete()

    def getCommits(self) -> list[GitCommitTuple]:
        for commit in self.__repo.walk(self.__checkedOutBranch.target):
            gitCommit = GitCommitTuple()
            gitCommit.authorName = commit.author.name
            gitCommit.authorEmail = commit.author.email
            gitCommit.message = commit.message
            gitCommit.timestamp = datetime.fromtimestamp(
                commit.commit_time
            ).strftime("%Y-%m-%d %H:%M:%S")
            gitCommit.hash = commit.short_id

            yield gitCommit

    def addRemote(self, remote: str, url: str) -> None:
        if remote in [r[0] for r in self.allRemotes()]:
            self.__repo.remotes.set_url(remote, url)
        else:
            self.__repo.remotes.create(remote, url)

    def deleteRemote(self, remote: str) -> None:
        if remote in [r[0] for r in self.allRemotes()]:
            self.__repo.remotes.delete(remote)
        else:
            raise ValueError(f"Remote {remote} does not exist")

    def pushToRemote(
        self, remote: str, username: str, password: str = None
    ) -> None:
        if remote not in [r[0] for r in self.allRemotes()]:
            raise NoRemoteDefined(f"Remote {remote} not set for project")

        if password is None:
            cred = pygit2.Username(username)
        else:
            cred = pygit2.UserPass(username, password)

        remote = self.__repo.remotes[remote]

        remote.push(
            [self.__checkedOutBranch.name],
            callbacks=pygit2.RemoteCallbacks(credentials=cred),
        )

    def pullFromRemote(
        self, remoteName: str, username: str, password: str = None
    ) -> None:
        if remoteName not in [r[0] for r in self.allRemotes()]:
            raise NoRemoteDefined(f"Remote {remoteName} not set for project")

        if password is None:
            cred = pygit2.Username(username)
        else:
            cred = pygit2.UserPass(username, password)

        remote = self.__repo.remotes[remoteName]
        remote.fetch(callbacks=RemoteCallbacks(credentials=cred))

        checkedOutBranch = self.__checkedOutBranch
        remoteBranchName = f"{remoteName}/{checkedOutBranch.shorthand}"
        # Try to merge remote equivalent into current checked out
        self.mergeBranches(remoteBranchName)

    def mergeBranches(self, sourceBranch: str) -> None:
        if sourceBranch not in self.allBranches():
            raise ValueError(f"Branch {sourceBranch} does not exist")

        working = self.__workingBranch
        checked = self.__checkedOutBranch

        logger.debug(f"Merging branches {sourceBranch} to {checked.name}")

        if working.target != checked.target:
            raise RuntimeError(
                f"Squash the commits for {self.__checkedOutBranch} first"
            )

        sourceBranchId = self.__repo.branches[sourceBranch].target
        checkedBranchId = checked.target

        mergeAnalysis, _ = self.__repo.merge_analysis(sourceBranchId)
        if mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            logger.debug("Both branches are up-to-date. Nothing to merge")
            return

        if mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            logger.debug("Branch can be fast-forwarded")
            # Fast-forward checked branch to source branch
            checked.set_target(sourceBranchId)

        elif mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            """
            IMPORTANT!!
            The `merge` method on the `Repository` object and the merging
            procedure below is dependent on the state of the index and the
            working tree. We cannot use self.__index or any other methods
            that mutate the index or working tree here. self.__index
            reloads the index if there is no working branch which causes
            the merged index to be lost and the merged changes won't be
            committed.
            """

            logger.debug("Merging branches")
            self.__repo.merge(sourceBranchId)
            # Check for merge conflicts and reverse merge if there are any
            if self.__repo.index.conflicts:
                self.__repo.reset(checkedBranchId, pygit2.GIT_RESET_HARD)
                raise MergeConflict("Cannot complete merge due to conflicts")

            logger.debug("Branches merged. Creating merge commit")
            self.__createCommit(
                "HEAD",
                "Merged pulled changes",
                [self.__repo.head.target, sourceBranchId],
                self.__repo.index,
            )

            # This is so Git CLI does not show status as MERGING
            self.__repo.state_cleanup()

        else:
            raise RuntimeError("Unknown Git merge analysis result")

        # Check for project validation errors after merge
        try:
            # This is the load method from GitObjectStorageContext
            self.load()
        except ProjectValidationError:
            logger.debug(
                "Merged project failed validation. Resetting to "
                "previous state"
            )
            self.__repo.reset(checkedBranchId, pygit2.GIT_RESET_HARD)
            logger.debug("Project reset")
            raise Exception("Merging failed due to project validation errors")

        logger.debug("No validation errors after merge")
