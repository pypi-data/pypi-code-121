import os
import io
import zipfile

from ..cat import PDF4Cat

class Img2Pdf(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(Img2Pdf, self).__init__(*args, **kwargs)

	@PDF4Cat.run_in_subprocess
	def img2pdf(self, 
		output_pdf = None) -> None:
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf)

		pic = self.pdf_open(self.doc_file, passwd=self.passwd)
		pdfbytes = pic.convert_to_pdf()
		with open(output_pdf, 'wb') as pdf:
			pdf.write(pdfbytes)
		del pdfbytes

	@PDF4Cat.run_in_subprocess
	def imgs2pdf(self, 
		output_pdf = None) -> None:
		if not output_pdf:
			output_pdf = os.path.join(self.doc_path, self.doc_name+"_out.pdf")
		output_pdf = os.path.join(os.getcwd(), output_pdf)

		len_docs = len(self.input_doc_list)

		result = self.pdf_open()
		for img_path in self.input_doc_list:
			pic = self.pdf_open(self.doc_file, passwd=self.passwd)
			pdfbytes = pic.convert_to_pdf()
			pdf_tmp = self.pdf_open("pdf", pdfbytes)
			pic.close()
			del pdfbytes
			result.insert_pdf(pdf_tmp)
			pdf_tmp.close()
			del pdf_tmp
			self.counter += 1
			self.progress_callback(self.counter, len_docs)
		result.save(output_pdf)

	# Generate name with BytesIO object (it is faster)
	def gen_imagesi2p(self, fimages, start_from) -> tuple:
		for num, img in enumerate(self.input_doc_list): ###
			io_data = io.BytesIO()
			img_ext = os.path.splitext(img)[1][1:]
			pic = self.pdf_open(img)
			pdfbytes = pic.convert_to_pdf()
			pic.close()
			del pic
			io_data.write(pdfbytes)
			del pdfbytes

			imfn = fimages.format(name=os.path.basename(img), num=num+start_from)
			imfi = io_data.getvalue()
			yield imfn, imfi

	@PDF4Cat.run_in_subprocess
	def imgs2pdfs_zip(self, 
		out_zip_file: str, 
		fimages: str = '{name}_{num}.pdf',
		start_from: int = 0) -> None:

		# Compression level: zipfile.ZIP_DEFLATED (8) and disable ZIP64 ext.
		with zipfile.ZipFile(out_zip_file, 'w', zipfile.ZIP_DEFLATED, False) as zf:

			for file_name, io_data in self.gen_imagesi2p(fimages, start_from):
				zf.writestr(file_name, io_data)
				self.counter += 1 #need enumerate
				self.progress_callback(self.counter, len(self.input_doc_list))

		self.counter = 0

#

class Pdf2Img(PDF4Cat):
	def __init__(self, *args, **kwargs):
		super(Pdf2Img, self).__init__(*args, **kwargs)
		# self.pdf = self.pdf_open(self.doc_file, password=self.passwd)

	# Generate name with BytesIO object (it is faster)
	def gen_imagesp2i(self, pages, fimages, start_from, zoom) -> tuple:
		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		ext_from_fimages = os.path.splitext(fimages)[1][1:]
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
			io_data.write(pix.tobytes(output=ext_from_fimages))
			#

			imfn = fimages.format(name=os.path.basename(self.doc_file), num=pageNo+start_from)
			imfi = io_data
			yield imfn, imfi

	@PDF4Cat.run_in_subprocess
	def pdf2imgs_zip(self, 
		out_zip_file: str, 
		pages: list = [],
		fimages: str = '{name}_{num}.png',
		start_from: int = 0,
		zoom: float = 1.5) -> None:
		
		pdf = self.pdf_open(self.doc_file, passwd=self.passwd)
		if not pages:
			pcount = pdf.page_count
		else:
			pcount = len(pages)

		# Compression level: zipfile.ZIP_DEFLATED (8) and disable ZIP64 ext.
		with zipfile.ZipFile(out_zip_file, 'w', zipfile.ZIP_DEFLATED, False) as zf:
		
			for file_name, io_data in self.gen_imagesp2i(pages, fimages, start_from, zoom):
				zf.writestr(file_name, io_data.getvalue())
				self.counter += 1 #need enumerate
				self.progress_callback(self.counter, pcount)

		self.counter = 0

