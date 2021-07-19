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
        repo_version_json = read_file.read()
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version_json)

    with open(local_version_file, "r") as read_file:
        local_version_json = read_file.read()

    repo_version = json.load(repo_version_json)
    local_version = json.load(local_version_json)

    now = datetime.datetime.now()
    if local_version[whatiuse] != repo_version[whatiuse] or (now.hour == 0 and now.minute == 0 and webserver is False and whitenoise is False):
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version)
        time.sleep(1)
    if webserver is True:
        os.system('sudo systemctl restart flaskrest.service')
    if webserver is False:
        os.system('sudo reboot now')
        exit()
        

doCheck()