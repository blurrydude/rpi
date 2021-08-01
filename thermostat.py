import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime, timedelta
import socket

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

temperature = None
humidity = None
failed_reads = 0
last_circulation = datetime.now()
circulate_until = datetime.now() + timedelta(minutes=1)
circulating = False
start_stage = datetime.now() - timedelta(minutes=1)
delay_stage = datetime.now()

heat = 26
ac = 20
fan = 21

heat_state = False
ac_state = False
fan_state = False
whf_state = False

low = GPIO.HIGH
high = GPIO.LOW

def read_sensor():
    global temperature
    global humidity
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
    temperature = temperature * 9/5.0 + 32

    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    
    if humidity is None:
        humidity = 0

def set_circuit(circuit_pin, state):
    if state is True:
        GPIO.output(circuit_pin, high)
    else:
        GPIO.output(circuit_pin, low)

def heat_off():
    global heat_state
    global last_circulation
    if heat_state is True:
        last_circulation = datetime.now()
    set_circuit(heat, False)
    heat_state = False
    report()

def ac_off():
    global ac_state
    global last_circulation
    if ac_state is True:
        last_circulation = datetime.now()
    set_circuit(ac, False)
    ac_state = False
    report()

def fan_off():
    global fan_state
    global last_circulation
    if fan_state is True:
        last_circulation = datetime.now()
    set_circuit(fan, False)
    fan_state = False
    report()

def heat_on():
    global heat_state
    if ac_state is True or fan_state is True:
        return
    set_circuit(heat, True)
    heat_state = True
    report()

def ac_on():
    global ac_state
    if heat_state is True or fan_state is True:
        return
    set_circuit(ac, True)
    ac_state = True
    report()

def fan_on():
    global fan_state
    if ac_state is True or heat_state is True:
        return
    set_circuit(fan, True)
    fan_state = True
    report()

def halt():
    GPIO.output(heat, low)
    GPIO.output(ac, low)
    GPIO.output(fan, low)

def cycle():
    global failed_reads
    global last_circulation

    load_settings()

    while temperature is None and failed_reads < failed_read_halt_limit:
        read_sensor()
        if temperature is None:
            failed_reads = failed_reads + 1
            time.sleep(1)

    if temperature is None:
        halt()
    
    report_readings()

    if circulating is True:
        if datetime.now() > circulate_until:
            stop_circulating()
        else:
            return

    if delay_stage > datetime.now():
        print("delayed")
        return
    
    if round(temperature) > temperature_high_setting:
        cool_down()
        return
    
    if round(temperature) < temperature_low_setting:
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
    if ac_state is True:
        if start_stage < datetime.now() - timedelta(minutes=stage_limit_minutes):
            delay_stage = datetime.now() + timedelta(minutes=stage_cooldown_minutes)
            ac_off()
        return
    if round(humidity) > humidity_setting and humidity_setting > 0:
        circulate_air(humidity_circulation_minutes, True)
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

def circulate_air(minutes, use_whf):
    global whf_state
    global circulate_until
    global circulating
    fan_on()
    if use_whf is True and use_whole_house_fan is True:
        whf_state = True
        report()
        sendCommand('turn on whole house fan')
    circulate_until = datetime.now() + timedelta(minutes=minutes)
    circulating = True

def stop_circulating():
    global whf_state
    global circulating
    if whf_state is True and use_whole_house_fan is True:
        whf_state = False
        report()
        sendCommand('turn off whole house fan')
    fan_off()
    circulating = False

def sendCommand(command):
    print("sending command: "+command)
    try:
        r =requests.get('https://api.idkline.com/control/'+command)
        print(str(r.status_code))
    except:
        print('failed to send command')

def report():
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
    except:
        print('failed to get thermosettings')

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
        r =requests.get('https://api.idkline.com/reportreadings/'+room+':{0:0.1f}:{1:0.1f}:{2}:{3}:{4}:{5}'.format(temp, hum,cool,circ,h,w))
        print(str(r.status_code))
    except:
        print('failed to send readings')
print("*\n*\n*\nbegin")
halt()
time.sleep(10)
circulate_air(2, False)
while True:
    try:
        cycle()
    except:
        print("BAD CYCLE!!!")
    time.sleep(10)