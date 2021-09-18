import json
import os
import _thread
import time
from SmarterLogging import SmarterLog
from ShellyDevices import RelayModule, DoorWindowSensor, HumidityTemperatureSensor, MotionSensor, MotionSensorCommand, CommandCondition

class SmarterConfig:
    def __init__(self, home_dir):
        self.smarter_config_file = home_dir+"SmarterConfig.json"
        self.circuits_config_file = home_dir+"circuits.json"
        self.motion_sensors_file = home_dir+"motionsensors.json"
        self.ht_sensors_file = home_dir+"thsensors.json"
        self.door_sensors_file = home_dir+"doorsensors.json"
        self.smarter_config_modified = 0.0
        self.circuits_config_modified = 0.0
        self.motion_sensors_config_modified = 0.0
        self.ht_sensors_config_modified = 0.0
        self.door_sensors_config_modified = 0.0
        self.brokers = []
        self.topics = []
        self.circuits = []
        self.motion_sensors = {}
        self.ht_sensors = {}
        self.door_sensors = {}
        self.time_commands = []
        self.touchscreen = False
        self.running = False
        self.loaded = False
        self.command_endpoint = ""
        self.use_api = False
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
        self.load_ht_sensors()
        self.load_door_sensors()
        self.loaded = True

    def load_config(self):
        self.log("load_config")
        config_data = open(self.smarter_config_file)
        config = json.load(config_data)
        self.brokers = config["brokers"]
        self.topics = config["topics"]
        self.command_endpoint = config["command_endpoint"]
        self.use_api = config["use_api"]
        self.touchscreen = config["touchscreen"]

    def load_circuits(self):
        self.log("load_circuits")
        circuit_data = open(self.circuits_config_file)
        circuit_list = json.load(circuit_data)
        self.circuits = []
        for circuit in circuit_list:
            #TODO: fix room
            self.circuits.append(RelayModule(circuit["id"],circuit["ip_address"],circuit["name"],circuit["relay_id"],circuit["location"],"",circuit["zones"],circuit["on_modes"],circuit["off_modes"]))

    def load_motion_sensors(self):
        self.log("load_motion_sensors")
        motion_sensor_data = open(self.motion_sensors_file)
        motion_sensor_list = json.load(motion_sensor_data)
        for sensor in motion_sensor_list:
            motion_sensor = MotionSensor(sensor["id"],sensor["ip_address"],sensor["room"],sensor["auto_off"],sensor["off_time_minutes"])
            for com in sensor["commands"]:
                conditions = []
                for con in com["conditions"]:
                    condition = CommandCondition(con["prop"],con["comparitor"],con["value"])
                    conditions.append(condition)
                command = MotionSensorCommand(com["start"], com["stop"],conditions)
                motion_sensor.commands.append(command)
            self.motion_sensors[motion_sensor.id] = motion_sensor

    def load_ht_sensors(self):
        self.log("load_ht_sensors")
        th_sensor_data = open(self.ht_sensors_file)
        ht_sensor_list = json.load(th_sensor_data)
        for sensor in ht_sensor_list:
            ht_sensor = HumidityTemperatureSensor(sensor["id"], sensor["ip_address"], sensor["name"])
            self.ht_sensors[ht_sensor.id] = ht_sensor

    def load_door_sensors(self):
        self.log("load_door_sensors")
        door_sensor_data = open(self.door_sensors_file)
        door_sensor_list = json.load(door_sensor_data)
        for sensor in door_sensor_list:
            door_sensor = DoorWindowSensor(sensor["id"], sensor["name"], sensor["ip_address"], sensor["open_command"], sensor["close_command"])
            self.door_sensors[door_sensor.id] = door_sensor
        
    def check_changes(self):
        now_smarter_config_modified = os.stat(self.smarter_config_file).st_mtime
        now_circuits_config_modified = os.stat(self.circuits_config_file).st_mtime
        now_motion_sensors_config_modified = os.stat(self.motion_sensors_file).st_mtime
        now_ht_sensors_config_modified = os.stat(self.ht_sensors_file).st_mtime
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

        if now_ht_sensors_config_modified != self.ht_sensors_config_modified:
            self.ht_sensors_config_modified = now_ht_sensors_config_modified
            self.load_ht_sensors()

        if now_door_sensors_config_modified != self.door_sensors_config_modified:
            self.door_sensors_config_modified = now_door_sensors_config_modified
            self.load_door_sensors()