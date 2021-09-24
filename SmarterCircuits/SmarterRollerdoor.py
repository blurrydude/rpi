import time
import _thread
import json
from SmarterLogging import SmarterLog
import traceback
libraries_available = False
try:
    import pifacedigitalio as p
    libraries_available = True
except:
    libraries_available = False

class RollerdoorState:
    def __init__(self, name, door_open):
        self.name = name
        self.door_open = door_open

class Rollerdoor:
    def __init__(self, mcp, name):
        self.mcp = mcp
        self.name = name
        self.running = True
        p.init()
        self.door_open = [
            str(p.digital_read(0)) == "1",
            str(p.digital_read(1)) == "1"
        ]
        self.state_change()
        while self.running is True:
            bay_door_0 = str(p.digital_read(0)) == "1"
            bay_door_1 = str(p.digital_read(1)) == "1"
            door_open = [
                bay_door_0,
                bay_door_1
            ]
            if self.door_open != door_open:
                self.door_open = door_open
                self.state_change()

    def stop(self):
        self.running = False
    
    def monitor(self):
        while self.running is True:
            # try:
            # bay_door_0 = str(p.digital_read(0)) == "1"
            # bay_door_1 = str(p.digital_read(1)) == "1"
            # door_open = [
            #     bay_door_0,
            #     bay_door_1
            # ]
            # if self.door_open != door_open:
            #     self.door_open = door_open
            #     self.state_change()
            # except Exception as e: 
            #     error = str(e)
            #     tb = traceback.format_exc()
            #     SmarterLog.log("SmarterRollerdoor","main_loop error: "+error)
            #     SmarterLog.log("SmarterRollerdoor","main_loop traceback: "+tb)
            #     self.mqtt.publish("smarter_circuits/errors/"+self.name,error)
            #     self.mqtt.publish("smarter_circuits/errors/"+self.name+"/traceback",tb)
            time.sleep(1)
    
    def emulate_button_press(self, bay):
        p.digital_write(bay,1)
        time.sleep(1)
        p.digital_write(bay,0)

    def state_change(self):
        self.mcp.mqtt.publish("smarter_circuits/rollerdoor/"+self.name+"/state",json.dumps(self.door_open))

    def set_state(self, bay, state):
        # to_open = state == 1
        # self.door_open = [
        #     str(p.digital_read(0)) == "1",
        #     str(p.digital_read(1)) == "1"
        # ]
        # if to_open == self.door_open[bay]:
        #     return
        _thread.start_new_thread(self.emulate_button_press, (bay,))