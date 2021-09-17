import time
from os import name
import SmarterCircuitsMQTT
import SmarterConfiguration
from SmarterLogging import SmarterLog
import socket
import subprocess
import _thread
import json
from datetime import datetime

class SmarterCircuitsMCP:
    def __init__(self, name, ip_address, model):
        self.id = 0
        self.name = name
        self.model = model
        self.running = False
        self.ticks = 0
        self.ip_address = ip_address
        self.circuit_authority = False
        self.discovery_mode = True
        self.config = None
        self.mqtt = None
        self.peers = []
        _thread.start_new_thread(self.main_loop, ())

    def start(self):
        SmarterLog.log("SmarterCircuits","starting...")
        self.config = SmarterConfiguration.SmarterConfig()
        while self.config.loaded is False:
            time.sleep(1)
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(self.config.brokers,["shellies/#","smarter_circuits/#"],self.on_message)
        
        input("Press any key to stop...")
    
    def main_loop(self):
        self.running = True
        while self.running is True:
            if self.config.loaded is False or self.mqtt.connected is False:
                continue
            if self.ticks >= 59:
                self.ticks = 0
                self.send_peer_data()
                if self.circuit_authority is True:
                    self.do_time_commands()
            time.sleep(1)
    
    def do_time_commands(self):
        donothing = True
    
    def send_peer_data(self):
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.mqtt.publish("smarter_circuits/peers",json.dumps(SmarterCircuitsPeer(self.id, self.name, self.ip_address, self.model, self.circuit_authority, timestamp)))

    def check_circuit_authority(self):
        existing_authority = False
        last_octet = int(self.ip_address.split('.')[3])
        lowest_ip = last_octet
        for peer in self.peers:
            peer_last_octet = int(peer.ip_address.split('.')[3])


    def stop(self):
        SmarterLog.log("SmarterCircuits","stopping...")
        self.running = False
        self.config.stop()
        self.mqtt.stop()
        time.sleep(5)
        SmarterLog.log("SmarterCircuits","stopped.")
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
        if topic == "smarter_circuits/peers":
            self.received_peer_data(json.loads(message))
    
    def received_peer_data(self, peer):
        found = False
        for p in self.peers:
            if p.name == peer.name:
                p = peer
                found = True
        if found is not True:
            self.peers.append(peer)

class SmarterCircuitsPeer:
    def __init__(self, id, name, ip_address, model, circuit_authority, timestamp):
        self.id = id
        self.name = name
        self.ip_address = ip_address
        self.model = model
        self.circuit_authority = circuit_authority
        self.timestamp = timestamp

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