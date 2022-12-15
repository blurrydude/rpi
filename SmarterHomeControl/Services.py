#! /usr/bin/env python3
import time
import json
import paho.mqtt.client as mqtt

class MQTT:
    def __init__(self, brain):
        self.brain = brain
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
    
    def start(self):
        self.client.connect(self.brain.config.mqtt_broker)
        self.client.subscribe('shellies/#')
        self.client.subscribe('smarter_circuits/sensors/#')
        self.client.subscribe('smarter_circuits/thermostats/#')
        self.client.subscribe('notifications')
        self.client.loop_start()
    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_disconnect(self, client, userdata, rc):
        if self.brain.running is False:
            return
        try:
            time.sleep(10)
            self.start()
        except:
            self.on_disconnect(client, userdata, rc)

    def on_message(self, client, userdata, message):
        try:
            result = str(message.payload.decode("utf-8"))
            topic = message.topic.split('/')
            if topic[0] == "notifications":
                if message != self.brain.last_notification:
                    self.brain.last_notification = result
                    self.brain.ui.draw_all()
                return
            if topic[0] == "shellies":
                self.handle_shelly_message(message.topic, result)
                return
            data = json.loads(result)
            if topic[1] == 'sensors':
                temp = round(data['temp'],2)
                hum = round(data['hum'],2)
                if topic[2] not in self.brain.roomstats.keys() or self.brain.roomstats[topic[2]]["temp"] != temp:
                    self.brain.roomstats[topic[2]] = {"temp":temp, "hum": hum, "hvac":False}
            elif topic[1] == 'thermostats':
                temp = data['state']['temperature']
                hum = data['state']['humidity']
                status = data['state']['status']
                high = data['settings']['temperature_high_setting']
                low = data['settings']['temperature_low_setting']
                disabled = data['settings']['system_disabled']
                if topic[2] not in self.brain.roomstats.keys() or self.brain.roomstats[topic[2]]["temp"] != temp:
                    self.brain.roomstats[topic[2]] = {"temp":temp, "hum": hum, "hvac":True, "high":high, "low":low, "disabled":disabled, "status":status}
        except:
            pass

    def handle_shelly_message(self, topic, message):
        s = topic.split('/')
        id = s[1]
        if "pro4pm" in id:
            self.handle_shelly_pro4pm_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "1pm" in id or "switch25" in id:
            self.handle_shelly_relay_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "dimmer2" in id:
            self.handle_shelly_dimmer_message(id, topic.replace("shellies/"+id+"/",""), message)
        return

    def handle_shelly_pro4pm_message(self, id, topic, message):
        if "status" not in topic:
            return
        data = json.loads(message)
        for circuit in self.brain.circuits:
            if(circuit.id != id):
                continue
            if(int(circuit.relay_id) != data["id"]):
                continue
            circuit.status.relay.on = data["output"]
            on = data["output"]
            if on != circuit.status.relay.on:
                circuit.status.relay.on = data["output"]
                self.brain.ui.check_room_states(circuit.name)
            power = data["apower"]
            if power != circuit.status.relay.power:
                circuit.status.relay.power = power
                self.brain.ui.check_room_states(circuit.name)
            circuit.status.relay.energy = data["current"]
            circuit.status.temperature = data["temperature"]["tC"]
            circuit.status.temperature_f = data["temperature"]["tF"]
            circuit.status.voltage = data["voltage"]

    def handle_shelly_dimmer_message(self, id, subtopic, message):
        for circuit in self.brain.circuits:
            if(circuit.id != id):
                continue
            if subtopic == "light/"+circuit.relay_id:
                on = message == "on"
                if on != circuit.status.relay.on:
                    circuit.status.relay.on = message == "on"
                    self.brain.ui.check_room_states(circuit.name)
            if subtopic == "light/"+circuit.relay_id+"/power":
                power = float(message)
                if power != circuit.status.relay.power:
                    circuit.status.relay.power = power
                    self.brain.ui.check_room_states(circuit.name)
            if subtopic == "light/"+circuit.relay_id+"/energy":
                circuit.status.relay.energy = int(message)
            if subtopic == "temperature":
                circuit.status.temperature = float(message)
            if subtopic == "temperature_f":
                circuit.status.temperature_f = float(message)
            if subtopic == "overtemperature":
                circuit.status.overtemperature = int(message)
            if subtopic == "temperature_status":
                circuit.status.temperature = message
            if subtopic == "voltage":
                circuit.status.voltage = float(message)  

    def handle_shelly_relay_message(self, id, subtopic, message):
        for circuit in self.brain.circuits:
            if(circuit.id != id):
                continue
            if subtopic == "relay/"+circuit.relay_id:
                on = message == "on"
                if on != circuit.status.relay.on:
                    circuit.status.relay.on = message == "on"
                    self.brain.ui.check_room_states(circuit.name)
            if subtopic == "relay/"+circuit.relay_id+"/power":
                power = float(message)
                if power != circuit.status.relay.power:
                    circuit.status.relay.power = power
                    self.brain.ui.check_room_states(circuit.name)
            if subtopic == "relay/"+circuit.relay_id+"/energy":
                circuit.status.relay.energy = int(message)
            if subtopic == "temperature":
                circuit.status.temperature = float(message)
            if subtopic == "temperature_f":
                circuit.status.temperature_f = float(message)
            if subtopic == "overtemperature":
                circuit.status.overtemperature = int(message)
            if subtopic == "temperature_status":
                circuit.status.temperature = message
            if subtopic == "voltage":
                circuit.status.voltage = float(message)    

class Configuration:
    def __init__(self, root):
        self.root = root
        self.points = []
        self.lines = []
        self.rooms = []
        self.mqtt_broker = '192.168.2.200'
        self.base_width = 800
        self.base_height = 600
        self.circuit_button_x = 690
        self.circuit_button_width = 250
        self.circuit_button_height = 48
        self.circuit_button_y_start = 35
        self.circuit_button_font_size = 20
        self.info_block_x = 20
        self.info_block_y = 600
        self.info_block_font_size = 20
        self.info_block_spacing = 32
        self.redraw_time_seconds = 3
        self.points_scale = 1

    def load_config(self):
        config_data = open(self.root+'DynamicUI.json')
        config = json.load(config_data)
        self.points_scale = config["points_scale"]
        self.points = config["points"]
        for point in self.points:
            point[0] = point[0] * self.points_scale
            point[1] = point[1] * self.points_scale
        self.lines = config["lines"]
        self.rooms = config["rooms"]
        self.circuit_button_x = config["circuit_button_x"]
        self.circuit_button_width = config["circuit_button_width"]
        self.circuit_button_height = config["circuit_button_height"]
        self.circuit_button_y_start = config["circuit_button_y_start"]
        self.circuit_button_font_size = config["circuit_button_font_size"]
        self.info_block_x = config["info_block_x"]
        self.info_block_y = config["info_block_y"]
        self.info_block_font_size = config["info_block_font_size"]
        self.info_block_spacing = config["info_block_spacing"]
        self.mqtt_broker = config["mqtt_broker"]
        self.redraw_time_seconds = config["redraw_time_seconds"]
        if config["base_width"] != self.base_width or config["base_height"] != self.base_height:
            self.base_width = config["base_width"]
            self.base_height = config["base_height"]