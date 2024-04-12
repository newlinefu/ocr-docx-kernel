COMMON_PARAGRAPH_TYPE = 'paragraph'
DOT_LIST_PARAGRAPH_TYPE = 'dot_list_paragraph'
EMPTY_DOT_LIST_PARAGRAPH_TYPE = 'empty_dot_list_paragraph'
NUMBER_DOT_LIST_PARAGRAPH_TYPE = 'number_dot_list_paragraph'
NUMBER_BRACKET_LIST_PARAGRAPH_TYPE = 'number_bracket_paragraph'
PAGE_BREAK = 'pageBreak'

LIST_TYPES = [
    DOT_LIST_PARAGRAPH_TYPE,
    EMPTY_DOT_LIST_PARAGRAPH_TYPE,
    NUMBER_DOT_LIST_PARAGRAPH_TYPE,
    NUMBER_BRACKET_LIST_PARAGRAPH_TYPE
]

LIST_NUMBERED_TYPES = [
    NUMBER_DOT_LIST_PARAGRAPH_TYPE,
    NUMBER_BRACKET_LIST_PARAGRAPH_TYPE
]

LIST_BULLET_TYPES = [
    DOT_LIST_PARAGRAPH_TYPE,
    EMPTY_DOT_LIST_PARAGRAPH_TYPE
]


class DocumentPartParagraphTypes:
    def __init__(self):
        self.COMMON_PARAGRAPH_TYPE = COMMON_PARAGRAPH_TYPE
        self.DOT_LIST_PARAGRAPH_TYPE = DOT_LIST_PARAGRAPH_TYPE
        self.EMPTY_DOT_LIST_PARAGRAPH_TYPE = EMPTY_DOT_LIST_PARAGRAPH_TYPE
        self.NUMBER_DOT_LIST_PARAGRAPH_TYPE = NUMBER_DOT_LIST_PARAGRAPH_TYPE
        self.NUMBER_BRACKET_LIST_PARAGRAPH_TYPE = NUMBER_BRACKET_LIST_PARAGRAPH_TYPE
        self.LIST_TYPES = LIST_TYPES
        self.LIST_NUMBERED_TYPES = LIST_NUMBERED_TYPES
        self.LIST_BULLET_TYPES = LIST_BULLET_TYPES
        self.PAGE_BREAK = PAGE_BREAK


class CreatedDocumentPart:
    def __init__(self, part_type, content=''):
        self.part_type = part_type
        self.content = content


documentPartParagraphTypes = DocumentPartParagraphTypes()