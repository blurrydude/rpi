import json
from datetime import datetime

class SmarterCircuitDevice:
    def __init__(self, data):
        self.mqtt_address = data["mqtt_address"]
        self.ip_address = data["ip_address"]
        self.name = data["name"]
        if data["last_message"] is None or data["last_message"] == "":
            self.last_message = None
        else:
            self.last_message = datetime.strptime(data["last_message"], "%m/%d/%Y, %H:%M:%S")
    
    def handleMessage(self, topic, message):
        print(topic)
        print(message)
        self.last_message = datetime.now()

class SmarterCircuitComponent(SmarterCircuitDevice):
    def __init__(self, data):
        SmarterCircuitDevice.__init__(self,data)
        self.version = data["version"]
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitServer(SmarterCircuitComponent):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitComponent.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

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
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitControlPanel(SmarterCircuitComponent):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitComponent.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitWebServer(SmarterCircuitServer):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitServer.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitRollerController(SmarterCircuitComponent):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitComponent.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitMQTTServer(SmarterCircuitServer):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitServer.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)

class SmarterCircuitThermostat(SmarterCircuitComponent):
    def __init__(self, json_data):
        data = json.loads(json_data)
        SmarterCircuitComponent.__init__(self,data)
    
    def handleMessage(self, topic, message):
        return super().handleMessage(topic, message)