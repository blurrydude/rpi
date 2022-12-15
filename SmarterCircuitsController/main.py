import time
time.sleep(15)
import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit

relay_pins = [17, 27, 22, 23, 24, 25, 10, 9, 11, 8, 7, 5, 6, 12, 13, 16]
button_pins = [19, 20, 21]
dht_pin = 4
pixel_pin = 18

pointer = 0

kit = MotorKit(0x61)

def on(pin):
    GPIO.output(relay_pins[pin], GPIO.LOW)

def off(pin):
    GPIO.output(relay_pins[pin], GPIO.HIGH)

def button_callback(channel):
    print(channel)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    for pin in relay_pins:
        GPIO.setup(pin, GPIO.OUT)

    for pin in button_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    for pin in button_pins:
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=button_callback)
    try:
        for i in range(len(relay_pins)):
            off(i)
        for i in range(len(relay_pins)):
            time.sleep(2)
            on(i)
        # while True:
        #     time.sleep(2)
        #     previous = pointer - 1
        #     if previous < 0:
        #         previous = len(relay_pins) - 1
        #     pointer = pointer + 1
        #     for i in range(pointer):
        #         on(pointer)
        #         time.sleep(0.1)
        #         off(previous)
        #         time.sleep(0.1)
                
        #     if pointer >= len(relay_pins):
        #         pointer = 0
    finally:
        GPIO.cleanup()
