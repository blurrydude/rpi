import os
import time
import os.path
from os import path
import datetime
import socket
import json
import sys
import subprocess
try:
    import psutil
except:
    os.system('pip3 install psutil')
    import psutil


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

lookup = {
    "rpi4-web-server": "app",
    "whitenoisepi": "command_whitenoise",
    "addresspi": "mqtt_rgb",
    "windowpi": "mqtt_rgb",
    "garagecontrolpi": "new_interface",
    "kitchenpi": "new_interface",
    "dayroompi": "new_interface",
    "tablepi": "new_interface",
    "hallwaypi": "new_interface",
    "thermopi": "thermostat",
    "rollerpi": "roller"
}

whatiuse = "command_light"
if myname in lookup.keys():
    whatiuse = lookup[myname]
else:
    try:
        xstart = open('/etc/xdg/lxsession/LXDE-pi/autostart')
        if "new_interface" in xstart:
            whatiuse = "new_interface"
    except:
        whatiuse = "command_light"

    try:
        xstart = open('/etc/rc.local')
        if "mqtt_rgb" in xstart:
            whatiuse = "mqtt_rgb"
        if "command_garage" in xstart:
            whatiuse = "command_garage"
    except:
        whatiuse = "command_light"

def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
    listOfProcessObjects = []
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
    return listOfProcessObjects

def mosquittoDo(topic, command):
    global received
    global result
    if mqtted is False:
        return
    try:
        client = mqtt.Client()
        if "192.168.1" in myip:
            client.connect("192.168.1.200")
        else:
            client.connect("192.168.0.20")
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
        log("Unexpected error:" + sys.exc_info()[0])

def doCheck():
    os.system('cd /home/pi/rpi && git pull --all')
    if myname == "mosquitto":
        os.system('cd /home/pi/rpi && sudo python3 new_automation.py')
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

    if webserver is True:
        print('local command_center: '+local_version["command_center"]+' repo command_center: '+repo_version["command_center"])
        if local_version["command_center"] != repo_version["command_center"]:
            with open(local_version_file, "w") as write_file:
                write_file.write(json.dumps(repo_version))
                print('updated local version file')
            sms('building command center on '+myname+' because version updated from '+local_version["command_center"]+' to '+repo_version["command_center"])
            os.system('cd /home/pi/rpi/command-center && sudo ng build && sudo mv /home/pi/rpi/command-center/dist/command-center/* /var/www/idkline.com/public_html')
            sms('built command center')
        if "system_monitor" not in local_version.keys() or local_version["system_monitor"] != repo_version["system_monitor"]:
            with open(local_version_file, "w") as write_file:
                write_file.write(json.dumps(repo_version))
                print('updated local version file')
            sms('restarting system_monitor on '+myname+' because version updated from '+local_version["system_monitor"]+' to '+repo_version["system_monitor"])
            os.system('cd /home/pi/rpi && sudo killall python3 && sudo python3 system_monitor.py')
            sms('system_monitor restarted')

    if whatiuse not in local_version.keys() or local_version[whatiuse] != repo_version[whatiuse]:
        with open(local_version_file, "w") as write_file:
            write_file.write(json.dumps(repo_version))
            print('updated local version file')
        time.sleep(1)
        if webserver is True:
            print('copying app')
            os.system('sudo cp /home/pi/rpi/new_app.py /var/www/api/app.py && sudo systemctl restart flaskrest.service')
            sms('restarting flask on '+myname+' because '+whatiuse+' updated from '+local_version[whatiuse]+' to '+repo_version[whatiuse])
        if webserver is False:
            try:
                mosquittoDo("pi/"+myname+"/status",myname + " "+str(myip).split(' ')[0].replace("b'","")+" restarting at "+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            except:
                print('nada')
            os.system('sudo reboot now')
            try:
                sms('restarting '+myname+' because '+whatiuse+' updated from '+local_version[whatiuse]+' to '+repo_version[whatiuse])
            except:
                print('neine')
            exit()
        

heartbeat()
doCheck()