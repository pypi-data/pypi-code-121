import os

from ..cat import PDF4Cat

class Rotate(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(Rotate, self).__init__(*args, **kwargs)
		
	@PDF4Cat.run_in_subprocess
	def rotate_doc_to(self, angle: int, output_pdf=None):
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf)

		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		pdf2 = self.pdf_open()

		if not angle % 90 == 0:
			raise TypeError("Angle must be a multiple of 90!")
		for num in range(pdf.page_count):
			pdf2.insert_pdf(pdf, from_page=num, to_page=num, rotate=angle)

			self.counter += 1
			self.progress_callback(self.counter, pdf.page_count)
		pdf2.save(output_pdf)