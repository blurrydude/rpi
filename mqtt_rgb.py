#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import board
import neopixel
import socket
import random

############# CONFIG #############
listentopic = "commands"
myname = "set later"
broker = "192.168.1.22"
pixel_pin = board.D18
num_pixels = 8
ORDER = neopixel.GRB
rainbow_cycle_delay = 0.001
##################################

myname = socket.gethostname()
current_colors = []
current_color = (0,0,0)
wait_till = time.time()

for i in range(0,num_pixels):
    current_colors.append((0,0,0))

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
    rainbow_cycle_delay = 0.05

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)
running = True
client = mqtt.Client()
mode = 0
# modes: 0-fill, 1-single pixel, 2-range, 3-gradient, 4-rainbow chase
j = 0

def mosquittoMessage(message):
    client.publish(myname+"/status",message)

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

def all_same():
    check = True
    for i in range(0,num_pixels):
        if current_colors[i] != current_color:
            check = False
    return check

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

def on_key_down(key):
    global running
    global mode
    mode = int(key)
    if mode == 0:
        fill(current_color)
    elif mode == 1:
        current_color = wheel(random.randint(1,8) * 32 - 1)
        fill(current_color)
    elif mode == 2:
        current_color = wheel(random.randint(1,8) * 32 - 1)
        fill(current_color)

def translate_name_address(a):
    if a == 0:
        return 5
    if a == 1:
        return 6
    if a == 2:
        return 7
    if a == 3:
        return 4
    if a == 4:
        return 3
    if a == 5:
        return 2
    if a == 6:
        return 1
    return 0

if __name__ == "__main__":
    client.on_message = on_message
    client.connect(broker)
    topic = myname + '/' + listentopic
    print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        now = time.time()
        if now < wait_till:
            continue
        if mode <= 2:
            wait_till = time.time() + 5.0
            #time.sleep(5)
            mosquittoMessage("alive at "+str(round(time.time())))
        elif mode == 3 or mode == 4:
            if j + 1 > 255:
                j = 0
                mosquittoMessage("alive at "+str(round(time.time())))
            else:
                j = j + 1
            if mode == 3:
                fill(wheel(j))
                wait_till = time.time() + 0.066
                continue
                #time.sleep(0.066)
            elif mode == 4:
                rainbow_cycle(rainbow_cycle_delay)
        elif mode == 5:
            r = random.randint(1,8) * 32 - 1
            a = random.randint(0, num_pixels-1)
            pixels[a] = wheel(r)
            pixels.show()
            wait_till = time.time() + 1.0
            continue
            #time.sleep(1)
        elif mode == 6:
            if all_same() is True and now < wait_till:
                original_color = current_color
                current_color = wheel(random.randint(1,8) * 32 - 1)
                while current_color == original_color:
                    current_color = wheel(random.randint(1,8) * 32 - 1)
                #time.sleep(random.randint(5,30))
                wait_till = time.time() + random.randint(5,30)
            a = random.randint(0, num_pixels-1)
            while current_colors[a] == current_color:
                a = random.randint(0, num_pixels-1)
            pixels[a] = current_color
            current_colors[a] = current_color
            pixels.show()
            #time.sleep(0.25)
            wait_till = time.time() + 0.25
            continue
        elif mode == 7:
            if all_same() is True and now < wait_till:
                original_color = current_color
                current_color = wheel(random.randint(1,8) * 32 - 1)
                while current_color == original_color:
                    current_color = wheel(random.randint(1,8) * 32 - 1)
                #time.sleep(random.randint(5,30))
                wait_till = time.time() + random.randint(5,30)
                continue
            a = 0
            while current_colors[a] == current_color:
                a = a + 1
            if a >= num_pixels:
                a = 0
            x = translate_name_address(a)
            pixels[x] = current_color
            current_colors[a] = current_color
            pixels.show()
            #time.sleep(0.1)
            wait_till = time.time() + 0.1
            continue
    client.loop_stop()
    client.disconnect()