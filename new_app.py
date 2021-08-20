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

dev = False
file_logging = True
myname = socket.gethostname()
twilled = False
try:
    from twilio.rest import Client
    twilled = True
except:
    twilled = False

homepath = "/home/pi"
if dev is True:
    homepath = "/home/ian/"
f = open(homepath+'/rpi/circuits.json')
circuits = json.load(f)
f = open(homepath+'/config.json')
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
    f = open(homepath+'/rpi/circuits.json')
    circuits = json.load(f)

def log(message):
    if type(message) is not type(""):
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = homepath+"/app_"+logfiledate+".log"
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
        log("sms: "+message)
        account_sid = config["account_sid"]
        auth_token = config["auth_token"] 
        client = Client(account_sid, auth_token)
        client.messages.create(  
            messaging_service_sid=config["messaging_service_sid"], 
            body=message,      
            to=to 
        )
        retries = 0
        log("sms success")
    except Exception as err:
        log("Unexpected error: "+str(err))
        if retries < 4:
            retries = retries + 1
            time.sleep(1)
            sms(message, to)

def mosquittoDo(topic, command):
    global received
    global result
    try:
        client = mqtt.Client()
        client.connect("192.168.1.200")
        client.publish(topic,command)
        client.disconnect()
    except:
        print('failed')
    return 'OK'

app = FlaskAPI(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

allowed_senders = ["+19377893750","+19377166465"]

def checktoken(request):
    username = request.headers["user"]
    token = request.headers["auth"]
    f = open(homepath+"/users.json")
    users = json.load(f)
    if username in users.keys():
        check_token = md5hash(username+":"+users[username]["password"]+datetime.now().strftime('%Y%m%d%H'))+md5hash(username+":"+datetime.now().strftime('%Y%m%d%H'))
        return token == check_token
    return False

@app.route('/gettoken',methods={"POST"})
def gettoken():
    try:
        f = open(homepath+"/users.json")
        users = json.load(f)
    except:
        users = {
            "0000":{"password":"I hate regulatory badgers"}
        }
        with open(homepath+"/users.json","w") as write_file:
            json.dump(users,fp=write_file)
    r = request.get_json(force=True)
    username = r["username"]
    passhash = r["passhash"]
    check_user = None
    if username in users.keys():
        check_user = users[username]
    if check_user is None:
        return {"auth":"invalid"}
    check_hash = md5hash(check_user["password"])
    if passhash == check_hash:
        return {"auth":md5hash(username+":"+check_user["password"]+datetime.now().strftime('%Y%m%d%H'))+md5hash(username+":"+datetime.now().strftime('%Y%m%d%H'))}
    return {"auth":"invalid"}

@app.route('/testtoken',methods={"GET"})
def testtoken():
    if checktoken(request) is not True:
        return 'UNAUTHORIZED'
    return 'OK'

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
    f = open(homepath+'/pistates.json')
    states = json.load(f)
    return states

@app.route('/checkins',methods=['GET'])
def checkins():
    f = open(homepath+'/checkins.json')
    checkins = json.load(f)
    output = {}
    for circuit in circuits:
        addy = circuit["address"]
        if addy in checkins.keys():
            output[circuit["label"]] = checkins[addy]
        else:
            output[circuit["label"]] = "NONCOMM: "+circuit["address"]+" @ "+circuit["notes"]
    return output

@app.route('/states',methods=['GET'])
def states():
    dirname = homepath
    
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
    dirname = homepath
    
    #f = open(dirname+"/shellies.json")
    #shellies = json.load(f)

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
                    states[circuit["label"]] = {"state":x.read(),"power":float(y.read()),"address":address,"relay":relay}
                    #if address in shellies.keys():
                    #    states[circuit["label"]]["shelly"] = shellies[address]
        else:
            continue
    
    return states

@app.route('/powerstates',methods=['GET'])
def powerstates():
    dirname = homepath
    
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

@app.route('/webcontrol/<text>')
def webcontrol(text):
    if checktoken(request) is not True:
        return 'UNAUTHORIZED'
    return control(text)

@app.route('/control/<text>')
def control(text):
    log("incoming text: "+text)
    shop_door = open(homepath+'/Shop_door.state').read().replace("\n","")
    garage_door = open(homepath+'/Garage_door.state').read().replace("\n","")
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
        detected_mode = None
        for ci in range(0,len(circuits)):
            c = circuits[ci]
            com = None
            for m in c["onModes"]:
                if m.lower() in command:
                    detected_mode = m.lower()
                    com = "on"
            for m in c["offModes"]:
                if m.lower() in command:
                    detected_mode = m.lower()
                    com = "off"
            if com is None:
                continue
            with open("/home/pi/mode.txt","w") as write_file:
                write_file.write(detected_mode)
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


    elif "first shade" in command:
        if "open" in command:
            command_list.append({"t":"pi/rollerpi/commands","c":"0:0"})
            text = text + "opening the first shade\n"
        else:
            command_list.append({"t":"pi/rollerpi/commands","c":"0:1"})
            text = text + "closing the first shade\n"
    elif "second shade" in command:
        if "open" in command:
            command_list.append({"t":"pi/rollerpi/commands","c":"1:0"})
            text = text + "opening the second shade\n"
        else:
            command_list.append({"t":"pi/rollerpi/commands","c":"1:1"})
            text = text + "closing the second shade\n"
    elif "third shade" in command:
        if "open" in command:
            command_list.append({"t":"pi/rollerpi/commands","c":"2:0"})
            text = text + "opening the third shade\n"
        else:
            command_list.append({"t":"pi/rollerpi/commands","c":"2:1"})
            text = text + "closing the third shade\n"
    elif "shade" in command:
        if "open" in command:
            command_list.append({"t":"pi/rollerpi/commands","c":"5:0"})
            text = text + "opening the shades\n"
        else:
            command_list.append({"t":"pi/rollerpi/commands","c":"5:1"})
            text = text + "closing the shades\n"

    elif "shop door" in command:
        if "open" in command and shop_door == "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:1"})
            text = text + "opening shop door\n"
        if ("close" in command or "shut" in command) and shop_door == "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"1:0"})
            text = text + "closing shop door\n"
    elif "garage door" in command:
        if "open" in command and garage_door == "closed":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:1"})
            text = text + "opening garage door\n"
        if ("close" in command or "shut" in command) and garage_door == "open":
            command_list.append({"t":"pi/baydoorpi/commands","c":"0:0"})
            text = text + "closing garage door\n"

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
    f = homepath+"/"+door+"_door.state"
    with open(f,"w") as write_file:
        write_file.write(state)
    return 'OK'

@app.route('/reportroller/<data>')
def reportroller(data):
    split = data.split('-')
    roller = split[0]
    state = split[1]
    f = homepath+"/"+roller+"_roller.state"
    with open(f,"w") as write_file:
        write_file.write(state)
    return 'OK'

@app.route('/getrollers')
def getrollers():
    dirname = homepath
    
    ext = ('_roller.state')
    states = {}
    for f in os.listdir(dirname):
        if f.endswith(ext):
            s = f.split('/')
            a = s[len(s)-1].split('.')[0].split('_roller')
            label = a[0]
            states[label] = open(dirname+"/"+label+"_roller.state").read().replace("\n","")
        else:
            continue
    return states

@app.route('/getdoors')
def getdoors():
    dirname = homepath
    
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
        f = homepath+"/temperatures.json"
        j = open(f)
    except:
        j = "{}"
    try:
        readings = json.load(j)
    except:
        readings = {}
    f2 = open(homepath+"/"+room+"_thermosettings.json")
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

@app.route('/pireport/<text>')
def pireport(text):
    s = text.replace(", ", "_").replace("-", "_").split(" ")
    name = s[0]
    ip = s[1]
    ts = datetime.now().strftime("%m/%d/%Y_%H:%M:%S")
    #log(name+" "+ip+" "+ts)
    try:
        f = open("/home/pi/pistates.json")
        pi = json.load(f)
    except:
        pi = {}
    pi[name] = {
        "name": name,
        "ip": ip,
        "heartbeat": ts
    }
    with open("/home/pi/pistates.json", "w") as write_file:
        write_file.write(json.dumps(pi))
    return True

@app.route('/getmode')
def getmode():
    f = open(homepath+"/mode.txt")
    return [f.read()]

@app.route('/getreadings')
def getreadings():
    f = open(homepath+"/temperatures.json")
    return json.load(f)

@app.route('/getpassivereadings')
def getpassivereadings():
    f = open(homepath+"/passivetemperatures.json")
    return json.load(f)

@app.route('/thermosettings/<room>')
def thermosettings(room):
    f = open(homepath+"/"+room+"_thermosettings.json")
    return json.load(f)

@app.route('/webthermoset/<data>')
def webthermoset(data):
    if checktoken(request) is not True:
        return 'UNAUTHORIZED'
    thermoset(data)

@app.route('/thermoset/<data>')
def thermoset(data):
    s = data.split('-')
    room = s[0]
    temp_low = int(s[1])
    temp_high = int(s[2])
    f = open(homepath+"/"+room+"_thermosettings.json")
    settings = json.load(f)
    settings["temperature_high_setting"] = temp_high
    settings["temperature_low_setting"] = temp_low

    if len(s) > 3:
        humidity_setting = int(s[3])
        settings["humidity_setting"] = humidity_setting

    if len(s) > 4:
        air_circulation_minutes = int(s[4])
        settings["air_circulation_minutes"] = air_circulation_minutes

    if len(s) > 5:
        humidity_circulation_minutes = int(s[5])
        settings["humidity_circulation_minutes"] = humidity_circulation_minutes

    if len(s) > 6:
        stage_limit_minutes = int(s[6])
        settings["stage_limit_minutes"] = stage_limit_minutes

    if len(s) > 7:
        stage_cooldown_minutes = int(s[7])
        settings["stage_cooldown_minutes"] = stage_cooldown_minutes

    with open(homepath+"/"+room+"_thermosettings.json","w") as write_file:
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
    
    with open(homepath+"/"+room+"_thermoreport.json","w") as write_file:
        write_file.write(json.dumps({
            "cooling": cooling,
            "circulation": circulation,
            "heating": heating,
            "whf": whf
        }))
    return 'OK'

@app.route('/getshellies')
def getshellies():
    f = open(homepath+"/shellies.json")
    return json.load(f)
    
@app.route('/getmotionsensors')
def getmotion():
    f1 = open(homepath+"/shellies.json")
    shellies = json.load(f1)
    f2 = open(homepath+"/rpi/motionsensors.json")
    motionsensors = json.load(f2)
    for sensor in motionsensors:
        if sensor["address"] in shellies.keys():
            sensor["shelly"] = shellies[sensor["address"]]
        else:
            sensor["shelly"] = {"status":{"bat":0,"lux":0,"timestamp":0,"motion":False}}
    return motionsensors

@app.route('/getsysmonlog')
def getsysmonlog():
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = "/home/pi/system_monitor_log_"+logfiledate+".txt"
    f = open(logfile)
    return [f.read()]

@app.route('/getapilog')
def getapilog():
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = homepath+"/app_"+logfiledate+".log"
    f = open(logfile)
    return [f.read()]

@app.route('/getsysmonlog/<logfiledate>')
def getsysmonlogbydate(logfiledate):
    logfile = "/home/pi/system_monitor_log_"+logfiledate+".txt"
    f = open(logfile)
    return [f.read()]

@app.route('/gettemplog')
def gettemplog():
    logfiledate = datetime.now().strftime("%Y%m%d")
    h = datetime.now().hour - 3
    data = []
    while h <= datetime.now().hour:
        hour = str(h)
        if h < 10:
            hour = "0" + hour
        a = gettemplogbydate(logfiledate + hour)
        data = data + a
    return data

@app.route('/gettemplog/<logfiledate>')
def gettemplogbydate(logfiledate):
    logfile = "/home/pi/templog_"+logfiledate+".txt"
    f = open(logfile)
    t = f.read()
    data = []
    for l in t.split('\n'):
        if l == "":
            continue
        data.append(json.loads(l))
    return data

@app.route('/getpowerlog')
def getpowerlog():
    logfiledate = datetime.now().strftime("%Y%m%d")
    return getpowerlogbydate(logfiledate)

@app.route('/getpowerlog/<logfiledate>')
def getpowerlogbydate(logfiledate):
    logfile = "/home/pi/powerlog_"+logfiledate+".txt"
    f = open(logfile)
    t = f.read()
    data = []
    for l in t.split('\n'):
        if l == "":
            continue
        data.append(json.loads(l))
    return data

@app.route('/getapilog/<logfiledate>')
def getapilogbydate(logfiledate):
    logfile = homepath+"/app_"+logfiledate+".log"
    f = open(logfile)
    return [f.read()]

@app.route('/notify/<data>')
def notify(data):
    sms(data,"+19377166465")
    return 'OK'

if __name__ == '__main__':
    if dev is False:
        app.run(debug=False, port=8080, host='192.168.1.201')
    else:
        app.run(debug=True, port=8080, host='127.0.0.1')

