import json
import os

class RemoteHandler:
    def __init__(self, mqtt_client):
        self.memory = ""
        self.menu_loc = "main"
        self.multi_input = False
        self.mqtt_client = mqtt_client
        self.config = {}
        self.load_config()
    
    def handle_i4_message(self, raw_message):
        self.load_config()
        message = Shellyi4Message(raw_message)
        button_id = message.source + "-" + message.circuit_id
        button_char = self.config["buttons"][button_id]

    
    def load_config(self):
        self.config = json.load(open(os.path.dirname(os.path.realpath(__file__))+"/"+"remoteconfig.json"))

class Shellyi4Message:
    def __init__(self, jsonData):
        data = json.loads(jsonData)
        self.circuit_id = str(data["params"]["events"][0]["id"])
        self.event = data["params"]["events"][0]["event"]
        self.source = data["src"]