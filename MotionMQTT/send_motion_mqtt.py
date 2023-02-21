#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import datetime

client = mqtt.Client()

if __name__ == "__main__":
    client.connect('192.168.0.41')
    topic = 'camera_motion/camera_1'
    now = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    client.publish(topic,f"motion detected on camera 1 at {now}")
    client.disconnect()