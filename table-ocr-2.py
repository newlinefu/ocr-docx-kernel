import cv2
import numpy as np
import pytesseract
from matplotlib import pyplot as plt


def plt_imshow(title, image):
    # convert the image frame BGR to RGB color space and display it
    new_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(new_image)
    plt.title(title)
    plt.grid(False)
    plt.show()


image = cv2.imread('./test-images/table-simple-created/Screenshot_3.jpg')
result = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255,
                       cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

plt_imshow('', thresh)

# Remove horizontal lines
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
remove_horizontal = cv2.morphologyEx(thresh,
                                     cv2.MORPH_OPEN,
                                     horizontal_kernel,
                                     iterations=2)
cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

# Remove vertical lines
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
remove_vertical = cv2.morphologyEx(thresh,
                                   cv2.MORPH_OPEN,
                                   vertical_kernel,
                                   iterations=2)
cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

df = pytesseract.image_to_string(np.array(result),
                                 lang='rus',
                                 output_type=pytesseract.Output.DICT)
print(df)
