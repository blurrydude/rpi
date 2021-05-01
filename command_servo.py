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
neck_rotation_range = 50
neck_rotation_step = 25
head_tilt_angle_range = 15
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

current_eye_x = eye_x_center
current_eye_y = eye_y_center

current_neck_rotation_position = 0
release_neck_stepper_after_movement = False

def center_eyes_y():
    global current_eye_y
    if current_eye_y != eye_y_center:
        current_y = eye_y_center
        servo_eye_y.angle = current_eye_y

def center_eyes_x():
    global current_eye_x
    if current_eye_x != eye_x_center:
        current_x = eye_x_center
        servo_eye_x.angle = current_eye_x

def center_eyes():
    center_eyes_x()
    center_eyes_y()

def eyes_go_left():
    center_eyes_y()
    if current_eye_x != eye_x_center + eye_x_angle_range-1:
        current_eye_x = eye_x_center + eye_x_angle_range-1
        servo_eye_x.angle = current_eye_x

def eyes_go_right():
    center_eyes_y()
    if current_eye_x != eye_x_center - eye_x_angle_range-1:
        current_eye_x = eye_x_center - eye_x_angle_range-1
        servo_eye_x.angle = current_eye_x

# def eyes_go_up():
# def eyes_go_down():
# def rotate_neck_left():
# def rotate_neck_right():
# def rotate_neck_center():
# def tilt_head_forward():
# def tilt_head_back():
# def tilt_head_left():
# def tilt_head_right():
# def level_head():
# def open_jaw():
# def close_jaw():
# def relax_brow():
# def furrow_brow():
# def curl_lips():
# def relax_lips():
# def lift_head():
# def lower_head():
# def extend_neck():
# def retract_neck():

center_eyes()

for event in gamepad.read_loop():
    #filters by event type
    if event.type == ecodes.EV_KEY:
        print("key:"+str(event.code)+" value:"+str(event.value))
        if event.code in [button_eyes_left, button_temp_eyes_left] and event.value == 1:
            eyes_go_left()

        if event.code in [button_eyes_right, button_temp_eyes_right] and event.value == 1:
            eyes_go_right()

        if event.code == button_neck_rotate_left and event.value == 1:
            target = current_neck_rotation_position + neck_rotation_step
            if target > neck_rotation_range/2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
                continue
            while current_neck_rotation_position < target:
                current_neck_rotation_position = current_neck_rotation_position + 1
                stepper_neck_rotation.onestep(style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")
        if event.code == button_neck_rotate_right and event.value == 1:
            target = current_neck_rotation_position - neck_rotation_step
            if target < neck_rotation_range/-2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
                continue
            while current_neck_rotation_position > target:
                current_neck_rotation_position = current_neck_rotation_position - 1
                stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")
        if event.code == button_head_tilt_forward and event.value == 1:
            head_tilt_position = head_tilt_center + head_tilt_angle_range
            servo_head_tilt.angle = head_tilt_position
        if event.code == button_head_tilt_backward and event.value == 1:
            head_tilt_position = head_tilt_center - head_tilt_angle_range
            servo_head_tilt.angle = head_tilt_position
        if event.code in [button_head_tilt_backward,button_head_tilt_forward] and event.value == 0:
            head_tilt_position = head_tilt_center
            servo_head_tilt.angle = head_tilt_position
        if event.code == button_eyes_center and event.value == 1 or event.code in [button_temp_eyes_left, button_temp_eyes_right] and event.value == 0: #start
            center_eyes()
        if event.code == button_toggle_stepper_release and event.value == 1:
            if release_neck_stepper_after_movement is True:
                release_neck_stepper_after_movement = False
                stepper_neck_rotation.onestep(style=stepper.DOUBLE)
                stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                print("release_neck_stepper_after_movement: False")
            else:
                release_neck_stepper_after_movement = True
                stepper_neck_rotation.release()
                print("release_neck_stepper_after_movement: True")
                print("neck stepper released")
            
    if event.type == ecodes.EV_ABS:
        print(event)
        if event.code == 0:
            percent = (event.value-128)/-127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_eye_x = percent * eye_x_angle_range + eye_x_center
            servo_eye_x.angle = current_eye_x
        if event.code == 1:
            percent = (event.value-128)/127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_eye_y = percent * eye_y_angle_range + eye_y_center
            servo_eye_y.angle = current_eye_y

        if event.code == 17 and event.value == -1: # up pressed
            head_tilt_position = head_tilt_center + head_tilt_angle_range
            servo_head_tilt.angle = head_tilt_position

        if event.code == 17 and event.value == 0: # up or down released
            head_tilt_position = head_tilt_center
            servo_head_tilt.angle = head_tilt_position

        if event.code == 17 and event.value == 1: # down pressed
            head_tilt_position = head_tilt_center - head_tilt_angle_range
            servo_head_tilt.angle = head_tilt_position

        if event.code == 16 and event.value == -1: # left pressed
            target = current_neck_rotation_position + neck_rotation_step
            if target > neck_rotation_range/2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
                continue
            while current_neck_rotation_position < target:
                current_neck_rotation_position = current_neck_rotation_position + 1
                stepper_neck_rotation.onestep(style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")

        if event.code == 16 and event.value == 0: # left or right released
            if current_neck_rotation_position > 0:
                while current_neck_rotation_position > 0:
                    current_neck_rotation_position = current_neck_rotation_position - 1
                    stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            if current_neck_rotation_position < 0:
                while current_neck_rotation_position < 0:
                    current_neck_rotation_position = current_neck_rotation_position + 1
                    stepper_neck_rotation.onestep(style=stepper.DOUBLE)

        if event.code == 16 and event.value == 1: # right pressed
            target = current_neck_rotation_position - neck_rotation_step
            if target < neck_rotation_range/-2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
                continue
            while current_neck_rotation_position > target:
                current_neck_rotation_position = current_neck_rotation_position - 1
                stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")
