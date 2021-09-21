import time
time.sleep(15)
from ShellyDevices import RelayModule, DoorWindowSensor, HumidityTemperatureSensor, MotionSensor, CommandCondition
from os import name
import SmarterCircuitsMQTT
import SmarterConfiguration
from SmarterTouchscreen import Touchscreen
from SmarterLogging import SmarterLog
from SmarterThermostat import Thermostat, ThermostatState, ThermostatSettings, ThermostatView
import socket
import subprocess
import _thread
import json
from datetime import datetime, timedelta
import requests
import os

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
        self.thermostats = {}
        self.thermostat = None
        self.last_seen = {}
        self.last_day = ""
        self.solar_data = False
        self.sunrise = ""
        self.sunset = ""
        self.civil_twilight_end = ""
        self.civil_twilight_begin = ""
        self.motion_detected = []
        self.source_modified = 0
        self.last_log_dump_hour = 0
        self.start()

    def start(self):
        SmarterLog.log("SmarterCircuits","starting...")
        self.running = True
        self.config = SmarterConfiguration.SmarterConfig(self)
        while self.config.loaded is False:
            time.sleep(1)
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(self.config.brokers,["shellies/#","smarter_circuits/#"],self.on_message)
        _thread.start_new_thread(self.main_loop, ())
        if self.config.thermostat is True:
            self.thermostat = Thermostat(self)
        if self.config.touchscreen is True:
            self.touchscreen = Touchscreen(self)
        else:
            while self.running is True:
                time.sleep(1)
            self.stop()
    
    def check_for_updates(self):
        modified = 0
        source_dir = os.path.dirname(os.path.realpath(__file__))+"/"
        for file in os.listdir(source_dir):
            ignore_file = True
            if file in self.config.update_files:
                ignore_file = False
            if self.config.touchscreen is True and file in self.config.touchscreen_update_files:
                ignore_file = False
            if self.config.thermostat is True and file in self.config.thermostat_update_files:
                ignore_file = False
            if ignore_file is True:
                continue
            file_check = round(os.stat(source_dir+file).st_mtime,0)
            if file_check > modified:
                modified = file_check
        if modified == self.source_modified:
            return
        if self.source_modified == 0:
            self.source_modified = modified
            SmarterLog.log("SmarterCircuitsMCP","got last source modification: "+str(self.source_modified))
            return
        self.source_modified = modified
        SmarterLog.log("SmarterCircuitsMCP","restarting due to source modification: "+str(self.source_modified))
        self.stop(True)
    
    def main_loop(self):
        while self.running is True:
            try:
                if self.config.loaded is False or self.mqtt.connected is False:
                    continue
                if self.ticks in [0,10,20,30,40,50]:
                    self.send_peer_data()
                    self.check_for_updates()
                
                now = datetime.now().strftime("%H:%M")
                day = datetime.now().strftime("%a").lower()
                if self.ticks >= 59:
                    self.ticks = 0
                    self.check_solar_data(day)
                    self.check_circuit_authority()
                    self.do_time_commands(now, day)
                    self.do_log_dump()
                self.ticks = self.ticks + 1
            except Exception as e: 
                error = str(e)
                SmarterLog.log("SmarterCircuitsMCP","main_loop error: "+error)
                self.mqtt.publish("smarter_circuits/errors/"+self.name,error)
            time.sleep(1)

    def do_log_dump(self):
        previouslogfiledate = (datetime.now()-timedelta(hours=1)).strftime("%Y%m%d%H")
        previouslogfilepath = os.path.dirname(os.path.realpath(__file__))+"/logs/SmarterCircuits_"+previouslogfiledate+".log"
        currenthour = datetime.now().hour
        if self.last_log_dump_hour != currenthour:
            self.last_log_dump_hour = currenthour
            f = open(previouslogfilepath)
            t = f.read()
            SmarterLog.send_email("smartercircuits@gmail.com","Logfile "+previouslogfiledate,t)


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
                    SmarterLog.log("SmarterCircuitsMCP","time command: "+tc["command"])
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
        now = datetime.now()
        last_octet = int(self.ip_address.split('.')[3])
        highest_ip = last_octet
        for peer in self.peers:
            if peer.id in self.last_seen.keys() and self.last_seen[peer.id] < now - timedelta(minutes=2):
                continue
            peer_last_octet = int(peer.ip_address.split('.')[3])
            if peer_last_octet > highest_ip:
                highest_ip = peer_last_octet
        if highest_ip == last_octet:
            if self.circuit_authority is not True:
                SmarterLog.log("SmarterCircuitsMCP","I am circuit authority")
                self.circuit_authority = True
        else:
            self.circuit_authority = False

    def stop(self, restart = False):
        SmarterLog.log("SmarterCircuits","stopping...")
        if restart is True:
            self.mqtt.publish("smarter_circuits/info/"+self.name,"restarting...")
        self.running = False
        self.config.stop()
        self.mqtt.stop()
        time.sleep(5)
        SmarterLog.log("SmarterCircuits","stopped.")
        if restart is True:
            SmarterLog.log("SmarterCircuits","restarting...")
            os.system('sudo reboot now')
        exit()
    
    def on_message(self, client, userdata, message):
        try:
            topic = message.topic
            text = str(message.payload.decode("utf-8"))
            if topic.startswith("shellies"):
                self.handle_shelly_message(topic, text)
            if topic.startswith("smarter_circuits"):
                self.handle_smarter_circuits_message(topic, text)
        except Exception as e: 
            error = str(e)
            SmarterLog.log("SmarterCircuitsMCP",error)
            self.mqtt.publish("smarter_circuits/errors/"+self.name,error)
    
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
        SmarterLog.log("SmarterCircuitsMCP","Motion detected: "+sensor.name)
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
            
        SmarterLog.log("SmarterCircuitsMCP","Time's up: "+sensor.name)
        for command in sensor.commands:
            if self.conditions_met(command.conditions) is True:
                self.execute_command(command.stop)
        self.motion_detected.remove(sensor.id)

    def handle_smarter_circuits_message(self, topic, message):
        #print(topic+": "+message)
        if "smarter_circuits/shellylogins" in topic:
            filepath = os.path.dirname(os.path.realpath(__file__))+"/shellylogins.json"
            self.mqtt.publish("smarter_circuits/info/"+self.name,"received shelly logins")
            with open(filepath, "w") as write_file:
                write_file.write(message)
            self.config.load_secrets()
        if "smarter_circuits/peers" in topic:
            self.received_peer_data(json.loads(message))
        if "smarter_circuits/mode" in topic and self.mode != message:
            self.mode = message
            self.handle_mode_change()
        if "smarter_circuits/command" in topic and self.circuit_authority is True:
            self.execute_command(message)
        if "smarter_circuits/restart/"+self.name in topic:
            SmarterLog.log("SmarterCircuitsMCP","received restart command")
            self.mqtt.publish("smarter_circuits/info/"+self.name,"received restart command")
            self.stop(True)
        if "smarter_circuits/thermosettings/" in topic:
            room = topic.split("/")[2]
            if self.thermostat is not None and self.thermostat.room == room:
                s = message.split(":")
                self.thermostat.set(s[0],s[1])
        if "smarter_circuits/thermostats/" in topic:
            room = topic.split("/")[2]
            self.thermostats[room] = ThermostatView(json.loads(message))
        if "smarter_circuits/info/" in topic and "settings please" in message and self.circuit_authority is True:
            room = topic.split("/")[2]
            if room in self.thermostats.keys():
                thermostat = self.thermostats[room]
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "failed_read_halt_limit:"+str(thermostat.settings.failed_read_halt_limit))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "temperature_high_setting:"+str(thermostat.settings.temperature_high_setting))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "temperature_low_setting:"+str(thermostat.settings.temperature_low_setting))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "humidity_setting:"+str(thermostat.settings.humidity_setting))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "air_circulation_minutes:"+str(thermostat.settings.air_circulation_minutes))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "circulation_cycle_minutes:"+str(thermostat.settings.circulation_cycle_minutes))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "ventilation_cycle_minutes:"+str(thermostat.settings.ventilation_cycle_minutes))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "stage_limit_minutes:"+str(thermostat.settings.stage_limit_minutes))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "stage_cooldown_minutes:"+str(thermostat.settings.stage_cooldown_minutes))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "use_whole_house_fan:"+str(thermostat.settings.use_whole_house_fan))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "system_disabled:"+str(thermostat.settings.system_disabled))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "swing_temp_offset:"+str(thermostat.settings.swing_temp_offset))
                time.sleep(0.5)
                self.mqtt.publish("smarter_circuits/thermosettings/"+room, "settings_from_circuit_authority:true")
    
    def handle_mode_change(self):
        SmarterLog.log("SmarterCircuitsMCP","mode set to "+self.mode)
        if self.circuit_authority is not True:
            return
        for circuit in self.config.circuits:
            if self.mode.lower() in (string.lower() for string in circuit.on_modes):
                self.execute_command("turn on "+circuit.name.lower())
            if self.mode.lower() in (string.lower() for string in circuit.off_modes):
                self.execute_command("turn off "+circuit.name.lower())
    
    def battery_status_check(self, sensor):
        if sensor.status.battery < 42:
            SmarterLog.log("BATTERY STATUS","Battery Low: "+sensor.id)
            SmarterLog.send_email("smartercircuits@gmail.com",sensor.name+" battery at "+str(sensor.status.battery)+"%")
    
    def conditions_met(self, conditions):
        for condition in conditions:
            target_value = None
            if "." in condition.prop:
                s = condition.prop.split(".")
                device = None
                if s[0] == "motion":
                    for sensor_id in self.config.motion_sensors.keys():
                        sensor = self.config.motion_sensors[sensor_id]
                        if sensor.name.replace(" ","") == s[1]:
                            device = sensor
                if s[0] == "circuit":
                    for circuit in self.config.circuits:
                        if circuit.name.replace(" ","") == s[1]:
                            device = circuit
                if device is not None:
                    for attr, value in device.__dict__.items():
                        if attr == s[2]:
                            if len(s) > 3:
                                for sattr, svalue in value.__dict__.items():
                                    if sattr == s[3]:
                                        if len(s) > 4:
                                            for ssattr, ssvalue in svalue.__dict__.items():
                                                if ssattr == s[4]:
                                                    target_value = ssvalue
                                        else:
                                            target_value = svalue
                            else:
                                target_value = value
            else:
                for attr, value in self.__dict__.items():
                    if attr == condition.prop:
                        target_value = value
            
            if condition.comparitor == "=":
                if str(target_value) != str(condition.value):
                    return False
            if condition.comparitor == "!=":
                if str(target_value) == str(condition.value):
                    return False
            if condition.comparitor == ">":
                if float(target_value) <= float(condition.value):
                    return False
            if condition.comparitor == ">=":
                if float(target_value) < float(condition.value):
                    return False
            if condition.comparitor == "<":
                if float(target_value) >= float(condition.value):
                    return False
            if condition.comparitor == "<=":
                if float(target_value) > float(condition.value):
                    return False
            if condition.comparitor == "in":
                if str(target_value) in str(condition.value):
                    return False
            if condition.comparitor == "not in":
                if str(target_value) not in str(condition.value):
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
        SmarterLog.log("SmarterCircuitsMCP","executing command: "+command)
        command = command.lower()
        com = "off"
        command_list = []
        if " on" in command:
            com = "on"
        if "zone" in command or "area" in command or "all of the" in command:
            for c in self.config.circuits:
                for z in c.zones:
                    if z.lower() in command:
                        topic = "shellies/"+c.id+"/relay/"+c.relay_id+"/command"
                        command_list.append({"t":topic,"c":com})
        elif "mode" in command:
            detected_mode = None
            for c in self.config.circuits:
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
        self.last_seen[peer["id"]] = datetime.now()
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
    if uname.__contains__("arm"):
        model = subprocess.check_output(['cat','/proc/device-tree/model']).decode("utf-8").replace("\n","")
    print(uname)
    print(model)
    mcp = SmarterCircuitsMCP(myname, myip, model)