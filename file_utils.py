from os import listdir
from os.path import isfile, join

START_TEST_DOCS_DIR = 'test-pdf'
START_TEST_IMAGES_DIR = 'test-images'
SECONDARY_IMAGES_DIR = 'secondary-images'
RESULT_DOCS_DIR = 'result-docs'

DEFAULT_FILE_NAME = 'result.docx'


def get_primary_files(directory, test_name):
    dir_test_path = join(directory, str(test_name))
    files = [join(dir_test_path, f) for f in listdir(dir_test_path) if
             isfile(join(dir_test_path, f))]
    return files


def get_primary_pdf_files(test_name):
    return get_primary_files(START_TEST_DOCS_DIR, test_name)


def get_primary_image_files(test_name):
    return get_primary_files(START_TEST_IMAGES_DIR, test_name)


def get_secondary_images(test_name):
    return get_primary_files(SECONDARY_IMAGES_DIR, test_name)


def get_secondary_image_name(test_name, image_index):
    return join(SECONDARY_IMAGES_DIR, test_name, str(image_index) + ".jpg")


def get_result_doc_name(test_name):
    return join(RESULT_DOCS_DIR, str(test_name), DEFAULT_FILE_NAME)


def is_pdf(file_name):
    return str.endswith(file_name, '.pdf')
