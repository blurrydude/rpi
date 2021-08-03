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
import base64
import hashlib

file_logging = True
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

def b64(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def md5hash(message):
    message_bytes = message.encode('ascii')
    base64_bytes = hashlib.md5(message_bytes)
    return base64_bytes.hexdigest()

def reloadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)

def log(message):
    if type(message) is not type(""):
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = "/home/pi/app_"+logfiledate+".log"
    entry = timestamp + ": " + message + "\n"
    print(entry)
    if file_logging is True:
        if os.path.exists(logfile):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        with open(logfile, append_write) as write_file:
            write_file.write(entry)

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
    except Exception as err:
        log("Unexpected error")
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

pronouns = ["I","We","They"]
spronouns = ["He","She","It"]
verb = ["love","hate","like","despise","admire","loathe","adore","tolerate","own","consume","paint","draw","sketch","build","sculpt","summon"]
adjectives = ["plastic","glass","stone","wooden","organic","regular","medium","large","small","irregular","moronic","beautiful","terrifying","regulatory"]
nouns = ["badgers","clowns","fruit","vegetables","crates","pillows","boats","pants","wheels","aardvarks","nighties","amoeba","cars","cathedrals","spoons","albums"]

allowed_senders = ["+19377893750","+19377166465"]

def checktoken(username, token):
    f = open("/home/pi/users.json")
    users = json.load(f)
    if username in users.keys():
        check_token = md5hash(username+":"+users[username]["password"]+datetime.now().strftime('%Y%m%d'))
        return token == check_token
    return False

@app.route('/gettoken',methods={"POST"})
def gettoken():
    try:
        f = open("/home/pi/users.json")
        users = json.load(f)
    except:
        users = {
            "0000":{"pasword":"I hate regulatory badgers"}
        }
        with open("/home/pi/users.json","w") as write_file:
            json.dump(users,fp=write_file)
    r = request.get_json(force=True)
    username = r["username"]
    passhash = r["passhash"]
    check_user = None
    if username in users.keys():
        check_user = users[username]
    return check_user
    if check_user is None:
        return {"auth":"invalid"}
    check_hash = md5hash(check_user["password"])
    if passhash == check_hash:
        return {"auth":md5hash(username+":"+check_user["password"]+datetime.now().strftime('%Y%m%d'))}

@app.route('/testtoken',methods={"GET"})
def testtoken():
    if checktoken(request.headers["auth"]) is True:
        return 'OK'
    return 'BAD'

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
    log("incoming text: "+text)
    shop_door = open('/home/pi/Shop_door.state').read().replace("\n","")
    garage_door = open('/home/pi/Garage_door.state').read().replace("\n","")
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
        if "open" in command and shop_door == "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:1"})
            text = text + "opening shop door\n"
            with open('/home/pi/Shop_door.state','w') as write_file:
                write_file.write("open")
        if ("close" in command or "shut" in command) and shop_door == "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:0"})
            text = text + "closing shop door\n"
            with open('/home/pi/Shop_door.state','w') as write_file:
                write_file.write("closed")
    elif "garage door" in command:
        if "open" in command and garage_door == "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:1"})
            text = text + "opening garage door\n"
            with open('/home/pi/Garage_door.state','w') as write_file:
                write_file.write("open")
        if ("close" in command or "shut" in command) and garage_door == "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:0"})
            text = text + "closing garage door\n"
            with open('/home/pi/Garage_door.state','w') as write_file:
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
    dirname = '/home/pi'
    
    ext = ('_door.state')
    states = {}
    for f in os.listdir(dirname):
        if f.endswith(ext):
            s = f.split('/')
            a = s[len(s)-1].split('.')[0].split('_door')
            label = a[0]
            states[label] = open(dirname+"/"+label+"_door.state").read().replace("\n","")
        else:
            continue
    return states

@app.route('/reportreadings/<message>')
def reportreadings(message):
    split = message.split(':')
    room = split[0]
    temp = split[1]
    hum = split[2]
    cooling = split[3]
    circulation = split[4]
    heating = split[5]
    whf = split[6]
    status = split[7]
    last_stage_start = split[8].replace("-",":").replace("~","/")
    last_circulation = split[9].replace("-",":").replace("~","/")
    try:
        f = "/home/pi/temperatures.json"
        j = open(f)
    except:
        j = "{}"
    readings = json.load(j)
    f2 = open("/home/pi/"+room+"_thermosettings.json")
    settings = json.load(f2)
    readings[room] = {
        "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "temperature": temp,
        "humidity": hum,
        "settings": settings,
        "cooling": cooling,
        "circulation": circulation,
        "heating": heating,
        "whf": whf,
        "status":status,
        "last_stage_start":last_stage_start,
        "last_circulation":last_circulation
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

@app.route('/thermoreport/<data>')
def thermoreport(data):
    s = data.split('-')
    room = s[0]
    cooling = s[1]
    circulation = s[2]
    heating = s[3]
    whf = s[4]
    
    with open("/home/pi/"+room+"_thermoreport.json","w") as write_file:
        write_file.write(json.dumps({
            "cooling": cooling,
            "circulation": circulation,
            "heating": heating,
            "whf": whf
        }))
    return 'OK'
    

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')

