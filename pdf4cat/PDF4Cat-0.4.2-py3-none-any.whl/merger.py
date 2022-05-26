import os

from .cat import PDF4Cat

class Merger(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(Merger, self).__init__(*args, **kwargs)

	# need in_memory merge func

	@PDF4Cat.run_in_subprocess
	def merge_file_with(self, input_pdf, output_pdf = None) -> None:
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf)
		input_pdf = os.path.join(os.getcwd(), input_pdf)
		
		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)

		input_pdf = self.pdf_open(input_pdf) # 2

		result = self.pdf_open()
		result.insert_pdf(pdf) # 1
		result.insert_pdf(input_pdf) # 2
		result.save(output_pdf)

	@PDF4Cat.run_in_subprocess
	def merge_files_to(self, output_pdf = None) -> None:
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf)

		result = self.pdf_open()
		len_idl = len(self.input_doc_list)
		for pdf in self.input_doc_list:
			with self.pdf_open(pdf) as f:
				result.insert_pdf(f)
			self.counter += 1
			self.progress_callback(self.counter, len_idl)
		self.counter = 0
		result.save(output_pdf)