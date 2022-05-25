from .images import *
from .ocr import *
from .any import *
from .soffice2pdf import *

class Converter(Img2Pdf, Pdf2Img, OCR, any_doc_convert, soffice_convert):
	def __init__(self, *args, **kwargs):
		super(Converter, self).__init__(*args, **kwargs)