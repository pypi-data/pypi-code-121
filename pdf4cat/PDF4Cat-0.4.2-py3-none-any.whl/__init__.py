""" PyMuPDF crypt methods """
from fitz import (
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

""" PDF4Cat methods """
from .splitter import Splitter
from .merger import Merger
from .crypt import Crypter
from .effects import Effects
from .compress import PdfOptimizer
from .converter import Converter
from .tools import Tools

from .doc import Doc