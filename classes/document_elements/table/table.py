from img2table.tables.objects.extraction import ExtractedTable
from img2table.document import Image as ImageTable
from img2table.ocr import TesseractOCR
from classes.bbox import BoundingBox
from classes.document_elements.block_content import BlockContent


class Table(BlockContent):

    def __init__(self, extracted_table: ExtractedTable):
        self.extracted_table = extracted_table
        table_bbox = extracted_table.bbox
        bbox = BoundingBox(x1=table_bbox.x1, x2=table_bbox.x2, y1=table_bbox.y1, y2=table_bbox.y2)
        super().__init__(bbox=bbox)

    def is_content_in_table(self, left, top):
        table_bbox = self.extracted_table.bbox
        suitable_by_x = table_bbox.x1 <= left <= table_bbox.x2
        suitable_by_y = table_bbox.x1 <= top <= table_bbox.x2
        return suitable_by_x and suitable_by_y

    def get_bbox(self):
        return self.extracted_table.bbox

    def get_columns_count(self):
        return len(self.extracted_table.content[0])

    def get_rows_count(self):
        return len(self.extracted_table.content)

    def add_to(self, document):
        rows_count = self.get_rows_count()
        columns_count = self.get_columns_count()

        table = document.add_table(rows=rows_count, cols=columns_count)
        table.style = 'Table Grid'

        for idx, row in self.extracted_table.content.items():
            for i in range(columns_count):
                text = ''
                if row[i].value is not None:
                    text = row[i].value
                cell = table.cell(idx, i)
                cell.text = text

    @staticmethod
    def get_tables_from_image(img_name):
        img = ImageTable(src=img_name)
        ocr = TesseractOCR(n_threads=1, lang="eng+rus", psm=4)
        extracted_tables = img.extract_tables(ocr=ocr,
                                              implicit_rows=False,
                                              borderless_tables=False,
                                              min_confidence=50)
        tables = []
        for table in extracted_tables:
            tables.append(Table(table))

        return tables
