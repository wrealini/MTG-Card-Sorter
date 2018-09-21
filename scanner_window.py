from guizero import Window, Text, Picture, PushButton, Slider
import scanner
import database
import cv2

last_scan = None

class ScannerWindow(Window):
    p1 = None
    p2 = None
    p3 = None
    m1 = None
    s1 = None
    s2 = None
    s3 = None
    s4 = None
    s5 = None

    def __init__(self, app):
        Window.__init__(self, app, title="Scanner", layout="grid")
        self.tk.attributes("-fullscreen", True)
        self.hide()

        # Components
        Text(self, text="Scanner", grid=[0,0,3,1])

        Text(self, text="Empty", grid=[0,1])
        p1 = Picture(self, image="data/empty.jpg", grid=[0,2])
        p1.height = 194
        p1.width = 259
        def update_empty():
            database.save_empty()
            p1.value = "data/empty.jpg"
        PushButton(self, command=update_empty, text="Retake Empty", grid=[0, 7])

        Text(self, text="Scan", grid=[1,1,2,1])
        p2 = Picture(self, image="data/testpic.jpg", grid=[1,2])
        p2.height = 194
        p2.width = 259
        p3 = Picture(self, image="data/testscan.jpg", grid=[2,2])
        p3.height = 135
        p3.width = 184
        m1 = Text(self, text="Card:", grid=[1, 6])

        def update_scan():
            global last_scan
            out = scanner.scan_card(img=last_scan)
            last_scan = out[0]
            if out[1] is not None:
                if len(out[1]) > 0:
                    cv2.drawContours(last_scan, out[1], -1, (0, 255, 0), 2)
            if out[2] is not None:
                cv2.drawContours(last_scan, [out[2]], -1, (255, 0, 0), 2)
            cv2.imwrite("data/testpic.jpg", last_scan)
            p2.value = "data/testpic.jpg"
            if out[3] is not None:
                cv2.imwrite("data/testscan.jpg", out[3])
                p3.value = "data/testscan.jpg"
                card = database.get_card(out[3])
                if card is None:
                    m1.value = "Card: Not Found"
                else:
                    m1.value = "Card: " + card.name

        def update_lower():
            scanner.lower = s1.value
            update_scan()
        s1 = Slider(self, command=update_lower, start=0, end=255, grid=[1,3])
        s1.value = scanner.lower
        s1.width = 259

        def update_upper():
            scanner.upper = s2.value
            update_scan()
        s2 = Slider(self, command=update_upper, start=0, end=255, grid=[2, 3])
        s2.value = scanner.upper
        s2.width = 259

        def update_width_min():
            scanner.width_min = s3.value
            update_scan()
        s3 = Slider(self, command=update_width_min, start=0, end=1500, grid=[1,4])
        s3.value = scanner.width_min
        s3.width = 259

        def update_width_max():
            scanner.width_max = s4.value
            update_scan()
        s4 = Slider(self, command=update_width_max, start=0, end=1500, grid=[2,4])
        s4.value = scanner.width_max
        s4.width = 259

        def update_height_min():
            scanner.height_min = s5.value
            update_scan()
        s5 = Slider(self, command=update_height_min, start=0, end=1500, grid=[1,5])
        s5.value = scanner.height_min
        s5.width = 259

        def test_scanner():
            out = scanner.scan_card()
            global last_scan
            last_scan = out[0]
            if out[1] is not None:
                if len(out[1]) > 0:
                    cv2.drawContours(last_scan, out[1], -1, (0, 255, 0), 2)
            if out[2] is not None:
               cv2.drawContours(last_scan, [out[2]], -1, (255, 0, 0), 2)
            cv2.imwrite("data/testpic.jpg", last_scan)
            p2.value = "data/testpic.jpg"
            if out[3] is not None:
                cv2.imwrite("data/testscan.jpg", out[3])
                p3.value = "data/testscan.jpg"
                card = database.get_card(out[3])
                if card is None:
                    m1.value = "Card: Not Found"
                else:
                    m1.value = "Card: " + card.name
        PushButton(self, command=test_scanner, text="Scan", grid=[1,7])

        def close_scanner():
            self.hide()
        PushButton(self, command=close_scanner, text="Exit", grid=[0,8,2,1])