from adafruit_servokit import ServoKit
import time
from evdev import InputDevice, categorize, ecodes

kit = ServoKit(channels=16)
gamepad = InputDevice('/dev/input/event0')

center = 90
angle_range = 45

kit.servo[0].angle = center
kit.servo[1].angle = center
current_x = center
current_y = center

for event in gamepad.read_loop():
    #filters by event type
    if event.type == ecodes.EV_KEY:
        print(event)
        # if event.code == 288 and event.value == 1: #Y
        #     all(0.25 * direction)
        # if event.code == 289 and event.value == 1: #B
        #     allStop()
        # if event.code == 290 and event.value == 1: #A
        #     all(0.5 * direction)
        # if event.code == 291 and event.value == 1: #X
        #     all(1.0 * direction)
        if event.code == 308 and event.value == 1: #left shoulder
            if current_y != center:
                curreny_y = center
                kit.servo[1].angle = current_y
            if current_x < center + angle_range:
                current_x = center + angle_range-1
                kit.servo[0].angle = current_x
        #     crabLeft()
        if event.code == 309 and event.value == 1: #right shoulder
            if current_y != center:
                curreny_y = center
                kit.servo[1].angle = current_y
            if current_x < center - angle_range:
                current_x = center - angle_range-1
                kit.servo[0].angle = current_x
        #     crabRight()
        # if event.code == 294 and event.value == 1: #left trigger
        #     rotateLeft()
        # if event.code == 295 and event.value == 1: #right trigger
        #     rotateRight()
        # if event.code == 292 and event.value == 0: #left shoulder release
        #     allStop()
        # if event.code == 293 and event.value == 0: #right shoulder release
        #     allStop()
        # if event.code == 294 and event.value == 0: #left trigger release
        #     allStop()
        # if event.code == 295 and event.value == 0: #right trigger release
        #     allStop()
        # if event.code == 296 and event.value == 1: #select
        #     trimRudderLeft()
        # if event.code == 297 and event.value == 1: #start
        #     trimRudderRight()
            
            
    if event.type == ecodes.EV_ABS:
        #print(event)
        if event.code == 0:
            percent = (event.value-128)/127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_x = percent * angle_range + center
            kit.servo[0].angle = current_x
        if event.code == 1:
            percent = (event.value-128)/127
            if percent > 1.0:
                percent = 1.0
            if percent < -1.0:
                percent = -1.0
            current_y = percent * angle_range + center
            kit.servo[1].angle = current_y
            