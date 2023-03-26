import requests
import json
state = {
    "ac_on": False,
    "fan_on": False,
    "heat_on": False,
    "humidity": 30.9,
    "status": "idle",
    "temperature": 70.9,
    "whf_on": False
}
room = "hallway"
ac_on = False
fan_on = False
heat_on = False
whf_on = False

with open('/home/ian/ha_token') as f:
    ha_token = f.read().strip()

tstate = {"state": str(state["temperature"]), "attributes": {"unit_of_measurement": "°F"}}
hstate = {"state": str(state["humidity"]), "attributes": {"unit_of_measurement": "%"}}
print(requests.post(f"http://192.168.2.82:8123/api/states/sensor.{room}_thermostat_temperature",json.dumps(tstate),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))
print(requests.post(f"http://192.168.2.82:8123/api/states/sensor.{room}_thermostat_humidity",json.dumps(hstate),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))
print(requests.post(f"http://192.168.2.82:8123/api/states/binary_sensor.{room}_heat_on",json.dumps({"state":heat_on}),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))
print(requests.post(f"http://192.168.2.82:8123/api/states/binary_sensor.{room}_ac_on",json.dumps({"state":ac_on}),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))
print(requests.post(f"http://192.168.2.82:8123/api/states/binary_sensor.{room}_fan_on",json.dumps({"state":fan_on}),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))
print(requests.post(f"http://192.168.2.82:8123/api/states/binary_sensor.{room}_whf_on",json.dumps({"state":whf_on}),headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}))