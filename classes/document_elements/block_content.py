from abc import ABC

from classes.bbox import BoundingBox
from classes.document_elements.document_part import DocumentPart


class BlockContent(DocumentPart, ABC):
    def __init__(self, bbox: BoundingBox):
        self.bbox = bbox
        self.is_on_start_page = False
        self.is_on_end_page = False

    def get_bbox(self):
        return self.bbox

    def is_before_by_top(self, y):
        return (self.bbox.y1 - 10) <= y

    def is_after_by_top(self, y):
        return y <= (self.bbox.y2 + 10)

    def is_coordinate_inside(self, x, y):
        return self.bbox.x1 <= x <= self.bbox.x2 and (self.bbox.y1 - 10) <= y <= (self.bbox.y2 + 10)
