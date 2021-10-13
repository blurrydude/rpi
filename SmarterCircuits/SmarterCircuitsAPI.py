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

        @self.app.route('/state',methods=['GET'])
        def state():
            peers = []
            for peer in self.mcp.peers:
                peers.append({
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
            thermostats = []
            for thermostat in self.mcp.thermostats:
                thermostats.append({
                    "room": thermostat.room,
                    "settings": {
                        "failed_read_halt_limit": thermostat.settings.failed_read_halt_limit,
                        "temperature_high_setting": thermostat.settings.temperature_high_setting,
                        "temperature_low_setting": thermostat.settings.temperature_low_setting,
                        "humidity_setting": thermostat.settings.humidity_setting,
                        "air_circulation_minutes": thermostat.settings.air_circulation_minutes,
                        "circulation_cycle_minutes": thermostat.settings.circulation_cycle_minutes,
                        "ventilation_cycle_minutes": thermostat.settings.ventilation_cycle_minutes,
                        "stage_limit_minutes": thermostat.settings.stage_limit_minutes,
                        "stage_cooldown_minutes": thermostat.settings.stage_cooldown_minutes,
                        "use_whole_house_fan": thermostat.settings.use_whole_house_fan,
                        "system_disabled": thermostat.settings.system_disabled,
                        "swing_temp_offset": thermostat.settings.swing_temp_offset
                    },
                    "state": {
                        "temperature": thermostat.state.temperature,
                        "humidity": thermostat.state.humidity,
                        "heat_on": thermostat.state.heat_on,
                        "ac_on": thermostat.state.ac_on,
                        "fan_on": thermostat.state.fan_on,
                        "whf_on": thermostat.state.whf_on,
                        "status": thermostat.state.status
                    }
                })
            circuits = []
            for circuit in self.mcp.config.circuits:
                circuits.append({
                    "id": circuit.id,
                    "ip_address": circuit.ip_address,
                    "name": circuit.name,
                    "relay_id": circuit.relay_id,
                    "rollershutter": circuit.rollershutter,
                    "location": circuit.location,
                    "zones": circuit.zones,
                    "on_modes": circuit.on_modes,
                    "off_modes": circuit.off_modes,
                    "status": {
                        "relay": {
                            "on": circuit.status.relay.on,
                            "power": circuit.status.relay.power,
                            "energy": circuit.status.relay.energy
                        },
                        "temperature": circuit.status.temperature,
                        "temperature_f": circuit.status.temperature_f,
                        "overtemperature": circuit.status.overtemperature,
                        "temperature_status": circuit.status.temperature_status,
                        "voltage": circuit.status.voltage
                    }
                })
            rollershades = []
            for rollershade in self.mcp.rollershades:
                rollershades.append({
                    "name": rollershade.name,
                    "shade_up": rollershade.shade_up
                })
            return {
                "peers": peers,
                "thermostats": thermostats,
                "rollershades": rollershades,
                "circuits": circuits
            }
        
        @self.app.route('/control/<text>')
        def control(text):
            self.mcp.mqtt.publish("smarter_circuits/command",text)

        _thread.start_new_thread(self.start, ())

    def start(self):
        self.app.run(debug=False, port=8080, host=self.mcp.ip_address)
