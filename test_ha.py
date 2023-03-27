import requests
import json

with open('/home/ian/ha_token') as f:
    ha_token = f.read().strip()
    
print(requests.get(f"http://192.168.2.82:8123/api/states/input_boolean.hvac_enabled",headers={
    "Authorization": f"Bearer {ha_token}",
    "content-type": "application/json",
}).json()["state"])

