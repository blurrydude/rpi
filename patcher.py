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
def doCheck():
    os.system('cd /home/pi/rpi && git pull --all')
    time.sleep(9)
    repo_version_file = '/home/pi/rpi/rpi_version.txt'
    local_version_file = '/home/pi/rpi_version.txt'
    with open(repo_version_file, "r") as read_file:
        repo_version = read_file.read()
    if path.exists(local_version_file) == False:
        with open(local_version_file, "w") as write_file:
            write_file.write("0.1")

    with open(local_version_file, "r") as read_file:
        local_version = read_file.read()

    now = datetime.datetime.now()
    if local_version != repo_version or (now.hour == 0 and now.minute == 0 and webserver is False and whitenoise is False):
        with open(local_version_file, "w") as write_file:
            write_file.write(repo_version)
        time.sleep(1)
    if webserver is True:
        os.system('sudo systemctl restart flaskrest.service')
    if webserver is False:
        os.system('sudo reboot now')
        exit()
        

doCheck()