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

def sms(message, to):
    if twilled is False:
        return
    account_sid = 'AC26cbcaf937e606af51c6a384728a4e75' 
    auth_token = '0bbd4df550e70c0e7350aa8db30a7329' 
    client = Client(account_sid, auth_token)
    client.messages.create(  
        messaging_service_sid='MG1cf18075f26dc8ff965a5d2d1940dab5', 
        body=message,      
        to=to 
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

allowed_senders = ["+19377893750","+19377166465"]

@app.route('/debug',methods=['GET'])
def debug():
    body = request.args.get("Body")
    sender = request.args.get("From")
    if sender not in allowed_senders:
        sms(sender + " tried to send me the command: "+ body, sender)
        return 'bad'
    return control("sms~"+sender+"~"+body)

@app.route('/control/<text>')
def control(text):
    command = text.lower()
    smst = False
    if "sms" in command:
        split = command.split('~')
        command = split[2]
        smssender = split[1]
        smst = True
    mosquittoDo("incoming/commands", command)
    com = "off"
    command_list = []
    text = ""
    if "on" in command:
        com = "on"
    if "zone" in command or "area" in command or "all of the" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            for z in c["zones"]:
                if z.lower() in command:
                    topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                    command_list.append({"t":topic,"c":com})
                    text = text + "Turning "+c["label"]+" "+com+"\n"
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
                continue
            topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
            command_list.append({"t":topic,"c":com})
            text = text + "Turning "+c["label"]+" "+com+"\n"
    elif "turn" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            if c["label"].lower() in command or c["label"].lower().replace("light","lamp") in command:
                topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                command_list.append({"t":topic,"c":com})
                text = text + "Turning "+c["label"]+" "+com+"\n"
    elif "shop door" in command:
        command_list.append({"t":"garagepi/commands","c":"1:0"})
        text = text + "opening shop door\n"
    if smst is True:
        sms(text,smssender)
    for cmd in command_list:
        mosquittoDo(cmd["t"],cmd["c"])
    return 'OK'

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')

