import time
from os import name
import SmarterCircuitsMQTT
import SmarterConfiguration
from SmarterLogging import SmarterLog
import socket
import subprocess

class SmarterCircuitsMCP:
    def __init__(self, name, ip_address, model):
        self.id = 0
        self.name = name
        self.model = model
        self.ip_address = ip_address
        self.circuit_authority = False
        self.discovery_mode = True
        self.config = None
        self.mqtt = None
        self.peers = []

    def start(self):
        SmarterLog.log("SmarterCircuits","starting...")
        self.config = SmarterConfiguration.SmarterConfig()
        while self.config.loaded is False:
            time.sleep(1)
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(self.config.brokers,["shellies/#","smarter_circuits/#"],self.on_message)
        
        input("Press any key to stop...")

    def stop(self):
        SmarterLog.log("SmarterCircuits","stopping...")
        self.config.stop()
        self.mqtt.stop()
        time.sleep(5)
        SmarterLog.log("Main","stopped.")
        exit()
    
    def on_message(self, client, userdata, message):
        topic = message.topic
        text = str(message.payload.decode("utf-8"))
        if topic.startswith("shellies"):
            self.handle_shelly_message(topic, text)
        if topic.startswith("smarter_circuits"):
            self.handle_smarter_circuits_message(topic, text)
    
    def handle_shelly_message(self, topic, message):
        print(topic+": "+message)
        if self.discovery_mode is True:
            return
        return
    
    def handle_smarter_circuits_message(self, topic, message):
        print(topic+": "+message)

if __name__ == "__main__":
    myname = socket.gethostname()
    myip = subprocess.check_output(['hostname', '-I']).decode("utf-8").replace("\n","")
    uname = subprocess.check_output(['uname','-m']).decode("utf-8").replace("\n","")
    model = "pc"
    if uname.__contains__("Raspberry"):
        model = subprocess.check_output(['cat','/proc/device-tree/model'])
    print(uname)
    print(model)
    mcp = SmarterCircuitsMCP(myname, myip, model)