import time
import _thread
import json
from SmarterLogging import SmarterLog
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS

class SmarterAPI:
    def __init__(self, mcp):
        self.mcp = mcp
        self.app = FlaskAPI(__name__)
        self.cors = CORS(self.app, resources={r"/*": {"origins": "*"}})

        @self.app.route('/pistates',methods=['GET'])
        def pistates():
            output = []
            for peer in self.mcp.peers:
                output.append({
                    "id": peer.id,
                    "name": peer.name,
                    "ip_address": peer.ip_address,
                    "model": peer.model,
                    "circuit_authority": peer.circuit_authority,
                    "timestamp": peer.timestamp,
                    "thermostat": peer.thermostat,
                    "rollershade": peer.rollershade,
                    "rollerdoor": peer.rollerdoor
                })
            return output
        
        @self.app.route('/states',methods=['GET'])
        def states():
            output = []
            for circuit in self.mcp.config.circuits:
                output.append({
                    "id": self.id,
                    "ip_address": self.ip_address,
                    "name": self.name,
                    "relay_id": self.relay_id,
                    "rollershutter": self.rollershutter,
                    "location": self.location,
                    "zones": self.zones,
                    "on_modes": self.on_modes,
                    "off_modes": self.off_modes,
                    "status": {
                        "relay": {
                            "on": self.status.relay.on,
                            "power": self.status.relay.power,
                            "energy": self.status.relay.energy
                        },
                        "temperature": self.status.temperature,
                        "temperature_f": self.status.temperature_f,
                        "overtemperature": self.status.overtemperature,
                        "temperature_status": self.status.temperature_status,
                        "voltage": self.status.voltage
                    }
                })
            return output
        
        @self.app.route('/control/<text>')
        def control(text):
            self.mcp.mqtt.publish("smarter_circuits/command",text)

        _thread.start_new_thread(self.start, ())

    def start(self):
        self.app.run(debug=False, port=8080, host=self.mcp.ip_address)
