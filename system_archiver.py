import requests
import time
import json
from datetime import datetime
import os

def getTempData():
    r = requests.get('https://api.idkline.com/getreadings')
    readings = json.loads(r.text)
    pr = requests.get('https://api.idkline.com/getpassivereadings')
    preadings = json.loads(pr.text)
    data = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S")]
    for key in readings.keys():
        reading = readings[key]
        data.append(float(reading["temperature"]))
        data.append(float(reading["humidity"]))
        if reading["cooling"]=="on":
            data.append(1)
        if reading["cooling"]=="off":
            data.append(0)
        if reading["heating"]=="on":
            data.append(1)
        if reading["heating"]=="off":
            data.append(0)
        if reading["circulation"]=="on":
            data.append(1)
        if reading["circulation"]=="off":
            data.append(0)
        if reading["whf"]=="on":
            data.append(1)
        if reading["whf"]=="off":
            data.append(0)
    for key in preadings.keys():
        reading = preadings[key]
        data.append(float(reading["temperature"]))
        data.append(float(reading["humidity"]))
    return json.dumps(data)

def logTempData(message):
    logfiledate = datetime.now().strftime("%Y%m%d")
    logfile = "/home/pi/templog_"+logfiledate+".txt"
    entry = message + "\n"
    print(entry)
    if os.path.exists(logfile):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    with open(logfile, append_write) as write_file:
        write_file.write(entry)

def logPowerData(message):
    logfiledate = datetime.now().strftime("%Y%m%d")
    logfile = "/home/pi/powerlog_"+logfiledate+".txt"
    entry = message + "\n"
    print(entry)
    if os.path.exists(logfile):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    with open(logfile, append_write) as write_file:
        write_file.write(entry)

def getPowerData():
    r = requests.get('https://api.idkline.com/powerstates')
    readings = json.loads(r.text)
    data = []
    total = 0.0
    for key in readings.keys():
        v = float(readings[key])
        total = total + v
        data.append(v)
    data.append(round(total))
    return json.dumps(data)

logTempData(getTempData())
logPowerData(getPowerData())