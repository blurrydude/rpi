import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime, timedelta

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

failed_read_halt_limit = 10
temperature_high_setting = 73
temperature_low_setting = 69
humidity_setting = 50
air_circulation_minutes = 30
humidity_circulation_minutes = 10

temperature = None
humidity = None
failed_reads = 0
last_circulation = datetime.now()
start_circulation = datetime.now()

heat = 26
ac = 20
fan = 21

heat_state = False
ac_state = False
fan_state = False
whf_state = False

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
        GPIO.output(circuit_pin, GPIO.HIGH)
    else:
        GPIO.output(circuit_pin, GPIO.LOW)

def heat_off():
    global heat_state
    global last_circulation
    if heat_state is True:
        last_circulation = datetime.now()
    set_circuit(heat, False)
    heat_state = False

def ac_off():
    global ac_state
    global last_circulation
    if ac_state is True:
        last_circulation = datetime.now()
    set_circuit(ac, False)
    ac_state = False

def fan_off():
    global fan_state
    global last_circulation
    if fan_state is True:
        last_circulation = datetime.now()
    set_circuit(fan, False)
    fan_state = False

def heat_on():
    global heat_state
    if ac_state is True or fan_state is True:
        return
    set_circuit(heat, True)
    heat_state = True

def ac_on():
    global ac_state
    if heat_state is True or fan_state is True:
        return
    set_circuit(ac, True)
    ac_state = True

def fan_on():
    global fan_state
    if ac_state is True or heat_state is True:
        return
    set_circuit(fan, True)
    fan_state = True

def halt():
    GPIO.output(heat, GPIO.LOW)
    GPIO.output(ac, GPIO.LOW)
    GPIO.output(fan, GPIO.LOW)

def cycle():
    global failed_reads
    global last_circulation
    global start_circulation

    load_settings()

    while temperature is None and failed_reads < failed_read_halt_limit:
        read_sensor()
        if temperature is None:
            failed_reads = failed_reads + 1
            time.sleep(1)

    if temperature is None:
        halt()
    
    if round(temperature) > temperature_high_setting:
        cool_down()
        return
    
    if round(temperature) < temperature_low_setting:
        warm_up()
        return

    if air_circulation_minutes > 0 and datetime.now() > last_circulation + timedelta(minutes=air_circulation_minutes):
        start_circulation = datetime.now()
        circulate_air(humidity_circulation_minutes, False)

def cool_down():
    if ac_state is True:
        return
    if round(humidity) > humidity_setting and humidity_circulation_minutes > 0:
        circulate_air(humidity_circulation_minutes, True)
    ac_on()

def warm_up():
    if heat_state is True:
        return
    heat_on()

def circulate_air(minutes, use_whf):
    fan_on()
    if use_whf is True:
        whf_state = True
        # send whf on command
    time.sleep(60*minutes)
    