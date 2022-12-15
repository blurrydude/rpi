#! /usr/bin/env python3
import time
from UI import UI
from Services import MQTT, Configuration
from RelayModule import RelayModule
import json
import os
import _thread

class Brain:
    def __init__(self):
        self.root = os.path.dirname(os.path.realpath(__file__))+"/"
        self.config = Configuration(self.root)
        self.running = True
        self.mqtt = MQTT(self)
        self.ui = UI(self)
        self.roomstats = {}
        self.circuits = []
        self.last_notification = ""
        self.ticks = 0
    
    def start(self):
        print('brain starting...')
        self.config.load_config()
        self.load_circuits()
        self.mqtt.start()
        _thread.start_new_thread(self.timer_tick,())
        self.ui.start()
    
    def stop(self):
        self.running = False
        self.mqtt.stop()
        self.ui.stop()
        exit()
    
    def timer_tick(self):
        time.sleep(1)
        self.ticks = self.ticks + 1
        if self.ticks == self.config.redraw_time_seconds:
            self.ticks = 0
            _thread.start_new_thread(self.redraw,())
        self.timer_tick()

    def redraw(self):
        self.ui.draw_all()

    def load_circuits(self):
        circuit_data = open(self.root+'circuits.json')
        circuit_list = json.load(circuit_data)
        self.circuits = []
        for circuit in circuit_list:
            self.circuits.append(RelayModule(circuit["id"],circuit["ip_address"],circuit["name"],circuit["relay_id"],circuit["location"],circuit["zones"],circuit["on_modes"],circuit["off_modes"]))

    def set_thermostat(self, room, heat_below, cool_above):
        topic = 'smarter_circuits/thermosettings/'+room
        self.mqtt.client.publish(topic,'temperature_high_setting:'+str(cool_above))
        self.mqtt.client.publish(topic,'temperature_low_setting:'+str(heat_below))

    def disable_thermostat(self, room):
        topic = 'smarter_circuits/thermosettings/'+room
        self.mqtt.client.publish(topic,'system_disabled:true')
        
    def enable_thermostat(self, room):
        topic = 'smarter_circuits/thermosettings/'+room
        self.mqtt.client.publish(topic,'system_disabled:false')