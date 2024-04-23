from docx.shared import Inches
from classes.document_elements.paragraph.list_paragraph import ListParagraph
from classes.lines_sequence import LinesSequence


class HollowDotListParagraph(ListParagraph):
    def __init__(self, lines_sequence: LinesSequence, start_line_idx: int, end_line_idx: int):
        super().__init__(lines_sequence, start_line_idx, end_line_idx)

    def is_actual_list_item_head(self, line_idx):
        line = self.lines_sequence.lines[line_idx]
        line_text = line.text
        return str.startswith(line_text, '©')

    @staticmethod
    def is_list_item_head(lines_sequence, line_idx):
        line = lines_sequence.lines[line_idx]
        line_text = line.text
        return str.startswith(line_text, '©')

    def add_to(self, document):
        self.__prepare_text_for_doc()
        paragraph = document.add_paragraph(self.prepared_text, style='List Bullet')
        paragraph.paragraph_format.first_line_indent = Inches(0.5)

    def __prepare_text_for_doc(self):
        self.construct_paragraph_text()
        self.prepared_text = str.strip(str.strip(self.text)[1:])[1:]
