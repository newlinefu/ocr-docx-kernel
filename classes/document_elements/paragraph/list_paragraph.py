from abc import abstractmethod, ABC
from classes.document_elements.paragraph.paragraph import Paragraph
from classes.lines_sequence import LinesSequence
from classes.raw_line import RawLine


class ListParagraph(Paragraph, ABC):
    def __init__(self, lines_sequence: LinesSequence, start_line_idx: int, end_line_idx: int):
        super().__init__(lines_sequence, start_line_idx, end_line_idx)

    def is_list_paragraph_continue(self, line_idx):
        line: RawLine = self.lines_sequence.lines[line_idx]
        if self.start_line_idx == line_idx - 1 and line.x_diff_with_prev < 0:
            return True

        if self.end_line_idx == line_idx - 1:
            if not self.lines_sequence.is_last_line(line_idx):
                is_next_item_head = self.is_actual_list_item_head(line_idx + 1)
                if self.lines_sequence.get_line(line_idx + 1).x_diff_with_prev > 1 and not is_next_item_head:
                    return False
            # 5 will be replaced with generic diff
            if abs(self.lines_sequence.get_line(line_idx).x_diff_with_prev) <= 5:
                return True

        return False

    @abstractmethod
    def is_actual_list_item_head(self, line_idx):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_list_item_head(lines_sequence, line_idx):
        raise NotImplementedError
