import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime, timedelta
import socket
import os

file_logging = True
myname = socket.gethostname()

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

room = myname.replace("thermopi","")

failed_read_halt_limit = 10
temperature_high_setting = 73
temperature_low_setting = 69
humidity_setting = 50
air_circulation_minutes = 30
circulation_cycle_minutes = 10
ventilation_cycle_minutes = 10
stage_limit_minutes = 15
stage_cooldown_minutes = 5
use_whole_house_fan = False
system_disabled = False
swing_temp_offset = 1
extra_ventilation_circuits = []
extra_circulation_circuits = []
humidification_circuits = []

post = True
temperature = None
humidity = None
failed_reads = 0
last_circulation = datetime.now()
circulate_until = datetime.now() + timedelta(minutes=1)
circulating = False
has_circulated = False
last_ventilation = datetime.now()
ventilate_until = datetime.now() + timedelta(minutes=1)
ventilating = False
has_ventilated = False
start_stage = datetime.now() - timedelta(minutes=1)
delay_stage = datetime.now()
shower_vent = False
status = "loading"

heat = 26
ac = 20
fan = 21

heat_state = False
ac_state = False
fan_state = False
whf_state = False

low = GPIO.HIGH
high = GPIO.LOW

def log(message):
    if type(message) is not type(""):
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d")
    logfile = "/home/pi/thermostat_"+logfiledate+".log"
    entry = timestamp + ": " + message + "\n"
    print(entry)
    if file_logging is True:
        if os.path.exists(logfile):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        with open(logfile, append_write) as write_file:
            write_file.write(entry)

def read_sensor():
    global temperature
    global humidity
    global failed_reads

    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
    while temperature is None and failed_reads < failed_read_halt_limit:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
        if temperature is None:
            failed_reads = failed_reads + 1
            time.sleep(1)
    if temperature is not None:
        temperature = temperature * 9/5.0 + 32

    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    
    if humidity is None:
        humidity = 0
    
    if temperature is None:
        log("sensor failed")
    
    failed_reads = 0

def set_circuit(circuit_pin, state):
    if state is True:
        GPIO.output(circuit_pin, high)
    else:
        GPIO.output(circuit_pin, low)

def heat_off():
    global heat_state
    global last_circulation
    log("heat_off")
    if heat_state is True:
        last_circulation = datetime.now()
    set_circuit(heat, False)
    heat_state = False
    report()

def ac_off():
    global ac_state
    global last_circulation
    global has_circulated
    log("ac_off")
    if ac_state is True:
        last_circulation = datetime.now()
    set_circuit(ac, False)
    ac_state = False
    has_circulated = False
    report()

def fan_off():
    global fan_state
    global last_circulation
    log("fan_off")
    if fan_state is True:
        last_circulation = datetime.now()
    set_circuit(fan, False)
    fan_state = False
    report()

def heat_on():
    global heat_state
    log("heat_on")
    if ac_state is True or fan_state is True:
        return
    set_circuit(heat, True)
    heat_state = True
    report()

def ac_on():
    global ac_state
    log("ac_on")
    if heat_state is True or fan_state is True:
        return
    set_circuit(ac, True)
    ac_state = True
    report()

def fan_on():
    global fan_state
    log("fan_on")
    if ac_state is True or heat_state is True:
        return
    set_circuit(fan, True)
    fan_state = True
    report()

def whf_on():
    global whf_state
    global shower_vent
    global status
    log("whf_on")
    whf_state = True
    sendCommand('turn on whole house fan')
    for evc in extra_ventilation_circuits:
        sendCommand('turn on '+evc)
    mode = getMode()
    more = temperature is not None and temperature > temperature_high_setting + 3
    if more is True and mode != "shower":
        status = "assisted_ventilation"
        sendCommand('turn on shower fan')
        shower_vent = True
    report()

def whf_off():
    global whf_state
    global shower_vent
    log("whf_off")
    whf_state = False
    sendCommand('turn off whole house fan')
    for evc in extra_ventilation_circuits:
        sendCommand('turn off '+evc)
    mode = getMode()
    if shower_vent is True and mode != "shower":
        sendCommand('turn off shower fan')
    shower_vent = False
    report()

def halt():
    global fan_state
    global heat_state
    global ac_state
    global whf_state
    log("halt")
    GPIO.output(heat, low)
    GPIO.output(ac, low)
    GPIO.output(fan, low)
    sendCommand('turn off whole house fan')
    sendCommand('turn off circulating fan')
    sendCommand('turn off floor fan')
    fan_state = False
    heat_state = False
    ac_state = False
    whf_state = False
    report()

def getMode():
    try:
        r =requests.get('https://{YOUR API HERE}/getmode')
        data = json.loads(r.text)
        return data["mode"].lower()
    except:
        return "unknown"

def cycle():
    global last_circulation
    global status

    load_settings()

    read_sensor()
    if temperature is None or temperature == 0:
        status = "sensor_fail"

    if temperature is None:
        halt()
        status = "halted"
        return
    
    report_readings()

    if circulating is True:
        if datetime.now() > circulate_until:
            stop_circulating()
        else:
            return

    if ventilating is True:
        if datetime.now() > ventilate_until:
            stop_ventilating()
        else:
            return

    if delay_stage > datetime.now():
        status = "delayed"
        return

    if system_disabled is True:
        status = "disabled"
        if ac_state is True:
            ac_off()
        if heat_state is True:
            heat_off()
        if circulating is True:
            stop_circulating()
        if ventilating is True:
            stop_ventilating()
        return
    
    if round(temperature) > temperature_high_setting and ac_state is False:
        cool_down()
        return
    
    if round(temperature) > temperature_high_setting - swing_temp_offset and ac_state is True: # cool beyond the on limit
        cool_down()
        return
    
    if round(temperature) < temperature_low_setting and heat_state is False:
        warm_up()
        return
    
    if round(temperature) < temperature_low_setting + swing_temp_offset and heat_state is True: # heat beyond the on limit
        warm_up()
        return
    
    if heat_state is True:
        heat_off()
    
    if ac_state is True:
        ac_off()

    if air_circulation_minutes > 0 and datetime.now() > last_circulation + timedelta(minutes=air_circulation_minutes):
        circulate_air(circulation_cycle_minutes)
        return
        
    status = "stand_by"

def cool_down():
    global start_stage
    global delay_stage
    global has_ventilated
    global status
    if ac_state is True:
        if start_stage < datetime.now() - timedelta(minutes=stage_limit_minutes):
            delay_stage = datetime.now() + timedelta(minutes=stage_cooldown_minutes)
            ac_off()
        return
    # if round(humidity) > humidity_setting and humidity_setting > 0 and has_circulated is False:
    #     circulate_air(circulation_cycle_minutes)
    if temperature > temperature_high_setting + 2 and has_ventilated is False:
        ventilate_air(ventilation_cycle_minutes)
    has_ventilated = False
    start_stage = datetime.now()
    ac_on()
    status = "cooling"

def warm_up():
    global start_stage
    global delay_stage
    global status
    if heat_state is True:
        if start_stage < datetime.now() - timedelta(minutes=stage_limit_minutes):
            delay_stage = datetime.now() + timedelta(minutes=stage_cooldown_minutes)
            heat_off()
        return
    start_stage = datetime.now()
    heat_on()
    status = "heating"

def circulate_air(minutes):
    global circulate_until
    global circulating
    global status
    if circulating is True:
        return
    fan_on()
    circulate_until = datetime.now() + timedelta(minutes=minutes) 
    circulating = True
    status = "circulating"

def ventilate_air(minutes):
    global ventilate_until
    global ventilating
    global status
    if ventilating is True:
        return
    if use_whole_house_fan is True:
        whf_on()
    ventilate_until = datetime.now() + timedelta(minutes=minutes) 
    ventilating = True
    status = "ventilating"

def stop_circulating():
    global circulating
    global has_circulated
    global status
    fan_off()
    circulating = False
    has_circulated = True

def stop_ventilating():
    global ventilating
    global has_ventilated
    global status
    if use_whole_house_fan is True:
        whf_off()
    ventilating = False
    has_ventilated = True

def sendCommand(command):
    print("sending command: "+command)
    try:
        r =requests.get('https://{YOUR API HERE}/control/'+command)
        print(str(r.status_code))
    except:
        print('failed to send command')

def report():
    global status
    hum = humidity
    temp = temperature
    #print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    if humidity == None:
        hum = 0
    if temperature == None:
        temp = 0
    cool = "off"
    if ac_state is True:
        cool = "on"
    circ = "off"
    if fan_state is True:
        circ = "on"
    h = "off"
    if heat_state is True:
        h = "on"
    w = "off"
    if whf_state is True:
        w = "on"
    if system_disabled is True:
        status = "disabled"
    log('report: {0:0.1f} F {1:0.1f}% AC:{2} Fan:{3} Heat:{4} WHF:{5} Status:{6} Last Start:{7} Last Circ:{8}'.format(temp, hum,cool,circ,h,w,status,start_stage.strftime("%m/%d/%Y, %H:%M:%S"),last_circulation.strftime("%m/%d/%Y, %H:%M:%S")))
    report_readings()

def load_settings():
    global failed_read_halt_limit
    global temperature_high_setting
    global temperature_low_setting
    global humidity_setting
    global air_circulation_minutes
    global circulation_cycle_minutes
    global ventilation_cycle_minutes
    global stage_limit_minutes
    global stage_cooldown_minutes
    global use_whole_house_fan
    global swing_temp_offset
    global extra_ventilation_circuits
    global extra_circulation_circuits
    global humidification_circuits
    global system_disabled

    try:
        r =requests.get('https://{YOUR API HERE}/thermosettings/'+room)
        j = r.text
        s = json.loads(j)
        failed_read_halt_limit = s["failed_read_halt_limit"]
        temperature_high_setting = s["temperature_high_setting"]
        temperature_low_setting = s["temperature_low_setting"]
        humidity_setting = s["humidity_setting"]
        air_circulation_minutes = s["air_circulation_minutes"]
        circulation_cycle_minutes = s["circulation_cycle_minutes"]
        ventilation_cycle_minutes = s["ventilation_cycle_minutes"]
        stage_limit_minutes = s["stage_limit_minutes"]
        stage_cooldown_minutes = s["stage_cooldown_minutes"]
        use_whole_house_fan = s["use_whole_house_fan"]
        swing_temp_offset = s["swing_temp_offset"]
        extra_ventilation_circuits = s["extra_ventilation_circuits"]
        extra_circulation_circuits = s["extra_circulation_circuits"]
        humidification_circuits = s["humidification_circuits"]
        system_disabled = s["system_disabled"]
        if temperature_high_setting <= temperature_low_setting:
            temperature_high_setting = temperature_low_setting + swing_temp_offset + 1
    except:
        print('failed to get thermosettings')
        log("failed to load thermosettings.json")

def report_readings():
    hum = humidity
    temp = temperature
    #print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    if humidity == None:
        hum = 0
    if temperature == None:
        temp = 0
    cool = "off"
    if ac_state is True:
        cool = "on"
    circ = "off"
    if fan_state is True:
        circ = "on"
    h = "off"
    if heat_state is True:
        h = "on"
    w = "off"
    if whf_state is True:
        w = "on"
    try:
        r =requests.get('https://{YOUR API HERE}/reportreadings/'+room+':{0:0.1f}:{1:0.1f}:{2}:{3}:{4}:{5}:{6}:{7}:{8}'.format(temp, hum,cool,circ,h,w,status,start_stage.strftime("%m~%d~%Y, %H-%M-%S"),last_circulation.strftime("%m~%d~%Y, %H-%M-%S")))
        print("report response: "+str(r.status_code))
    except:
        print('failed to send readings')
        log('failed to send readings')
print("*\n*\n*\nbegin")
log("*\n*\n*\nbegin power-on self-test")
halt()
time.sleep(2)
#circulate_air(2, False)
post = False
log("*\n*\n*\nbegin cycling")
while True:
    try:
        cycle()
    except:
        print("BAD CYCLE!!!")
    time.sleep(10)