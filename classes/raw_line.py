class RawLine:
    def __init__(self, text, line_idx, left, diff):
        self.text = text
        self.line_idx = line_idx
        self.left = left
        self.diff = diff

