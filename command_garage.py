#! /usr/bin/env python3
import time
time.sleep(15)
import paho.mqtt.client as mqtt
import pifacedigitalio as p
import subprocess
import socket
import requests

myname = socket.gethostname()
myip = subprocess.check_output(['hostname', '-I'])

dooropen = [False,False]
running = True
client = mqtt.Client()

def openDoor(bay):
    global dooropen
#    if dooropen[bay] == True:
#        return 'NO'
    p.digital_write(bay,1)
    time.sleep(1)
    p.digital_write(bay,0)
    dooropen[bay] = True
    return True

def closeDoor(bay):
    global dooropen
#    if dooropen[bay] == False:
#        return 'NO'
    p.digital_write(bay,1)
    time.sleep(1)
    p.digital_write(bay,0)
    dooropen[bay] = False
    return True

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
    client.connect('192.168.1.22')
    topic = 'pi/' + myname + '/commands'
    #print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()