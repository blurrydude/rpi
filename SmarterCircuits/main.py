from SmarterCameraManager import CameraManager
from SmarterUI import SmartLabel, SmartButton
from SmarterCircuitsWebService import SmarterCircuitsWeb
from SmarterCircuitsAPI import SmarterAPI
from SmarterRollershade import Rollershade, RollershadeState
from SmarterRollerdoor import Rollerdoor, RollerdoorState
from SmarterRemote import RemoteHandler
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
import traceback
import textwrap

class SmarterCircuitsMCP:
    def __init__(self, name, ip_address, model):
        self.discord_house_room = "976692334920077342"
        self.discord_debug_room = "922927575884505119"
        self.id = 0
        self.name = name
        self.model = model
        self.mode = "day"
        self.running = False
        self.ip_address = ip_address
        self.circuit_authority = False
        self.config = None
        self.mqtt = None
        self.api = None
        self.touchscreen = None
        self.peers = []
        self.thermostats = {}
        self.rollershades = {}
        self.rollerdoors = {}
        self.thermostat = None
        self.rollershade = None
        self.rollerdoor = None
        self.cam_manager = None
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
        self.thermostat_history = []
        self.web_server = SmarterCircuitsWeb(ip_address, 8081)
        self.buttons = {}
        self.switch_states = {}
        self.last_notification = datetime.now() - timedelta(minutes=1)
        self.last_minute_cycle = datetime.now() - timedelta(minutes=1)
        self.hex_waiting = False
        self.hex_search = False
        self.hex_input = False
        self.hex_input_mode = ""
        self.hex_command = ""
        self.source_dir = os.path.dirname(os.path.realpath(__file__))+"/"
        self.start()

    def start(self):
        self.log("SmarterCircuitsMCP","starting...")
        roles = []
        self.running = True
        self.config = SmarterConfiguration.SmarterConfig(self)
        while self.config.loaded is False:
            time.sleep(1)
        self.remote = RemoteHandler(self)
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(self.config.brokers,["shellies/#","smarter_circuits/#","remote_menu","crittercam/#"],self.on_message)
        _thread.start_new_thread(self.main_loop, ())
        self.api = SmarterAPI(self)
        if self.config.thermostat is True:
            roles.append("thermostat")
            self.log("SmarterCircuitsMCP","instantiating thermostat...")
            dev = Thermostat(self)
            self.thermostat = dev
        if self.config.touchscreen is True:
            roles.append("touchscreen")
            self.log("SmarterCircuitsMCP","instantiating touchscreen...")
            dev = Touchscreen(self)
            self.touchscreen = dev
        if self.config.rollershade is True:
            roles.append("rollershade")
            self.log("SmarterCircuitsMCP","instantiating rollershade...")
            dev = Rollershade(self,self.name)
            self.rollershade = dev
        if self.config.rollerdoor is True:
            roles.append("rollerdoor")
            self.log("SmarterCircuitsMCP","instantiating rollerdoor...")
            dev = Rollerdoor(self,self.name)
            self.rollerdoor = dev
        if self.config.cam_manager is True:
            roles.append("camera manager")
            self.log("SmarterCircuitsMCP","instantiating camera manager...")
            dev = CameraManager(self)
            self.cam_manager = dev
        self.send_discord_message(self.discord_house_room, self.name+" is now started as"+", ".join(roles)+".")
        self.web_server.start()
    
    def log(self, origin, message):
        self.debug(origin+": "+message)
        SmarterLog.log(origin, message)
        
    def debug(self, message):
        if self.config is None or self.mqtt is None or self.config.loaded is False or self.mqtt.connected is False:
            return
        self.mqtt.publish("debug/"+self.name,message)

    def check_for_updates(self):
        modified = 0
        for file in os.listdir(self.source_dir):
            ignore_file = True
            if file in self.config.update_files:
                ignore_file = False
            if self.config.touchscreen is True and file in self.config.touchscreen_update_files:
                ignore_file = False
            if self.config.thermostat is True and file in self.config.thermostat_update_files:
                ignore_file = False
            if self.config.cam_manager is True and file in self.config.cam_manager_update_files:
                ignore_file = False
            if ignore_file is True:
                continue
            file_check = round(os.stat(self.source_dir+file).st_mtime,0)
            if file_check > modified:
                modified = file_check
        if modified == self.source_modified:
            return
        if self.source_modified == 0:
            self.source_modified = modified
            self.log("SmarterCircuitsMCP","got last source modification: "+str(self.source_modified))
            return
        self.source_modified = modified
        self.log("SmarterCircuitsMCP","restarting due to source modification: "+str(self.source_modified))
        self.send_discord_message(self.discord_debug_room, self.name+" restarting due to source modification: "+str(self.source_modified))
        self.stop(True)
    
    def main_loop(self):
        while self.running is True:
            try:
                if self.config.loaded is False or self.mqtt.connected is False:
                    continue
                if self.last_notification < datetime.now() - timedelta(seconds=10):
                    self.last_notification = datetime.now()
                    self.check_for_updates()
                    _thread.start_new_thread(self.send_peer_data, ())
                now = datetime.now().strftime("%H:%M")
                day = datetime.now().strftime("%a").lower()
                if self.last_minute_cycle < datetime.now() - timedelta(minutes=1):
                    self.last_minute_cycle = datetime.now()
                    self.check_circuit_authority()
                    _thread.start_new_thread(self.check_solar_data, (day,))
                    _thread.start_new_thread(self.do_time_commands, (now, day))
                    _thread.start_new_thread(self.do_log_dump, ())
                    _thread.start_new_thread(self.log_temp_data, ())
            except Exception as e: 
                error = str(e)
                tb = traceback.format_exc()
                self.handle_exception(error, tb)
            time.sleep(1)
    
    def send_system_state(self):
        data = ""
        for thermokey in self.thermostats.keys():
            thermo = self.thermostats[thermokey]
            dp = self.get_dew_point_f(thermo.state.temperature, thermo.state.humidity)
            data = data + thermo.room.upper() + ": " + str(round(thermo.state.temperature,1)) + " F " + str(round(thermo.state.humidity,1)) +"% (dew point: "+str(dp)+" F)\n"
        for sensor_id in self.config.ht_sensors.keys():
            sensor = self.config.ht_sensors[sensor_id]
            dp = self.get_dew_point_f(sensor.status.temperature, sensor.status.humidity)
            data = data + sensor.name.upper() + ": " + str(round(sensor.status.temperature,1)) + " F " + str(round(sensor.status.humidity,1)) +"% (dew point: "+str(dp)+" F, batt "+str(round(sensor.status.battery,1))+"%)\n"
        power = 0.0
        for circuit in self.config.circuits:
            power = power + circuit.status.relay.power
            if circuit.status.relay.power > 0:
                data = data + circuit.name +": "+str(circuit.status.relay.power) + " W\n"
        data = data + "System Power Usage: "+str(power)+" W\nCurrent Mode: " + self.mode.upper()
        self.send_discord_message(self.discord_house_room, data)
        self.mqtt.publish("notifications",data)

    def send_sensor_states(self):
        data = ""
        for thermokey in self.thermostats.keys():
            thermo = self.thermostats[thermokey]
            dp = self.get_dew_point_f(thermo.state.temperature, thermo.state.humidity)
            data = data + thermo.room.upper() + ": " + str(round(thermo.state.temperature,1)) + " F " + str(round(thermo.state.humidity,1)) +"% (dew point: "+str(dp)+" F)\n"
        for sensor_id in self.config.ht_sensors.keys():
            sensor = self.config.ht_sensors[sensor_id]
            dp = self.get_dew_point_f(sensor.status.temperature, sensor.status.humidity)
            data = data + sensor.name.upper() + ": " + str(round(sensor.status.temperature,1)) + " F " + str(round(sensor.status.humidity,1)) +"% (dew point: "+str(dp)+" F, batt "+str(round(sensor.status.battery,1))+"%)\n"
        for motion_id in self.config.motion_sensors.keys():
            motion = self.config.motion_sensors[motion_id]
            data = data + motion.name.upper() + ": " + str(motion.status.timestamp) + " : " + str(round(motion.status.lux,1)) +" lux, "+str(round(motion.status.battery,1))+"% battery\n"
            
        self.send_discord_message(self.discord_house_room, data)
        self.mqtt.publish("notifications",data)
    
    def log_temp_data(self):
        if self.circuit_authority is False:
            return
        try:
            data = datetime.now().strftime("%Y%m%d%H%M")
            logfile = self.source_dir+"logs/Thermostat_"+(datetime.now()).strftime("%Y%m%d")+".log"
            for thermokey in self.thermostats.keys():
                thermo = self.thermostats[thermokey]
                data = data + ":" + thermo.room + "=" + self.binarize(thermo.state.heat_on) + self.binarize(thermo.state.ac_on) + self.binarize(thermo.state.fan_on) + self.binarize(thermo.state.whf_on) + "|" + str(thermo.state.temperature) + "|" + str(thermo.state.humidity)
            mode = "a"
            if os.path.exists(logfile) is False:
                mode = "w"
            with open(logfile,mode) as write_file:
                write_file.write(data+"\n")
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.handle_exception(error, tb)

    def binarize(self, b):
        if b is True:
            return "1"
        return "0"

    def do_log_dump(self):
        try:
            old_dates = []
            for i in range(7,15):
                old_dates.append((datetime.now()-timedelta(days=i)).strftime("%Y%m%d"))
            previouslogfiledate = (datetime.now()-timedelta(hours=1)).strftime("%Y%m%d%H")
            logs_dir = self.source_dir+"logs/"
            for file in os.listdir(logs_dir):
                for old_date in old_dates:
                    if old_date in file:
                        os.remove(logs_dir+file)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.handle_exception(error, tb)

    def check_solar_data(self, day):
        if day != self.last_day:
            self.last_day = day
            r = requests.get("https://api.sunrise-sunset.org/json?lat=39.68021508778703&lng=-84.17636552954109")
            j = r.json()
            self.sunrise = self.convert_suntime(j["results"]["sunrise"],False)
            self.log("SmarterCircuitsMCP","got sunrise time: "+self.sunrise)
            self.sunset = self.convert_suntime(j["results"]["sunset"],False)
            self.log("SmarterCircuitsMCP","got sunset time: "+self.sunset)
            self.civil_twilight_begin = self.convert_suntime(j["results"]["civil_twilight_begin"],False)
            self.log("SmarterCircuitsMCP","got civil_twilight_begin time: "+self.civil_twilight_begin)
            self.civil_twilight_end = self.convert_suntime(j["results"]["civil_twilight_end"],False)
            self.log("SmarterCircuitsMCP","got civil_twilight_end time: "+self.civil_twilight_end)
    
    def do_time_commands(self, now, day):
        if self.circuit_authority is False:
            return
        if len(self.config.time_commands)== 0:
            self.log("SmarterCircuitsMCP","no time commands")
        for tc in self.config.time_commands:
            check = tc["days_time"].lower()
            if day.lower() not in check:
                continue
            if self.time_check(now,check) is True:
                if "thermoset" in tc["command"]:
                    #TODO: make this work again
                    #thermoset_command(tc["command"])
                    donothing = True
                else:
                    self.log("SmarterCircuitsMCP","time command: "+tc["command"])
                    self.send_discord_message(self.discord_house_room,"Executing time command: "+tc["command"])
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
        self.mqtt.publish("smarter_circuits/peers/"+self.name,SmarterCircuitsPeer(self.id, self.name, self.ip_address, self.model, self.circuit_authority, timestamp, self.config.thermostat, self.config.rollershade, self.config.rollerdoor).toJSON())

    def check_circuit_authority(self):
        if self.name == "rpi4-web-server":
            self.circuit_authority = True
        # now = datetime.now()
        # if "192" not in self.ip_address:
        #     self.ip_address = subprocess.check_output(['hostname', '-I']).decode("utf-8").replace("\n","").split(' ')[0]
        #     if "192" not in self.ip_address:
        #         return
        # last_octet = int(self.ip_address.split('.')[3])
        # highest_ip = last_octet
        # bad_peers = []
        # circuit_authority_exists = False
        # for peer in self.peers:
        #     # if datetime.strptime(peer.timestamp, '%m/%d/%Y, %H:%M:%S') < now - timedelta(minutes=2):
        #     #     bad_peers.append(peer)
        #     #     continue
        #     if peer.id in self.last_seen.keys() and self.last_seen[peer.id] < now - timedelta(minutes=2):
        #         bad_peers.append(peer)
        #         continue
        #     if peer.circuit_authority is True:
        #         circuit_authority_exists = True
        #         continue
        #     if "192" not in peer.ip_address:
        #         continue
        #     peer_last_octet = int(peer.ip_address.split('.')[3])
        #     if peer_last_octet > highest_ip:
        #         highest_ip = peer_last_octet
        # for bad_peer in bad_peers:
        #     self.peers.remove(bad_peer)
        #     self.log("SmarterCircuitsMCP","Forgot stale peer "+peer.name)
        # if highest_ip == last_octet and self.circuit_authority is not True and circuit_authority_exists is not True:
        #         self.log("SmarterCircuitsMCP","I am circuit authority")
        #         self.circuit_authority = True
        #         self.mqtt.publish("notifications",self.name+"\\nCircuit Authority")
        #         self.send_discord_message(self.discord_house_room, self.name+" is now the circuit authority.")
        #         # try:
        #         #     requests.get("https://api.idkline.com/circuitauthority/"+self.ip_address)
        #         #     self.log("SmarterCircuitsMCP","Told the API I am circuit authority")
        #         # except:
        #         #     self.log("SmarterCircuitsMCP","Could not tell the API I am circuit authority")
        # elif (highest_ip > last_octet or circuit_authority_exists is True) and self.circuit_authority is True:
        #         self.log("SmarterCircuitsMCP","I am no longer circuit authority")
        #         self.circuit_authority = False
        #         self.mqtt.publish("notifications",self.name+"\\nCircuit Authority")
        #         self.send_discord_message(self.discord_house_room, self.name+" is no longer the circuit authority.")

    def stop(self, restart = False):
        self.log("SmarterCircuitsMCP","stopping...")
        if restart is True:
            self.log("SmarterCircuitsMCP","restarting...")
            self.send_discord_message(self.discord_house_room, self.name+" is restarting.")
        self.running = False
        if self.cam_manager is not None:
            self.cam_manager.dispose()
        self.config.stop()
        self.mqtt.stop()
        time.sleep(5)
        self.log("SmarterCircuitsMCP","stopped.")
        if restart is True:
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
            if topic == "remote_menu" and self.config.touchscreen is True:
                self.handle_remote_menu(text)
            if topic.startswith("crittercam"):
                self.handle_camera_message(topic, text)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.handle_exception(error, tb)
    
    def handle_camera_message(self, topic, text):
        if self.config.cam_manager is False:
            return
        if self.cam_manager is None:
            self.log("SmarterCircuitsMCP","re-instantiating camera manager...")
            self.cam_manager = CameraManager(self)
        try:
            self.cam_manager.on_message(topic, text)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.handle_exception(error, tb)

    
    def handle_remote_menu(self, text):
        try:
            labels = []
            if "\\n" in text:
                wrapped = text.split('\\n')
            else:
                wrapped = textwrap.wrap(text,42)
            if wrapped[-1] == "":
                wrapped.pop(-1)
            wrapcount = len(wrapped)
            for i in range(wrapcount):
                labels.append(SmartLabel(i+1,0,wrapped[i],"Times",24,"black","white",5,5))
            buttons = [
                SmartButton(0,0,"Main Menu",self.touchscreen.main_screen,"",1,"Times",16,"darkorange","black",5,5)
            ]
            self.touchscreen.screen_wipe(buttons,labels)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.handle_exception(error, tb)

    def handle_shelly_message(self, topic, message):
        s = topic.split('/')
        id = s[1]
        if "pro4pm" in id:
            self.handle_shelly_pro4pm_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "1pm" in id or "switch25" in id:
            self.handle_shelly_relay_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "dimmer2" in id:
            self.handle_shelly_dimmer_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "dw" in id:
            self.handle_shelly_dw_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "ht" in id:
            self.handle_shelly_ht_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "motion" in id:
            self.handle_shelly_motion_message(id, topic.replace("shellies/"+id+"/",""), message)
        if "shellyplusi4" in id and "rpc" in topic and self.circuit_authority is True:
            self.handle_shelly_i4_message(message)
        if "shellyuni" in id and "input" in topic:
            self.handle_shelly_uni_message(id, topic, message)
        return
    
    def handle_shelly_pro4pm_message(self, id, topic, message):
        if "status" not in topic:
            return
        data = json.loads(message)
        for circuit in self.config.circuits:
            if(circuit.id != id):
                continue
            if(int(circuit.relay_id) != data["id"]):
                continue
            circuit.status.relay.on = data["output"]
            circuit.status.relay.power = data["apower"]
            circuit.status.relay.energy = data["current"]
            circuit.status.temperature = data["temperature"]["tC"]
            circuit.status.temperature_f = data["temperature"]["tF"]
            circuit.status.voltage = data["voltage"]


    def handle_shelly_uni_message(self, id, topic, message):
        if self.circuit_authority is False:
            return
        alluniconfig = json.load(open(self.source_dir+"shellyuniconfig.json"))
        sid = id.split('-')[-1]
        rid = topic.split('/')[-1]
        uniconfig = alluniconfig[sid]
        if sid not in self.switch_states.keys():
            self.switch_states[sid] = {"0":{"on":False},"1":{"on":False}}
        if message == "1":
            self.switch_states[sid][rid] = {
                "last_on": datetime.now(),
                "on": True
            }
        else:
            states = ""
            last_on = datetime.now()
            for r in self.switch_states[sid]:
                relay = self.switch_states[sid][r]
                if relay["on"] is True:
                    states = states + "1"
                    last_on = relay["last_on"]
                else:
                    states = states + "0"
            if states == "" or states == "00":
                return
            self.switch_states[sid] = {"0":{"on":False},"1":{"on":False}}
            long = "short"
            if last_on < datetime.now() - timedelta(seconds=2):
                long = "long"
            commands = []
            m = self.mode.lower()
            if states == "10":
                if m not in uniconfig["button_a"][long].keys():
                    m = "default"
                commands = uniconfig["button_a"][long][m]
            if states == "01":
                if m not in uniconfig["button_b"][long].keys():
                    m = "default"
                commands = uniconfig["button_b"][long][m]
            if states == "11":
                if m not in uniconfig["button_c"][long].keys():
                    m = "default"
                commands = uniconfig["button_c"][long][m]
            for command in commands:
                if command != "ignore":
                    self.mqtt.publish("smarter_circuits/command",command)
    
    def handle_shelly_i4_message(self, message):
        if self.circuit_authority is False:
            return
        self.mqtt.publish("smarter_circuits/i4_message",message)
        self.remote.handle_i4_message(message)

    def handle_shelly_dimmer_message(self, id, subtopic, message):
        for circuit in self.config.circuits:
            if(circuit.id != id):
                continue
            if subtopic == "light/"+circuit.relay_id:
                circuit.status.relay.on = message == "on"
            if subtopic == "light/"+circuit.relay_id+"/power":
                circuit.status.relay.power = float(message)
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
                if self.circuit_authority is True:
                    self.send_discord_message(self.discord_house_room, sensor.name+" battery level is "+str(sensor.status.battery)+" %")
                self.battery_status_check(sensor)
        if subtopic == "sensor/temperature":
            sensor.status.temperature = float(message)
            if self.circuit_authority is True:
                self.send_discord_message(self.discord_house_room, sensor.name+" temperature is "+message+" F")

        if subtopic == "sensor/humidity":
            sensor.status.humidity = float(message)
            if self.circuit_authority is True:
                dp = self.get_dew_point_f(sensor.status.temperature, sensor.status.humidity)
                self.send_discord_message(self.discord_house_room, sensor.name+" humidity is "+message+" % dew point is "+str(dp)+" F")
    
    def get_dew_point_f(self, tf, rh):
        TC = self.FtoC(tf)
        Td = TC - ((100-rh)/5)
        dp = self.CtoF(Td)
        return dp

    def FtoC(self, f):
        return round((f - 32) * (5 / 9), 2)
    
    def CtoF(self, c):
        return round((c * (9 / 5)) + 32, 2)

    def handle_shelly_motion_message(self, id, subtopic, message):
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
            self.handle_lux(sensor)
        if sensor.status.vibration != data["vibration"]:
            sensor.status.vibration = data["vibration"]
        if sensor.status.timestamp != data["timestamp"]:
            sensor.status.timestamp = data["timestamp"]
        if sensor.status.motion != data["motion"]:
            sensor.status.motion = data["motion"]
            self.handle_motion(sensor)

    def handle_lux(self, sensor:MotionSensor):
        if self.circuit_authority is not True:
            return
        if sensor.status.lux < sensor.lux_under_limit and sensor.lux_last_state_over is True:
            self.execute_command(sensor.lux_under_command)
            sensor.lux_last_state_over = False
        elif sensor.status.lux > sensor.lux_over_limit and sensor.lux_last_state_over is not True:
            self.execute_command(sensor.lux_over_command)
            sensor.lux_last_state_over = True

    def handle_motion(self, sensor:MotionSensor):
        if self.circuit_authority is not True:
            return
        if sensor.id in self.motion_detected:
            return
        if sensor.status.motion is not True:
            return
        
        self.log("SmarterCircuitsMCP","Motion detected: "+sensor.name)
        self.send_discord_message(self.discord_house_room,"Motion detected: "+sensor.name+" (batt "+str(sensor.status.battery)+"%)")
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
        time.sleep(1)
            
        self.log("SmarterCircuitsMCP","Time's up: "+sensor.name)
        for command in sensor.commands:
            if self.conditions_met(command.conditions) is True:
                self.execute_command(command.stop)
        self.motion_detected.remove(sensor.id)

    def handle_smarter_circuits_message(self, topic, message):
        #print(topic+": "+message)
        if topic == "smarter_circuits/restart" and (message == self.name or message == "all"):
            self.log("SmarterCircuitsMCP","restarting by command")
            self.send_discord_message(self.discord_debug_room, self.name+" restarting by command")
            self.stop(True)
            return
        if "smarter_circuits/secrets" in topic:
            filepath = self.source_dir+"secrets.json"
            self.mqtt.publish("smarter_circuits/info/"+self.name,"received secrets")
            with open(filepath, "w") as write_file:
                write_file.write(message)
            self.config.load_secrets()
        if "smarter_circuits/peers" in topic:
            self.received_peer_data(json.loads(message))
        if "smarter_circuits/rollershade" in topic:
            self.received_rollershade_data(topic, message)
        if "smarter_circuits/rollerdoor" in topic:
            self.received_rollerdoor_data(topic, message)
        if "smarter_circuits/mode" in topic and self.mode != message:
            self.mode = message
            self.handle_mode_change()
        if "smarter_circuits/command" in topic and self.circuit_authority is True:
            self.log("SmarterCircuitsMCP","handling smarter circuits command: "+message)
            self.execute_command(message)
        if "smarter_circuits/restart/"+self.name in topic:
            self.log("SmarterCircuitsMCP","received restart command")
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
    
    def received_rollershade_data(self, topic, message):
        s = topic.split("/")
        name = s[2]
        mode = s[3]
        if mode == "state":
            if name not in self.rollershades.keys():
                self.rollershades[name] = RollershadeState(name)
            self.rollershades[name].shade_up = json.loads(message)
        if mode == "command" and self.config.rollershade is True and name == self.name:
            self.log("SmarterCircuitsMCP","rollershade command "+message)
            d = message.split(":")
            addy = int(d[0])
            state = int(d[1])
            if self.rollershade is None:
                self.log("SmarterCircuitsMCP","rollershade is null")
                self.mqtt.publish("smarter_circuits/info/"+self.name, "rollershade is null")
            else:
                self.rollershade.set_state(addy, state)

    def received_rollerdoor_data(self, topic, message):
        s = topic.split("/")
        name = s[2]
        mode = s[3]
        self.log("SmarterCircuitsMCP","received_rollerdoor_data: "+name+" "+mode)
        if mode == "state":
            if name not in self.rollerdoors.keys():
                self.rollerdoors[name] = RollerdoorState(name)
            self.rollerdoors[name].door_open = json.loads(message)
        if mode == "command" and self.config.rollerdoor is True and name == self.name:
            d = message.split(":")
            addy = int(d[0])
            state = int(d[1])
            if self.rollerdoor is None:
                self.log("SmarterCircuitsMCP","rollerdoor is null, try to reinstantiate")
                self.mqtt.publish("smarter_circuits/info/"+self.name, "rollerdoor is null, try to reinstantiate")
                try:
                    self.rollerdoor = Rollerdoor(self,self.name)
                    self.rollerdoor.set_state(addy, state)
                except Exception as e: 
                    error = str(e)
                    tb = traceback.format_exc()
                    self.handle_exception(error, tb)
            else:
                self.rollerdoor.set_state(addy, state)

    def handle_mode_change(self):
        self.log("SmarterCircuitsMCP","mode set to "+self.mode)
        if self.circuit_authority is not True:
            return
        self.send_discord_message(self.discord_house_room,"mode set to "+self.mode)
        for circuit in self.config.circuits:
            if self.mode.lower() in (string.lower() for string in circuit.on_modes):
                self.execute_command("turn on "+circuit.name.lower())
            if self.mode.lower() in (string.lower() for string in circuit.off_modes):
                self.execute_command("turn off "+circuit.name.lower())
            if self.mode == "night":
                self.execute_command("close shades")
            if self.mode == "morning":
                self.execute_command("open shades")
    
    def battery_status_check(self, sensor):
        if sensor.status.battery < 50:
            self.log("BATTERY STATUS","Battery Low: "+sensor.id+"("+sensor.name+")")
            if self.circuit_authority is True:
                self.send_discord_message(self.discord_house_room,"Battery Low: "+sensor.id+" ("+sensor.name+") @ "+str(sensor.status.battery)+"%")
                self.mqtt.publish("notifications","Battery at "+str(sensor.status.battery)+"%\\n"+sensor.id+"\\n("+sensor.name+")")

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

    def send_discord_message(self, room, message):
        self.mqtt.publish("discord/out/"+room,message)

    def send_api_command(self, command):
        #TODO: remove API altogether from system
        self.log("SmarterCircuitsMCP","sending command: "+command)
        try:
            r =requests.get(self.config.command_endpoint+command)
            self.log("SmarterCircuitsMCP","command response: "+str(r.status_code))
        except:
            self.log("SmarterCircuitsMCP",'failed to send command')
    
    def execute_command(self, command):
        if self.circuit_authority is False:
            return
        self.log("SmarterCircuitsMCP","executing command: "+command)
        command = command.lower().replace('-', ' ')
        if " bot says " in command:
            room = command.split(' ')[0]
            command = command.split(' !c ')[1]
            self.send_discord_message(room,"executing command: "+command)
        self.send_discord_message(self.discord_debug_room,"executing command: "+command)
        com = "off"
        command_list = []
        if "show status" in command:
            self.send_system_state()
            return
        if "sensor status" in command:
            self.send_sensor_states()
            return
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
        elif "toggle" in command:
            for ci in range(0,len(self.config.circuits)):
                c = self.config.circuits[ci]
                if c.name.lower() in command or c.name.lower().replace("light","lamp") in command:
                    com = "on"
                    if c.status.relay.on is True:
                        com = "off"
                        c.status.relay.on = False
                    if "dimmer" in c.id:
                        topic = "shellies/"+c.id+"/light/0/command"
                        command_list.append({"t":topic,"c":com})
                    if "pro4pm" in c.id:
                        topic = "shellies/"+c.id+"/rpc"
                        rid = int(c.relay_id)
                        ison = com == "on"
                        ncom = json.dumps({"id": rid, "src":"smarter circuits", "method": "Switch.Set", "params": {"id": rid, "on": ison} })
                        command_list.append({"t":topic,"c":ncom})
                    else:
                        topic = "shellies/"+c.id+"/relay/"+c.relay_id+"/command"
                        command_list.append({"t":topic,"c":com})
        elif "turn" in command:
            for ci in range(0,len(self.config.circuits)):
                c = self.config.circuits[ci]
                if c.name.lower() in command or c.name.lower().replace("light","lamp") in command:
                    if "dimmer" in c.id:
                        topic = "shellies/"+c.id+"/light/0/command"
                        command_list.append({"t":topic,"c":com})
                    if "pro4pm" in c.id:
                        topic = "shellies/"+c.id+"/rpc"
                        rid = int(c.relay_id)
                        ison = com == "on"
                        ncom = json.dumps({"id": rid, "src":"smarter circuits", "method": "Switch.Set", "params": {"id": rid, "on": ison} })
                        command_list.append({"t":topic,"c":ncom})
                    else:
                        topic = "shellies/"+c.id+"/relay/"+c.relay_id+"/command"
                        command_list.append({"t":topic,"c":com})

        elif "first shade" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"0:0"})
            else:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"0:1"})
        elif "second shade" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"1:0"})
            else:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"1:1"})
        elif "third shade" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"2:0"})
            else:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"2:1"})
        elif "shade" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"5:0"})
            else:
                command_list.append({"t":"smarter_circuits/rollershades/rollerpi/command","c":"5:1"})

        elif "shop door" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollerdoors/baydoorpi/command","c":"1:1"})
            if ("close" in command or "shut" in command):
                command_list.append({"t":"smarter_circuits/rollerdoors/baydoorpi/command","c":"1:0"})
        elif "garage door" in command:
            if "open" in command:
                command_list.append({"t":"smarter_circuits/rollerdoors/baydoorpi/command","c":"0:1"})
            if "close" in command or "shut" in command:
                command_list.append({"t":"smarter_circuits/rollerdoors/baydoorpi/command","c":"0:0"})
        elif "set temperature" in command:
            s = command.replace("set ","").replace(" the ","").split(' ')
            val = int(s[len(s)-1])
            for thermokey in self.thermostats.keys():
                thermo = self.thermostats[thermokey]
                command_list.append({"t":"smarter_circuits/thermosettings/"+thermo.room.lower(),"c":"temperature_high_setting:"+str(val+1)})
                command_list.append({"t":"smarter_circuits/thermosettings/"+thermo.room.lower(),"c":"temperature_low_setting:"+str(val-1)})
        elif "set" in command:
            s = command.split(' ')
            room = s[1]
            setting = s[2]
            command_list.append({"t":"smarter_circuits/thermosettings/"+room,"c":setting})
        elif "peers" in command:
            data = self.peer_report()
            self.send_discord_message(self.discord_house_room,data)
        elif "circuits" in command:
            data = self.circuit_report()
            self.send_discord_message(self.discord_house_room,data)
        elif "sensors" in command:
            data = self.sensor_report()
            self.send_discord_message(self.discord_house_room,data)
        elif "full report" in command:
            data = self.peer_report()
            data = data + "\n" + self.circuit_report()
            data = data + "\n" + self.sensor_report()
            self.send_discord_message(self.discord_house_room,data)

        for cmd in command_list:
            self.mqtt.publish(cmd["t"],cmd["c"])
    
    def peer_report(self):
        data = "Peers:\n"
        for peer in self.peers:
            data = data + peer.name + " (" + peer.ip_address.split('.')[-1] + ") " + peer.model + " "
            if peer.circuit_authority is True:
                data = data + "circuit authority"
            data = data + "\n"
        return data

    def circuit_report(self):
        data = "Circuits:\n"
        for c in self.config.circuits:
            data = data + c.name + " (" + c.ip_address.split('.')[-1] + ") " + str(c.status.relay.power) + "W "
            if c.status.relay.on is True:
                data = data + "on"
            data = data + "\n"
        return data
    
    def sensor_report(self):
        data = "Sensors:\n"
        for sensor_id in self.config.motion_sensors.keys():
            sensor = self.config.motion_sensors[sensor_id]
            data = data + sensor.name + " motion (" + sensor.ip_address.split('.')[-1] + ") batt: " + str(sensor.status.battery) + "% lux: " + str(sensor.status.lux) + " timestamp: " + str(sensor.status.timestamp) + "\n"
        for sensor_id in self.config.ht_sensors.keys():
            sensor = self.config.ht_sensors[sensor_id]
            data = data + sensor.name + " HT " + str(round(sensor.status.temperature,1)) + " F " + str(round(sensor.status.humidity,1)) +"% (batt "+str(round(sensor.status.battery,1))+"%)\n"
        return data

    def set_command(self, args):
        if args[1] == "high":
            val = int(args[len(args)-1])


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
            self.log("SmarterCircuitsMCP","new peer "+peer["name"])
            self.peers.append(SmarterCircuitsPeer(peer["id"],peer["name"],peer["ip_address"],peer["model"],peer["circuit_authority"],peer["timestamp"],peer["thermostat"],peer["rollershade"],peer["rollerdoor"]))
    
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
    
    def handle_exception(self, error, tb, origin = "SmarterCircuitsMCP"):
        try:
            self.log(origin,"error: "+error)
            self.log(origin,"traceback: "+tb)
            self.mqtt.publish("smarter_circuits/errors/"+self.name,error)
            self.mqtt.publish("smarter_circuits/errors/"+self.name+"/traceback",tb)
            self.send_discord_message(self.discord_debug_room,self.name+" error: "+error+"\n"+tb)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            print(error)
            print(tb)


class SmarterCircuitsPeer:
    def __init__(self, id, name, ip_address, model, circuit_authority, timestamp, thermostat, rollershade, rollerdoor):
        self.id = id
        self.name = name
        self.ip_address = ip_address
        self.model = model
        self.circuit_authority = circuit_authority
        self.timestamp = timestamp
        self.thermostat = thermostat
        self.rollershade = rollershade
        self.rollerdoor = rollerdoor
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


if __name__ == "__main__":
    myname = socket.gethostname()
    try:
        myip = subprocess.check_output(['hostname', '-I']).decode("utf-8").replace("\n","").split(' ')[0]
    except:
        myip = "127.0.0.1"
    try:
        uname = subprocess.check_output(['uname','-m']).decode("utf-8").replace("\n","")
    except:
        uname = "x86"
    model = "pc"
    if uname.__contains__("arm"):
        model = subprocess.check_output(['cat','/proc/device-tree/model']).decode("utf-8").replace("\n","")
    print(uname)
    print(model)
    mcp = SmarterCircuitsMCP(myname, myip, model)