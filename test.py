from typing import Tuple
import RPi.GPIO as GPIO

BEAM_PIN_L = 21
BEAM_PIN_R = 20
seq = ""
occupants = 0

def break_beam_callback(channel):
    global seq
    global occupants
    left = GPIO.input(BEAM_PIN_L)
    right = GPIO.input(BEAM_PIN_R)
    seq = seq + str(left)+str(right)
    if seq == "10000111":
        seq = ""
        occupants = occupants + 1
    elif seq == "01001011":
        seq = ""
        occupants = occupants - 1
        if occupants < 0:
            occupants = 0
    elif len(seq) > 8:
        seq = ""
    print(str(occupants))

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BEAM_PIN_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BEAM_PIN_L, GPIO.BOTH, callback=break_beam_callback)
GPIO.add_event_detect(BEAM_PIN_R, GPIO.BOTH, callback=break_beam_callback)

message = input("Press enter to quit\n\n")
GPIO.cleanup()