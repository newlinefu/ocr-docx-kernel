from classes.document_elements.document_part import DocumentPart


class PageBreak(DocumentPart):
    def add_to(self, document):
        document.add_page_break()
