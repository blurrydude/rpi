#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import board
import neopixel

############# CONFIG #############
listentopic = "commands"
myname = "gameroompi"
broker = "192.168.1.22"
pixel_pin = board.D18
num_pixels = 83
ORDER = neopixel.GRB
##################################

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)
running = True
client = mqtt.Client()
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
    client.on_message = on_message
    client.connect(broker)
    topic = myname + '/' + listentopic
    print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        if mode <= 2:
            time.sleep(1)
        else:
            if j + 1 > 255:
                j = 0
            else:
                j = j + 1
            if mode == 3:
                fill(wheel(j))
                time.sleep(0.066)
            elif mode == 4:
                rainbow_cycle(0.001)
    client.loop_stop()
    client.disconnect()