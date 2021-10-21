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
import requests

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

def set_circuit_authority(ip_address):
    with open('/home/pi/circuit_authority.txt', 'w') as write_file:
        write_file.write(ip_address)

def get_circuit_authority():
    return open('/home/pi/circuit_authority.txt').read()

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

@app.route('/state',methods=['GET'])
def state():
    circuit_authority = get_circuit_authority()
    r =requests.get('http://'+circuit_authority+':8080/state')
    states = json.loads(r.text)
    return states

@app.route('/circuitauthority',methods=['GET'])
def circuitauthority():
    circuit_authority = get_circuit_authority()
    return circuit_authority

@app.route('/webcontrol/<text>')
def webcontrol(text):
    if checktoken(request) is not True:
        return 'UNAUTHORIZED'
    return control(text)

@app.route('/control/<text>')
def control(text):
    log("incoming text: "+text)
    mosquittoDo("smarter_circuits/command",text)
    return 'OK'

@app.route('/getapilog')
def getapilog():
    logfiledate = datetime.now().strftime("%Y%m%d%H")
    logfile = homepath+"/app_"+logfiledate+".log"
    f = open(logfile)
    return [f.read()]

@app.route('/getapilog/<logfiledate>')
def getapilogbydate(logfiledate):
    logfile = homepath+"/app_"+logfiledate+".log"
    f = open(logfile)
    return [f.read()]

@app.route('/notify/<data>')
def notify(data):
    sms(data,"+19377166465")
    return 'OK'

@app.route('/circuitauthority/<ip_address>')
def circuitauthorityset(ip_address):
    set_circuit_authority(ip_address)

@app.route('/getminers')
def getminers():
    IPS = ('192.168.1.40','192.168.1.41','192.168.1.42','192.168.1.43')
    for IP in IPS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, 4028))
        c = "{\"command\":\"stats\"}"
        s.send(c.encode('utf-8'))
        data = s.recv(2048).decode('utf-8')
        data = format(data)
        x = data.split("id\":1}")
        y = x[0].replace("}{","},{")+"id\":1}"
        s.close()
        return y

if __name__ == '__main__':
    if dev is False:
        app.run(debug=False, port=8080, host='192.168.1.201')
    else:
        app.run(debug=True, port=8080, host='127.0.0.1')

