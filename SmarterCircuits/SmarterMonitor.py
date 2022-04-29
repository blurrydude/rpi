#! /usr/bin/env python3
from datetime import datetime
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
        self.last_sent_alert = False
        self.ignore_fields = [
            "relay_0_energy",
            "relay_1_energy",
            "events_rpc",
            "input_0",
            "input_1",
            "source",
            "output",
            "apower",
            "aenergy",
            "announce",
            "info"
        ]
        self.circuit_states = {}
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
        print("client connected at "+datetime.now().strftime("%x %X"))
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
        print("publish reports at "+datetime.now().strftime("%x %X"))
        self.publish("full_system_report", json.dumps(self.full_state))
        self.publish("circuit_states", json.dumps(self.circuit_states))

    def handle_shelly_message(self, topic, rawdata):
        identity = topic[0].split('-')
        device = identity[0]
        id = identity[1].upper()
        topic.pop(0)
        self.handle_single_field_message(device, id, topic, rawdata)
    
    def handle_single_field_message(self, device, id, topic, value):
        if device not in self.full_state.keys():
            self.full_state[device] = {}
            mess = "Detected\\n"+device
            if device in self.name_lookup.keys():
                mess = mess + "\\n"+self.name_lookup[device]
            self.client.publish("notifications", mess)
        if id not in self.full_state[device].keys():
            self.full_state[device][id] = {}
        field_name = str(topic).replace(', ','_').replace("'",'').replace('[','').replace(']','')
        if field_name in self.ignore_fields:
            return
        if value[0] == "{":
            obj = json.loads(value)
            nobj = {}
            for key in obj:
                if key not in self.ignore_fields:
                    nobj[key] = obj[key]
            self.full_state[device][id][field_name] = nobj
        else:
            self.full_state[device][id][field_name] = value
        try:
            self.full_state[device][id]["name"] = self.name_lookup[id]
        except:
            print(device+" "+id+" was not found.")

    def process_state(self):
        total_current = 0.0
        alerts = []
        
        if "shellyswitch25" in self.full_state.keys():
            for did in self.full_state["shellyswitch25"]:
                device = self.full_state["shellyswitch25"][did]
                if "name" not in device.keys():
                    continue
                current = 0.0
                name = device["name"].split('/')
                if name[0] not in self.circuit_states.keys():
                    self.circuit_states[name[0]] = {}
                if name[1] not in self.circuit_states.keys():
                    self.circuit_states[name[1]] = {}
                if "relay_0_power" in device.keys():
                    c = float(device["relay_0_power"])
                    if c > 50:
                        alerts.append(name[0] + " using " + str(round(c,1)) + "W")
                    current = current + c
                    self.circuit_states[name[0]]["watts"] = c
                if "temperature_f" in device.keys():
                    self.circuit_states[name[0]]["temp"] = float(device["temperature_f"])
                    self.circuit_states[name[1]]["temp"] = float(device["temperature_f"])
                if "relay_1_power" in device.keys():
                    c = float(device["relay_1_power"])
                    if c > 50:
                        alerts.append(name[1] + " using " + str(round(c,1)) + "W")
                    current = current + c
                    self.circuit_states[name[1]]["watts"] = c
                if "overtemperature" in device.keys() and device["overtemperature"] != "0":
                    alerts.append(name[0] + " over temp")
                    alerts.append(name[1] + " over temp")
                total_current = total_current + current

        if "shelly1pm" in self.full_state.keys():
            for did in self.full_state["shelly1pm"]:
                device = self.full_state["shelly1pm"][did]
                if "name" not in device.keys():
                    continue
                current = 0.0
                name = device["name"]
                if name not in self.circuit_states.keys():
                    self.circuit_states[name] = {}
                if "relay_0_power" in device.keys():
                    c = float(device["relay_0_power"])
                    if c > 50:
                        alerts.append(name + " using " + str(round(c,1)) + "W")
                    current = current + c
                    self.circuit_states[name]["watts"] = c
                if "temperature_f" in device.keys():
                    self.circuit_states[name]["temp"] = float(device["temperature_f"])
                if "overtemperature" in device.keys() and device["overtemperature"] != "0":
                    alerts.append(name + " over temp")
                total_current = total_current + current

        if "shellypro4pm" in self.full_state.keys():
            for did in self.full_state["shellypro4pm"]:
                device = self.full_state["shellypro4pm"][did]
                current = 0.0
                for i in range(4):
                    sid = "status_switch:"+str(i)
                    if sid in device.keys():
                        switch = device[sid]
                        p = float(switch["current"])
                        v = float(switch["voltage"])
                        if p == 0:
                            c = 0
                        else:
                            c = v * p
                        current = current + c
                        name = did + "-" + str(switch["id"])
                        if c > 50:
                            alerts.append(name + " using " + str(round(c,1)) + "W")
                        self.circuit_states[name] = {
                            "watts": c,
                            "temp": switch["temperature"]["tF"]
                        }
                total_current = total_current + current

        if "shellymotionsensor" in self.full_state.keys():
            for did in self.full_state["shellymotionsensor"]:
                device = self.full_state["shellymotionsensor"][did]
                if "name" not in device.keys():
                    continue
                if device["status"]["bat"] < 30:
                    alerts.append(device["name"] + " batt @ "+str(device["status"]["bat"])+"%")
        self.write_state()
        if len(alerts) > 0:
            self.last_sent_alert = True
            alerts.append("Total: "+str(round(total_current,1))+"W")
            notify = ""
            for i in range(len(alerts)):
                notify = notify + alerts[i] + '\\n'
            self.client.publish("notifications",notify)
        elif self.last_sent_alert is True:
            self.last_sent_alert = False
            self.client.publish("notifications","No alerts as of "+datetime.now().strftime("%X"))

if __name__ == "__main__":
    monitor = SmarterMonitor()
    while monitor.running is True:
        time.sleep(15)
        monitor.process_state()
        time.sleep(15)
    exit()