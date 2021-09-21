import _thread
import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import socket
import sys

class SmarterCircuitControl:
    def __init__(self, config_location):
        self.mqtt_client = None
        self.config_location = config_location
        self.config = {}
        self.running = True
        self.stop = False
    
    def start(self):
        _thread.start_new_thread(self.tcp_listener_thread, ())
        _thread.start_new_thread(self.heartbeat_thread, ())
        count = 0
        while self.running is True:
            time.sleep(1)
            count = count + 1
            if count > 5:
                self.stop = True

    def loadConfig(self):
        f = open(self.config_location)
        self.config = json.load(f)

    def send_receive_tcp_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 4260)
        print('client: connecting to %s port %s' % server_address)
        sock.connect(server_address)
        try:
            
            # Send data
            message = 'This is the message.  It will be repeated.'
            print('client: sending "%s"' % message)
            sock.sendall(message.encode('ascii'))

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                print('client: received "%s"' % data)

        finally:
            print('client: closing socket')
            sock.close()
        
        print("end client thread")

    def heartbeat_thread(self):
        while self.running is True:
            print("beat")
            self.send_receive_tcp_data()
            time.sleep(1)
    
    def mqtt_listener_thread(self):
        print("do stuff")
    
    def tcp_listener_thread(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 4260)
        sock.bind(server_address)
        sock.listen(1)
        while self.stop is False:
            print('server: waiting for a connection')
            connection, client_address = sock.accept()
            try:
                print('server: connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    print('server: received "%s"' % data)
                    if data:
                        print('server: sending data back to the client')
                        connection.sendall(data)
                    else:
                        print('server: no more data from', client_address)
                        break
                    
            finally:
                # Clean up the connection
                print('server: closing connection')
                connection.close()
        self.running = False
        print('server: closing socket')
        sock.close()
        print("end server thread")

class SmarterCircuitHouse:
    def __init__(self):
        self.mqtt_server = None
        self.web_server = None
        self.components = []

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


if __name__ == '__main__':
    controller = SmarterCircuitControl("config.json")
    print("starting")
    controller.start()