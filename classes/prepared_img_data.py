from typing import List

from classes.document_elements.block_content import BlockContent


class PreparedImgData:
    def __init__(self, img_data, block_elements: List[BlockContent]):
        self.conf: List[int] = img_data['conf']
        self.top: List[int] = img_data['top']
        self.left: List[int] = img_data['left']
        self.word_num: List[int] = img_data['word_num']
        self.text: List[str] = img_data['text']
        self.line_num: List[int] = img_data['line_num']

        self.block_elements = block_elements
        self.__filter_img_data_empty_symbols()
        self.__filter_img_data_block_symbols()

        max_diff, min_diff = self.__get_diffs_min_max()
        self.min_diff = min_diff
        self.max_diff = max_diff

    def __get_diffs_min_max(self):
        diffs = []
        for i in range(len(self.top) - 1):
            actual_line_y = self.top[i]
            next_line_y = self.top[i + 1]
            diff = abs(next_line_y - actual_line_y)
            diffs.append(diff)

        max_diff = max(diffs)
        min_diff = min(diffs)

        for block_elem in self.block_elements:
            max_diff -= block_elem.bbox.y2 - block_elem.bbox.y1
        return max_diff, min_diff

    def __filter_img_data_empty_symbols(self):
        new_text: List[str] = []
        new_conf: List[int] = []
        new_line_num: List[int] = []
        new_word_num: List[int] = []
        new_top: List[int] = []
        new_left: List[int] = []

        for i in range(len(self.conf)):
            conf_value = self.conf[i]
            if conf_value != -1:
                new_conf.append(self.conf[i])
                new_top.append(self.top[i])
                new_left.append(self.left[i])
                new_word_num.append(self.word_num[i])
                new_text.append(self.text[i])
                new_line_num.append(self.line_num[i])

        self.conf = new_conf
        self.top = new_top
        self.left = new_left
        self.word_num = new_word_num
        self.text = new_text
        self.line_num = new_line_num

    def __filter_img_data_block_symbols(self):
        new_text: List[str] = []
        new_conf: List[int] = []
        new_line_num: List[int] = []
        new_word_num: List[int] = []
        new_top: List[int] = []
        new_left: List[int] = []

        for block in self.block_elements:
            for idx in range(len(self.left)):
                x = self.left[idx]
                y = self.top[idx]

                is_inside = block.is_coordinate_inside(x, y)
                if not is_inside:
                    new_conf.append(self.conf[idx])
                    new_top.append(self.top[idx])
                    new_left.append(self.left[idx])
                    new_word_num.append(self.word_num[idx])
                    new_text.append(self.text[idx])
                    new_line_num.append(self.line_num[idx])

        if len(self.block_elements) > 0:
            self.conf = new_conf
            self.top = new_top
            self.left = new_left
            self.word_num = new_word_num
            self.text = new_text
            self.line_num = new_line_num
