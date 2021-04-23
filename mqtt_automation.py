import paho.mqtt.client as mqtt
import time
import datetime
import socket

myname = socket.gethostname()
############# CONFIG #############
broker = "192.168.1.22"
##################################
client = mqtt.Client()

circuits = {
    "A1": {"id": "A1", "address": "shelly1pm-8CAAB574C489", "relay":"0"     , "label":"Fireplace", "last_update": 0}, #192.168.1.60 - Fireplace Lights
    "B1": {"id": "B1", "address": "shelly1pm-84CCA8A11963", "relay":"0"     , "label":"Lamp post", "last_update": 0}, #192.168.1.62 - Lamp Post and Driveway
    "C1": {"id": "C1", "address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "label":"Porch", "last_update": 0}, #192.168.1.243 - Porch Light
    "C2": {"id": "C2", "address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "label":"Dining Room", "last_update": 0}, #192.168.1.243 - Dining Room Light
    "D1": {"id": "D1", "address": "shellyswitch25-8CAAB55F405D", "relay":"0", "label":"Office Fan", "last_update": 0}, #192.168.1.242 - Office Fan
    "D2": {"id": "D2", "address": "shellyswitch25-8CAAB55F405D", "relay":"1", "label":"Kitchen", "last_update": 0}, #192.168.1.242 - Kitchen Lights
    "E1": {"id": "E1", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "label":"Office Lights", "last_update": 0}, #192.168.1.244 - Office Lights
    "E2": {"id": "E2", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "label":"Unknown 1", "last_update": 0}, #192.168.1.244 - Unknown
    "F1": {"id": "F1", "address": "shellyswitch25-8CAAB55F4553", "relay":"0", "label":"Unknown 2", "last_update": 0}, #192.168.1.245 - Unknown
    "F2": {"id": "F2", "address": "shellyswitch25-8CAAB55F4553", "relay":"1", "label":"Bar", "last_update": 0}, #192.168.1.245 - Bar Lights
    "G1": {"id": "G1", "address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "label":"Unknown 3", "last_update": 0}, #192.168.1.61  - Unknown
    "G2": {"id": "G2", "address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "label":"Unknown 4", "last_update": 0}, #192.168.1.61  - Unknown
    "H1": {"id": "H1", "address": "shellyswitch25-8CAAB561DDED", "relay":"0", "label":"Guest Bathroom", "last_update": 0}, #192.168.1.240 - Bathroom Lights and Fan
    "H2": {"id": "H2", "address": "shellyswitch25-8CAAB561DDED", "relay":"1", "label":"Garage Lights", "last_update": 0}, #192.168.1.240 - Garage Lights
    "I1": {"id": "I1", "address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "label":"Master Bath", "last_update": 0}, #192.168.1.241 - Master Bath Lights
    "I2": {"id": "I2", "address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "label":"Stairway", "last_update": 0}, #192.168.1.241 - Stairway Lights
    "J1": {"id": "J1", "address": "shellyswitch25-8CAAB55F402F", "relay":"0", "label":"Hallway", "last_update": 0}, #192.168.1.239 - Hallway
    "J2": {"id": "J2", "address": "shellyswitch25-8CAAB55F402F", "relay":"1", "label":"Shower Fan", "last_update": 0} #192.168.1.239 - Master Bath Vent Fan
}

rules = [
    {"circuit":"D2", "type":"timeOfDay", "time":"00:00","state":"off","last_execution":0},
    {"circuit":"H2", "type":"timeOfDay", "time":"00:00","state":"off","last_execution":0},
    {"circuit":"I2", "type":"timeOfDay", "time":"00:00","state":"on","last_execution":0},
    {"circuit":"I2", "type":"timeOfDay", "time":"02:00","state":"off","last_execution":0},
    {"circuit":"J2", "type":"timer", "time":"01:00","last_start":0}
]

circuit_state = {
    "A1": False,
    "B1": False,
    "C1": False,
    "C2": False,
    "D1": False,
    "D2": False,
    "E1": False,
    "E2": False,
    "F1": False,
    "F2": False,
    "G1": False,
    "G2": False,
    "H1": False,
    "H2": False,
    "I1": False,
    "I2": False,
    "J1": False,
    "J2": False
}
reverse_lookup = {} #I can't figure out a better or faster way

running = False

def check_time_of_day_rule(now, rid):
    global rules
    since_last = now - rules[rid]["last_execution"]
    if since_last < 60:
        return
    target = rules[rid]["time"].split(":")
    dtnow = datetime.datetime.now()
    if target[0] == dtnow.hour and target[1] == dtnow.minute:
        rules[rid]["last_execution"] = now
        circuit = circuits[rules[rid]["circuit"]]
        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]+"/command"
        mosquittoDo(topic,rules[rid]["state"])

def check_timer_rule(now, rid):
    global rules

def check_rule(now, rid):
    if rule["type"] == "timeOfDay":
        check_time_of_day_rule(rid)
    if rule["type"] == "timer":
        check_timer_rule(rid)

def on_message(client, userdata, message):
    global circuit_state
    global circuits
    if running is not True:
        return
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
    while running is True:
        now = round(time.time())
        for i in range(0, len(rules)):
            check_rule(now, i)
        # always wait a second at the bottom to allow subscribers to update states
        time.sleep(1)

    try:
        client.loop_stop()
        client.disconnect()
    except:
        print("INFO - Client diconnet failed. Maybe, the connection failed first or during runtime.")