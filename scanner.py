import imutils
import io
import picamera
import cv2
import numpy as np
import math
import sys

#region Scanner Summary

# This module uses the picamera to take pictures and then uses
# OpenCV to find the four flat edges around each card's artwork
# to isolate this artwork and warp the image, producing a 135
# by 184 pixel image of each card's artwork. This image can then
# be used with the Card Database module to find a matching card.
#endregion

#region Constants and Variables

threshhold    =  127

left_boundary = 1248

height_min    = 1080
width_min     =  800
width_max     = 1130
#endregion

#region Basic Functions

def scan_card():
    img = None
    cont = None
    dc = None

    # take picture up to 8 times until drawing contours are recognized
    for t in range(8):
        sys.stdout.write('.')
        img = take_picture()
        cont = get_contours(img)
        cont.extend(get_contours(cv2.bitwise_not(img)))

        # find drawing countour that fits height and width ranges
        dc = None
        for c in cont:
            widtha  = math.fabs(c[3][0][0] - c[0][0][0])
            widthb  = math.fabs(c[1][0][0] - c[0][0][0])
            heighta = math.fabs(c[1][0][1] - c[0][0][1])
            heightb = math.fabs(c[3][0][1] - c[0][0][1])
            if heighta > height_min and width_max > widtha > width_min:
                dc = c
                break
            elif heightb > height_min and width_max > widthb > width_min:
                dc = c
                break

        if dc is not None:
            # apply the four point transform to obtain top-down
            # views of the original drawing image and resize
            dimg = four_point_transform(img, dc.reshape(4, 2))
            dimg = cv2.resize(dimg, (135, 184))

            # rotate clockwise if drawing is on the left
            # or counterclockwise if drawing is on the right
            # to set drawing image upright
            angle = 270
            for x in dc:
                if x[0][0] < left_boundary:
                    angle = 90
                    break
            dimg = imutils.rotate_bound(dimg, angle)

            # return picture, all contours, drawing contour, and drawing image
            print('.')
            return [img, cont, dc, dimg]

    # return picture and all contours
    print('.')
    return [img, cont, None, None]

def take_picture():
    # Create a memory stream
    stream = io.BytesIO()

    # Initialize camera and take picture
    with picamera.PiCamera() as camera:
        camera.resolution = (2592, 1944)
        camera.capture(stream, format='jpeg')

    # Convert the picture into a numpy array
    buff = np.fromstring(stream.getvalue(), dtype=np.uint8)

    # Return decoded image
    return cv2.imdecode(buff, 1)
#endregion

#region Complex Functions

def get_contours(image):
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # equalize histogram to improve contrast
    gray = cv2.equalizeHist(gray)

    # apply midpoint threshold
    ret, thresh = cv2.threshold(gray, threshhold, 255, 0)

    # find the contours, keeping only the largest ones
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

    # make empty output list and loop over the contours
    output = []
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)

        # if our approximated contour has four points,
        # add it to the list of outputs
        if len(approx) == 4:
            output.append(approx)

    return output

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect
#endregion
