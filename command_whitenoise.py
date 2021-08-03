#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
#from omxplayer.player import OMXPlayer
from pathlib import Path
import subprocess
import socket

myname = socket.gethostname()

running = True
client = mqtt.Client()
#player = OMXPlayer("/home/pi/Desktop/OceanWaves1.mp4")
#player.quit()

def on_message(client, userdata, message):
    #global player
    global running
    result = str(message.payload.decode("utf-8"))
    print("Received: "+result)
    if "start" in result:
        #os.system("/usr/bin/omxplayer -b -o local /home/pi/Desktop/OceanWaves1.mp4")
        #player = OMXPlayer("/home/pi/Desktop/OceanWaves1.mp4")
        #os.startfile("/home/pi/Desktop/OceanWaves1.mp4")
        subprocess.check_output("/home/pi/rpi/start_whitenoise.sh")
    elif "stop" in result:
        #player.quit()
        #os.system("killall omxplayer ")
        #os.system("killall -s 9 omxplayer ")
        subprocess.check_output("/home/pi/rpi/stop_whitenoise.sh")

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.1.200')
    topic = 'pi/' + myname + '/commands'
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(5)
    #try:
        #player.quit()
    #except:
        #print("meh")
    client.loop_stop()
    client.disconnect()