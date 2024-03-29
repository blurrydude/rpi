import time
time.sleep(15)
import requests
import Adafruit_DHT
import RPi.GPIO as GPIO

with open('/home/pi/ha_token') as f:
    ha_token = f.read().strip()

heat_pin = 26
ac_pin = 20
fan_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(heat_pin, GPIO.OUT)
GPIO.setup(ac_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)

ac_on = False
heat_on = False

def set_circuit(circuit_pin, state):
    if state is False:
        GPIO.output(circuit_pin, GPIO.HIGH)
    else:
        GPIO.output(circuit_pin, GPIO.LOW)


set_circuit(heat_pin, False)
set_circuit(ac_pin, False)
set_circuit(fan_pin, False)
while True:
    try:
        flip_ac = requests.get(f"http://192.168.2.82:8123/api/states/input_boolean.gameroom_ac",headers={
                "Authorization": f"Bearer {ha_token}",
                "content-type": "application/json",
            }).json()["state"].lower() == "on"
        flip_heat = requests.get(f"http://192.168.2.82:8123/api/states/input_boolean.gameroom_heat",headers={
                "Authorization": f"Bearer {ha_token}",
                "content-type": "application/json",
            }).json()["state"].lower() == "on"
        if flip_ac is True and flip_heat is True:
            continue
        if flip_ac != ac_on:
            ac_on = flip_ac
            if ac_on:
                set_circuit(ac_pin, True)
            else:
                set_circuit(ac_pin, False)
        if flip_heat != heat_on:
            heat_on = flip_heat
            if heat_on:
                set_circuit(heat_pin, True)
            else:
                set_circuit(heat_pin, False)
    except:
        print("bad cycle")
    time.sleep(10)