#!/usr/bin/python3 -B

from os import remove
from os.path import isfile, exists
from .utils.crawler import Crawler
from .utils.commoncmd import CommonCmd as cmd

class BulkFileChanger:

	def change_filename(self, filepath, outpath, overrite=True):

		if exists(filepath) != True:
			return {'status': 400, 'message': 'Error: no such file path: {}'.format(filepath)}

		if isfile(filepath) != True:
			return {'status': 400, 'message': 'Error: file path is corrupt: {}'.format(filepath)}

		if exists(outpath) == True:
			return {'status': 400, 'message': 'Error, output path already exists: {}'.format(filepath)}

		response = cmd.copyfile(filepath, outpath)
		if response['status'] == 200 and overrite == True:
			remove(filepath)
			return response
		else:
			return response

	def char_replace(self, filepath, findchar, replacechar):
		filename = Crawler.get_basename(filepath)
		dirname = Crawler.get_rootdir(filepath)
		new_filename = filename.replace(findchar, replacechar)
		outpath = Crawler.joinpath(dirname, new_filename)
		if filepath == outpath:
			return {'status': 400, 'message': 'No change made: {}'.format(outpath), 'outpath': outpath}
		else:
			return {'status': 200, 'message': 'Successfully changed: {}'.format(outpath), 'outpath': outpath}

	def char_replace_all(self, wd, extension, findchar, replacechar):
		results = []
		filepaths = Crawler.get_files(wd, extension)

		for filepath in filepaths:
			outpath = self.char_replace(filepath, findchar, replacechar)
			if outpath['status'] == 400:
				results.append(outpath['message'])
			else:
				response = self.change_filename(filepath, outpath)
				results.append(response['message'])

		return results

	def _format_ext(self, raw_extension, ifblank = '.txt', ifstar = None):
		if raw_extension == '*':
			return ifstar
		if raw_extension == '':
			return ifblank
		if raw_extension[0] != '.':
			return '.' + raw_extension
		else:
			return raw_extension

	def run(self):
		cmd.clear()
		wd = cmd.pwd()
		file_count = len(Crawler.get_files(wd))
		if file_count <= 0:
			print('No Files found in: {}'.format(wd))
			return
		print('Bulk File Changer has found {} files in the following:'.format(str(file_count)))
		print(wd)
		print(' ')
		print('What character string do you want to change in these files?')
		findchar = input()
		if findchar == '':
			cmd.clear()
			print('Character string not specified, no action taken.')
			return
		print(' ')
		print('What is the new character string that you want to replace it with?')
		replacechar = input()
		print(' ')
		print('You may specify a file type. Leaving blank will default to .txt files.')
		print('Use * for all files regardless of type (this can be dangerous).')
		print(' ')
		raw_extension = input('Specify a file type [Optional]: ')
		extension = self._format_ext(raw_extension)
		cmd.clear()
		if extension == None:
			print('You are about to bulk change all files in the following directory and its subdirectories:')
		else:
			print('You are about to bulk change all {} files in the following directory and its subdirectories:'.format(extension))

		print(wd)
		print(' ')
		confirm = input('Are you sure you want to make this change [y/n]: ')
		cmd.clear()
		if confirm != 'y': print('Exited, no action taken.'); return
		print('Bulk file change started...')
		response = self.char_replace_all(wd, extension, findchar, replacechar)
		for r in response: print(r)
		print('Bulk file change complete.')
		input(); cmd.clear(); return
