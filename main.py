from pathlib import Path
from file_utils import get_result_doc_name, get_primary_image_files
from utils import create_document

# TEST_NAME = 'one-paragraph-simple-test'
# TEST_NAME = 'one-paragraph-one-image'
# TEST_NAME = 'two-paragraphs-one-image'

# TEST_NAME = 'multiple-par-rotated'

# TEST_NAME = 'list-numbers'
TEST_NAME = 'list-dots'

Path('./secondary-images/' + TEST_NAME).mkdir(parents=True, exist_ok=True)
Path('./result-docs/' + TEST_NAME).mkdir(parents=True, exist_ok=True)

primary_file_names = get_primary_image_files(TEST_NAME)
result_filename = get_result_doc_name(TEST_NAME)

create_document(primary_file_names, result_filename, TEST_NAME)
