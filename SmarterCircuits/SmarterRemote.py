import json
import os

class RemoteHandler:
    def __init__(self, mcp):
        self.memory = ""
        self.menu_loc = "main"
        self.multi_input = False
        self.mcp = mcp
        self.config = {}
        self.load_config()
    
    def handle_i4_message(self, raw_message):
        message = Shellyi4Message(raw_message)
        if message.event != "btn_up":
            return
        self.load_config()
        button_id = message.source + "-" + message.circuit_id
        button_char = self.config["buttons"][button_id]
        if button_char == "0":
            self.menu_loc = "main"
            menu = self.config["menus"][self.menu_loc]
            self.send_menu(menu)
            return
        menu = self.config["menus"][self.menu_loc]
        option = menu["options"][button_char]
        action = option["action"]
        value = option["value"]
        if action == "nav":
            self.menu_loc = value
            menu = self.config["menus"][self.menu_loc]
            self.send_menu(menu)
            return
        if action == "command":
            self.mcp.execute_command(value)
            #self.send_menu(menu, value + " executed")
        
    def send_menu(self, menu, message = ""):
        if message != "":
            data = message+"\\n"
        else:
            data = menu["title"]+"\\n"
        for k in menu["options"].keys():
            option = menu["options"][k]
            data = data + k + ": " + option["title"] + "\\n"
        self.mcp.mqtt.publish("notifications", data)
    
    def load_config(self):
        self.config = json.load(open(os.path.dirname(os.path.realpath(__file__))+"/"+"remoteconfig.json"))

class Shellyi4Message:
    def __init__(self, jsonData):
        data = json.loads(jsonData)
        self.circuit_id = str(data["params"]["events"][0]["id"])
        self.event = data["params"]["events"][0]["event"]
        self.source = data["src"]