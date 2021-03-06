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
    def __init__(self, name):
        self.name = name
        self.door_open = [False,False]

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
        #_thread.start_new_thread(self.monitor, ())

    def stop(self):
        self.running = False

    def read_state(self):
        bay_door_0 = str(p.digital_read(0)) == "1"
        bay_door_1 = str(p.digital_read(1)) == "1"
        door_open = [
            bay_door_0,
            bay_door_1
        ]
        if self.door_open != door_open:
            self.door_open = door_open
            self.state_change()
    
    def monitor(self):
        while self.running is True:
            try:
                self.read_state()
            except:
                donothing = True
            time.sleep(1)
    
    def emulate_button_press(self, bay):
        SmarterLog.log("Rollerdoor","Pressing button for bay "+str(bay+1))
        p.digital_write(bay,1)
        time.sleep(1)
        p.digital_write(bay,0)

    def state_change(self):
        state = "closed"
        if self.door_open[1] is True:
            state = "open"

        self.mcp.send_discord_message(self.mcp.discord_house_room,"Shop door "+state)
        self.mcp.mqtt.publish("smarter_circuits/rollerdoor/"+self.name+"/state",json.dumps(self.door_open))

    def set_state(self, bay, state):
        # to_open = state == 1
        # self.door_open = [
        #     str(p.digital_read(0)) == "1",
        #     str(p.digital_read(1)) == "1"
        # ]
        # if to_open == self.door_open[bay]:
        #     return
        self.read_state()
        _thread.start_new_thread(self.emulate_button_press, (bay,))