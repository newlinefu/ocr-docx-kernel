from typing import List

import numpy as np
import pytesseract
from docx import Document
from pdf2image import convert_from_path
from pytesseract import Output
from PIL import Image

from classes.document_elements.table.table import Table
from classes.page_structure import PageStructure

from file_utils import is_pdf, get_secondary_image_name, get_secondary_images


def get_doc_structure_from_image(img_name):
    img = np.array(Image.open(img_name))
    tables = Table.get_tables_from_image(img_name)
    image_data = pytesseract.image_to_data(img, lang="eng+rus", output_type=Output.DICT)
    page_structure = PageStructure(image_data, tables)

    return [page_structure]


def get_doc_structure_from_pdf(pdf_name, test_name):
    pages = convert_from_path(pdf_name, 500)
    image_counter = 1

    for page in pages:
        filename = get_secondary_image_name(test_name, image_counter)
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1

    secondary_images = get_secondary_images(test_name)
    doc_structure = []

    for secondary_image in secondary_images:
        structure_part = get_doc_structure_from_image(secondary_image)
        doc_structure.append(structure_part[0])

    return doc_structure


def get_doc_structure_from_files(file_names, test_name):
    result_structure = []
    for img in file_names:
        single_structure = get_doc_structure_from_pdf(img, test_name) if is_pdf(img) else get_doc_structure_from_image(
            img)
        for part in single_structure:
            result_structure.append(part)
    return result_structure


def create_document_object(file_names, test_name):
    document = Document()
    document_structure: List[PageStructure] = get_doc_structure_from_files(file_names, test_name)
    for part in document_structure:
        part.add_to(document)

    return document


def create_document(file_names, output_file_name, test_name):
    document = create_document_object(file_names, test_name)
    document.save(output_file_name)
