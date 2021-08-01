from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import json
import sys
import socket
import os
from datetime import datetime

myname = socket.gethostname()
twilled = False
try:
    from twilio.rest import Client
    twilled = True
except:
    twilled = False

f = open('/home/pi/rpi/circuits.json')
circuits = json.load(f)
f = open('/home/pi/config.json')
config = json.load(f)
retries = 0

def reloadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)

def log(message):
    with open('/home/pi/SMS.log','a') as write_file:
        write_file.write(message+'\n')

def sms(message, to):
    global retries
    if twilled is False:
        return
    try:
        account_sid = config["account_sid"]
        auth_token = config["auth_token"] 
        client = Client(account_sid, auth_token)
        client.messages.create(  
            messaging_service_sid=config["messaging_service_sid"], 
            body=message,      
            to=to 
        )
        retries = 0 
    except:
        log("Unexpected error:" + sys.exc_info()[0])
        if retries < 4:
            retries = retries + 1
            time.sleep(1)
            sms(message, to)

def mosquittoDo(topic, command):
    global received
    global result
    try:
        client = mqtt.Client()
        client.connect("192.168.1.22")
        client.publish(topic,command)
        client.disconnect()
    except:
        print('failed')
    return 'OK'

app = FlaskAPI(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

allowed_senders = ["+19377893750","+19377166465"]

@app.route('/debug',methods=['GET'])
def debug():
    body = request.args.get("Body")
    sender = request.args.get("From")
    log("received: "+body+"\nfrom: "+sender+'\n\n')
    if sender not in allowed_senders:
        sms(sender + " tried to send me the command: "+ body, "+19377166465")
        time.sleep(1)
        sms("I think you have the wrong number, you don't appear to be authorized to talk to me.", sender)
        return 'bad'
    return control("sms~"+sender+"~"+body)

@app.route('/pistates',methods=['GET'])
def pistates():
    f = open('/home/pi/pistates.json')
    states = json.load(f)
    return states

@app.route('/states',methods=['GET'])
def states():
    dirname = '/home/pi'
    
    ext = ('.state')
    states = {}
    for f in os.listdir(dirname):
        if f.endswith(ext):
            s = f.split('/')
            a = s[len(s)-1].split('.')[0].split('_')
            address = a[0]
            relay = a[1]
            for circuit in circuits:
                if circuit["address"] == address and circuit["relay"] == relay:
                    x = open(dirname+'/'+address+'_'+relay+'.state')
                    states[circuit["label"]] = x.read()
        else:
            continue
    return states

@app.route('/webstates',methods=['GET'])
def webstates():
    reloadCircuits()
    dirname = '/home/pi'
    
    ext = ('.state')
    states = {}
    for f in os.listdir(dirname):
        if f.endswith(ext):
            s = f.split('/')
            a = s[len(s)-1].split('.')[0].split('_')
            address = a[0]
            relay = a[1]
            for circuit in circuits:
                if circuit["address"] == address and circuit["relay"] == relay:
                    x = open(dirname+'/'+address+'_'+relay+'.state')
                    y = open(dirname+'/'+address+'_'+relay+'_power.state')
                    states[circuit["label"]] = {"state":x.read(),"power":float(y.read())}
        else:
            continue
    
    return states

@app.route('/powerstates',methods=['GET'])
def powerstates():
    dirname = '/home/pi'
    
    ext = ('.state')
    states = {}
    for f in os.listdir(dirname):
        if f.endswith(ext):
            s = f.split('/')
            a = s[len(s)-1].split('.')[0].split('_')
            address = a[0]
            relay = a[1]
            for circuit in circuits:
                if circuit["address"] == address and circuit["relay"] == relay:
                    x = open(dirname+'/'+address+'_'+relay+'_power.state')
                    states[circuit["label"]] = x.read()
        else:
            continue
    return states

@app.route('/control/<text>')
def control(text):
    shop_door = open('home/pi/shop_door.state').read().replace("\n","")
    garage_door = open('home/pi/garage_door.state').read().replace("\n","")
    reloadCircuits()
    command = text.lower()
    smst = False
    if "sms" in command:
        split = command.split('~')
        command = split[2]
        smssender = split[1]
        smst = True
    mosquittoDo("pi/"+myname+"/command", command)
    com = "off"
    command_list = []
    text = ""
    if " on" in command:
        com = "on"
    if "zone" in command or "area" in command or "all of the" in command:
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            for z in c["zones"]:
                if z.lower() in command:
                    topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                    command_list.append({"t":topic,"c":com})
                    text = text + c["label"]+" "+com+"\n"
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
            text = text + c["label"]+" "+com+"\n"
    elif "turn" in command:
        command = command.replace("shop", "garage")
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            if c["label"].lower() in command or c["label"].lower().replace("light","lamp") in command:
                topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                command_list.append({"t":topic,"c":com})
                text = text + c["label"]+" "+com+"\n"
    elif "shop door" in command:
        if "open" in command and shop_door is "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:1"})
            text = text + "opening shop door\n"
        if ("close" in command or "shut" in command) and shop_door is "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:0"})
            text = text + "closing shop door\n"
    elif "garage door" in command:
        if "open" in command and garage_door is "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:1"})
            text = text + "opening garage door\n"
            with open('/home/pi/garage_door.state','w') as write_file:
                write_file.write("open")
        if ("close" in command or "shut" in command) and garage_door is "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:0"})
            text = text + "closing garage door\n"
            with open('/home/pi/garage_door.state','w') as write_file:
                write_file.write("closed")
    elif "status" in command:
        text = text + "Yeah, I'm alive\n"
    log(text)
    if smst is True:
        sms(text,smssender)
    for cmd in command_list:
        mosquittoDo(cmd["t"],cmd["c"])
    return 'OK'

@app.route('/circuitinfo/<circuitlabel>')
def circuitinfo(circuitlabel):
    reloadCircuits()
    for circuit in circuits:
        if circuit["label"] == circuitlabel:
            return circuit
    return None

@app.route('/reportdoor/<data>')
def reportdoor(data):
    split = data.split('-')
    door = split[0]
    state = split[1]
    f = "/home/pi/"+door+"_door.state"
    with open(f,"w") as write_file:
        write_file.write(state)
    return 'OK'

@app.route('/getdoors')
def getdoors():
    f1 = "/home/pi/garage_door.state"
    f2 = "/home/pi/shop_door.state"
    data = {
        "garage": open(f1).read().replace("\n",""),
        "shop": open(f2).read().replace("\n","")
    }
    return data

@app.route('/reportreadings/<message>')
def reportreadings(message):
    split = message.split(':')
    room = split[0]
    temp = split[1]
    hum = split[2]
    f = "/home/pi/temperatures.json"
    j = open(f)
    readings = json.load(j)
    f2 = open("/home/pi/"+room+"_thermosettings.json")
    settings = json.load(f2)
    readings[room] = {
        "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "temperature": temp,
        "humidity": hum,
        "settings": settings
    }
    with open(f,"w") as write_file:
        write_file.write(json.dumps(readings))
    return 'OK'

@app.route('/getreadings')
def getreadings():
    f = open("/home/pi/temperatures.json")
    return json.load(f)

@app.route('/thermosettings/<room>')
def thermosettings(room):
    f = open("/home/pi/"+room+"_thermosettings.json")
    return json.load(f)

@app.route('/thermoset/<data>')
def thermoset(data):
    s = data.split('-')
    room = s[0]
    temp_low = int(s[1])
    temp_high = int(s[2])
    f = open("/home/pi/"+room+"_thermosettings.json")
    settings = json.load(f)
    settings["temperature_high_setting"] = temp_high
    settings["temperature_low_setting"] = temp_low
    with open("/home/pi/"+room+"_thermosettings.json","w") as write_file:
        write_file.write(json.dumps(settings))
    return 'OK'
    

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')

