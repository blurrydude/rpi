#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
#from omxplayer.player import OMXPlayer
from pathlib import Path
#import os
import subprocess

############# CONFIG #############
listentopic = "commands"
myname = "whitenoisepi"
broker = "192.168.1.22"
##################################

running = True
client = mqtt.Client()
#player = OMXPlayer("/home/pi/Desktop/OceanWaves1.mp4")
#player.quit()

def mosquittoMessage(message):
    client.publish(myname+"/status",message)

def on_message(client, userdata, message):
    #global player
    global running
    result = str(message.payload.decode("utf-8"))
    print("Received: "+result)
    if "start" in result:
        #os.system("/usr/bin/omxplayer -b -o local /home/pi/Desktop/OceanWaves1.mp4")
        #player = OMXPlayer("/home/pi/Desktop/OceanWaves1.mp4")
        #os.startfile("/home/pi/Desktop/OceanWaves1.mp4")
        subprocess.call("/usr/bin/omxplayer -b -o local /home/pi/Desktop/OceanWaves1.mp4")
    elif "stop" in result:
        #player.quit()
        #os.system("killall omxplayer ")
        #os.system("killall -s 9 omxplayer ")
        subprocess.call("killall omxplayer ")

if __name__ == "__main__":
    client.on_message = on_message
    client.connect(broker)
    topic = myname + '/' + listentopic
    mosquittoMessage('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(5)
        mosquittoMessage("alive at "+str(round(time.time())))
    #try:
        #player.quit()
    #except:
        #print("meh")
    client.loop_stop()
    client.disconnect()