from guizero import Window, Text, CheckBox, Slider, PushButton
import arm

w = None

def update():
    print("update...")
    # Adjust horizontal position.
    if arm.position != w.s1.value:
        arm.go_to(w.s1.value)
    # Adjust vertical arm.
    if w.cb1.value:
        arm.set_servo(w.s2.value)
    else:
        arm.set_servo(0)
    # Toggle vacuum on and off.
    arm.set_vacuum(w.cb2.value)
    print("done")


class TestWindow(Window):
    s1 = None
    s2 = None
    cb1 = None
    cb2 = None

    def open_window(self):
        self.show()
        self.repeat(1, update)

    def __init__(self, app):
        Window.__init__(self, app, title="Test")
        self.tk.attributes("-fullscreen", True)
        self.hide()

        # Components
        Text(self, text="Test")
        Text(self, text="Horizontal")
        self.s1 = Slider(self, start=0, end=1736)
        self.s1.width = 500
        Text(self, text="Vertical")
        self.cb1 = CheckBox(self, text="Servo On")
        self.s2 = Slider(self, start=1200, end=1950)
        self.s2.width = 500
        self.s2.value = 1950
        self.cb2 = CheckBox(self, text="Vacuum On")
        def close_window():
            self.hide()
            self.cancel(update)
            self.s1.value = 0
            self.s2.value = 1950
            self.cb1.value = 0
            self.cb2.value = 0
            arm.set_vacuum(0)
            arm.reset()
            arm.set_servo(0)
        PushButton(self, command=close_window, text="Exit")
        global w
        w = self
