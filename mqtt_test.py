#! /usr/bin/env python3
import json
import paho.mqtt.client as mqtt
import time
import datetime

client = mqtt.Client()

last_message = None
rooms = {}

def on_message(client, userdata, message):
    global last_message
    global rooms
    result = str(message.payload.decode("utf-8"))
    topic = message.topic.split('/')
    room = topic[2]
    data = json.loads(result)
    if topic[1] == 'sensors':
        temp = data['temp']
        hum = data['hum']
    else:
        temp = data['state']['temperature']
        hum = data['state']['humidity']
    rooms[room] = {
        "temp":temp, "hum": hum
    }
    myFile = open("sensor_states.txt", "w")
    for rm in rooms:
        myFile.write(rm+ ': ' + str(round(rooms[rm]['temp'],2)) + ' ' + str(round(rooms[rm]['hum'],2)) + '\n')
    myFile.close()
    last_message = result
    
def failure_detected():
    print('Detected MQTT failure. Sending power cycle command and waiting two minutes.')
    time.sleep(120)

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.2.200')
    client.subscribe('smarter_circuits/sensors/#')
    client.subscribe('smarter_circuits/thermostats/#')
    client.loop_start()
    running = True
    while running is True:
        # pass
        # now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        # print("Sending: "+now)
        # client.publish(topic,now)
        # time.sleep(2)
        # if last_message is not None and last_message != now:
        #     failure_detected()
        time.sleep(8)
        
    client.loop_stop()
    client.disconnect()