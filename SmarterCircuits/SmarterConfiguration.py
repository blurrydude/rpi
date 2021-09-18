import json
import os
import _thread
import time
from SmarterLogging import SmarterLog
from ShellyDevices import RelayModule, DoorWindowSensor, HumidityTemperatureSensor, MotionSensor

class SmarterConfig:
    def __init__(self):
        self.smarter_config_file = "SmarterConfig.json"
        self.circuits_config_file = "circuits.json"
        self.motion_sensors_file = "motionsensors.json"
        self.th_sensors_file = "thsensors.json"
        self.door_sensors_file = "doorsensors.json"
        self.smarter_config_modified = 0.0
        self.circuits_config_modified = 0.0
        self.motion_sensors_config_modified = 0.0
        self.th_sensors_config_modified = 0.0
        self.door_sensors_config_modified = 0.0
        self.brokers = []
        self.topics = []
        self.circuits = {}
        self.motion_sensors = {}
        self.th_sensors = {}
        self.door_sensors = {}
        self.time_commands = []
        self.running = False
        self.loaded = False
        _thread.start_new_thread(self.change_observer, ())
    
    def log(self, message):
        SmarterLog.log("SmarterConfig", message)

    def stop(self):
        self.log("stop")
        self.running = False
        time.sleep(2)

    def change_observer(self):
        self.log("change_observer")
        self.load()
        self.running = True
        while self.running is True:
            self.check_changes()
            time.sleep(1)

    def load(self):
        self.log("load")
        self.load_config()
        self.load_circuits()
        self.load_motion_sensors()
        self.load_th_sensors()
        self.load_door_sensors()
        self.loaded = True

    def load_config(self):
        self.log("load_config")
        config_data = open(self.smarter_config_file)
        config = json.load(config_data)
        self.brokers = config["brokers"]
        self.topics = config["topics"]

    def load_circuits(self):
        self.log("load_circuits")
        circuit_data = open(self.circuits_config_file)
        circuit_list = json.load(circuit_data)
        for circuit in circuit_list:
            relay_module = RelayModule(circuit["id"],circuit["ip_address"],circuit["name"],circuit["location"],circuit["room"],circuit["zones"],circuit["on_modes"],circuit["off_modes"])
            self.circuits[relay_module.id] = relay_module

    def load_motion_sensors(self):
        self.log("load_motion_sensors")
        motion_sensor_data = open(self.motion_sensors_file)
        self.motion_sensors = json.load(motion_sensor_data)

    def load_th_sensors(self):
        self.log("load_th_sensors")
        th_sensor_data = open(self.th_sensors_file)
        self.th_sensors = json.load(th_sensor_data)

    def load_door_sensors(self):
        self.log("load_door_sensors")
        door_sensor_data = open(self.door_sensors_file)
        self.door_sensors = json.load(door_sensor_data)
        
    def check_changes(self):
        now_smarter_config_modified = os.stat(self.smarter_config_file).st_mtime
        now_circuits_config_modified = os.stat(self.circuits_config_file).st_mtime
        now_motion_sensors_config_modified = os.stat(self.motion_sensors_file).st_mtime
        now_th_sensors_config_modified = os.stat(self.th_sensors_file).st_mtime
        now_door_sensors_config_modified = os.stat(self.door_sensors_file).st_mtime

        if now_smarter_config_modified != self.smarter_config_modified:
            self.smarter_config_modified = now_smarter_config_modified
            self.load_config()

        if now_circuits_config_modified != self.circuits_config_modified:
            self.circuits_config_modified = now_circuits_config_modified
            self.load_circuits()

        if now_motion_sensors_config_modified != self.motion_sensors_config_modified:
            self.motion_sensors_config_modified = now_motion_sensors_config_modified
            self.load_motion_sensors()

        if now_th_sensors_config_modified != self.th_sensors_config_modified:
            self.th_sensors_config_modified = now_th_sensors_config_modified
            self.load_th_sensors()

        if now_door_sensors_config_modified != self.door_sensors_config_modified:
            self.door_sensors_config_modified = now_door_sensors_config_modified
            self.load_door_sensors()