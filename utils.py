import numpy as np
import pytesseract
from docx import Document
from docx.shared import Inches
from pdf2image import convert_from_path
from pytesseract import Output
import re
from PIL import Image

from classes.document_part import CreatedDocumentPart, documentPartParagraphTypes

from file_utils import is_pdf, get_secondary_image_name, get_secondary_images


def filter_img_data_empty_symbols(img_data):
    data = {
        'conf': [],
        'top': [],
        'left': [],
        'word_num': [],
        'text': [],
        'line_num': []
    }
    for i in range(len(img_data['conf'])):
        conf_value = img_data['conf'][i]
        if conf_value != -1:
            data['conf'].append(img_data['conf'][i])
            data['top'].append(img_data['top'][i])
            data['left'].append(img_data['left'][i])
            data['word_num'].append(img_data['word_num'][i])
            data['text'].append(img_data['text'][i])
            data['line_num'].append(img_data['line_num'][i])

    return data


def get_diffs_min_max(img_data):
    diffs = []
    for i in range(len(img_data['top']) - 1):
        actual_line_y = img_data['top'][i]
        next_line_y = img_data['top'][i + 1]
        diff = abs(next_line_y - actual_line_y)
        diffs.append(diff)

    max_diff = max(diffs)
    min_diff = min(diffs)

    return max_diff, min_diff


# 10
# 70
# actual - 15
# 5 >= 55

def get_is_new_line(actual_diff, max_diff, min_diff):
    return abs(actual_diff - min_diff) >= abs(max_diff - actual_diff)


def get_lines_information(img_data):
    lines_data = []

    actual_line_text = ''
    actual_line_num = -1

    actual_x = -1
    actual_x_diff = -1

    actual_y = -1

    line_index = 0

    max_diff, min_diff = get_diffs_min_max(img_data)

    for i in range(len(img_data['text'])):
        local_line_num = img_data['line_num'][i]
        is_new_line = False

        if actual_line_num == -1:
            actual_line_num = local_line_num
            actual_x = img_data['left'][i]
            actual_x_diff = 0

            actual_y = img_data['top'][i]
            is_new_line = True

        y_diff = img_data['top'][i] - actual_y
        actual_y = img_data['top'][i]
        if not is_new_line:
            is_new_line = get_is_new_line(y_diff, max_diff, min_diff)

        if local_line_num != actual_line_num or is_new_line:
            lines_data.append({
                'text': actual_line_text,
                'line_num': line_index,
                'left': actual_x,
                'diff': actual_x_diff
            })
            line_index += 1
            actual_line_text = img_data['text'][i]
            actual_line_num = local_line_num

            actual_x_diff = actual_x - img_data['left'][i]
            actual_x = img_data['left'][i]
        else:
            actual_line_text += ' ' + img_data['text'][i]

    lines_data.append({
        'text': str.strip(actual_line_text),
        'line_num': line_index,
        'left': actual_x,
        'diff': actual_x_diff
    })

    return lines_data


# note: this functions will be replaced with native
# methods of cv / tesseract

# def get_most_common_line_x_bias(lines_info):
#     common_line_bias = 1000000
#     for i in range(len(lines_info)):
#         diff = lines_info[i]['diff']
#         if diff < common_line_bias:
#             common_line_bias = diff
#
#     return common_line_bias
# def rotate_lines_coordinates(lines_info, common_line_bias):
#     if common_line_bias == 0:
#         return lines_info
#
#     for i in range(len(lines_info)):
#         bias_count = i if common_line_bias > 0 else len(lines_info) - 1 - i
#         lines_info[i]['left'] = lines_info[i]['left'] + common_line_bias * bias_count
#
#     return lines_info


def get_line_list_item(line_idx, lists_information):
    according_list_item = None
    for j in range(len(lists_information)):
        actual_list = lists_information[j]
        for k in range(len(actual_list['list_items'])):
            actual_list_item = actual_list['list_items'][k]
            if actual_list_item['start'] <= line_idx <= actual_list_item['end']:
                according_list_item = actual_list_item
    return according_list_item


def remove_list_point_from_paragraph_text(paragraph):
    if 'list_type' not in paragraph:
        return paragraph['text']

    if paragraph['list_type'] == documentPartParagraphTypes.DOT_LIST_PARAGRAPH_TYPE or \
            paragraph['list_type'] == documentPartParagraphTypes.EMPTY_DOT_LIST_PARAGRAPH_TYPE:
        return str.strip(str.strip(paragraph['text'])[1:])[1:]

    if paragraph['list_type'] == documentPartParagraphTypes.NUMBER_DOT_LIST_PARAGRAPH_TYPE:
        return str.strip(re.sub(r'^\d+\.', '', paragraph['text']))

    if paragraph['list_type'] == documentPartParagraphTypes.NUMBER_BRACKET_LIST_PARAGRAPH_TYPE:
        return str.strip(re.sub(r'^\d+\.', '', paragraph['text']))

    return paragraph['text']


def get_paragraphs(lines_info, lists_information):
    average_lines_bias = 0
    lines_count = 0
    for i in range(len(lines_info)):
        according_list_item = get_line_list_item(i, lists_information)
        if according_list_item is None:
            average_lines_bias += abs(lines_info[i]['diff'])
            lines_count += 1
    average_lines_bias /= len(lines_info)

    paragraphs = []
    actual_paragraph_index = 0
    first_paragraph = {'text': ''}

    if len(lists_information) > 0 and lists_information[0]['list_items'][0]['start'] == 0:
        first_paragraph = {'text': '', 'list_type': lists_information[0]['type']}

    paragraphs.append(first_paragraph)

    for i in range(len(lines_info)):
        according_list_item = get_line_list_item(i, lists_information)

        if according_list_item is not None:
            if according_list_item['start'] == i:
                paragraphs.append({'text': lines_info[i]['text'], 'list_type': lists_information[0]['type']})
                actual_paragraph_index += 1
            else:
                paragraphs[actual_paragraph_index]['text'] += ' ' + str.strip(lines_info[i]['text'])
        else:
            if (lines_info[i]['diff'] < 0 and abs(lines_info[i]['diff']) > average_lines_bias) or \
                    'list_type' in paragraphs[actual_paragraph_index]:
                paragraphs.append({'text': lines_info[i]['text']})
                actual_paragraph_index += 1
            else:
                paragraphs[actual_paragraph_index]['text'] += ' ' + str.strip(lines_info[i]['text'])

    for i in range(len(paragraphs)):
        new_text = remove_list_point_from_paragraph_text(paragraphs[i])
        paragraphs[i]['text'] = new_text

    return paragraphs


def get_is_list_item_head(line_text):
    if str.startswith(line_text, '®'):
        return documentPartParagraphTypes.DOT_LIST_PARAGRAPH_TYPE, True

    if str.startswith(line_text, '©'):
        return documentPartParagraphTypes.EMPTY_DOT_LIST_PARAGRAPH_TYPE, True

    if re.match(r'\s*\d+\.', line_text) is not None:
        return documentPartParagraphTypes.NUMBER_DOT_LIST_PARAGRAPH_TYPE, True

    if re.match(r'\s*\d+\)', line_text) is not None:
        return documentPartParagraphTypes.NUMBER_BRACKET_LIST_PARAGRAPH_TYPE, True

    return '', False


# list item starts with ®, ©, d+), d+. (list item head)
# list item head and next item have + bias
# list items will not have been taken

def get_is_list_continue(list_information, line_idx, lines_information):
    if len(list_information) == 0:
        return False
    last_list = list_information[len(list_information) - 1]
    last_list_last_item = last_list['list_items'][len(last_list['list_items']) - 1]
    if (last_list_last_item['start'] == line_idx - 1 and
            lines_information[line_idx]['diff'] < 0):
        return True

    if last_list_last_item['end'] == line_idx - 1:
        if line_idx != len(lines_information) - 1:
            next_text = lines_information[line_idx + 1]['text']
            _, is_list_item_head = get_is_list_item_head(next_text)
            if lines_information[line_idx + 1]['diff'] > 1 and not is_list_item_head:
                return False
        # 5 will be replaced with generic diff
        if abs(lines_information[line_idx]['diff']) <= 5:
            return True

    return False


def get_lists_items(lines_info):
    lists_information = []

    actual_list_idx = -1
    actual_list_item_idx = -1
    running_by_list = False

    for i in range(len(lines_info)):
        line = lines_info[i]
        old_running_by_list = running_by_list

        actual_list_type, is_list_item_head = get_is_list_item_head(line['text'])

        if is_list_item_head:
            actual_list_item_idx += 1
            running_by_list = True

        if not is_list_item_head:
            running_by_list = get_is_list_continue(lists_information, i, lines_info)

        if old_running_by_list != running_by_list and running_by_list:
            actual_list_idx += 1
            lists_information.append({
                'type': actual_list_type,
                'list_items': [{'start': i, 'end': i}]
            })

        if old_running_by_list == running_by_list and running_by_list:
            if is_list_item_head:
                lists_information[actual_list_idx]['list_items'].append({'start': i, 'end': i})
            else:
                lists_information[actual_list_idx]['list_items'][actual_list_item_idx]['end'] = i

    return lists_information


#     asdasdasd
# asdasdasdasda
# 1. asdasdasdad
#    asdasdasdasdasd
# 2. asdasdasdasd
# 3. asdasdasdasd
#    asdasdasdasd


def get_paragraphs_info(img):
    image_data = pytesseract.image_to_data(img, lang="eng+rus", output_type=Output.DICT)

    # remove empty symbols from result
    # 'conf' - -1 - empty string
    # 'top' - y coordinates
    # 'left' - x coordinates
    # 'word_num' - word in line index
    # 'text' - words
    # 'line_num' - line number

    # 1. Filter '' in 'text', 'word_num', 'left', 'top', 'conf'
    transformed_data = filter_img_data_empty_symbols(image_data)

    # 2. Take start lines x pos (dict: line + line number + x pos + diff relative prev)
    lines_info = get_lines_information(transformed_data)

    # 3. Find lower diff
    # common_bias = get_most_common_line_x_bias(lines_info)

    # 4. transform x pos (actual_x_pos + lower_diff * (sign_is_minus ? lines count - i : i))
    # lines_info = rotate_lines_coordinates(lines_info, common_bias)

    lists_information = get_lists_items(lines_info)

    # 5. Find nearest
    paragraphs_info = get_paragraphs(lines_info, lists_information)

    return paragraphs_info


def get_doc_structure_from_image(img_name):
    img = np.array(Image.open(img_name))

    paragraphs = get_paragraphs_info(img)
    result = []

    for i in range(len(paragraphs)):
        # todo refactor algo
        # todo add lists as paragraphs
        if 'list_type' in paragraphs[i]:
            result.append(CreatedDocumentPart(paragraphs[i]['list_type'], paragraphs[i]['text']))
        else:
            result.append(CreatedDocumentPart("paragraph", paragraphs[i]['text']))

    result.append(CreatedDocumentPart("pageBreak"))
    return result


def get_doc_structure_from_pdf(pdf_name, test_name):
    pages = convert_from_path(pdf_name, 500)
    image_counter = 1

    for page in pages:
        filename = get_secondary_image_name(test_name, image_counter)
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1

    secondary_images = get_secondary_images(test_name)
    doc_structure = []

    for secondary_image in secondary_images:
        structure_part = get_doc_structure_from_image(secondary_image)

        for j in range(len(structure_part)):
            doc_structure.append(structure_part[j])

    return doc_structure


def get_doc_structure_from_files(file_names, test_name):
    result_structure = []
    for img in file_names:
        single_structure = get_doc_structure_from_pdf(img, test_name) if is_pdf(img) else get_doc_structure_from_image(
            img)
        for part in single_structure:
            result_structure.append(part)
    return result_structure


def create_document_object(file_names, test_name):
    document = Document()
    document_structure = get_doc_structure_from_files(file_names, test_name)
    for part in document_structure:
        if part.part_type in documentPartParagraphTypes.LIST_NUMBERED_TYPES:
            paragraph_style = 'List Number'
            paragraph = document.add_paragraph(part.content, style=paragraph_style)
            paragraph.paragraph_format.first_line_indent = Inches(0.5)
        if part.part_type in documentPartParagraphTypes.LIST_BULLET_TYPES:
            paragraph_style = 'List Bullet'
            paragraph = document.add_paragraph(part.content, style=paragraph_style)
            paragraph.paragraph_format.first_line_indent = Inches(0.5)
        if part.part_type == documentPartParagraphTypes.COMMON_PARAGRAPH_TYPE:
            paragraph = document.add_paragraph(part.content)
            paragraph.paragraph_format.first_line_indent = Inches(0.5)
        elif part.part_type == documentPartParagraphTypes.PAGE_BREAK:
            document.add_page_break()

    return document


def create_document(file_names, output_file_name, test_name):
    document = create_document_object(file_names, test_name)
    document.save(output_file_name)
