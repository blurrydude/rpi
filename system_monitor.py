#! /usr/bin/env python3
import string
import time
time.sleep(30)
import paho.mqtt.client as mqtt
import json
from datetime import date, datetime, timedelta
import os
from os import path, read
import requests
import subprocess

file_logging = True
running = True
client = mqtt.Client()
circuits = None
motionSensors = None
doorSensors = None
thsensors = None
timeCommands = None
last_loop = time.time()
last_day = ""
sunrise = "08:00"
sunset = "21:00"
civil_twilight_end = "21:30"
civil_twilight_begin = "07:30"
ignore_from_shelly = ["temperature", "temperature_f", "overtemperature", "input", "energy","online","announce","voltage"]
last_motion = {}
shellies = {}

def loadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)
    log('circuits')
    log(circuits)

def loadTHSensors():
    global thsensors
    f = open('/home/pi/rpi/thsensors.json')
    thsensors = json.load(f)
    log('thsensors')
    log(thsensors)

def loadTimeCommands():
    global timeCommands
    f = open('/home/pi/rpi/timeCommands.json')
    timeCommands = json.load(f)
    #log('timeCommands')
    #log(timeCommands)

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
    client.on_disconnect = on_disconnect
    client.connect('192.168.2.200')
    client.subscribe('shellies/#')
    client.subscribe('pi/#')
    client.loop_start()

def stopMqtt():
    client.loop_stop()
    client.disconnect()

def loop():
    global last_loop
    global last_day
    global sunrise
    global sunset
    global civil_twilight_end
    global civil_twilight_begin
    time.sleep(0.5)
    if time.time() - last_loop >= 60:
        try:
            loadTimeCommands()
            last_loop = time.time()
            now = datetime.now().strftime("%H:%M")
            day = datetime.now().strftime("%a").lower()
            
            if day != last_day:
                last_day = day
                r = requests.get("https://api.sunrise-sunset.org/json?lat=39.68021508778703&lng=-84.17636552954109")
                j = r.json()
                sunrise = convert_suntime(j["results"]["sunrise"],False)
                sunset = convert_suntime(j["results"]["sunset"],False)
                civil_twilight_begin = convert_suntime(j["results"]["civil_twilight_begin"],False)
                civil_twilight_end = convert_suntime(j["results"]["civil_twilight_end"],False)

            # for circuit in circuits:
            #     for ontime in circuit["onTimes"]:
            #         if day not in ontime.lower():
            #             continue
            #         if time_check(now,ontime) is True:
            #             sendCommand("turn " + circuit["label"] + " on")
            #     for offtime in circuit["offTimes"]:
            #         if day not in offtime.lower():
            #             continue
            #         if time_check(now,offtime) is True:
            #             sendCommand("turn " + circuit["label"] + " off")
            
            for tc in timeCommands:
                check = tc["days_time"].lower()
                if day not in check:
                    continue
                if time_check(now,check) is True:
                    if "thermoset" in tc["command"]:
                        thermoset_command(tc["command"])
                    else:
                        sendCommand(tc["command"])
            #TODO: thread this later
            #snapshot()
        except:
            print("bad loop")

def thermoset_command(command):
    words = command.split(" ")
    room = words[1]
    field = words[2]
    value = words[3]
    f = open("/home/pi/"+room+"_thermosettings.json")
    settings = json.load(f)
    settings[field] = int(value)
    with open("/home/pi/"+room+"_thermosettings.json","w") as write_file:
        write_file.write(json.dumps(settings))
        

def time_check(now,check):
    is_sunrise = now == sunrise
    is_sunset = now == sunset
    is_civil_twilight_end = now == civil_twilight_end
    is_civil_twilight_begin = now == civil_twilight_begin
    check = check.lower()
    return now in check or (is_sunrise and "sunrise" in check) or (is_sunset and "sunset" in check) or (is_civil_twilight_end and "civil_twilight_end" in check) or (is_civil_twilight_begin and "civil_twilight_begin" in check)

def snapshot():
    try:
        snap = {
            "thermostats":{},
            "thsensors":{},
            "shellies":{},
            "doors":{},
            "shades":{}
        }
        tf = open("/home/pi/temperatures.json")
        snap["thermostats"] = json.load(tf)
        ptf = open("/home/pi/passivetemperatures.json")
        snap["thsensors"] = json.load(ptf)
        sf = open("/home/pi/shellies.json")
        snap["shellies"] = json.load(sf)
        for f in os.listdir("/home/pi"):
            if f.endswith("_door.state"):
                s = f.split('/')
                a = s[len(s)-1].split('.')[0].split('_door')
                label = a[0]
                try:
                    snap["doors"][label] = open("/home/pi/"+label+"_door.state").read().replace("\n","")
                except Exception as e:
                    log("snapshot failed doors: "+str(e))
            if f.endswith("_roller.state"):
                s = f.split('/')
                a = s[len(s)-1].split('.')[0].split('_roller')
                label = a[0]
                try:
                    snap["shades"][label] = open("/home/pi/"+label+"_roller.state").read().replace("\n","")
                except Exception as e:
                    log("snapshot failed shades: "+str(e))
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        with open("/home/pi/rpi/snapshots/"+timestamp+".json","w") as write_file:
            write_file.write(json.dumps(snap))
    except Exception as e:
        log("snapshot failed: "+str(e))

def convert_suntime(jdata, winter):
    a = jdata.split(' ')
    s = a[0].split(":")
    h = int(s[0])
    if a[1] == "AM" and h == 12:
        h = 0
    if a[1] == "PM" and h != 12:
        h = h + 12
    if winter is True:
        h = h - 5
    else:
        h = h - 4
    if h < 0:
        h = h + 24
    if h == 24:
        h = 0
    m = int(s[1])
    o = ""
    if h < 10:
        o = "0"
    o = o + str(h) + ":"
    if m < 10:
        o = o + "0"
    o = o + str(m)
    return o

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
        log("Unexpected error in on_message: "+str(err))

def shelly_log(topic,text):
    global shellies
    try:
        if path.exists("/home/pi/shellies.json") == False:
            with open("/home/pi/shellies.json","w") as write_file:
                write_file.write("{}")
        s = topic.split('/')
        addy = s[1]
        field = topic.replace("shellies/"+addy+"/","").replace("/","_")
        try:
            f = open("/home/pi/shellies.json")
            shellies = json.load(f)
        except:
            shellies = {}
        if addy not in shellies.keys():
            shellies[addy] = {}
        if "{" in text:
            try:
                shellies[addy][field] = json.loads(text)
            except:
                shellies[addy][field] = text
        else:
            shellies[addy][field] = text
        with open("/home/pi/shellies.json","w") as write_file:
            write_file.write(json.dumps(shellies))
    except Exception as err:
        log("Unexpected error in shelly_log: "+str(err))

def handleMessage(topic, text):
    #log("handle message: "+topic+" : "+text)
    if "shellyht" in topic:
        shelly_log(topic,text)
        if handleTHMessage(topic, text) is True:
            return
    if "shellies" in topic:
        for tword in ignore_from_shelly:
            if tword in topic:
                return
    for circuit in circuits:
        if circuit["address"] in topic and "relay/"+circuit["relay"] in topic:
            if handleCircuitMessage(topic, text) is True:
                shelly_log(topic,text)
                return
    for sensor in motionSensors:
        if sensor["address"] in topic:
            if handleMotionSensorMessage(sensor, text) is True:
                shelly_log(topic,text)
                return
    for sensor in doorSensors:
        if sensor["address"] in topic:
            if "state" not in topic:
                return
            if handleDoorSensorMessage(sensor, text) is True:
                shelly_log(topic,text)
                return
    if "pi/" in topic:
        if handlePiMessage(text) is True:
            return
    log("unhandled message:")
    log(topic)
    log(text)

def handleTHMessage(topic, text):
    log("handleTHMessage: "+topic+" "+text)
    try:
        s = topic.split('/')
        addy = s[1]
        label = ""
        for ths in thsensors:
            if ths["address"] == addy:
                label = ths["label"]
        if os.path.exists("/home/pi/passivetemperatures.json"):
            try:
                f = open("/home/pi/passivetemperatures.json")
                data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        data[addy]["label"] = label
        data[addy]["timestamp"] = timestamp
        if "temperature" in topic:
            data[addy]["temperature"] = text
        if "humidity" in topic:
            data[addy]["humidity"] = text
        with open("/home/pi/passivetemperatures.json","w") as write_file:
            write_file.write(json.dumps(data))
    except Exception as err:
        log("Unexpected error in handleTHMessage: "+str(err))
    return True

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
    elif "on" in text or "off" in text: # TODO: do this better
        with open("/home/pi/"+address+"_"+relay+".state", "w") as write_file:
            #log(address + " " + relay + " " + text)
            write_file.write(text)
            return True
    
    return False

def checkin(address):
    f = "/home/pi/checkins.json"
    checkins = {}
    if os.path.exists(f):
        try:
            checkins = json.load(open(f))
        except:
            checkins = {}
    checkins[address] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    with open(f, "w") as write_file:
        write_file.write(json.dumps(checkins))

def handleMotionSensorMessage(sensor, text):
    global last_motion
    checkin(sensor["address"])
    try:
        f = open("/home/pi/mode.txt")
        mode = f.read().replace("\n","")
    except:
        mode = "default"
    data = json.loads(text)
    if data["motion"] is True:
        log("motion started")
        com = "start"
        if sensor["address"] not in last_motion.keys():
            last_motion[sensor["address"]] = datetime.now()
        elif last_motion[sensor["address"]] > datetime.now() - timedelta(minutes=1):
            log("motion ignored")
            return True
        else:
            last_motion[sensor["address"]] = datetime.now()

    else:
        log("motion stopped")
        com = "stop"
    
    for command in sensor["commands"]:
        failed_conditions = False
        for condition in command["conditions"]:
            if condition["type"] == "mode_is":
                if condition["value"] != mode:
                    failed_conditions = True
            if condition["type"] == "mode_isnt":
                if condition["value"] == mode:
                    failed_conditions = True
            if "light" in condition["type"]:
                sensor = None
                for ms in motionSensors:
                    if ms["room"] == condition["device_label"]:
                        sensor = ms
                if sensor is None:
                    continue
                if "status" not in sensor.keys():
                    continue
                if "lux" not in sensor["status"].keys():
                    continue
                if ("over" in condition["type"] and int(sensor["status"]["lux"]) < int(condition["value"])) or ("under" in condition["type"] and int(sensor["status"]["lux"]) > int(condition["value"])):
                    failed_conditions = True
        if failed_conditions is not True:
            sendCommand(command[com])
    
    return True

def handlePiMessage(text):
    if "alive at" not in text:
        return True
    s = text.replace(", ", "_").replace("-", "_").replace("alive at ", "").split(" ")
    name = s[0]
    ip = s[1]
    ts = s[2]
    #log(name+" "+ip+" "+ts)
    try:
        f = open("/home/pi/pistates.json")
        pi = json.load(f)
    except:
        pi = {}
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
        log("Unexpected error in mosquittoDo: "+str(err))
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

def on_disconnect(client, userdata, rc):
    log("restarting due to MQTT disconnect")
    restart()

def restart():
    subprocess.Popen(["python3","system_monitor.py"])
    exit()

def loadAll():
    loadCircuits()
    loadMotionSensors()
    loadTHSensors()
    loadDoorSensors()

if __name__ == "__main__":
    loadAll()
    initializeMqtt()
    while running is True:
        if os.path.exists("/home/pi/killmonitor.txt"):
            os.remove("/home/pi/killmonitor.txt")
            restart()
        loop()
    stopMqtt()