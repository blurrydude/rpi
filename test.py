import json

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

# Opening JSON file
f = open('rules.json',)
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list

by_time = {}

for rule in data:
    t = rule["time"]
    if t not in by_time.keys():
        by_time[t] = []
    by_time[t].append(rule)

for t in sorted (by_time.keys()) : 
    for rule in by_time[t]:
        circuit = circuits[rule["circuit"]]
        if rule["type"] == "timeOfDay":
            print("Turn "+circuit["label"]+" "+rule["state"]+ " at "+ rule["time"])
for t in sorted (by_time.keys()) : 
    for rule in by_time[t]:
        circuit = circuits[rule["circuit"]]
        if rule["type"] != "timeOfDay":
            print("Turn "+circuit["label"]+" off after "+ rule["time"].replace(":"," hour(s) and ") + " minute(s)")
  
# Closing file
f.close()