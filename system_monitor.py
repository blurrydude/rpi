#! /usr/bin/env python3
import string
import time
time.sleep(30)
import paho.mqtt.client as mqtt
import json
from datetime import date, datetime
import os
import requests

file_logging = False
running = True
client = mqtt.Client()
circuits = None
motionSensors = None
doorSensors = None
ignore_from_shelly = ["temperature", "temperature_f", "overtemperature", "input", "energy","online","announce"]

def loadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)
    log('circuits')
    log(circuits)

def loadMotionSensors():
    global motionSensors
    f = open('/home/pi/rpi/motionsensors.json')
    motionSensors = json.load(f)
    log('motionSensors')
    log(motionSensors)

def loadDoorSensors():
    global doorSensors
    f = open('/home/pi/rpi/doorsensors.json')
    doorSensors = json.load(f)
    log('doorSensors')
    log(doorSensors)

def initializeMqtt():
    log('initializeMqtt')
    client.on_message = on_message
    client.connect('192.168.1.200')
    client.subscribe('shellies/#')
    client.subscribe('pi/#')
    client.loop_start()

def stopMqtt():
    client.loop_stop()
    client.disconnect()

def loop():
    time.sleep(0.1)

def on_message(client, userdata, message):
    try:
        topic = message.topic
        text = str(message.payload.decode("utf-8"))
        if "motion" in topic:
            log("MOTION")
            log(topic)
            log(text)
        handleMessage(topic, text)
    except Exception as err:
        log(err)


def handleMessage(topic, text):
    #log("handle message: "+topic+" : "+text)
    if "shellies" in topic:
        for tword in ignore_from_shelly:
            if tword in topic:
                return
    for circuit in circuits:
        if circuit["address"] in topic and "relay/"+circuit["relay"] in topic:
            if handleCircuitMessage(topic, text) is True:
                return
    for sensor in motionSensors:
        if sensor["address"] in topic:
            if handleMotionSensorMessage(sensor, text) is True:
                return
    for sensor in doorSensors:
        if sensor["address"] in topic:
            if "state" not in topic:
                return
            if handleDoorSensorMessage(sensor, text) is True:
                return
    if "pi/" in topic:
        if handlePiMessage(text) is True:
            return
    log("unhandled message:")
    log(topic)
    log(text)

def handleDoorSensorMessage(sensor, text):
    if text == "open":
        sendCommand(sensor["open_command"])
        f = "/home/pi/"+sensor["label"]+"_door.state"
        with open(f,"w") as write_file:
            write_file.write("open")
        return True
    if text == "close":
        sendCommand(sensor["close_command"])
        f = "/home/pi/"+sensor["label"]+"_door.state"
        with open(f,"w") as write_file:
            write_file.write("closed")
        return True
    return False

def handleCircuitMessage(topic, text):
    bits = topic.split('/')
    address = bits[1]
    relay = bits[3]

    if "command" not in topic:
        checkin(address)

    if "power" in topic:
        with open("/home/pi/"+address+"_"+relay+"_power.state", "w") as write_file:
            #log(address + " " + relay + " " + text)
            write_file.write(text)
            return True
    elif "energy" not in topic: # TODO: do this better
        with open("/home/pi/"+address+"_"+relay+".state", "w") as write_file:
            #log(address + " " + relay + " " + text)
            write_file.write(text)
            return True
    
    return False

def checkin(address):
    f = "/home/pi/checkins.json"
    checkins = {}
    if os.path.exists(f):
        checkins = json.load(open(f))
    checkins[address] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    with open(f, "w") as write_file:
        write_file.write(json.dumps(checkins))

def handleMotionSensorMessage(sensor, text):
    log("handle motion")
    log(sensor)
    log(text)

    checkin(sensor["address"])

    data = json.loads(text)
    if data["motion"] is True:
        log("motion detected")
        for circuit in circuits:
            if circuit["label"] == sensor["activate"]:
                log("activate: "+circuit["label"]+" @ "+circuit["address"])
                log(circuit)
                # topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                # mosquittoDo(topic,"on")
                sendCommand("turn on "+circuit["label"].lower())
                return True
    if data["motion"] is False:
        log("motion stopped")
        if sensor["auto_off"] is True:
            for circuit in circuits:
                if circuit["label"] == sensor["activate"]:
                    log("deactivate: "+circuit["label"]+" @ "+circuit["address"])
                    log(circuit)
                    # topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                    # mosquittoDo(topic,"off")
                    sendCommand("turn off "+circuit["label"].lower())
                    return True
    return False

def handlePiMessage(text):
    if "alive at" not in text:
        return True
    s = text.replace(", ", "_").replace("-", "_").replace("alive at ", "").split(" ")
    name = s[0]
    ip = s[1]
    ts = s[2]
    #log(name+" "+ip+" "+ts)
    f = open("/home/pi/pistates.json")
    pi = json.load(f)
    pi[name] = {
        "name": name,
        "ip": ip,
        "heartbeat": ts
    }
    with open("/home/pi/pistates.json", "w") as write_file:
        write_file.write(json.dumps(pi))
    return True

def sendCommand(command):
    log("sending command: "+command)
    try:
        r =requests.get('https://api.idkline.com/control/'+command)
        log(str(r.status_code))
    except:
        log('failed to send command')

def mosquittoDo(topic, command):
    global received
    global result
    try:
        retries = 5
        data = client.publish(topic,command)
        while data.is_published() is False and retries > 0:
            data = client.publish(topic,command)
            time.sleep(0.5)
            retries = retries - 1
        log("sent command "+topic+" "+command)
        log("published: "+str(data.is_published()))
    except Exception as err:
        log(err)
    return 'OK'

def log(message):
    if type(message) is not string:
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = "/home/pi/system_monitor_log_"+logfiledate+".txt"
    entry = timestamp + ": " + message + "\n"
    print(entry)
    if file_logging is True:
        if os.path.exists(logfile):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        with open(logfile, append_write) as write_file:
            write_file.write(entry)

def loadAll():
    loadCircuits()
    loadMotionSensors()
    loadDoorSensors()

if __name__ == "__main__":
    loadAll()
    initializeMqtt()
    while running is True:
        loop()
    stopMqtt()