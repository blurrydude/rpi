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
humidity_circulation_minutes = 10
stage_limit_minutes = 15
stage_cooldown_minutes = 5
use_whole_house_fan = False
swing_temp_offset = 1

post = True
temperature = None
humidity = None
failed_reads = 0
last_circulation = datetime.now()
circulate_until = datetime.now() + timedelta(minutes=1)
circulating = False
start_stage = datetime.now() - timedelta(minutes=1)
delay_stage = datetime.now()
has_circulated = False
base_humidity = 0

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
    log("ac_off")
    if ac_state is True:
        last_circulation = datetime.now()
    set_circuit(ac, False)
    ac_state = False
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
    log("whf_on")
    whf_state = True
    sendCommand('turn on whole house fan')
    report()

def whf_off():
    global whf_state
    log("whf_off")
    whf_state = False
    sendCommand('turn off whole house fan')
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
    fan_state = False
    heat_state = False
    ac_state = False
    whf_state = False
    report()

def cycle():
    global last_circulation
    #global base_humidity

    load_settings()

    read_sensor()

    if temperature is None:
        halt()
        return
    
    report_readings()

    if circulating is True:
        #if (humidity is not None and humidity > base_humidity - 0.2) or datetime.now() > circulate_until: # the humidity should fall for a bit, but when it starts to come back up, that means the air from the basement has arrived, also we should bail if it runs too long
        if datetime.now() > circulate_until:
            stop_circulating()
        else:
            #base_humidity = humidity
            return

    if delay_stage > datetime.now():
        print("delayed")
        return
    
    if round(temperature) > temperature_high_setting and ac_state is False:
        cool_down()
        return
    
    if round(temperature) > temperature_high_setting - swing_temp_offset and ac_state is True: # this is half of my mercury switch/magnet for delaying a "swing" state
        cool_down()
        return
    
    if round(temperature) < temperature_low_setting and heat_state is False:
        warm_up()
        return
    
    if round(temperature) < temperature_low_setting + swing_temp_offset and heat_state is True: # this is the other half of my mercury switch/magnet for delaying a "swing" state
        warm_up()
        return
    
    if heat_state is True:
        heat_off()
    
    if ac_state is True:
        ac_off()

    if air_circulation_minutes > 0 and datetime.now() > last_circulation + timedelta(minutes=air_circulation_minutes):
        circulate_air(humidity_circulation_minutes, False)

def cool_down():
    global start_stage
    global delay_stage
    global has_circulated
    if ac_state is True:
        if start_stage < datetime.now() - timedelta(minutes=stage_limit_minutes):
            delay_stage = datetime.now() + timedelta(minutes=stage_cooldown_minutes)
            ac_off()
        return
    if round(humidity) > humidity_setting and humidity_setting > 0 and has_circulated is False:
        circulate_air(humidity_circulation_minutes, True)
    has_circulated = False
    start_stage = datetime.now()
    ac_on()

def warm_up():
    global start_stage
    global delay_stage
    if heat_state is True:
        if start_stage < datetime.now() - timedelta(minutes=stage_limit_minutes):
            delay_stage = datetime.now() + timedelta(minutes=stage_cooldown_minutes)
            heat_off()
        return
    start_stage = datetime.now()
    heat_on()

def circulate_air(minutes, use_whf_if_set):
    global whf_state
    global circulate_until
    global circulating
    global base_humidity
    if circulating is True:
        return
    fan_on()
    if use_whf_if_set is True and use_whole_house_fan is True:
        whf_on()
    # if humidity is not None:
    #     base_humidity = humidity + 0.5 # in case the humidity wiggles a bit at the wrong time
    circulate_until = datetime.now() + timedelta(minutes=minutes) 
    circulating = True

def stop_circulating():
    global whf_state
    global circulating
    global has_circulated
    if whf_state is True and use_whole_house_fan is True:
        whf_off()
    fan_off()
    circulating = False
    has_circulated = True

def sendCommand(command):
    print("sending command: "+command)
    try:
        r =requests.get('https://api.idkline.com/control/'+command)
        print(str(r.status_code))
    except:
        print('failed to send command')

def report():
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
    status = "normal"
    if delay_stage > datetime.now():
        status = "delayed"
    if temperature is None or temperature == 0:
        status = "sensor_fail"
    if post is True:
        status = "post"
    log('report: {0:0.1f} F {1:0.1f}% AC:{2} Fan:{3} Heat:{4} WHF:{5} Status:{6} Last Start:{7} Last Circ:{8}'.format(temp, hum,cool,circ,h,w,status,start_stage.strftime("%m/%d/%Y, %H:%M:%S"),last_circulation.strftime("%m/%d/%Y, %H:%M:%S")))
    report_readings()

def load_settings():
    global failed_read_halt_limit
    global temperature_high_setting
    global temperature_low_setting
    global humidity_setting
    global air_circulation_minutes
    global humidity_circulation_minutes
    global stage_limit_minutes
    global stage_cooldown_minutes
    global use_whole_house_fan
    global swing_temp_offset

    try:
        r =requests.get('https://api.idkline.com/thermosettings/'+room)
        j = r.text
        s = json.loads(j)
        failed_read_halt_limit = s["failed_read_halt_limit"]
        temperature_high_setting = s["temperature_high_setting"]
        temperature_low_setting = s["temperature_low_setting"]
        humidity_setting = s["humidity_setting"]
        air_circulation_minutes = s["air_circulation_minutes"]
        humidity_circulation_minutes = s["humidity_circulation_minutes"]
        stage_limit_minutes = s["stage_limit_minutes"]
        stage_cooldown_minutes = s["stage_cooldown_minutes"]
        use_whole_house_fan = s["use_whole_house_fan"]
        swing_temp_offset = s["swing_temp_offset"]
        #log("loaded thermosettings.json")
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
    status = "normal"
    if delay_stage > datetime.now():
        status = "delayed"
    if temperature is None or temperature == 0:
        status = "sensor_fail"
    try:
        r =requests.get('https://api.idkline.com/reportreadings/'+room+':{0:0.1f}:{1:0.1f}:{2}:{3}:{4}:{5}:{6}:{7}:{8}'.format(temp, hum,cool,circ,h,w,status,start_stage.strftime("%m~%d~%Y, %H-%M-%S"),last_circulation.strftime("%m~%d~%Y, %H-%M-%S")))
        print("report response: "+str(r.status_code))
    except:
        print('failed to send readings')
        log('failed to send readings')
print("*\n*\n*\nbegin")
log("*\n*\n*\nbegin power-on self-test")
halt()
time.sleep(60)
circulate_air(2, False)
post = False
log("*\n*\n*\nbegin cycling")
while True:
    try:
        cycle()
    except:
        print("BAD CYCLE!!!")
    time.sleep(10)