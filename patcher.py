import os
import time
import os.path
from os import path
import datetime
import socket
import json
import sys
import subprocess

myname = socket.gethostname()
myip = subprocess.check_output(['hostname', '-I'])
webserver = myname == "rpi4-web-server"
whitenoise = myname == "whitenoisepi"
twilled = False
mqtted = False
f = open('/home/pi/config.json')
config = json.load(f)
try:
    from twilio.rest import Client
    twilled = True
    print('we have twilio')
except:
    os.system('pip3 install twilio')
    twilled = False
    print('we do not have twilio')
try:
    import paho.mqtt.client as mqtt
    mqtted = True
    print('we have paho')
except:
    os.system('pip3 install paho-mqtt')
    mqtted = False
    print('we do not have paho')

def mosquittoDo(topic, command):
    global received
    global result
    if mqtted is False:
        return
    try:
        client = mqtt.Client()
        client.connect("192.168.1.22")
        client.publish(topic,command)
        client.disconnect()
    except:
        print('failed')
    return 'OK'

def heartbeat():
    mosquittoDo("pi/"+myname+"/status",myname + " "+str(myip).split(' ')[0].replace("b'","")+" alive at "+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

def log(message):
    with open('/home/pi/SMS.log','a') as write_file:
        write_file.write(message+'\n')

def sms(message):
    print('sms: '+message)
    if twilled is False:
        return
    try:
        account_sid = config["account_sid"]
        auth_token = config["auth_token"] 
        client = Client(account_sid, auth_token)
        client.messages.create(  
            messaging_service_sid=config["messaging_service_sid"], 
            body=message,      
            to='+19377166465' 
        )
    except:
        log("Unexpected error:", sys.exc_info()[0])

lookup = {
    "rpi4-web-server": "app",
    "whitenoisepi": "command_whitenoise",
    "mosquitto": "new_interface",
    "hallwaypi": "new_interface",
    "canvaspi": "mqtt_rgb",
    "clockpi": "mqtt_rgb",
    "addresspi": "mqtt_rgb",
    "windowpi": "mqtt_rgb",
    "raspberrypi": "new_interface",
    "baydoorpi": "command_garage"
}

whatiuse = "command_light"
if myname in lookup.keys():
    whatiuse = lookup[myname]

def doCheck():
    os.system('cd /home/pi/rpi && git pull --all')
    time.sleep(9)
    repo_version_file = '/home/pi/rpi/version.json'
    local_version_file = '/home/pi/version.json'
    with open(repo_version_file, "r") as read_file:
        repo_version = json.load(read_file)
        print('loaded repo version file')
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write(json.dumps(repo_version))
            print('created new local version file')

    with open(local_version_file, "r") as read_file:
        local_version = None
        try:
            local_version = json.load(read_file)
            print('loaded local version file')
        except:
            with open(local_version_file, "w") as write_file:
                write_file.write(json.dumps(repo_version))
                print('error loading. created local version file')

    print('local: '+local_version[whatiuse]+' repo: '+repo_version[whatiuse])
    now = datetime.datetime.now()
    if local_version[whatiuse] != repo_version[whatiuse] or (now.hour == 0 and now.minute == 0 and webserver is False and whitenoise is False):
        with open(local_version_file, "w") as write_file:
            write_file.write(json.dumps(repo_version))
            print('updated local version file')
        time.sleep(1)
        if webserver is True:
            print('copying app')
            os.system('sudo cp /home/pi/rpi/new_app.py /var/www/api/app.py && sudo systemctl restart flaskrest.service')
            sms('restarting flask on '+myname+' because '+whatiuse+' updated from '+local_version[whatiuse]+' to '+repo_version[whatiuse])
        if webserver is False:
            sms('restarting '+myname+' because '+whatiuse+' updated from '+local_version[whatiuse]+' to '+repo_version[whatiuse])
            mosquittoDo("pi/"+myname+"/status",myname + " "+str(myip).split(' ')[0].replace("b'","")+" restarting at "+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            os.system('sudo reboot now')
            exit()
        

heartbeat()
doCheck()