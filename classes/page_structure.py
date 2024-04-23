from typing import List

from classes.document_elements.block_content import BlockContent
from classes.document_elements.document_part import DocumentPart
from classes.document_elements.page_break.page_break import PageBreak
from classes.document_elements.paragraph.dot_list_paragraph import DotListParagraph
from classes.document_elements.paragraph.hollow_dot_list_paragraph import HollowDotListParagraph
from classes.document_elements.paragraph.list_paragraph import ListParagraph
from classes.document_elements.paragraph.number_bracket_list_paragraph import NumberBracketListParagraph
from classes.document_elements.paragraph.number_dot_list_paragraph import NumberDotListParagraph
from classes.document_elements.paragraph.paragraph import Paragraph
from classes.document_elements.table.table import Table
from classes.lines_sequence import LinesSequence


class PageStructure:
    def __init__(self, img_data, block_elements: List[BlockContent]):
        self.raw_img_data = img_data
        self.page_block_elements = block_elements
        self.lines_sequence = LinesSequence(img_data, block_elements)
        self.page_parts: List[DocumentPart] = []

        self.page_lists_paragraphs: List[ListParagraph] = []
        self.page_lists_paragraph_lines: List[int] = []

        self.create_page_structure()

    def __add_tables_to_page_structure(self):
        for table in self.page_block_elements:
            self.page_parts.append(table)

    def create_page_structure(self):
        # 3. Find lower diff
        # common_bias = get_most_common_line_x_bias(lines_info)

        # 4. transform x pos (actual_x_pos + lower_diff * (sign_is_minus ? lines count - i : i))
        # lines_info = rotate_lines_coordinates(lines_info, common_bias)

        self.__fill_lists_items()

        # 5. Find nearest
        self.__fill_paragraphs()

        self.__add_tables_to_page_structure()

        return self.page_parts

    def __get_average_line_bias(self):
        average_lines_bias = 0
        non_list_lines_count = 0
        for i in range(len(self.lines_sequence.lines)):
            according_list_items = list(filter(lambda p: p.is_line_belong(i), self.page_lists_paragraphs))
            if len(according_list_items) == 0:
                average_lines_bias += abs(self.lines_sequence.get_line(i).x_diff_with_prev)
                non_list_lines_count += 1
        average_lines_bias /= non_list_lines_count
        return average_lines_bias

    def __fill_paragraphs(self):
        page_paragraphs: List[Paragraph] = []
        average_lines_bias = self.__get_average_line_bias()

        if len(self.page_lists_paragraph_lines) == len(self.lines_sequence.lines):
            return

        non_list_lines = []
        for i in range(len(self.lines_sequence.lines)):
            if i not in self.page_lists_paragraph_lines:
                non_list_lines.append(i)
        start_index = non_list_lines[0]

        page_paragraphs.append(
            Paragraph(self.lines_sequence, start_index, start_index)
        )

        prev_line_idx = start_index
        line_idx = start_index + 1

        while line_idx < len(self.lines_sequence.lines):
            if line_idx in self.page_lists_paragraph_lines:
                list_paragraph = self.__find_list_by_line_index(line_idx)
                page_paragraphs.append(list_paragraph)
                line_idx = list_paragraph.end_line_idx + 1
                continue

            line_step = line_idx - prev_line_idx
            prev_line_idx = line_idx

            is_diff_negative = self.lines_sequence.get_line(line_idx).x_diff_with_prev < 0
            is_diff_more_than_avg = abs(self.lines_sequence.get_line(line_idx).x_diff_with_prev) > average_lines_bias

            if line_step > 1 or is_diff_negative and is_diff_more_than_avg:
                page_paragraphs.append(Paragraph(self.lines_sequence, line_idx, line_idx))
            else:
                page_paragraphs[-1].set_end_line_idx(line_idx)
            line_idx += 1

        for paragraph in page_paragraphs:
            self.page_parts.append(paragraph)

    def __get_list_head_class(self, line_idx):

        if DotListParagraph.is_list_item_head(self.lines_sequence, line_idx):
            return DotListParagraph
        if HollowDotListParagraph.is_list_item_head(self.lines_sequence, line_idx):
            return HollowDotListParagraph
        if NumberDotListParagraph.is_list_item_head(self.lines_sequence, line_idx):
            return NumberDotListParagraph
        if NumberBracketListParagraph.is_list_item_head(self.lines_sequence, line_idx):
            return NumberBracketListParagraph

        return None

    def __fill_lists_items(self):

        for i in range(len(self.lines_sequence.lines)):
            list_head_class = self.__get_list_head_class(i)
            is_list_item_head = list_head_class is not None

            running_by_list = False
            if is_list_item_head:
                running_by_list = True

            if not running_by_list and len(self.page_lists_paragraphs) > 0:
                last_list_paragraph: ListParagraph = self.page_lists_paragraphs[-1]
                running_by_list = last_list_paragraph.is_list_paragraph_continue(i)

            if running_by_list:
                self.page_lists_paragraph_lines.append(i)

            if is_list_item_head:
                list_item = list_head_class(self.lines_sequence, i, i)
                self.page_lists_paragraphs.append(list_item)

            if not is_list_item_head and running_by_list:
                self.page_lists_paragraphs[-1].set_end_line_idx(i)

    def __find_list_by_line_index(self, line_idx):
        for paragraph in self.page_lists_paragraphs:
            if paragraph.is_line_belong(line_idx):
                return paragraph
        return None

    def add_to(self, document):
        for page_part in self.page_parts:
            page_part.add_to(document)

        page_break = PageBreak()
        page_break.add_to(document)
