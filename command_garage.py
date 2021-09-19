#! /usr/bin/env python3
import time
time.sleep(15)
import paho.mqtt.client as mqtt
import pifacedigitalio as p
import subprocess
import socket
import requests
import json

myname = socket.gethostname()
myip = subprocess.check_output(['hostname', '-I'])

dooropen = [False,False]
running = True
client = mqtt.Client()

p.digital_read()

def openDoor(bay):
    global dooropen
#    if dooropen[bay] == True:
#        return 'NO'
    p.digital_write(bay,1)
    time.sleep(1)
    p.digital_write(bay,0)
    return True

def closeDoor(bay):
    global dooropen
#    if dooropen[bay] == False:
#        return 'NO'
    p.digital_write(bay,1)
    time.sleep(1)
    p.digital_write(bay,0)
    return True

def on_disconnect(client, userdata, rc):
    subprocess.Popen(["python3","roller.py"])
    exit()

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    #print("Received: "+result)
    bits = result.split(':')
    addy = int(bits[0])
    if addy == 0:
        door = "Garage"
    else:
        door = "Shop"
    # TODO: remove checks and sendReport when additional sensors arrive
    if bits[1] == '1':
        check = openDoor(addy)
        if check is True:
            sendReport(door,"open")
    else:
        check = closeDoor(addy)
        if check is True:
            sendReport(door,"closed")
    #print(check)

def sendReport(door, state):
    try:
        r =requests.get('https://api.idkline.com/reportdoor/'+door+"-"+state)
    except:
        print('failed to send command')

if __name__ == "__main__":
    p.init()
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect('192.168.1.200')
    topic = 'pi/' + myname + '/commands'
    #print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        bay_1_open = str(p.digital_read(0)) == "1"
        bay_0_open = str(p.digital_read(1)) == "1"
        if dooropen[0] != bay_0_open or dooropen[0] != bay_1_open:
            dooropen = [bay_0_open,bay_1_open]
            client.publish("smarter_circuits/baydoors",json.dumps(dooropen))
        time.sleep(1)
    client.loop_stop()
    client.disconnect()