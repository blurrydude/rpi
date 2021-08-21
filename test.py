from typing import Tuple
import RPi.GPIO as GPIO

BEAM_PIN_L = 21
BEAM_PIN_R = 20
first = "none"

def break_beam_callback(channel):
    left = GPIO.input(BEAM_PIN_L)
    right = GPIO.input(BEAM_PIN_R)
    print(str(left)+" "+str(right))
    if left == 1:
        print("left beam unbroken")
    elif left == 0:
        print("left beam broken")
    if right == 1:
        print("right beam unbroken")
    elif right == 0:
        print("right beam broken")

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BEAM_PIN_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BEAM_PIN_L, GPIO.BOTH, callback=break_beam_callback)
GPIO.add_event_detect(BEAM_PIN_R, GPIO.BOTH, callback=break_beam_callback)

message = input("Press enter to quit\n\n")
GPIO.cleanup()