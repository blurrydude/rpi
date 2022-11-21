#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import datetime

client = mqtt.Client()

last_message = None

def on_message(client, userdata, message):
    global last_message
    result = str(message.payload.decode("utf-8"))
    print("Received: "+result)
    last_message = result
    
def failure_detected():
    print('Detected MQTT failure. Sending power cycle command and waiting two minutes.')
    time.sleep(120)

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.2.200')
    topic = 'test'
    client.subscribe(topic)
    client.loop_start()
    running = True
    while running is True:
        now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        print("Sending: "+now)
        client.publish(topic,now)
        time.sleep(2)
        if last_message is not None and last_message != now:
            failure_detected()
        time.sleep(8)
        
    client.loop_stop()
    client.disconnect()