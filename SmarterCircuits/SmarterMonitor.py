#! /usr/bin/env python3
import os
import paho.mqtt.client as mqtt
import _thread
import time
import json

running = True

class SmarterMonitor:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.running = True
        self.full_state = {}
        self.name_lookup = {
            "C45BBE5FE891": "Little Remote"
        }
        self.load_configs()
        _thread.start_new_thread(self.start_listening, ())

    def load_configs(self):
        homedir = os.path.dirname(os.path.realpath(__file__))+"/"
        circuits_file = homedir+"circuits.json"
        motion_file = homedir+"motionsensors.json"
        ht_file = homedir+"thsensors.json"
        circuits = json.load(open(circuits_file))
        motions = json.load(open(motion_file))
        hts = json.load(open(ht_file))
        for circuit in circuits:
            cid = circuit["id"].split('-')[-1].upper()
            if cid in self.name_lookup:
                self.name_lookup[cid] = self.name_lookup[cid]+"/"+circuit["name"]
            else:
                self.name_lookup[cid] = circuit["name"]
        for motion in motions:
            mid = motion["id"].split('-')[-1]
            self.name_lookup[mid] = motion["name"]
        for ht in hts:
            htid = ht["id"].split('-')[-1]
            self.name_lookup[htid] = ht["name"]

    def on_message(self, client, userdata, message):
        global running
        rawtopic = message.topic
        topic = rawtopic.split('/')
        rawdata = str(message.payload.decode("utf-8"))
        if topic[0] == "shellies":
            topic.pop(0)
            self.handle_shelly_message(topic, rawdata)

    def start_listening(self):
        self.client.connect('192.168.2.200')
        print("client connected.")
        self.client.subscribe("shellies/#")
        self.client.subscribe("smarter_circuits/#")
        self.client.loop_start()
        while self.running is True:
            time.sleep(1)
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic, message):
        self.client.publish(topic, message)
    
    def write_state(self):
        print("try write")
        self.publish("smarter_circuits/full_system_state", json.dumps(self.full_state))

    def handle_shelly_message(self, topic, rawdata):
        identity = topic[0].split('-')
        device = identity[0]
        id = identity[1].upper()
        topic.pop(0)
        self.handle_single_field_message(device, id, topic, rawdata)
    
    def handle_single_field_message(self, device, id, topic, value):
        if device not in self.full_state.keys():
            self.full_state[device] = {}
        if id not in self.full_state[device].keys():
            self.full_state[device][id] = {}
        field_name = str(topic).replace(', ','_').replace("'",'').replace('[','').replace(']','')
        if value[0] == "{":
            self.full_state[device][id][field_name] = json.loads(value)
        else:
            self.full_state[device][id][field_name] = value
        try:
            self.full_state[device][id]["name"] = self.name_lookup[id]
        except:
            print(device+" "+id+" was not found.")

    def process_state(self):
        
        self.write_state()

if __name__ == "__main__":
    monitor = SmarterMonitor()
    while monitor.running is True:
        time.sleep(30)
        monitor.process_state()
    exit()