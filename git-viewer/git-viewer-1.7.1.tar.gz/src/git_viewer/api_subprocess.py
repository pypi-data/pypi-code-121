#!/usr/bin/env python3

import os
import subprocess


gitdir = None
worktree = None


CalledProcessError = subprocess.CalledProcessError

class CommandError(Exception):

	def __init__(self, cmd, err):
		if isinstance(err, str):
			exception = None
			returncode = None
			err = err
		elif isinstance(err, CalledProcessError):
			exception = err
			returncode = err.returncode
			err = err.stderr.decode('utf-8')
		else:
			exception = err
			returncode = None
			err = str(err)

		super().__init__(err)
		self.cmd = cmd
		self.err = err
		self.returncode = returncode
		self.exception = exception

	def executable_was_found(self):
		return not isinstance(self.exception, FileNotFoundError)


class Runner:

	encoding = "utf-8"
	decode_errors = "replace"

	RETURNCODE_PROGRAM_NOT_FOUND = "program-not-found"

	def run(self, cmd, stdin=None, check=True):
		"""
		Executes cmd without a shell and returns it's return code.
		Does not raise exceptions if check is False.
		Returns RETURNCODE_PROGRAM_NOT_FOUND if check is False and the program is not found.
		Raises CommandError if check is True and the program is not found or fails.

		cmd: list or tuple representing a command with it's arguments
		"""
		cmd = self._amend_command(cmd)

		if stdin:
			stdin = stdin.encode(self.encoding)

		try:
			p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=check, input=stdin)
			return p.returncode
		except CalledProcessError as e:
			raise CommandError(cmd, e)
		except FileNotFoundError as e:
			if check:
				raise CommandError(cmd, e)
			else:
				return self.RETURNCODE_PROGRAM_NOT_FOUND

	def run_and_get_output(self, cmd):
		"""
		Executes cmd without a shell and returns stdout as unicode/str.
		Raises CommandError if program is not found or fails.

		cmd: list or tuple representing a command with it's arguments
		"""
		cmd = self._amend_command(cmd)

		try:
			p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
		except (CalledProcessError, FileNotFoundError) as e:
			raise CommandError(cmd, e)
		out = p.stdout
		out = out.decode(self.encoding, errors=self.decode_errors)
		return out

	def run_interactive(self, cmd, shell=False):
		"""
		Executes cmd without rediricting it's streams.
		Exit the main loop before calling this.
		Returns the return code or RETURNCODE_PROGRAM_NOT_FOUND if the program is not installed.
		Does not raise exceptions.

		cmd: list or tuple representing a command with it's arguments
		"""
		cmd = self._amend_command(cmd)

		try:
			p = subprocess.run(cmd, shell=shell, check=False)
			return p.returncode
		except FileNotFoundError:
			return self.RETURNCODE_PROGRAM_NOT_FOUND


	def _amend_command(self, cmd):
		if isinstance(cmd, str):
			return cmd

		cmd = list(cmd)
		if os.path.split(cmd[0])[1] == "git":
			if worktree:
				cmd.insert(1, '--work-tree')
				cmd.insert(2, worktree)
			if gitdir:
				cmd.insert(1, '--git-dir')
				cmd.insert(2, gitdir)
		return cmd


if __name__ == '__main__':
	r = Runner()
	rc = r.run(["git", "status"])
	if rc == Runner.RETURNCODE_PROGRAM_NOT_FOUND:
		print("git is not installed")
	elif rc != 0:
		print("current working directory is not in a git repository")
	else:
		commit = r.run_and_get_output(["git", "log", "-1", "--pretty=format:%H"])
		print("the last commit was %s" % commit)
