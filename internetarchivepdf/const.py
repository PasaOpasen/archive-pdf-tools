VERSION = '1.0.0'

PRODUCER = 'Internet Archive PDF %s; including '\
           'mupdf and pymupdf/skimage' % (VERSION,)


IMAGE_MODE_PASSTHROUGH = 0
IMAGE_MODE_PIXMAP = 1
IMAGE_MODE_MRC = 2
IMAGE_MODE_SKIP = 3


RECODE_RUNTIME_WARNING_INVALID_PAGE_SIZE = 'invalid-page-size'
RECODE_RUNTIME_WARNING_INVALID_PAGE_NUMBERS = 'invalid-page-numbers'
RECODE_RUNTIME_WARNING_INVALID_JP2_HEADERS = 'invalid-jp2-headers'

RECODE_RUNTIME_WARNINGS = {
    RECODE_RUNTIME_WARNING_INVALID_PAGE_SIZE,
    RECODE_RUNTIME_WARNING_INVALID_PAGE_NUMBERS,
}

__version__ = VERSION
