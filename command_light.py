#! /usr/bin/env python3
import board
import neopixel
import paho.mqtt.client as mqtt
import time
import socket
import os
import subprocess

myname = socket.gethostname()
myip = subprocess.call(['hostname', '-I'])
############# CONFIG #############
listentopic = "commands"
broker = "192.168.1.22"
led_count = 16
##################################
if myname == "windowpi":
    led_count = 16
elif myname == "clockpi":
    led_count = 60
elif myname == "canvaspi":
    led_count = 50
elif myname == "gameroompi":
    led_count = 83
elif myname == "namepi":
    num_pixels = 8
    rainbow_cycle_delay = 0.001

running = True
pixels = neopixel.NeoPixel(board.D18, led_count)
client = mqtt.Client()

bad = 0

def mosquittoMessage(message):
    global bad
    try:
        client.publish(myname+"/status",message)
    except:
        bad = bad + 1
        if bad > 10:
            os.system('sudo reboot now')

def on_message(client, userdata, message):
    global running
    global pixels
    try:
        result = str(message.payload.decode("utf-8"))
        print("Received: "+result)
        if 'stop' in result:
            running = False
            return
        chunks = result.split('|')
        for chunk in chunks:
            data = chunk.split(',')
            r = int(data[1])
            g = int(data[2])
            b = int(data[3])
            if data[0] == '*':
                for i in range(0,led_count):
                    pixels[i] = (r, g, b)
            else:
                a = int(data[0])
                pixels[a] = (r, g, b)
    except:
        print("bad")

if __name__ == "__main__":
    client.on_message = on_message
    client.connect(broker)
    topic = myname + '/' + listentopic
    print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(5)
        mosquittoMessage(str(myip)+" alive at "+str(round(time.time())))
    client.loop_stop()
    client.disconnect()