from machine import Pin, PWM, I2C, RTC
from comms import Comms
from led import RGBLED
import utime

rgb = RGBLED(64, 7)
comms = Comms()

def handle_message(message):
    pixels = message.split('|')
    for pixel in pixels:
        if len(pixel) > 1:
            x = int(pixel[0])
            y = int(pixel[1])
            r = int(f"0x{pixel[2]}{pixel[3]}")
            g = int(f"0x{pixel[4]}{pixel[5]}")
            b = int(f"0x{pixel[6]}{pixel[7]}")
            v = int(f"0x{pixel[8]}{pixel[9]}") / 256
            rgb.set_pixel(x, y, (r, g, b), v)

rgb.breathing_led((255,0,0))
utime.sleep(0.5)
rgb.breathing_led((0,0,255))
utime.sleep(0.5)
rgb.breathing_led((0,255,0))
utime.sleep(0.5)

while True:
    message = comms.read().strip('\n')
    handle_message(message)
    utime.sleep(0.2)