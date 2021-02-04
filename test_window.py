from guizero import Window, Text, CheckBox, Slider, PushButton
import arm

#region Test Window Summary

# This module creates the test window used to test this device's arm.

# The leftmost image displays the current empty tray image and has
# a button beneath it to retake this image and set a new hash.

# Sliders are used to adjust the arm's horizontal and vertical
# positions, and CheckBoxes are used to activate and deactivate
# the servo that controls the vertical position and the vacuum
# pump used to pick up cards.

# At the bottom of the window is a Button to minimize this window.
#endregion


#region Constants and Variables

w = None
#endregion

#region Fundamental Functions

def update():
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
#endregion

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
        self.s2 = Slider(self, start=1000, end=2000)
        self.s2.width = 500
        self.s2.value = 2000
        self.cb2 = CheckBox(self, text="Vacuum On")
        def close_window():
            self.hide()
            self.cancel(update)
            self.s1.value = 0
            self.s2.value = 2000
            self.cb1.value = 0
            self.cb2.value = 0
            arm.set_vacuum(0)
            arm.reset()
            arm.set_servo(0)
        PushButton(self, command=close_window, text="Exit")
        global w
        w = self
