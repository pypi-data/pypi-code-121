#!/usr/bin/env python3

import shlex
import argparse
import inspect
import io
import gettext
_ = gettext.gettext

from . import utils
from .api_subprocess import Runner


class ParseException(Exception):
	pass

class ArgumentParser(argparse.ArgumentParser):

	def error(self, message):
		raise ParseException(message)

class ErrorInCommand(Exception):
	pass


class CommandContainer:

	SEP = " "

	def __init__(self, app):
		self.commands = {}
		self.app = app

	def load_commands_from_module(self, module):
		self.load_commands_from_list(vars(module).values())

	def load_commands_from_list(self, classes):
		for var in classes:
			try:
				if not issubclass(var, Command):
					continue
			except TypeError:
				continue
			if var == Command:
				continue

			self.init_command_type(var)
			self.commands[var.get_name()] = var

	def init_command_type(self, cmd):
		cmd.app = self.app

		if cmd.run_before_init is None and cmd.run_after_init is None:
			cmd.run_before_init = False
			cmd.run_after_init = True
		elif cmd.run_before_init is None:
			cmd.run_before_init = False
		elif cmd.run_after_init is None:
			cmd.run_after_init = False

		cmd.create_parser()

	def split_cmd_args(self, command_line):
		assert isinstance(command_line, str)
		if self.SEP in command_line:
			command_name, args = command_line.split(self.SEP, 1)
		else:
			command_name = command_line
			args = ""
		return command_name, args

	def parse(self, command_line, silent=False):
		command_line = command_line.replace(r'\n', '\n')
		command_name, args = self.split_cmd_args(command_line)
		cmd = self.commands.get(command_name)
		if cmd is None and not silent:
			self.error(_("no such command: %s") % command_name)
		return cmd, args

	def execute(self, command_line, state=None):
		is_second_run = state == self.app.STATE_AFTER_INIT
		cmd, args = self.parse(command_line, silent=is_second_run)
		if cmd is None:
			return

		if state != self.app.STATE_RUNNING:
			if not cmd.run_before_init and not cmd.run_after_init:
				if not is_second_run:
					self.app.show_error(_("{cmd} cannot be used in config file").format(cmd=cmd.get_name()))
				return
			if state == self.app.STATE_BEFORE_INIT and not cmd.run_before_init:
				return
			if state == self.app.STATE_AFTER_INIT and not cmd.run_after_init:
				return

		try:
			cmd(args)
		except (ParseException, ErrorInCommand) as e:
			# error messages *from argparse* are internationalized
			# https://stackoverflow.com/a/35964548/2828064
			msg = self.app.pattern_error_in_command.format(err=e, cmd=command_line)
			self.app.show_error(msg, contains_align_character=True, contains_color_markup=True)

	def get_help(self, command_line):
		cmd, args = self.parse(command_line, silent=True)
		if cmd is None:
			mentioned_settings = []
			if self.is_primitive_command(command_line):
				out = self.get_help_primitive(command_line)
			else:
				out = [_("This command is undefined.")]
			return out, mentioned_settings

		out = cmd.get_help()
		out = out + cmd.get_config_file_behaviour()

		out, mentioned_settings = self.app.parse_help(out, parse_mentioned_settings=cmd.parse_mentioned_settings)
		return out, mentioned_settings

	def get_help_primitive(self, cmd):
		out = [_("This is a primitive command without further description.")]
		out.append("")
		out.append(_("possible usages:"))
		fmt = _("  {usage}")
		cmd = self.split_cmd_args(cmd)[0]
		for usage in sorted(self.app.primitive_commands):
			if self.split_cmd_args(usage)[0] == cmd:
				out.append(fmt.format(usage=usage))

		return out

	def is_primitive_command(self, cmd):
		cmd, args = self.split_cmd_args(cmd)
		for primitive_command in self.app.primitive_commands:
			primitive_command, args = self.split_cmd_args(primitive_command)
			if cmd == primitive_command:
				return True
		return False

	def error(self, msg):
		self.app.show_error(msg)

class Command(Runner):
	"""Abstract command class"""

	class AlignedLine:
		__slots__ = ('ln')

		def __init__(self, ln):
			self.ln = ln

	name = None
	run_before_init = None
	run_after_init = None
	parse_mentioned_settings = True

	# ------- class methods -------

	@classmethod
	def get_name(cls):
		classdict = cls.__mro__[0].__dict__
		if 'name' in classdict and classdict['name']:
			return cls.name
		return cls.__name__.replace("_", "-")

	@classmethod
	def create_parser(cls):
		cls.parser = ArgumentParser(prog=cls.get_name(), add_help=False, formatter_class=argparse.RawTextHelpFormatter)
		cls.init_parser(cls.parser)

	@classmethod
	def init_parser(cls, parser):
		"""override this method if the command takes arguments"""
		pass

	@classmethod
	def init_help(cls, parser):
		"""override this method if you want to generate a help description"""
		doc = cls.__doc__
		if doc is None:
			doc = ""
		cls.parser.description = inspect.cleandoc(doc)

	@classmethod
	def init_help_lines(cls, parser):
		cls.init_help(parser)

		stdout = io.StringIO()
		cls.parser.print_help(stdout)
		cls.help_lines = stdout.getvalue().splitlines()

	@classmethod
	def get_help(cls):
		cls.init_help_lines(cls.parser)
		cls.init_help_lines = lambda parser: None
		return cls.help_lines

	@classmethod
	def get_config_file_behaviour(cls):
		out = []
		out.append("")
		out.append(_("behavior in config file:"))
		indent = "  "
		if cls.run_before_init and cls.run_after_init:
			out.append(indent + _("This command is executed before and after initialization."))
		elif cls.run_before_init:
			out.append(indent + _("This command is executed before initialization."))
		elif cls.run_after_init:
			out.append(indent + _("This command is executed after initialization."))
		else:
			out.append(indent + _("This command cannot be used in a config file."))
		return out


	# ------- instance methods -------

	def __init__(self, args):
		args = self.split_args(args)
		args = self.parse_args(args)
		self.execute(args)

	def split_args(self, args):
		try:
			return shlex.split(args)
		except ValueError as e:
			raise ParseException("Failed to split args of %s: %s" % (self.get_name(), e))

	def parse_args(self, args):
		return self.parser.parse_args(args)

	def execute(self, args):
		"""
		override this method

		args: argparse.Namespace instance
		"""
		pass


def quote(arg):
	return shlex.quote(arg)
