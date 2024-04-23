from typing import List

from classes.document_elements.block_content import BlockContent
from classes.prepared_img_data import PreparedImgData
from classes.raw_line import RawLine


# todo need to get diff between lines and use it for delta
class LinesSequence:
    def __init__(self, img_data, block_elements: List[BlockContent]):
        self.__raw_img_data = img_data
        self.__prepared_img_data = PreparedImgData(img_data, block_elements)
        self.__img_data = self.__prepared_img_data

        self.lines: List[RawLine] = []
        self.create_lines()

    def get_line(self, line_idx) -> RawLine:
        return self.lines[line_idx]

    def is_last_line(self, line_idx):
        return line_idx == len(self.lines) - 1

    def create_lines(self):
        lines_data = []

        actual_line_text = ''
        actual_line_num = -1

        actual_x = -1
        actual_x_diff = -1

        actual_y = -1
        last_y_diff = -1
        line_index = 0

        for i in range(len(self.__img_data.text)):
            local_line_num = self.__img_data.line_num[i]
            is_new_line = False

            if actual_line_num == -1:
                actual_line_num = local_line_num
                actual_x = self.__img_data.left[i]
                actual_x_diff = 0

                actual_y = self.__img_data.top[i]
                is_new_line = True

            y_diff = self.__img_data.top[i] - actual_y
            actual_y = self.__img_data.top[i]
            last_y_diff = y_diff

            if not is_new_line:
                is_new_line = self.__get_is_new_line(y_diff)

            if local_line_num != actual_line_num or is_new_line:
                lines_data.append(
                    RawLine(text=actual_line_text, line_idx=line_index, left=actual_x,
                            x_diff_with_prev=actual_x_diff, y_diff_with_prev=y_diff)
                )

                line_index += 1
                actual_line_text = self.__img_data.text[i]
                actual_line_num = local_line_num

                actual_x_diff = actual_x - self.__img_data.left[i]
                actual_x = self.__img_data.left[i]
            else:
                added_text = self.__img_data.text[i]
                actual_line_text += ' ' + added_text

        lines_data.append(
            RawLine(text=str.strip(actual_line_text), line_idx=line_index, left=actual_x,
                    x_diff_with_prev=actual_x_diff, y_diff_with_prev=last_y_diff)
        )

        self.lines = lines_data

    def __get_is_new_line(self, actual_diff):
        return abs(actual_diff - self.__prepared_img_data.min_diff) >= abs(
            self.__prepared_img_data.max_diff - actual_diff)
