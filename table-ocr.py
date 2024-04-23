from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from tabulate import tabulate
import pandas as pd
import numpy as np
import pytesseract
from pytesseract import Output
import imutils
import cv2


def plt_imshow(title, image):
    # convert the image frame BGR to RGB color space and display it
    new_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(new_image)
    plt.title(title)
    plt.grid(False)
    plt.show()


np.random.seed(42)
image = cv2.imread('./test-images/table-simple-created/Screenshot_3.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (51, 11))
gray = cv2.GaussianBlur(gray, (3, 3), 0)
blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
grad = np.absolute(grad)
(minVal, maxVal) = (np.min(grad), np.max(grad))
grad = (grad - minVal) / (maxVal - minVal)
grad = (grad * 255).astype("uint8")

# apply a closing operation using the rectangular kernel to close gaps in between characters,
# apply Otsu's thresholding method, and finally a dilation operation to enlarge foreground regions
grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, kernel)
thresh = cv2.threshold(grad, 0, 255,
                       cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
thresh = cv2.dilate(thresh, None, iterations=3)
# plt_imshow("Thresh", thresh)

# --------------------------------------------------------------------

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
tableCnt = max(cnts, key=cv2.contourArea)

# compute the bounding box coordinates of the stats table and extract
# the table from the input image
(x, y, w, h) = cv2.boundingRect(tableCnt)
table = image[y:y + h, x:x + w]

# show the original input image and extracted table to our screen
plt_imshow("Input", image)
plt_imshow("Table", table)

# -----------------------------------------------------------------------

# Set the PSM mode to detect sparse text, and then localize text in the table
results = pytesseract.image_to_data(
    cv2.cvtColor(table, cv2.COLOR_BGR2RGB),
    lang="eng+rus",
    output_type=Output.DICT)

# Initialize a list to store the (x, y)-coordinates of the detected text along with the OCR'd text itself
coords = []
ocrText = []

# loop over each of the individual text localizations
for i in range(0, len(results["text"])):
    # extract the bounding box coordinates of the text region from
    # the current result
    x = results["left"][i]
    y = results["top"][i]
    w = results["width"][i]
    h = results["height"][i]

    # extract the OCR text itself along with the confidence of the
    # text localization
    text = results["text"][i]
    conf = int(float(results["conf"][i]))

    # filter out weak confidence text localizations
    if conf > 0:
        # update our text bounding box coordinates and OCR'd text,
        # respectively
        coords.append((x, y, w, h))
        ocrText.append(text)

# Extract all x-coordinates from the text bounding boxes, setting the y-coordinate value to zero
xCoords = [(c[0], 0) for c in coords]

# Apply hierarchical agglomerative clustering to the coordinates
clustering = AgglomerativeClustering(
    n_clusters=None,
    affinity="manhattan",
    linkage="complete",
    distance_threshold=25.0)
clustering.fit(xCoords)

# Initialize our list of sorted clusters
sortedClusters = []

# loop over all clusters
for l in np.unique(clustering.labels_):
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]

    # verify that the cluster is sufficiently large
    if len(idxs) > 2:
        # compute the average x-coordinate value of the cluster and
        # update our clusters list with the current label and the
        # average x-coordinate
        avg = np.average([coords[i][0] for i in idxs])
        sortedClusters.append((l, avg))

# sort the clusters by their average x-coordinate and initialize our
# data frame
sortedClusters.sort(key=lambda c: c[1])
df = pd.DataFrame()

# loop over the clusters again, this time in sorted order
for (l, _) in sortedClusters:
    # extract the indexes for the coordinates belonging to the
    # current cluster
    idxs = np.where(clustering.labels_ == l)[0]

    # extract the y-coordinates from the elements in the current
    # cluster, then sort them from top-to-bottom
    yCoords = [coords[i][1] for i in idxs]
    sortedIdxs = idxs[np.argsort(yCoords)]

    # generate a random color for the cluster
    color = np.random.randint(0, 255, size=(3,), dtype="int")
    color = [int(c) for c in color]

    # loop over the sorted indexes
    for i in sortedIdxs:
        # extract the text bounding box coordinates and draw the
        # bounding box surrounding the current element
        (x, y, w, h) = coords[i]
        cv2.rectangle(table, (x, y), (x + w, y + h), color, 2)

    # extract the OCR'd text for the current column, then construct
    # a data frame for the data where the first entry in our column
    # serves as the header
    cols = [ocrText[i].strip() for i in sortedIdxs]
    currentDF = pd.DataFrame({cols[0]: cols[1:]})

    # concatenate *original* data frame with the *current* data
    # frame (we do this to handle columns that may have a varying
    # number of rows)
    df = pd.concat([df, currentDF], axis=1)

df.fillna("", inplace=True)
print(tabulate(df, headers="keys", tablefmt="psql"))
