import os
import tempfile
import subprocess, shlex
import shutil

from ..cat import PDF4Cat

class soffice_convert(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(soffice_convert, self).__init__(*args, **kwargs)

	def soffice_convert_to(self, doc_type: str, output_doc: str):
		temp_pdf = os.path.join(tempfile.gettempdir(), f"""{self.doc_name}.{doc_type}""")
		subprocess.run(shlex.split(f"""soffice --headless --convert-to {doc_type} {self.doc_file} --outdir {tempfile.gettempdir()}"""), 
			) # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		shutil.move(temp_pdf, output_doc)
		
	def soffice_convert2pdf(self, output_pdf: str):
		if self.doc_fileext in self.libre_exts:
			temp_pdf = os.path.join(tempfile.gettempdir(), f"""{self.doc_name}.pdf""")
			subprocess.run(shlex.split(f"""soffice --headless --convert-to pdf {self.doc_file} --outdir {tempfile.gettempdir()}"""), 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			shutil.move(temp_pdf, output_pdf)
		else:
			raise NotImplementedError(f"File extension '{self.doc_fileext}' => '.pdf' not supported")

	def soffice_convert2pdf_a(self, a: int, output_pdf: str):
		if not a:
			a = 1
		# soffice --headless --convert-to pdf:"writer_pdf_Export:SelectPdfVersion=1" --outdir outdir input.pdf
		if self.doc_fileext in self.libre_exts:
			temp_pdf = os.path.join(tempfile.gettempdir(), f"""{self.doc_name}.pdf""")
			subprocess.run(shlex.split(f"""soffice --headless --convert-to pdf:"writer_pdf_Export:SelectPdfVersion={a}" {self.doc_file} --outdir {tempfile.gettempdir()}"""), 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			shutil.move(temp_pdf, output_pdf)
		else:
			raise NotImplementedError(f"File extension '{self.doc_fileext}' => '.pdf' not supported")



