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
    for circuit in circuits:
        for ontime in circuit["onTimes"]:
            if ontime == now:
                sendCommand("turn " + circuit["label"] + " on")
        for ontime in circuit["offTimes"]:
            if ontime == now:
                sendCommand("turn " + circuit["label"] + " off")

circuits = []

loadConfig()
doCheck()