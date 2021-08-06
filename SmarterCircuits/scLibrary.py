import json

class SmarterCircuitDevice:
    def __init__(self, data):
        self.mqtt_address = data["mqtt_address"]
        self.ip_address = data["ip_address"]
        self.name = data["name"]
        self.last_message = 

class SmarterCircuit(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)
        self.relay = data["relay"]
        self.on_modes = data["on_modes"]
        self.off_modes = data["off_modes"]
        self.zones = data["zones"]
        self.topics = {
            "temperature": "shellies/"+self.mqtt_address+"/temperature",
            "temperature_f": "shellies/"+self.mqtt_address+"/temperature_f",
            "overtemperature": "shellies/"+self.mqtt_address+"/overtemperature",
            "temperature_status": "shellies/"+self.mqtt_address+"/temperature_status",
            "relay_command": "shellies/"+self.mqtt_address+"/relay/"+self.relay+"/command",
            "relay_state": "shellies/"+self.mqtt_address+"/relay/"+self.relay,
            "relay_power": "shellies/"+self.mqtt_address+"/relay/"+self.relay+"/power",
            "relay_energy": "shellies/"+self.mqtt_address+"/relay/"+self.relay+"/energy"
        }
        self.status = {
            "temperature": 0,
            "temperature_f": 0,
            "overtemperature": 0,
            "temperature_status": "Normal",
            "relay_state": "off",
            "relay_power": 0,
            "relay_energy": 0
        }

class SmarterCircuitControlPanel(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)

class SmarterCircuitWebServer(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)

class SmarterCircuitRollerController(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)

class SmarterCircuitMQTTServer(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)

class SmarterCircuitThermostat(SmarterCircuitDevice):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitDevice.__init__(self,data)