import requests
import json
from requests.models import HTTPBasicAuth
#import os
# import subprocess
# import time

# repeat = False

# for i in range(3):
#     print("waiting "+str(i))
#     time.sleep(1)

# if repeat is True:
#     #os.system("python3 test.py")
#     subprocess.Popen(["python3","test.py"])
#     print("after")
# print("exiting")
# exit()

#print(os.path.dirname(os.path.realpath(__file__)))

set_mqtt = "settings/mqtt?mqtt_server=192.168.1.200:1883"

passwords = json.load(open("SmarterCircuits/shellylogins.json"))
circuits = json.load(open("SmarterCircuits/circuits.json"))
motion_sensors = json.load(open("SmarterCircuits/motionsensors.json"))
door_sensors = json.load(open("SmarterCircuits/doorsensors.json"))
ht_sensors = json.load(open("SmarterCircuits/thsensors.json"))
ips = {}
output = {}
for circuit in circuits:
    ip = circuit["ip_address"]
    id = circuit["id"]
    if id not in passwords.keys():
        print("NOT FOUND: "+id)
        continue
    r = requests.get("http://"+ip+"/status", auth=HTTPBasicAuth('admin', passwords[id]))
    raw = r.text
    data = json.loads(raw)
    ison = data["relays"][int(circuit["relay_id"])]["ison"]
    power = data["meters"][int(circuit["relay_id"])]["power"]
    print(id+": "+str(ison)+" - "+str(power))