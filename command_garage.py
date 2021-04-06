#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import pifacedigitalio as p

############# CONFIG #############
listentopic = "commands"
myname = "garagepi"
broker = "192.168.1.22"
##################################

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
    return 'OK'

def closeDoor(bay):
    global dooropen
#    if dooropen[bay] == False:
#        return 'NO'
    p.digital_write(bay,1)
    time.sleep(1)
    p.digital_write(bay,0)
    dooropen[bay] = False
    return 'OK'

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    print("Received: "+result)
    bits = result.split(':')
    addy = int(bits[0])
    if bits[1] == '1':
        check = openDoor(addy)
    else:
        check = closeDoor(addy)
    print(check)

if __name__ == "__main__":
    p.init()
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