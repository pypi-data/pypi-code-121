import os
import io

from ..cat import PDF4Cat

class OCR(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(OCR, self).__init__(*args, **kwargs)

	# Generate name with BytesIO object (it is faster)
	def gen_pdfImagesOCR(self, pages, language, zoom) -> tuple:
		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		mat = self.fitz_Matrix(zoom, zoom)
		noOfPages = range(pdf.page_count)
		if pages:
			noOfPages = pages
		for pageNo in noOfPages:
			if pages and pageNo not in pages:
				continue
			io_data = io.BytesIO()
			#
			page = pdf.load_page(pageNo) #number of page
			pix = page.get_pixmap(matrix = mat)
			bytes_ = pix.pdfocr_tobytes(language=language)
			#

			yield bytes_

	@PDF4Cat.run_in_subprocess
	def pdfocr(self, 
		language: str = "eng",
		output_pdf = None,
		pages: list = [],
		start_from: int = 0,
		zoom: float = 1.5) -> None:

		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf) #doc.insert_pdf(imgpdf)

		pdf_doc = self.pdf_open(self.doc_file)
		pdf = self.pdf_open()
		if not pages:
			pcount = pdf_doc.page_count
		else:
			pcount = len(pages)

		for bytes_ in self.gen_pdfImagesOCR(pages, language, zoom):
			with self.pdf_open("pdf", bytes_) as ocr_processed:
				pdf.insert_pdf(ocr_processed)

			self.counter += 1 #need enumerate
			self.progress_callback(self.counter, pcount)

		pdf.save(output_pdf)

		self.counter = 0



