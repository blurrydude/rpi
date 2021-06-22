#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
#from omxplayer.player import OMXPlayer
from pathlib import Path
import os
import subprocess
import subprocess

myip = subprocess.check_output(['hostname', '-I'])
############# CONFIG #############
listentopic = "commands"
myname = "whitenoisepi"
broker = "192.168.1.22"
##################################

running = True
client = mqtt.Client()
#player = OMXPlayer("/home/pi/Desktop/OceanWaves1.mp4")
#player.quit()

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
    client.connect(broker)
    topic = myname + '/' + listentopic
    mosquittoMessage('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(5)
        mosquittoMessage(str(myip).split(' ')[1].replace("b'","")++" alive at "+str(round(time.time())))
    #try:
        #player.quit()
    #except:
        #print("meh")
    client.loop_stop()
    client.disconnect()