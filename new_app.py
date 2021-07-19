from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import json


f = open('/home/pi/rpi/circuits.json',)
circuits = json.load(f)

def mosquittoDo(topic, command):
    global received
    global result
    client = mqtt.Client()
    client.connect("192.168.1.22")
    client.publish(topic,command)
    client.disconnect()
    return 'OK'

app = FlaskAPI(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/control/<text>')
def control(text):
    command = text.lower()
    mosquittoDo("incoming/commands", command)
    com = "off"
    command_list = []
    if "on" in command:
        com = "on"
    if "zone" in command or "area" in command or "all of the" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            for z in c["zones"]:
                if z.lower() in command:
                    topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                    command_list.append({"t":topic,"c":com})
    elif "mode" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            com = None
            for m in c["onModes"]:
                if m.lower() in command:
                    com = "on"
            for m in c["offModes"]:
                if m.lower() in command:
                    com = "off"
            if com is None:
                return
            topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
            command_list.append({"t":topic,"c":com})
    elif "turn" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            if c["label"].lower() in command or c["label"].lower().replace("light","lamp") in command:
                topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                command_list.append({"t":topic,"c":com})
    for cmd in command_list:
        mosquittoDo(cmd["t"],cmd["c"])
    return 'OK'

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')

