import time
time.sleep(30)
from ShellyDevices import RelayModule, DoorWindowSensor, HumidityTemperatureSensor, MotionSensor, CommandCondition
from os import name
import SmarterCircuitsMQTT
import SmarterConfiguration
from SmarterTouchscreen import Touchscreen
from SmarterLogging import SmarterLog
import socket
import subprocess
import _thread
import json
from datetime import datetime, timedelta
import requests

class SmarterCircuitsMCP:
    def __init__(self, name, ip_address, model):
        self.id = 0
        self.name = name
        self.model = model
        self.mode = "day"
        self.running = False
        self.ticks = 0
        self.ip_address = ip_address
        self.circuit_authority = False
        self.config = None
        self.mqtt = None
        self.touchscreen = None
        self.peers = []
        self.last_day = ""
        self.solar_data = False
        self.sunrise = ""
        self.sunset = ""
        self.civil_twilight_end = ""
        self.civil_twilight_begin = ""
        self.motion_detected = []
        self.start()

    def start(self):
        SmarterLog.log("SmarterCircuits","starting...")
        self.config = SmarterConfiguration.SmarterConfig()
        while self.config.loaded is False:
            time.sleep(1)
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(self.config.brokers,["shellies/#","smarter_circuits/#"],self.on_message)
        _thread.start_new_thread(self.main_loop, (self))
        if self.config.touchscreen is True:
            self.touchscreen = Touchscreen()
        
        input("Press any key to stop...")

        self.stop()
    
    def main_loop(self):
        self.running = True
        while self.running is True:
            if self.config.loaded is False or self.mqtt.connected is False:
                continue
            if self.ticks in [0,10,20,30,40,50]:
                self.send_peer_data()
            
            now = datetime.now().strftime("%H:%M")
            day = datetime.now().strftime("%a").lower()
            if self.ticks >= 59:
                self.ticks = 0
                self.check_solar_data(day)
                self.check_circuit_authority()
                self.do_time_commands(now, day)
            self.ticks = self.ticks + 1
            time.sleep(1)

    def check_solar_data(self, day):
        if day != self.last_day:
            self.last_day = day
            r = requests.get("https://api.sunrise-sunset.org/json?lat=39.68021508778703&lng=-84.17636552954109")
            j = r.json()
            self.sunrise = self.convert_suntime(j["results"]["sunrise"],False)
            SmarterLog.log("SmarterCircuitsMCP","got sunrise time: "+self.sunrise)
            self.sunset = self.convert_suntime(j["results"]["sunset"],False)
            SmarterLog.log("SmarterCircuitsMCP","got sunset time: "+self.sunset)
            self.civil_twilight_begin = self.convert_suntime(j["results"]["civil_twilight_begin"],False)
            SmarterLog.log("SmarterCircuitsMCP","got civil_twilight_begin time: "+self.civil_twilight_begin)
            self.civil_twilight_end = self.convert_suntime(j["results"]["civil_twilight_end"],False)
            SmarterLog.log("SmarterCircuitsMCP","got civil_twilight_end time: "+self.civil_twilight_end)
    
    def do_time_commands(self, now, day):
        if self.circuit_authority is False:
            return
        for tc in self.config.time_commands:
            check = tc["days_time"].lower()
            if day not in check:
                continue
            if self.time_check(now,check) is True:
                if "thermoset" in tc["command"]:
                    #TODO: make this work again
                    #thermoset_command(tc["command"])
                    donothing = True
                else:
                    self.execute_command(tc["command"])

    def time_check(self, now, check):
        is_sunrise = now == self.sunrise
        is_sunset = now == self.sunset
        is_civil_twilight_end = now == self.civil_twilight_end
        is_civil_twilight_begin = now == self.civil_twilight_begin
        check = check.lower()
        return now in check or (is_sunrise and "sunrise" in check) or (is_sunset and "sunset" in check) or (is_civil_twilight_end and "civil_twilight_end" in check) or (is_civil_twilight_begin and "civil_twilight_begin" in check)
    
    def send_peer_data(self):
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.mqtt.publish("smarter_circuits/peers/"+self.name,SmarterCircuitsPeer(self.id, self.name, self.ip_address, self.model, self.circuit_authority, timestamp).toJSON())

    def check_circuit_authority(self):
        last_octet = int(self.ip_address.split('.')[3])
        lowest_ip = last_octet
        for peer in self.peers:
            peer_last_octet = int(peer.ip_address.split('.')[3])
            if peer_last_octet < lowest_ip:
                lowest_ip = peer_last_octet
        if lowest_ip == last_octet:
            if self.circuit_authority is not True:
                SmarterLog.log("SmarterCircuitsMCP","I am circuit authority")
                self.circuit_authority = True
        else:
            self.circuit_authority = False

    def stop(self):
        SmarterLog.log("SmarterCircuits","stopping...")
        self.running = False
        self.config.stop()
        self.mqtt.stop()
        time.sleep(5)
        SmarterLog.log("SmarterCircuits","stopped.")
        exit()
    
    def on_message(self, client, userdata, message):
        topic = message.topic
        text = str(message.payload.decode("utf-8"))
        if topic.startswith("shellies"):
            self.handle_shelly_message(topic, text)
        if topic.startswith("smarter_circuits"):
            self.handle_smarter_circuits_message(topic, text)
    
    def handle_shelly_message(self, topic, message):
        #print(topic+": "+message)
        s = topic.split('/')
        id = s[1]
        if "1pm" in id or "switch25" in id:
            self.handle_shelly_relay_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "dw" in id:
            self.handle_shelly_dw_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "ht" in id:
            self.handle_shelly_ht_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "motion" in id:
            self.handle_shelly_motion_message(id, topic.replace("shellies/"+id+"/",""), message)
        return

    def handle_shelly_relay_message(self, id, subtopic, message):
        for circuit in self.config.circuits:
            if(circuit.id != id):
                continue
            if subtopic == "relay/"+circuit.relay_id:
                circuit.status.relay.on = message == "on"
            if subtopic == "relay/"+circuit.relay_id+"/power":
                circuit.status.relay.power = float(message)
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

    def handle_shelly_dw_message(self, id, subtopic, message):
        sensor = self.config.door_sensors[id]
        if subtopic == "sensor/tilt":
            sensor.status.tilt = int(message)
        if subtopic == "sensor/vibration":
            sensor.status.vibration = int(message)
        if subtopic == "sensor/temperature":
            sensor.status.temperature = float(message)
        if subtopic == "sensor/lux":
            sensor.status.lux = int(message)
        if subtopic == "sensor/illumination":
            sensor.status.illumination = message
        if subtopic == "sensor/battery":
            battery = int(message)
            if sensor.status.battery != battery:
                sensor.status.battery = battery
                self.battery_status_check(sensor)
        if subtopic == "sensor/error":
            sensor.status.error = int(message)
        if subtopic == "sensor/act_reasons":
            sensor.status.act_reasons = json.dumps(message)
        if subtopic == "sensor/state":
            if sensor.status.state != message:
                sensor.status.state = message
                #TODO: fix this
                #self.handle_dw_state_change(sensor)
    
    def hande_dw_state_change(self, sensor:DoorWindowSensor):
        if self.circuit_authority is not True:
            return
        if sensor.status.state == "open":
            self.execute_command(sensor.open_command)
        else:
            self.execute_command(sensor.close_command)

    def handle_shelly_ht_message(self, id, subtopic, message):
        sensor = self.config.ht_sensors[id]
        if subtopic == "sensor/battery":
            battery = int(message)
            if sensor.status.battery != battery:
                sensor.status.battery = battery
                self.battery_status_check(sensor)
        if subtopic == "sensor/temperature":
            sensor.status.temperature = float(message)
        if subtopic == "sensor/humidity":
            sensor.status.humidity = float(message)

    def handle_shelly_motion_message(self, id, subtopic, message):
        SmarterLog.log("SmarterCircuitsMCP", "handle motion message: "+message)
        sensor = self.config.motion_sensors[id]
        if subtopic != "status":
            return
        data = json.loads(message)
        if sensor.status.active != data["active"]:
            sensor.status.active = data["active"]
        if sensor.status.battery != data["bat"]:
            sensor.status.battery = data["bat"]
            self.battery_status_check(sensor)
        if sensor.status.lux != data["lux"]:
            sensor.status.lux = data["lux"]
        if sensor.status.vibration != data["vibration"]:
            sensor.status.vibration = data["vibration"]
        if sensor.status.timestamp != data["timestamp"]:
            sensor.status.timestamp = data["timestamp"]
        if sensor.status.motion != data["motion"]:
            sensor.status.motion = data["motion"]
            self.handle_motion(sensor)

    def handle_motion(self, sensor:MotionSensor):
        SmarterLog.log("SmarterCircuitsMCP","Motion detected: "+sensor.room)
        if self.circuit_authority is not True:
            return
        if sensor.id in self.motion_detected:
            return
        self.motion_detected.append(sensor.id)
        for command in sensor.commands:
            if self.conditions_met(command.conditions) is True:
                self.execute_command(command.start)
        if sensor.auto_off is True:
            auto_off_at = datetime.now() + timedelta(minutes=int(sensor.off_time_minutes))
            _thread.start_new_thread(self.motion_auto_off_timer, (sensor, auto_off_at))

    def motion_auto_off_timer(self, sensor:MotionSensor, auto_off_time):
        now = datetime.now()
        while now < auto_off_time:
            now = datetime.now()
            time.sleep(1)
        for command in sensor.commands:
            if self.conditions_met(command.conditions) is True:
                self.execute_command(command.stop)
        self.motion_detected.remove(sensor.id)

    def handle_smarter_circuits_message(self, topic, message):
        #print(topic+": "+message)
        if "smarter_circuits/peers" in topic:
            self.received_peer_data(json.loads(message))
        if "smarter_circuits/mode" in topic and self.mode != message:
            self.mode = message
            self.handle_mode_change()
        if "smarter_circuits/command" in topic:
            self.execute_command(message)
    
    def handle_mode_change(self):
        SmarterLog.log("SmarterCircuitsMCP","mode set to "+self.mode)
        if self.circuit_authority is not True:
            return
        for circuit in self.config.circuits:
            if self.mode in circuit.on_modes:
                self.execute_command("turn on "+circuit.name.lower())
            if self.mode in circuit.off_modes:
                self.execute_command("turn off "+circuit.name.lower())
    
    def battery_status_check(self, sensor):
        if sensor.status.battery < 42:
            SmarterLog.log("BATTERY STATUS","Battery Low: "+sensor.id)
    
    def conditions_met(self, conditions):
        for condition in conditions:
            target_value = None
            if "." in condition.prop:
                s = condition.prop.split(".")
                device = None
                if s[0] == "motion":
                    for sensor in self.config.motion_sensors:
                        if sensor.room.replace(" ","") == s[1]:
                            device = sensor
                if s[0] == "circuit":
                    for circuit in self.config.circuits:
                        if circuit.name.replace(" ","") == s[1]:
                            device = circuit
                for attr, value in device.__dict__.items():
                    if attr == s[2]:
                        target_value = value
            else:
                for attr, value in self.__dict__.items():
                    if attr == condition.prop:
                        target_value = value
            
            if condition.comparitor == "=":
                if str(target_value) != condition.value:
                    return False
            if condition.comparitor == "!=":
                if str(target_value) == condition.value:
                    return False
            if condition.comparitor == ">":
                if str(target_value) <= condition.value:
                    return False
            if condition.comparitor == ">=":
                if str(target_value) < condition.value:
                    return False
            if condition.comparitor == "<":
                if str(target_value) >= condition.value:
                    return False
            if condition.comparitor == "<=":
                if str(target_value) > condition.value:
                    return False
            if condition.comparitor == "in":
                if str(target_value) in condition.value:
                    return False
            if condition.comparitor == "not in":
                if str(target_value) not in condition.value:
                    return False
        return True

    def send_api_command(self, command):
        #TODO: remove API altogether from system
        SmarterLog.log("SmarterCircuitsMCP","sending command: "+command)
        try:
            r =requests.get(self.config.command_endpoint+command)
            SmarterLog.log("SmarterCircuitsMCP","command response: "+str(r.status_code))
        except:
            SmarterLog.log("SmarterCircuitsMCP",'failed to send command')

    def execute_command(self, command):
        if self.circuit_authority is not True:
            return
        if self.config.use_api is True:
            self.send_api_command(command)
            return
        SmarterLog.log("SmarterCircuitsMCP","executing command: "+command)
        command = command.lower()
        com = "off"
        command_list = []
        if " on" in command:
            com = "on"
        if "zone" in command or "area" in command or "all of the" in command:
            for ci in range(0,len(self.config.circuits)):
                c = self.config.circuits[ci]
                for z in c.zones:
                    if z.lower() in command:
                        topic = "shellies/"+c.id+"/relay/"+c.relay_id+"/command"
                        command_list.append({"t":topic,"c":com})
        elif "mode" in command:
            detected_mode = None
            for ci in range(0,len(self.config.circuits)):
                c = self.config.circuits[ci]
                for m in c.on_modes:
                    if m.lower() in command:
                        detected_mode = m.lower()
                for m in c.off_modes:
                    if m.lower() in command:
                        detected_mode = m.lower()
                if detected_mode is None:
                    continue
                self.mode = detected_mode
                self.handle_mode_change()
        elif "turn" in command:
            for ci in range(0,len(self.config.circuits)):
                c = self.config.circuits[ci]
                if c.name.lower() in command or c.name.lower().replace("light","lamp") in command:
                    topic = "shellies/"+c.id+"/relay/"+c.relay_id+"/command"
                    command_list.append({"t":topic,"c":com})

        elif "first shade" in command:
            if "open" in command:
                command_list.append({"t":"pi/rollerpi/commands","c":"0:0"})
            else:
                command_list.append({"t":"pi/rollerpi/commands","c":"0:1"})
        elif "second shade" in command:
            if "open" in command:
                command_list.append({"t":"pi/rollerpi/commands","c":"1:0"})
            else:
                command_list.append({"t":"pi/rollerpi/commands","c":"1:1"})
        elif "third shade" in command:
            if "open" in command:
                command_list.append({"t":"pi/rollerpi/commands","c":"2:0"})
            else:
                command_list.append({"t":"pi/rollerpi/commands","c":"2:1"})
        elif "shade" in command:
            if "open" in command:
                command_list.append({"t":"pi/rollerpi/commands","c":"5:0"})
            else:
                command_list.append({"t":"pi/rollerpi/commands","c":"5:1"})

        elif "shop door" in command:
            if "open" in command:
                command_list.append({"t":"pi/baydoorpi/commands","c":"1:1"})
            if ("close" in command or "shut" in command):
                command_list.append({"t":"pi/baydoorpi/commands","c":"1:0"})
        elif "garage door" in command:
            if "open" in command:
                command_list.append({"t":"pi/baydoorpi/commands","c":"0:1"})
            if "close" in command or "shut" in command:
                command_list.append({"t":"pi/baydoorpi/commands","c":"0:0"})

        for cmd in command_list:
            self.mqtt.publish(cmd["t"],cmd["c"])

    def received_peer_data(self, peer):
        found = False
        for p in self.peers:
            if p.name == peer["name"]:
                p.id = peer["id"]
                p.ip_address = peer["ip_address"]
                p.model = peer["model"]
                p.circuit_authority = peer["circuit_authority"]
                p.timestamp = peer["timestamp"]
                found = True
        if found is not True:
            SmarterLog.log("SmarterCircuits","new peer "+peer["name"])
            self.peers.append(SmarterCircuitsPeer(peer["id"],peer["name"],peer["ip_address"],peer["model"],peer["circuit_authority"],peer["timestamp"]))
    
    def convert_suntime(self, jdata, winter):
        a = jdata.split(' ')
        s = a[0].split(":")
        h = int(s[0])
        if a[1] == "AM" and h == 12:
            h = 0
        if a[1] == "PM" and h != 12:
            h = h + 12
        if winter is True:
            h = h - 5
        else:
            h = h - 4
        if h < 0:
            h = h + 24
        if h == 24:
            h = 0
        m = int(s[1])
        o = ""
        if h < 10:
            o = "0"
        o = o + str(h) + ":"
        if m < 10:
            o = o + "0"
        o = o + str(m)
        return o

class SmarterCircuitsPeer:
    def __init__(self, id, name, ip_address, model, circuit_authority, timestamp):
        self.id = id
        self.name = name
        self.ip_address = ip_address
        self.model = model
        self.circuit_authority = circuit_authority
        self.timestamp = timestamp
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

if __name__ == "__main__":
    myname = socket.gethostname()
    myip = subprocess.check_output(['hostname', '-I']).decode("utf-8").replace("\n","").split(' ')[0]
    uname = subprocess.check_output(['uname','-m']).decode("utf-8").replace("\n","")
    model = "pc"
    if uname.__contains__("Raspberry"):
        model = subprocess.check_output(['cat','/proc/device-tree/model'])
    print(uname)
    print(model)
    mcp = SmarterCircuitsMCP(myname, myip, model)