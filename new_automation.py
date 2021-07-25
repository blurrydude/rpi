import json
import requests
from datetime import datetime

def sendCommand(command):
    print("sending command: "+command)
    r =requests.get('https://api.idkline.com/control/'+command)
    print(str(r.status_code))

def loadConfig():
    global circuits
    f = open('circuits.json')
    circuits = json.load(f)

def doCheck():
    now = datetime.now().strftime("%H:%M")
    day = datetime.now().strftime("%a").lower()
    print('do check: '+now)
    for circuit in circuits:
        for ontime in circuit["onTimes"]:
            if now in ontime and day in ontime:
                sendCommand("turn " + circuit["label"] + " on")
        for offtime in circuit["offTimes"]:
            if now in offtime and day in offtime:
                sendCommand("turn " + circuit["label"] + " off")

circuits = []

loadConfig()
doCheck()