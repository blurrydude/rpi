#! /usr/bin/env python3
import time
import paho.mqtt.client as mqtt
import json

running = True
client = mqtt.Client()
circuits = None
motionSensors = None

def loadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)

def loadMotionSensors():
    global motionSensors
    f = open('/home/pi/rpi/motionsensors.json')
    motionSensors = json.load(f)

def initializeMqtt():
    client.on_message = on_message
    client.connect('192.168.1.22')
    client.subscribe('shellies/#')
    client.subscribe('pi/#')
    client.loop_start()

def stopMqtt():
    client.loop_stop()
    client.disconnect()

def loop():
    time.sleep(1)

def on_message(client, userdata, message):
    topic = message.topic
    text = str(message.payload.decode("utf-8"))
    for circuit in circuits:
        if circuit["address"] in topic and "relay/"+circuit["relay"] in topic:
            handleCircuitMessage(topic, text)
            return
    for sensor in motionSensors:
        if sensor["address"] in topic:
            handleMotionSensorMessage(sensor, text)
            return
    if "pi/" in topic:
        handlePiMessage(text)

def handleCircuitMessage(topic, text):
    bits = topic.split('/')
    address = bits[1]
    relay = bits[3]
    if "power" in topic:
        with open("/home/pi/"+address+"_"+relay+"_power.state", "w") as write_file:
            print(address + " " + relay + " " + text)
            write_file.write(text)
    else:
        with open("/home/pi/"+address+"_"+relay+".state", "w") as write_file:
            print(address + " " + relay + " " + text)
            write_file.write(text)

def handleMotionSensorMessage(circuit, text):
    data = json.loads(text)
    if data["motion"] is True:
        print("motion detected")
        for sensor in motionSensors:
            if sensor["address"] in topic:
                print("address in topic")
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        print("label in activate_light")
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"on")
    if data["motion"] is False:
        print("motion stopped")
        for sensor in motionSensors:
            if sensor["address"] in topic and sensor["auto_off"] is True:
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"off")

def handlePiMessage(text):
    if "alive at" not in text:
        return
    s = text.replace(", ", "_").replace("-", "_").replace("alive at ", "").split(" ")
    name = s[0]
    ip = s[1]
    ts = s[2]
    print(name+" "+ip+" "+ts)
    f = open("/home/pi/pistates.json")
    pi = json.load(f)
    pi[name] = {
        "name": name,
        "ip": ip,
        "heartbeat": ts
    }
    with open("/home/pi/pistates.json", "w") as write_file:
        write_file.write(json.dumps(pi))

def mosquittoDo(topic, command):
    global received
    global result
    try:
        client.publish(topic,command)
        print("sent command "+topic+" "+command)
    except:
        print('failed')
    return 'OK'

if __name__ == "__main__":
    loadCircuits()
    loadMotionSensors()
    while running is True:
        loop()
    stopMqtt()