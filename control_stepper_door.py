from adafruit_servokit import ServoKit
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
from evdev import InputDevice, categorize, ecodes

servos = ServoKit(channels=16)
steppers = MotorKit(address=0x61)
gamepad = InputDevice('/dev/input/event0')

cbuttons = {
    "GAMEPAD_X": 16,
    "GAMEPAD_Y": 17,
    "CARDINAL_N": 313,
    "CARDINAL_E": 312,
    "CARDINAL_S": 304,
    "CARDINAL_W": 307,
    "A": 305,
    "B": 306,
    "LEFT_SHOULDER": 308,
    "RIGHT_SHOULDER": 309,
    "START": 316,
    "TRIGGER": 310
}

############# CONFIG #############
eye_x_center = 90
eye_y_center = 90
eye_x_angle_range = 50
eye_y_angle_range = 15
neck_rotation_range = 300
neck_rotation_step = 50
head_tilt_angle_range = 45
head_tilt_center = 90
servo_eye_x = servos.servo[0]
servo_eye_y = servos.servo[1]
servo_head_tilt = servos.servo[2]
stepper_neck_rotation = steppers.stepper1

button_eyes_left = 308 # left shoulder
button_eyes_right = 309 # right shoulder
button_eyes_center = 310 # trigger
button_temp_eyes_left = 307 # left button
button_temp_eyes_right = 312 # right button
button_neck_rotate_left = 313 # up button for now
button_neck_rotate_right = 304 # down button for now
button_toggle_stepper_release = 316 # start button
button_head_tilt_forward = 306 # B button
button_head_tilt_backward = 305 # A button
##################################

for event in gamepad.read_loop():
    #filters by event type
    if event.type == ecodes.EV_KEY:
        if event.code == button_neck_rotate_left and event.value == 1:
            x = 0
            while x < 17800:
                x = x + 1
                stepper_neck_rotation.onestep(style=stepper.DOUBLE)
            stepper_neck_rotation.release()
        if event.code == button_neck_rotate_right and event.value == 1:
            x = 17800
            while x > 0:
                x = x - 1
                stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            stepper_neck_rotation.release()