import os
import io
import zipfile

from .cat import PDF4Cat

class Splitter(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(Splitter, self).__init__(*args, **kwargs)

	# Generate name with BytesIO object (it is faster)
	def gen_split(self, from_pdf = None, 
		fpages: str = '{name}_{num}.pdf', 
		add2num: int = 0) -> tuple: # pdfname & pdfbytes
		if not from_pdf:
			from_pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		for num in range(from_pdf.page_count): ###
			# dst = from_pdf.convert_to_pdf() # if already pdf returns bytes
			# dst = self.pdf_open("pdf", stream=dst) # 
			dst = self.pdf_open()
			dst.insert_pdf(from_pdf, from_page=num, to_page=num) # need load page
			io_data = io.BytesIO()
			dst.save(io_data)
			dst.close()
			del dst

			pdfn = fpages.format(name=self.doc_filename, num=num+add2num)
			pdfp = io_data
			yield pdfn, pdfp

	@PDF4Cat.run_in_subprocess # need add range
	def split_pages2zip(
		self,
		out_zip_file: str, 
		fpages: str = '{name}_{num}.pdf',
		add2num: int = 0) -> None:
		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)

		# Compression level: zipfile.ZIP_DEFLATED (8) and disable ZIP64 ext.
		with zipfile.ZipFile(out_zip_file, 'w', zipfile.ZIP_DEFLATED, False) as zf:

			for file_name, io_data in self.gen_split(pdf, fpages, add2num):
				zf.writestr(file_name, io_data.getvalue())
				self.counter += 1 #need enumerate
				self.progress_callback(self.counter, pdf.page_count)

				del io_data

		self.counter = 0
	