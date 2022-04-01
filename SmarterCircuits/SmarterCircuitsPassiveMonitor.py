from time import sleep
import SmarterCircuitsMQTT
import os
import time

class SmarterCircuitsPassiveMonitor:
    def __init__(self):
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.2.200"],["notifications"],self.on_message)
    
    def on_message(self, client, userdata, message):
        try:
            topic = message.topic
            text = str(message.payload.decode("utf-8"))
            os.system("echo 'on 0.0.0.0' | cec-client -s -d 1")
            print(text)
            time.sleep(30)
            os.system("echo 'standby 0.0.0.0' | cec-client -s -d 1")

        except Exception as e: 
            error = str(e)
            print(error)