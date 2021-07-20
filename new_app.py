from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import json
twilled = False
try:
    from twilio.rest import Client
    twilled = True
except:
    twilled = False

f = open('/home/pi/rpi/circuits.json')
circuits = json.load(f)

def sms(message):
    if twilled is False:
        return
    account_sid = 'AC26cbcaf937e606af51c6a384728a4e75' 
    auth_token = '0bbd4df550e70c0e7350aa8db30a7329' 
    client = Client(account_sid, auth_token)
    client.messages.create(  
        messaging_service_sid='MG1cf18075f26dc8ff965a5d2d1940dab5', 
        body=message,      
        to='+19377166465' 
    ) 

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

@app.route('/debug',method=['POST'])
def debug():
    command = json.dumps(request.args.to_dict())
    sms(command)

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

