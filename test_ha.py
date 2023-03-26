import requests

state = {
    "ac_on": False,
    "fan_on": False,
    "heat_on": False,
    "humidity": 30.9,
    "status": "idle",
    "temperature": 70.9,
    "whf_on": False
}

settings = {
    "air_circulation_minutes": 10,
    "circulation_cycle_minutes": 10,
    "failed_read_halt_limit": 10,
    "humidity_setting": 0,
    "stage_cooldown_minutes": 10,
    "stage_limit_minutes": 20,
    "swing_temp_offset": 2,
    "system_disabled": False,
    "temperature_high_setting": 76,
    "temperature_low_setting": 72,
    "use_whole_house_fan": False,
    "ventilation_cycle_minutes": 10
}

data = {
    "room": "hallway",
    "state": state,
    "settings": settings
}

with open('/home/ian/ha_token') as f:
    ha_token = f.read().strip()

requests.post(f"http://192.168.2.82:8123/api/states/sensor.hallwaythermostat",data,headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
})