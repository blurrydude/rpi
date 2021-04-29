from adafruit_servokit import ServoKit
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
from evdev import InputDevice, categorize, ecodes

servos = ServoKit(channels=16)
steppers = MotorKit(address=0x61)
gamepad = InputDevice('/dev/input/event0')

############# CONFIG #############
eye_x_center = 90
eye_y_center = 90
eye_x_angle_range = 50
eye_y_angle_range = 35
neck_rotation_range = 100
neck_rotation_step = 20
servo_eye_x = servos.servo[0]
servo_eye_y = servos.servo[1]
stepper_neck_rotation = steppers.stepper1
button_eyes_left = 308 # left shoulder
button_eyes_right = 309 # right shoulder
button_eyes_center = 316 # start button
button_temp_eyes_left = 307 # left button
button_temp_eyes_right = 312 # right button
button_neck_rotate_left = 313 # up button for now
button_neck_rotate_right = 304 # down button for now
##################################

current_eye_x = eye_x_center
current_eye_y = eye_y_center

current_neck_rotation_position = 0
release_neck_stepper_after_movement = True

def center_eyes():
    current_eye_x = eye_x_center
    current_eye_y = eye_y_center
    servo_eye_x.angle = current_eye_x
    servo_eye_y.angle = current_eye_y

center_eyes()

for event in gamepad.read_loop():
    #filters by event type
    if event.type == ecodes.EV_KEY:
        print("key:"+str(event.code)+" value:"+event.value)
        if event.code in [button_eyes_left, button_temp_eyes_left] and event.value == 1:
            if current_eye_y != eye_y_center:
                curreny_y = eye_y_center
                servo_eye_y.angle = current_eye_y
            if current_eye_x != eye_x_center + angle_range:
                current_eye_x = eye_x_center + angle_range-1
                servo_eye_x.angle = current_eye_x
        if event.code in [button_eyes_right, button_temp_eyes_right] and event.value == 1:
            if current_eye_y != eye_y_center:
                curreny_y = eye_y_center
                servo_eye_y.angle = current_eye_y
            if current_eye_x != eye_x_center - angle_range:
                current_eye_x = eye_x_center - angle_range-1
                servo_eye_x.angle = current_eye_x
        if event.code in [313] and event.value == 1:
            target = current_neck_rotation_position + neck_rotation_step
            if target > neck_rotation_range/2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
                return
            while current_neck_rotation_position < target:
                current_neck_rotation_position = current_neck_rotation_position + 1
                stepper_neck_rotation.onestep(style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")
        #     crabLeft()
        if event.code in [304] and event.value == 1:
            target = current_neck_rotation_position - neck_rotation_step
            if target < neck_rotation_range/-2:
                print("neck_rotation_range limit: +/- "+str(neck_rotation_range/2))
            while current_neck_rotation_position > target:
                current_neck_rotation_position = current_neck_rotation_position - 1
                stepper_neck_rotation.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print("current_neck_rotation_position: "+str(current_neck_rotation_position))
            if release_neck_stepper_after_movement is True:
                stepper_neck_rotation.release()
                print("neck stepper released")
        if event.code == button_eyes_center and event.value == 1 or event.code in [button_temp_eyes_left, button_temp_eyes_right] and event.value == 0: #start
            center_eyes()
            
            
    if event.type == ecodes.EV_ABS:
        #print(event)
        if event.code == 0:
            percent = (event.value-128)/-127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_eye_x = percent * angle_range + eye_x_center
            servo_eye_x.angle = current_eye_x
        if event.code == 1:
            percent = (event.value-128)/127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_eye_y = percent * angle_range + eye_y_center
            servo_eye_y.angle = current_eye_y
