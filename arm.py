import RPi.GPIO as GPIO
from time import sleep
from os import system
import pigpio
import numpy

#region Arm Summary

# This module controls the robotic arm of the card sorter.

# This arm moves horizontally utilizing a stepper motor
# and vertically utilizing a servo motor. The arm picks up
# cards one at a time utilizing a vacuum pump.

# This arm moves 1 inch in 157 steps.

# The suction cup on this arm reaches its highest point at
# PWM 1650 and its lowest point at PWM 1100. It moves 4/16
# of an inch forward when descending from PWM 1650 to 1550
# and 4/16 of an inch backward when descending from PWM
# 1550 to 1100.
#endregion


#region Constants and Variables

step_time = 0.005
position = 0
#endregion

#region Fundamental Functions

def set_step(w1, w2, w3, w4):
    GPIO.output(36, w1)
    GPIO.output(35, w2)
    GPIO.output(38, w3)
    GPIO.output(40, w4)

def step_forward():
    global position
    set_step(1, 0, 1, 0)
    sleep(step_time)
    set_step(0, 1, 1, 0)
    sleep(step_time)
    set_step(0, 1, 0, 1)
    sleep(step_time)
    set_step(1, 0, 0, 1)
    sleep(step_time)
    position += 1

def step_backward():
    global position
    set_step(1, 0, 0, 1)
    sleep(step_time)
    set_step(0, 1, 0, 1)
    sleep(step_time)
    set_step(0, 1, 1, 0)
    sleep(step_time)
    set_step(1, 0, 1, 0)
    sleep(step_time)
    position -= 1

def set_servo(pos):
    pi.set_servo_pulsewidth(13, pos)

def set_vacuum(on):
    GPIO.output(22, on)
#endregion

#region Basic Functions

def reset():
    global position
    set_vacuum(0)
    set_servo(2000)
    while GPIO.input(29):
        step_backward()
    step_forward()
    set_step(0, 0, 0, 0)
    position = 0

def forward(steps):
    global position
    for n in range(steps):
        step_forward()
        if position > 1730:
            break
    set_step(0, 0, 0, 0)

def backward(steps):
    global position
    for n in range(steps):
        step_backward()
        if not GPIO.input(29):
            step_forward()
            position = 0
            break
    set_step(0, 0, 0, 0)
            
#endregion

#region Complex Functions

def go_to(pos):
    global position
    if position < pos:
        forward(pos - position)
    if position > pos:
        backward(position - pos)

def move_card(start, finish):
    if finish is not 1 and finish is not 2 and finish is not 3 and finish is not 4:
        return None

    if start is 1:
        go_to(230)
    elif start is 2:
        go_to(730)
    elif start is 3:
        go_to(1230)
    elif start is 4:
        go_to(1730)
    else:
        return None

    m = 1930
    e = 600
    p = 440
    for n in range(e):
        set_servo(m - n)
        sleep(0.0025)
        if GPIO.input(18):
            e = n
            print(m - e - p)
            if((m - e - p) < 1000):
                set_servo(1000)
            else:
                set_servo(m - e - p)
            break
    set_vacuum(1)
    sleep(6)
    for n in range(e + p):
        set_servo(m - e - p + n)
        sleep(0.005)
        if n > p and n % 12 == 0:
            backward(1)
            
    b = -20
    if finish is 1:
        go_to(230+b)
    elif finish is 2:
        go_to(730+b)
    elif finish is 3:
        go_to(1230+b)
    elif finish is 4:
        go_to(1730+b)
    
    for n in range(150):
        set_servo(m-n)
        sleep(0.005)
    set_vacuum(0)
    sleep(3)

    reset()
#endregion

#region Initialization

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# Setup position reset switch input.
GPIO.setup(29, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
# Setup horizontal stepper motor outputs.
GPIO.setup(36, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)
set_step(0, 0, 0, 0)
# Setup vacuum pump motor output.
GPIO.setup(22, GPIO.OUT)
set_vacuum(0)
# Setup vertical arm touch sensor.
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
# Setup vertical servo motor PWM output.
system("sudo killall pigpiod")
sleep(3)
system("sudo pigpiod")
sleep(3)
pi = pigpio.pi()
# Reset arm and turn off servo motor, going idle.
reset()
set_servo(0)
#endregion
