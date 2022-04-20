from datetime import datetime, timedelta
import json
import time
import paho.mqtt.client as mqtt
import requests

class SmarterRemote:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.running = False
        self.last_status = ""
        self.lux = 0

    def on_connect(self, clent, userdata, flags, rc):
        print("client connected")

    def on_disconnect(self, client, userdata, rc):
        print("client disconnected")

    def start(self):
        self.client.connect("192.168.2.200")
        self.client.subscribe("shellyplusi4-083af200fe38/events/rpc")
        self.running = True
        self.client.loop_start()
        while self.running is True:
            time.sleep(1)
        self.dispose()
    
    def dispose(self):
        self.client.disconnect()
        exit()
    
    def on_message(self, client, userdata, message):
        try:
            topic = message.topic
            if "stopremote" in topic:
                self.running = False
                self.dispose()
            if "shellyplusi4" not in topic:
                return
            text = str(message.payload.decode("utf-8"))
            data = json.loads(text)
            evnt = data["params"]["events"][0]["event"]
            cid = data["params"]["events"][0]["id"]
            if evnt == "single_push" and cid == 0:
                self.client.publish("smarter_circuits/command", "turn on the game room")
                self.client.publish("smarter_circuits/command", "turn on the game tables")
            if evnt == "long_push" and cid == 0:
                self.client.publish("smarter_circuits/command", "turn off the game room")
                self.client.publish("smarter_circuits/command", "turn off the game tables")

            if evnt == "single_push" and cid == 1:
                self.client.publish("smarter_circuits/command", "switch to night mode")
                #requests.get("http://192.168.2.128/rpc/Switch.Toggle?id=0")
            if evnt == "long_push" and cid == 1:
                self.client.publish("smarter_circuits/command", "switch to day mode")
        except:
            donothing = True

if __name__ == "__main__":
    cc = SmarterRemote()
    cc.start()