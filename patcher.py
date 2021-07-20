import os
import time
import os.path
from os import path
import datetime
import socket
import json

myname = socket.gethostname()
webserver = myname == "rpi4-web-server"
whitenoise = myname == "whitenoisepi"

if webserver is True:
    from twilio.rest import Client

def sms(message):
    if webserver is False:
        return
    account_sid = 'AC26cbcaf937e606af51c6a384728a4e75' 
    auth_token = '0bbd4df550e70c0e7350aa8db30a7329' 
    client = Client(account_sid, auth_token)
    client.messages.create(  
        messaging_service_sid='MG1cf18075f26dc8ff965a5d2d1940dab5', 
        body=message,      
        to='+19377166465' 
    ) 

lookup = {
    "rpi4-web-server": "app",
    "whitenoisepi": "command_whitenoise",
    "mosquitto": "new_interface",
    "workbenchpi": "new_interface",
    "canvaspi": "mqtt_rgb",
    "clockpi": "mqtt_rgb",
    "gameroompi": "mqtt_rgb",
    "raspberrypi": "new_interface",
    "motorpi": "command_garage"
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
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write(json.dumps(repo_version))

    with open(local_version_file, "r") as read_file:
        local_version = json.load(read_file)

    now = datetime.datetime.now()
    if local_version[whatiuse] != repo_version[whatiuse] or (now.hour == 0 and now.minute == 0 and webserver is False and whitenoise is False):
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version)
        time.sleep(1)
    if webserver is True:
        os.system('sudo cp /home/pi/rpi/new_app.py /var/www/api/app.py && sudo systemctl restart flaskrest.service')
        sms(myname+' updated '+whatiuse+' from '+local_version[whatiuse]+' to '+repo_version[whatiuse])
    if webserver is False:
        os.system('sudo reboot now')
        exit()
        

doCheck()