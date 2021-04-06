#! /usr/bin/env python3
import board
import neopixel
import paho.mqtt.client as mqtt
import time

############# CONFIG #############
listentopic = "commands"
myname = "windowpi"
broker = "192.168.1.22"
led_count = 16
##################################

running = True
pixels = neopixel.NeoPixel(board.D18, led_count)
client = mqtt.Client()

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
        time.sleep(1)
    client.loop_stop()
    client.disconnect()