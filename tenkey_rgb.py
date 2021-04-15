import keyboard

while True:
    if keyboard.read_key() == "p":
        print("You pressed p")
        break

#! /usr/bin/env python3
import time
import board
import neopixel
import socket

############# CONFIG #############
myname = "set later"
pixel_pin = board.D18
num_pixels = 83
ORDER = neopixel.GRB
rainbow_cycle_delay = 0.001
##################################

myname = socket.gethostname()

if myname == "gameroompi":
    num_pixels = 83
    rainbow_cycle_delay = 0.001
elif myname == "canvaspi":
    num_pixels = 50
    rainbow_cycle_delay = 0.001
elif myname == "clockpi":
    num_pixels = 60
    rainbow_cycle_delay = 0.001
elif myname == "windowpi":
    num_pixels = 16
    rainbow_cycle_delay = 0.001
elif myname == "namepi":
    num_pixels = 8
    rainbow_cycle_delay = 0.001

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)
mode = 0
# modes: 0-fill, 1-single pixel, 2-range, 3-gradient, 4-rainbow chase
j = 0

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def fill(color):
    pixels.fill(color)
    pixels.show()

def rainbow_cycle(wait):
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + j
        pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    time.sleep(wait)

def on_message(client, userdata, message):
    global running
    global mode
    result = str(message.payload.decode("utf-8"))
    print("Received: "+result)
    if result == "stop":
        running = False
    args = result.split(':')
    mode = int(args[0])
    if mode <= 2:
        r = int(args[1])
        g = int(args[2])
        b = int(args[3])
        if mode == 0:
            fill((r,g,b))
        elif mode == 1:
            pixels[int(args[4])] = (r,g,b)
            pixels.show()
        elif mode == 2:
            s = int(args[4])
            e = int(args[5])
            while s <= e:
                pixels[s] = (r,g,b)
                s = s + 1
            pixels.show()

if __name__ == "__main__":
    while True:
        key = keyboard.read_key()
        if key in ["0","1","2","3","4","5","6","7","8","9",".","/","*","-","+"]:
            
        if mode > 2:
            if j + 1 > 255:
                j = 0
            else:
                j = j + 1
            if mode == 3:
                fill(wheel(j))
                time.sleep(0.066)
            elif mode == 4:
                rainbow_cycle(rainbow_cycle_delay)