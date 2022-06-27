import time
import requests
import json
from datetime import datetime, timedelta
import socket
import os
import _thread
from SmarterLogging import SmarterLog
libraries_available = False
try:
    import Adafruit_DHT
    import RPi.GPIO as GPIO
    libraries_available = True
except:
    libraries_available = False

class ThermostatView:
    def __init__(self, data):
        self.room = data["room"]
        self.settings = ThermostatSettings()
        self.settings.failed_read_halt_limit = data["settings"]["failed_read_halt_limit"]
        self.settings.temperature_high_setting = data["settings"]["temperature_high_setting"]
        self.settings.temperature_low_setting = data["settings"]["temperature_low_setting"]
        self.settings.humidity_setting = data["settings"]["humidity_setting"]
        self.settings.air_circulation_minutes = data["settings"]["air_circulation_minutes"]
        self.settings.circulation_cycle_minutes = data["settings"]["circulation_cycle_minutes"]
        self.settings.ventilation_cycle_minutes = data["settings"]["ventilation_cycle_minutes"]
        self.settings.stage_limit_minutes = data["settings"]["stage_limit_minutes"]
        self.settings.stage_cooldown_minutes = data["settings"]["stage_cooldown_minutes"]
        self.settings.use_whole_house_fan = data["settings"]["use_whole_house_fan"]
        self.settings.system_disabled = str(data["settings"]["system_disabled"]).lower() == "true"
        self.settings.swing_temp_offset = data["settings"]["swing_temp_offset"]
        self.state = ThermostatState()
        self.state.temperature = data["state"]["temperature"]
        self.state.humidity = data["state"]["humidity"]
        self.state.heat_on = data["state"]["heat_on"]
        self.state.ac_on = data["state"]["ac_on"]
        self.state.fan_on = data["state"]["fan_on"]
        self.state.whf_on = data["state"]["whf_on"]
        self.state.status = data["state"]["status"]

class ThermostatSettings:
    def __init__(self):
        self.failed_read_halt_limit = 10
        self.temperature_high_setting = 73
        self.temperature_low_setting = 69
        self.humidity_setting = 50
        self.air_circulation_minutes = 30
        self.circulation_cycle_minutes = 10
        self.ventilation_cycle_minutes = 10
        self.stage_limit_minutes = 15
        self.stage_cooldown_minutes = 5
        self.use_whole_house_fan = False
        self.system_disabled = False
        self.swing_temp_offset = 1
        self.manual_override = False

    def load_json(self, json_string):
        data = json.loads(json_string)
        self.failed_read_halt_limit = data["failed_read_halt_limit"]
        self.temperature_high_setting = data["temperature_high_setting"]
        self.temperature_low_setting = data["temperature_low_setting"]
        self.humidity_setting = data["humidity_setting"]
        self.air_circulation_minutes = data["air_circulation_minutes"]
        self.circulation_cycle_minutes = data["circulation_cycle_minutes"]
        self.ventilation_cycle_minutes = data["ventilation_cycle_minutes"]
        self.stage_limit_minutes = data["stage_limit_minutes"]
        self.stage_cooldown_minutes = data["stage_cooldown_minutes"]
        self.use_whole_house_fan = data["use_whole_house_fan"]
        self.system_disabled = str(data["system_disabled"]).lower() == "true"
        self.swing_temp_offset = data["swing_temp_offset"]
        try:
            self.manual_override = data["manual_override"]
        except:
            pass
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class ThermostatState:
    def __init__(self):
        self.temperature = None
        self.humidity = None
        self.heat_on = False
        self.ac_on = False
        self.fan_on = False
        self.whf_on = False
        self.status = "loading"

class Thermostat:
    def __init__(self, mcp):
        self.mcp = mcp
        self.room = self.mcp.name.replace("thermopi","")

        self.settings = ThermostatSettings()
        self.settings_loaded = False
        
        self.extra_ventilation_circuits = []
        self.extra_circulation_circuits = []
        self.humidification_circuits = []
        self.post = True

        self.state = ThermostatState()
        
        self.failed_reads = 0
        self.last_circulation = datetime.now()
        self.circulate_until = datetime.now() + timedelta(minutes=1)
        self.circulating = False
        self.has_circulated = False
        self.last_ventilation = datetime.now()
        self.ventilate_until = datetime.now() + timedelta(minutes=1)
        self.ventilating = False
        self.has_ventilated = False
        self.start_stage = datetime.now() - timedelta(minutes=1)
        self.delay_stage = datetime.now()
        self.shower_vent = False
        self.heat_pin = 26
        self.ac_pin = 20
        self.fan_pin = 21
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heat_pin, GPIO.OUT)
        GPIO.setup(self.ac_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)

        _thread.start_new_thread(self.start, ())

    def start(self):
        self.halt()
        time.sleep(2)
        self.post = False
        self.log("begin cycling")
        self.load_settings()
        while True:
            try:
                self.cycle()
            except:
                self.log("BAD CYCLE!!!")
            time.sleep(10)
    
    def set(self, setting, value):
        SmarterLog.log("SmarterThermostat","set setting "+setting+" = "+ str(value))
        self.mcp.send_discord_message(self.mcp.discord_house_room, self.mcp.name+" "+setting+" set to "+str(value))
        if setting == "air_circulation_minutes": self.settings.air_circulation_minutes = int(value)
        if setting == "circulation_cycle_minutes": self.settings.circulation_cycle_minutes = int(value)
        if setting == "failed_read_halt_limit": self.settings.failed_read_halt_limit = int(value)
        if setting == "humidity_setting": self.settings.humidity_setting = int(value)
        if setting == "stage_cooldown_minutes": self.settings.stage_cooldown_minutes = int(value)
        if setting == "stage_limit_minutes": self.settings.stage_limit_minutes = int(value)
        if setting == "swing_temp_offset": self.settings.swing_temp_offset = int(value)
        if setting == "system_disabled": self.settings.system_disabled = str(value).lower() == "true"
        if setting == "temperature_high_setting": self.settings.temperature_high_setting = int(value)
        if setting == "temperature_low_setting": self.settings.temperature_low_setting = int(value)
        if setting == "use_whole_house_fan": self.settings.use_whole_house_fan = bool(value)
        if setting == "ventilation_cycle_minutes": self.settings.ventilation_cycle_minutes = int(value)
        if setting == "settings_from_circuit_authority": self.settings_loaded = bool(value)
        if setting == "manual_override": self.settings_loaded = bool(value)
        if setting == "ac" and value == "on": 
            self.ac_on()
            return
        if setting == "heat" and value == "on": 
            self.heat_on()
            return
        if setting == "fan" and value == "on": 
            self.fan_on()
            return
        if setting == "ac" and value == "off": 
            self.ac_off()
            return
        if setting == "heat" and value == "off": 
            self.heat_off()
            return
        if setting == "fan" and value == "off": 
            self.fan_off()
            return
        self.save_settings()
    
    def save_settings(self):
        settings_file = os.path.dirname(os.path.realpath(__file__))+"/thermosettings.json"
        with open(settings_file, "w") as write_file:
            write_file.write(self.settings.toJSON())
        
    def load_settings(self):
        settings_file = os.path.dirname(os.path.realpath(__file__))+"/thermosettings.json"
        if os.path.exists(settings_file) is True:
            f = open(settings_file)
            self.settings.load_json(f.read())
            self.settings_loaded = True
            
    def log(self, message):
        text = "[" + self.room + "] " + message
        if self.state.temperature is not None:
            text = text  + " ("+str(round(self.state.temperature,2))+"F "+str(round(self.state.humidity,2))+"%)"
        SmarterLog.log("SmarterThermostat", text)
        self.mcp.send_discord_message(self.mcp.discord_house_room, text)
    
    def set_circuit(self, circuit_pin, state):
        if state is False:
            GPIO.output(circuit_pin, GPIO.HIGH)
        else:
            GPIO.output(circuit_pin, GPIO.LOW)
    
    def read_sensor(self):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
        while temperature is None and self.failed_reads < self.settings.failed_read_halt_limit:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
            if temperature is None:
                self.failed_reads = self.failed_reads + 1
                time.sleep(1)
        if temperature is not None:
            self.state.temperature = temperature * 9/5.0 + 32
        else:
            self.log("sensor failed")
            self.state.temperature = 0

        if humidity is not None:
            self.state.humidity = humidity
        else:
            self.state.humidity = 0
        
        self.failed_reads = 0

    def heat_off(self):
        try:
            self.log("heat_off")
            self.report(True)
        except:
            print("nolog")
        if self.state.heat_on is True:
            self.last_circulation = datetime.now()
        self.set_circuit(self.heat_pin, False)
        self.state.heat_on = False
        self.report()

    def ac_off(self):
        try:
            self.log("ac_off")
            self.report(True)
        except:
            print("nolog")
        if self.state.ac_on is True:
            self.last_circulation = datetime.now()
        self.set_circuit(self.ac_pin, False)
        self.state.ac_on = False
        self.has_circulated = False
        self.report()

    def fan_off(self):
        try:
            self.log("fan_off")
            self.report(True)
        except:
            print("nolog")
        if self.state.fan_on is True:
            self.last_circulation = datetime.now()
        self.set_circuit(self.fan_pin, False)
        self.state.fan_on = False
        self.report()

    def heat_on(self):
        try:
            self.log("heat_on")
            self.report(True)
        except:
            print("nolog")
        if self.state.ac_on is True or self.state.fan_on is True:
            return
        self.set_circuit(self.heat_pin, True)
        self.state.heat_on = True
        self.report()

    def ac_on(self):
        try:
            self.log("ac_on")
            self.report(True)
        except:
            print("nolog")
        if self.state.heat_on is True or self.state.fan_on is True:
            return
        self.set_circuit(self.ac_pin, True)
        self.state.ac_on = True
        self.report()

    def fan_on(self):
        try:
            self.log("fan_on")
            self.report(True)
        except:
            print("nolog")
        if self.state.ac_on is True or self.state.heat_on is True:
            return
        self.set_circuit(self.fan_pin, True)
        self.state.fan_on = True
        self.report()

    def whf_on(self):
        try:
            self.log("whf_on")
            self.report(True)
        except:
            print("nolog")
        self.state.whf_on = True
        self.send_command('turn on whole house fan')
        for evc in self.extra_ventilation_circuits:
            self.send_command('turn on '+evc)
        mode = self.mcp.mode.lower()
        more = self.state.temperature is not None and self.state.temperature > self.settings.temperature_high_setting + 3
        if more is True and mode != "shower":
            self.state.status = "assisted_ventilation"
            self.send_command('turn on shower fan')
            self.shower_vent = True
        self.report()

    def whf_off(self):
        try:
            self.log("whf_off")
            self.report(True)
        except:
            print("nolog")
        self.state.whf_on = False
        self.send_command('turn off whole house fan')
        for evc in self.extra_ventilation_circuits:
            self.send_command('turn off '+evc)
        mode = self.mcp.mode.lower()
        if self.shower_vent is True and mode != "shower":
            self.send_command('turn off shower fan')
        self.shower_vent = False
        self.report()

    def halt(self):
        try:
            SmarterLog.log("SmarterThermostat","halting")
            self.report(True)
        except:
            print("nolog")
        GPIO.output(self.heat_pin, GPIO.HIGH)
        GPIO.output(self.ac_pin, GPIO.HIGH)
        GPIO.output(self.fan_pin, GPIO.HIGH)
        self.send_command('turn off whole house fan')
        self.send_command('turn off circulating fan')
        self.send_command('turn off floor fan')
        self.state.fan_on = False
        self.state.heat_on = False
        self.state.ac_on = False
        self.state.whf_on = False
        self.report()

    def cycle(self):
        self.read_sensor()
        if self.state.temperature is None or self.state.temperature == 0:
            self.halt()
            self.state.status = "sensor_fail"
            SmarterLog.log("SmarterThermostat","halting because sensor sucks")
            self.report()
            return
        
        self.report()

        if self.settings.manual_override is True:
            return

        if self.circulating is True:
            if datetime.now() > self.circulate_until:
                self.stop_circulating()
            else:
                return

        if self.ventilating is True:
            if datetime.now() > self.ventilate_until:
                self.stop_ventilating()
            else:
                return

        if self.delay_stage > datetime.now():
            self.state.status = "delayed"
            return

        if self.settings.system_disabled is True:
            self.state.status = "disabled"
            if self.state.ac_on is True:
                self.ac_off()
            if self.state.heat_on is True:
                self.heat_off()
            if self.circulating is True:
                self.stop_circulating()
            if self.ventilating is True:
                self.stop_ventilating()
            return
        
        if round(self.state.temperature) > self.settings.temperature_high_setting and self.state.ac_on is False:
            self.cool_down()
            return
        
        if round(self.state.temperature) > self.settings.temperature_high_setting - self.settings.swing_temp_offset and self.state.ac_on is True: # this is half of my mercury switch/magnet for delaying a "swing" state
            self.cool_down()
            return
        
        if round(self.state.temperature) < self.settings.temperature_low_setting and self.state.heat_on is False:
            self.warm_up()
            return
        
        if round(self.state.temperature) < self.settings.temperature_low_setting + self.settings.swing_temp_offset and self.state.heat_on is True: # this is the other half of my mercury switch/magnet for delaying a "swing" state
            self.warm_up()
            return
        
        if self.state.heat_on is True:
            self.heat_off()
        
        if self.state.ac_on is True:
            self.ac_off()

        if self.settings.air_circulation_minutes > 0 and datetime.now() > self.last_circulation + timedelta(minutes=self.settings.air_circulation_minutes):
            self.circulate_air(self.settings.circulation_cycle_minutes)
            return
            
        self.state.status = "stand_by"

    def cool_down(self):
        if self.state.ac_on is True:
            if self.start_stage < datetime.now() - timedelta(minutes=self.settings.stage_limit_minutes):
                self.delay_stage = datetime.now() + timedelta(minutes=self.settings.stage_cooldown_minutes)
                self.ac_off()
            return
        # if round(humidity) > self.settings.humidity_setting and self.settings.humidity_setting > 0 and self.has_circulated is False:
        #     self.circulate_air(circulation_cycle_minutes)
        if self.state.temperature > self.settings.temperature_high_setting + 2 and self.has_ventilated is False:
            self.ventilate_air(self.settings.ventilation_cycle_minutes)
        self.has_ventilated = False
        self.start_stage = datetime.now()
        self.ac_on()
        self.state.status = "cooling"

    def warm_up(self):
        if self.state.heat_on is True:
            if self.start_stage < datetime.now() - timedelta(minutes=self.settings.stage_limit_minutes):
                self.delay_stage = datetime.now() + timedelta(minutes=self.settings.stage_cooldown_minutes)
                self.heat_off()
            return
        self.start_stage = datetime.now()
        self.heat_on()
        self.state.status = "heating"

    def circulate_air(self, minutes):
        if self.circulating is True:
            return
        self.fan_on()
        self.circulate_until = datetime.now() + timedelta(minutes=minutes) 
        self.circulating = True
        self.state.status = "circulating"

    def ventilate_air(self, minutes):
        if self.ventilating is True:
            return
        if self.settings.use_whole_house_fan is True:
            self.whf_on()
        self.ventilate_until = datetime.now() + timedelta(minutes=minutes) 
        self.ventilating = True
        self.state.status = "ventilating"

    def stop_circulating(self):
        self.fan_off()
        self.circulating = False
        self.has_circulated = True

    def stop_ventilating(self):
        if self.settings.use_whole_house_fan is True:
            self.whf_off()
        self.ventilating = False
        self.has_ventilated = True

    def send_command(self, command):
        self.log("sending command: "+command)
        self.mcp.mqtt.publish("smarter_circuits/command",command)

    def report(self, to_log = False):
        state = {
            "ac_on": self.state.ac_on,
            "fan_on": self.state.fan_on,
            "heat_on": self.state.heat_on,
            "humidity": self.state.humidity,
            "status": self.state.status,
            "temperature": self.state.temperature,
            "whf_on": self.state.whf_on
        }

        settings = {
            "air_circulation_minutes": self.settings.air_circulation_minutes,
            "circulation_cycle_minutes": self.settings.circulation_cycle_minutes,
            "failed_read_halt_limit": self.settings.failed_read_halt_limit,
            "humidity_setting": self.settings.humidity_setting,
            "stage_cooldown_minutes": self.settings.stage_cooldown_minutes,
            "stage_limit_minutes": self.settings.stage_limit_minutes,
            "swing_temp_offset": self.settings.swing_temp_offset,
            "system_disabled": self.settings.system_disabled,
            "temperature_high_setting": self.settings.temperature_high_setting,
            "temperature_low_setting": self.settings.temperature_low_setting,
            "use_whole_house_fan": self.settings.use_whole_house_fan,
            "ventilation_cycle_minutes": self.settings.ventilation_cycle_minutes
        }

        data = {
            "room": self.room,
            "state": state,
            "settings": settings
        }
        json_string = json.dumps(data)
        if to_log is True:
            SmarterLog.log("SmarterThermostat",json_string)
        else:
            self.mcp.mqtt.publish("smarter_circuits/thermostats/"+self.room, json_string)