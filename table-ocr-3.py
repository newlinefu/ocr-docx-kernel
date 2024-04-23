from img2table.document import Image
from img2table.ocr import TesseractOCR

from utils import get_doc_structure_from_image

img = Image(src='./test-images/table/Screenshot_2.jpg')

ocr = TesseractOCR(n_threads=1, lang="eng+rus")

# Table identification
image_tables = img.extract_tables()

# Result of table identification
extracted_tables = img.extract_tables(ocr=ocr,
                                      implicit_rows=False,
                                      borderless_tables=False,
                                      min_confidence=10)


prev = get_doc_structure_from_image('./test-images/table/Screenshot_2.jpg')

if len(extracted_tables) > 0:
    founded_values = extracted_tables[0].content
    print(founded_values)
    print(prev)
