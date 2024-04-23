from docx.shared import Inches
from classes.document_elements.document_part import DocumentPart
from classes.lines_sequence import LinesSequence


class Paragraph(DocumentPart):
    def __init__(self, lines_sequence: LinesSequence, start_line_idx: int, end_line_idx: int):
        self.start_line_idx = start_line_idx
        self.end_line_idx = end_line_idx
        self.lines_sequence: LinesSequence = lines_sequence
        self.text = ''
        self.prepared_text = self.text

    def get_text(self):
        return self.text

    def set_end_line_idx(self, end_line_idx: int):
        self.end_line_idx = end_line_idx

    def add_to(self, document):
        self.prepare_text_for_doc()
        paragraph = document.add_paragraph(self.text)
        paragraph.paragraph_format.first_line_indent = Inches(0.5)

    def construct_paragraph_text(self):
        text = ''
        for i in range(self.start_line_idx, self.end_line_idx + 1):
            line_text = self.lines_sequence.lines[i].text
            text += line_text + ' '
        self.text = str.strip(text)

    def is_line_belong(self, line_idx):
        return self.start_line_idx <= line_idx <= self.end_line_idx

    def prepare_text_for_doc(self):
        self.__prepare_text_for_doc()

    def __prepare_text_for_doc(self):
        self.construct_paragraph_text()
        self.prepared_text = str.strip(self.text)
