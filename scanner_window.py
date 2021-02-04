from guizero import Window, Text, Picture, PushButton, Slider
import scanner
import cv2
import numpy as np

#region Scanner Window Summary

# This module creates the scanner window used to set the empty tray
# image hash before each scanning session to accurately reflect the
# current lighting conditions and to adjust the camera, lighting,
# and scanner module's edge detection parameters to ensure accurate
# card artwork detection and card recognition.

# The leftmost image displays the current empty tray image and has
# a button beneath it to retake this image and set a new hash.

# The middle image displays the last scan, overlayed with the edges
# detected within the image, taken with this window and the rightmost
# image next to it displays the last detected card artwork and the
# name of the card detected below it. Beneath both of these images
# are a number of Sliders used to adjust scanner variables.

# At the bottom of the window is a Button to minimize this window.
#endregion


#region Constants and Variables

last_scan = None
#endregion

class ScannerWindow(Window):
    p1 = None
    p2 = None
    p3 = None
    m1 = None
    s1 = None
    s2 = None
    s3 = None

    CD = None

    def __init__(self, app, cd):
        Window.__init__(self, app, title="Scanner", layout="grid")
        CD = cd
        self.tk.attributes("-fullscreen", True)
        self.hide()

        # Scanner page title
        Text(self, text="Scanner", grid=[0,0,3,1])

        # Empty column 0
        Text(self, text="Empty", grid=[0,1])
        p1 = Picture(self, image="data/empty.jpg", grid=[0,2])
        p1.height = 194
        p1.width = 259
        def update_empty():
            cd.save_empty()
            p1.value = "data/empty.jpg"
        PushButton(self, command=update_empty, text="Retake Empty", grid=[0, 7])

        # Scan columns 1 & 2
        Text(self, text="Scan", grid=[1,1,2,1])
        p2 = Picture(self, image="data/testpic.jpg", grid=[1,2])
        p2.height = 194
        p2.width = 259
        p3 = Picture(self, image="data/testscan.jpg", grid=[2,2])
        p3.height = 135
        p3.width = 184
        m1 = Text(self, text="Card: Tragic Arrogance", grid=[1,3,2,1])

        # Scan parameter sliders
        def update_width_min():
            scanner.width_min = s1.value
        s1 = Slider(self, command=update_width_min, start=0, end=1500, grid=[1,4,2,1])
        s1.value = scanner.width_min
        def update_width_max():
            scanner.width_max = s2.value
        s2 = Slider(self, command=update_width_max, start=0, end=1500, grid=[1,5,2,1])
        s2.value = scanner.width_max
        def update_height_min():
            scanner.height_min = s3.value
        s3 = Slider(self, command=update_height_min, start=0, end=1500, grid=[1,6,2,1])
        s3.value = scanner.height_min

        # Scan button
        def test_scanner():
            # use scanner to scan card and set last_scan as image taken
            out = scanner.scan_card()
            global last_scan
            last_scan = out[0]

            # draw contours of left boundary and min-max width x min height box
            # in red within image dimensions 2592 x 1944
            lb = scanner.left_boundary

            hb = (1944 - scanner.height_min)/2
            ht = 1944 - hb
            wnb = (2592 - scanner.width_min)/2
            wnt = 2592 - wnb
            wxb = (2592 - scanner.width_max)/2
            wxt = 2592 - wxb
            
            red = [np.array([[[  lb,    0]],
                             [[  lb,    0]],
                             [[  lb, 1943]],
                             [[  lb, 1943]]], dtype=np.int32),
                   np.array([[[ wnb,   hb]],
                             [[ wnt,   hb]],
                             [[ wnt,   ht]],
                             [[ wnb,   ht]]], dtype=np.int32),
                   np.array([[[ wxb,   hb]],
                             [[ wxt,   hb]],
                             [[ wxt,   ht]],
                             [[ wxb,   ht]]], dtype=np.int32)]
            
            cv2.drawContours(last_scan, red, -1, (0, 0, 255), 2)

            # if any contours were detected, draw them in green
            if out[1] is not None:
                if len(out[1]) > 0:
                    cv2.drawContours(last_scan, out[1], -1, (0, 255, 0), 3)

            # if artwork contour was detected, draw it in blue
            if out[2] is not None:
                cv2.drawContours(last_scan, [out[2]], -1, (255, 0, 0), 4)

            # save last_scan
            cv2.imwrite("data/testpic.jpg", last_scan)
            p2.value = "data/testpic.jpg"

            # if artwork image was detected, save it and display the
            # corresponding card name if one is found
            if out[3] is not None:
                cv2.imwrite("data/testscan.jpg", out[3])
                p3.value = "data/testscan.jpg"
                card = CD.get_card(out[3])
                if card is None:
                    m1.value = "Card: Not Found"
                else:
                    m1.value = "Card: " + card.name
        PushButton(self, command=test_scanner, text="Scan", grid=[1,7,2,1])

        # Exit button
        def close_scanner():
            self.hide()
        PushButton(self, command=close_scanner, text="Exit", grid=[0,8,3,1])
