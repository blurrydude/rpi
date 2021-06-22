import subprocess
import paho.mqtt.client as mqtt
import time
import datetime
import socket
import json
import os

myname = socket.gethostname()
myip = subprocess.check_output(["hostname","-I"])
############# CONFIG #############
broker = "192.168.1.22"
##################################
client = mqtt.Client()
bad = 0

circuits = {
    "fireplace": {"id": "fireplace", "address": "shelly1pm-8CAAB574C489", "relay":"0"     , "label":"Fireplace", "last_update": 0}, #192.168.1.60 - Fireplace Lights
    "lamppost": {"id": "lamppost", "address": "shelly1pm-84CCA8A11963", "relay":"0"     , "label":"Lamp post", "last_update": 0}, #192.168.1.62 - Lamp Post and Driveway
    "porch": {"id": "porch", "address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch", "last_update": 0}, #192.168.1.243 - Porch Light
    "dining": {"id": "dining", "address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room", "last_update": 0}, #192.168.1.243 - Dining Room Light
    "officefan": {"id": "officefan", "address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan", "last_update": 0}, #192.168.1.242 - Office Fan
    "kitchen": {"id": "kitchen", "address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen", "last_update": 0}, #192.168.1.242 - Kitchen Lights
    "office": {"id": "office", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights", "last_update": 0}, #192.168.1.244 - Office Lights
    "unknown1": {"id": "unknown1", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Unknown 1", "last_update": 0}, #192.168.1.244 - Unknown
    "unknown2": {"id": "unknown2", "address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Unknown 2", "last_update": 0}, #192.168.1.245 - Unknown
    "bar": {"id": "bar", "address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar", "last_update": 0}, #192.168.1.245 - Bar Lights
    "unknown3": {"id": "unknown3", "address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Unknown 3", "last_update": 0}, #192.168.1.61  - Unknown
    "unknown4": {"id": "unknown4", "address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Unknown 4", "last_update": 0}, #192.168.1.61  - Unknown
    "guestbath": {"id": "guestbath", "address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom", "last_update": 0}, #192.168.1.240 - Bathroom Lights and Fan
    "garage": {"id": "garage", "address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights", "last_update": 0}, #192.168.1.240 - Garage Lights
    "masterbath": {"id": "masterbath", "address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath", "last_update": 0}, #192.168.1.241 - Master Bath Lights
    "stairway": {"id": "stairway", "address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway", "last_update": 0}, #192.168.1.241 - Stairway Lights
    "hallway": {"id": "hallway", "address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway", "last_update": 0}, #192.168.1.239 - Hallway
    "showerfan": {"id": "showerfan", "address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan", "last_update": 0} #192.168.1.239 - Master Bath Vent Fan
}

rules = [
    {"circuit":"hallway", "type":"timeOfDay", "time":"05:00","state":"on","last_execution":0},
    {"circuit":"hallway", "type":"timeOfDay", "time":"07:00","state":"off","last_execution":0},
    {"circuit":"hallway", "type":"timeOfDay", "time":"21:15","state":"on","last_execution":0},
    {"circuit":"hallway", "type":"timeOfDay", "time":"21:45","state":"off","last_execution":0},
    {"circuit":"fireplace", "type":"timeOfDay", "time":"18:00","state":"on","last_execution":0},
    {"circuit":"fireplace", "type":"timeOfDay", "time":"21:00","state":"off","last_execution":0},
    {"circuit":"dining", "type":"timeOfDay", "time":"15:00","state":"on","last_execution":0},
    {"circuit":"dining", "type":"timeOfDay", "time":"23:00","state":"off","last_execution":0},
    {"circuit":"kitchen", "type":"timeOfDay", "time":"05:00","state":"on","last_execution":0},
    {"circuit":"kitchen", "type":"timeOfDay", "time":"09:00","state":"off","last_execution":0},
    {"circuit":"kitchen", "type":"timeOfDay", "time":"16:00","state":"on","last_execution":0},
    {"circuit":"kitchen", "type":"timeOfDay", "time":"20:00","state":"off","last_execution":0},
    {"circuit":"bar", "type":"timeOfDay", "time":"16:00","state":"on","last_execution":0},
    {"circuit":"bar", "type":"timeOfDay", "time":"00:00","state":"off","last_execution":0},
    {"circuit":"office", "type":"timeOfDay", "time":"22:00","state":"off","last_execution":0},
    {"circuit":"officefan", "type":"timeOfDay", "time":"22:00","state":"off","last_execution":0},
    {"circuit":"lamppost", "type":"timeOfDay", "time":"08:00","state":"off","last_execution":0},
    {"circuit":"lamppost", "type":"timeOfDay", "time":"20:00","state":"on","last_execution":0},
    {"circuit":"porch", "type":"timeOfDay", "time":"08:00","state":"off","last_execution":0},
    {"circuit":"porch", "type":"timeOfDay", "time":"20:00","state":"on","last_execution":0},
    {"circuit":"porch", "type":"timeOfDay", "time":"23:00","state":"off","last_execution":0},
    {"circuit":"porch", "type":"timeOfDay", "time":"04:00","state":"on","last_execution":0},
    {"circuit":"garage", "type":"timeOfDay", "time":"23:00","state":"off","last_execution":0},
    {"circuit":"garage", "type":"timeOfDay", "time":"09:00","state":"off","last_execution":0},
    {"circuit":"garage", "type":"timeOfDay", "time":"16:30","state":"on","last_execution":0},
    {"circuit":"garage", "type":"timeOfDay", "time":"06:00","state":"on","last_execution":0},
    {"circuit":"stairway", "type":"timeOfDay", "time":"04:00","state":"on","last_execution":0},
    {"circuit":"stairway", "type":"timeOfDay", "time":"06:00","state":"off","last_execution":0},
    {"circuit":"stairway", "type":"timeOfDay", "time":"22:50","state":"on","last_execution":0},
    {"circuit":"stairway", "type":"timeOfDay", "time":"01:00","state":"off","last_execution":0},
    {"circuit":"showerfan", "type":"timer", "time":"01:15","last_start":0}
]

circuit_state = {
    "fireplace": False,
    "lamppost": False,
    "porch": False,
    "dining": False,
    "officefan": False,
    "kitchen": False,
    "office": False,
    "unknown1": False,
    "unknown2": False,
    "bar": False,
    "unknown3": False,
    "unknown4": False,
    "guestbath": False,
    "garage": False,
    "masterbath": False,
    "stairway": False,
    "hallway": False,
    "showerfan": False
}
reverse_lookup = {} #I can't figure out a better or faster way

running = False

last_rule_update = round(time.time())

def load_rules():
    global rules
    f = open('rules.json',)
    rules = json.load(f)

def check_time_of_day_rule(now, rid):
    global rules
    since_last = now - rules[rid]["last_execution"]
    if since_last < 60:
        return
    target = rules[rid]["time"].split(":")
    dtnow = datetime.datetime.now()
    if int(target[0]) == dtnow.hour and int(target[1]) == dtnow.minute:
        print("time of day rule triggered for "+circuits[rules[rid]["circuit"]]["label"])
        rules[rid]["last_execution"] = now
        circuit = circuits[rules[rid]["circuit"]]
        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
        mosquittoDo(topic,rules[rid]["state"])

def check_timer_rule(now, rid):
    global rules
    t = rules[rid]["time"].split(":")
    h = int(t[0])
    m = int(t[1])
    s = (m*60) + (h*3600)
    l = rules[rid]["last_start"]
    d = now - l
    cid = rules[rid]["circuit"]
    o = circuit_state[cid]
    if o is True and d >= s:
        print("timer rule triggered for "+circuits[cid]["label"])
        circuit = circuits[cid]
        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
        mosquittoDo(topic,"off")
        rules[rid]["last_start"] = now

def check_rule(now, rid):
    if rules[rid]["type"] == "timeOfDay":
        check_time_of_day_rule(now, rid)
    if rules[rid]["type"] == "timer":
        check_timer_rule(now, rid)

def on_message(client, userdata, message):
    global circuit_state
    global circuits
    if running is not True:
        return
    now = round(time.time())
    result = str(message.payload.decode("utf-8"))
    topic = message.topic
    cid = reverse_lookup[topic]
    previous = circuit_state[cid]
    if result == "on":
        circuit_state[cid] = True
    else:
        circuit_state[cid] = False
    if circuit_state[cid] != previous:
        circuits[cid]["last_update"] = round(time.time())
        if circuit_state[cid] is True:
            for rid in range(0,len(rules)):
                if rules[rid]["circuit"] == cid and rules[rid]["type"] == "timer":
                    rules[rid]["last_start"] = now

def mosquittoMessage(message):
    global bad
    try:
        client.publish(myname+"/status",message)
    except:
        bad = bad + 1
        if bad > 10:
            os.system('sudo reboot now')

def mosquittoDo(topic, command):
    try:
        print("publishing '"+command+"' to "+topic)
        client.publish(topic,command)
    except:
        print("BAD - Failed to publish "+command+" to "+topic)

if __name__ == "__main__":
    subscriptions = []
    for k in circuits.keys():
        c = circuits[k]
        addy = "shellies/"+c["address"]+"/relay/"+c["relay"]
        print("preparing "+addy)
        subscriptions.append((addy, 0))
        reverse_lookup[addy] = k
    connected = False
    while connected is False:
        try:
            client.on_message = on_message
            client.connect(broker)
            client.subscribe(subscriptions)
            client.loop_start()
            connected = True
        except:
            print("BAD - client failed connection. Will try again in five seconds")
            connected = False
            time.sleep(5)
    
    running = True
    circuit = circuits["stairway"]
    topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
    mosquittoDo(topic,"on")
    time.sleep(1)
    mosquittoDo(topic,"off")
    time.sleep(1)
    mosquittoDo(topic,"on")
    time.sleep(1)
    mosquittoDo(topic,"off")
    time.sleep(1)
    mosquittoDo(topic,"on")
    time.sleep(1)
    mosquittoDo(topic,"off")
    time.sleep(1)
    while running is True:
        now = round(time.time())
        if last_rule_update <= now - 10:
            load_rules()
            last_rule_update = round(time.time())
            mosquittoMessage("mqtt_automation "+str(myip).split(' ')[0].replace("b'","")+" alive at "+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        for i in range(0, len(rules)):
            check_rule(now, i)
        # always wait a second at the bottom to allow subscribers to update states
        time.sleep(1)

    try:
        client.loop_stop()
        client.disconnect()
    except:
        print("INFO - Client diconnet failed. Maybe, the connection failed first or during runtime.")