import os

from .cat import PDF4Cat

class PdfOptimizer(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(PdfOptimizer, self).__init__(*args, **kwargs)
		
	@PDF4Cat.run_in_subprocess
	def DeFlate_to(self, output_pdf = None):
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")

		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		pdf.save(output_pdf, 
			deflate=True,
			deflate_images=True,
			deflate_fonts=True,
			garbage=4,
			clean=1) # clean is compressing
		pdf.close()
