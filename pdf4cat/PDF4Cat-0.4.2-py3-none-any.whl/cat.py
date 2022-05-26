import os
import fitz

class PDF4Cat:
	from .helpers import run_in_subprocess
	""" PyMuPDF crypt methods """
	from . import (
		PDF_ENCRYPT_AES_128,
		PDF_ENCRYPT_AES_256,
		PDF_ENCRYPT_KEEP,
		PDF_ENCRYPT_NONE,
		PDF_ENCRYPT_RC4_128,
		PDF_ENCRYPT_RC4_40,
		PDF_ENCRYPT_UNKNOWN,

		PDF_PERM_ACCESSIBILITY,
		PDF_PERM_ANNOTATE,
		PDF_PERM_ASSEMBLE,
		PDF_PERM_COPY,
		PDF_PERM_FORM,
		PDF_PERM_MODIFY,
		PDF_PERM_PRINT,
		PDF_PERM_PRINT_HQ
		)
	def __init__(self, 
		doc_file=None, 
		input_doc_list: list=None, 
		passwd: str='', 
		progress_callback=None):
		if not doc_file and input_doc_list:
			doc_file = input_doc_list[0]
		elif doc_file:
			pass
		else:
			raise TypeError("Required 1 argument of doc_file, input_doc_list. ")
		self.input_doc_list = input_doc_list
		self.doc_file = doc_file
		self.doc_path = os.path.split(doc_file)[0]
		self.doc_name = os.path.basename(os.path.splitext(doc_file)[0])
		self.doc_filename = os.path.basename(doc_file)
		self.doc_fileext = os.path.splitext(doc_file)[1]

		self.libre_exts = [
		".doc", ".odt", ".ott", 
		".docx", ".fodp", ".dotx",
		".csv", ".otp", ".ods",
		".odp", ".odf", ".otg",
		".xls", ".xlsx", ".ppt", 
		".pptx", ".txt", ".xml",
		".epub"
		]


		""" PyMuPDF methods """
		self.fitz_Matrix = fitz.Matrix
		self.fitz_get_pdf_now = fitz.get_pdf_now
		self.fitz_LINK_NAMED = fitz.LINK_NAMED
		
		self.passwd = passwd

		self.progress_callback = progress_callback
		self.counter = 0
		if not progress_callback:
			self.progress_callback = self.pc

	def pdf_open(self, filename: str = None, stream: bytes = None, passwd: str = ''):
		fo = fitz.open(filename, stream)
		if fo.needsPass:
			fo.authenticate(passwd)

		return fo


	def pc(self, current, total) -> None:
		#
		print(f'Progress: {current} of {total} complete', end="\r")
		# if current != total:
		# 	print(f'Progress: {current} of {total} complete', end="\r")
		# else:
		# 	print(f'Progress: {current} of {total} complete')

	@property
	def pages_count(self) -> int:
		return self.pdf.page_count

