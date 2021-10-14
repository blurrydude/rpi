from SmarterLogging import SmarterLog
from ShellyDevices import RelayModule
import _thread
try:
    import tkinter as tk
    libraries_available = True
except:
    libraries_available = False
import time

class Touchscreen:
    def __init__(self, mcp):
        self.mcp = mcp
        self.window = tk.Tk()
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()

        self.zone = "Living Room"
        self.buttons = []
        self.labels = []

        self.window.attributes("-fullscreen", 1)
        self.window.geometry(str(width)+"x"+str(height))
        self.window.configure(bg='black')
        self.window.columnconfigure(0, minsize=width/3)
        self.window.columnconfigure(1, minsize=width/3)
        self.window.columnconfigure(2, minsize=width/3)

        self.title = SmartLabel(0,1,"Main 2.0","Times",24,"black","white",5,5)
        self.title.draw()

        self.main_screen()
        
        self.start()

    
    def start(self):
        self.window.mainloop()
    
    def stop(self):
        self.window.destroy()
        self.mcp.stop()
    
    def toggle_circuit(self, circuit:RelayModule):
        state = "on"
        if circuit.status.relay.on is True:
            state = "off"
        command = "turn "+state+" "+circuit.name.lower()
        SmarterLog.log("SmarterTouchscreen","command: "+command)
        self.mcp.mqtt.publish("smarter_circuits/command",command)
        _thread.start_new_thread(self.make_sure, (circuit,state))
        self.main_screen()
    
    def make_sure(self,circuit:RelayModule,expected_state):
        if circuit.id in self.mcp.config.secrets.keys():
            SmarterLog.log("SmarterTouchscreen","make_sure: no key to check "+circuit.id+"("+circuit.name+") "+expected_state)
            return
        key = self.mcp.config.secrets[circuit.id]
        SmarterLog.log("SmarterTouchscreen","make_sure: "+circuit.id+"("+circuit.name+") "+expected_state)
        data = circuit.http_status(key)
        check = data["relays"][int(circuit.relay_id)]["ison"]
        done = (check is True and expected_state == "on") or (check is not True and expected_state == "off")
        tries = 0
        while done is not True and tries < 3:
            data = circuit.http_status(key)
            check = data["relays"][int(circuit.relay_id)]["ison"]
            done = (check is True and expected_state == "on") or (check is not True and expected_state == "off")
            tries = tries + 1
            time.sleep(1)
        if done is not True:
            SmarterLog.log("SmarterTouchscreen","make_sure: "+circuit.id+"("+circuit.name+") is not "+expected_state+" so we'll http_toggle")
            circuit.http_toggle(key,expected_state)
        else:
            SmarterLog.log("SmarterTouchscreen","make_sure: "+circuit.id+"("+circuit.name+") is "+expected_state)
        
    def set_mode(self, mode):
        self.mcp.mqtt.publish("smarter_circuits/mode",mode.lower())
        self.main_screen()
    
    def screen_wipe(self, buttons, labels):
        self.clear()
        self.buttons = buttons
        self.labels = labels
        self.draw()
    
    def main_screen(self):
        self.title.text.set(self.mcp.name)
        buttons = [
            SmartButton(0,2,"Close",self.stop,"",1,"Times",16,"darkred","white",5,5),
            SmartButton(1,1,"Zones",self.zone_screen,"",2,"Times",20,"darkblue","white",5,5),
            SmartButton(2,1,"Modes",self.mode_screen,"",2,"Times",20,"darkgreen","white",5,5),
            SmartButton(3,1,"Thermostat",self.thermostat_screen,"",2,"Times",20,"magenta","black",5,5),
            SmartButton(4,1,"Shades",self.roller_screen,"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(5,1,"Doors",self.door_screen,"",2,"Times",20,"green","black",5,5),
            SmartButton(6,1,"Info",self.status_screen,"",2,"Times",20,"purple","black",5,5),
        ]
        labels = []

        self.screen_wipe(buttons,labels)
    
    def status_screen(self):
        self.title.text.set(self.mcp.name)
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5)
        ]
        labels = []
        data = {}
        total = 0.0
        for circuit in self.mcp.config.circuits:
            power = circuit.status.relay.power
            data[circuit.name] = {"power":str(round(power,2)) + " W","on":circuit.status.relay.on}
            total = total + power
        labels.append(SmartLabel(1,1,"Total: "+str(round(total,2))+" W","Times",24,"black","white",5,5))
        r = 2
        c = 0
        for key in data.keys():
            datum = data[key]
            color = "white"
            if datum["on"] is True:
                color = "cyan"
            labels.append(SmartLabel(r,c,key+": "+datum["power"],"Times",16,"black","white",5,5))
            if c == 2:
                r = r + 1
                c = 0
            else:
                c = c + 1

        self.screen_wipe(buttons,labels)
    
    def open_door(self, which):
        self.mcp.mqtt.publish("smarter_circuits/command","open "+which+" door")
    
    def close_door(self, which):
        self.mcp.mqtt.publish("smarter_circuits/command","close "+which+" door")

    def door_screen(self):
        self.title.text.set("Doors")
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5),
            SmartButton(3,0,"Open Garage Door",lambda d="garage": self.open_door(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(3,2,"Open Shop Door",lambda d="shop": self.open_door(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(4,0,"Close Garage Door",lambda d="garage": self.close_door(d),"",2,"Times",20,"darkblue","white",5,5),
            SmartButton(4,2,"Close Shop Door",lambda d="shop": self.close_door(d),"",2,"Times",20,"darkblue","white",5,5),
        ]
        labels = []

        self.screen_wipe(buttons,labels)
    
    def open_shade(self, which):
        self.mcp.mqtt.publish("smarter_circuits/command","open "+which+" shade")
    
    def close_shade(self, which):
        self.mcp.mqtt.publish("smarter_circuits/command","close "+which+" shade")

    def roller_screen(self):
        self.title.text.set("Shades")
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5),
            SmartButton(1,1,"Open All",lambda d="": self.open_shade(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(2,1,"Close All",lambda d="": self.close_shade(d),"",2,"Times",20,"darkblue","white",5,5),
            SmartButton(3,0,"Open Left",lambda d="first": self.open_shade(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(3,1,"Open Center",lambda d="second": self.open_shade(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(3,2,"Open Right",lambda d="third": self.open_shade(d),"",2,"Times",20,"darkorange","black",5,5),
            SmartButton(4,0,"Close Left",lambda d="first": self.close_shade(d),"",2,"Times",20,"darkblue","white",5,5),
            SmartButton(4,1,"Close Center",lambda d="second": self.close_shade(d),"",2,"Times",20,"darkblue","white",5,5),
            SmartButton(4,2,"Close Right",lambda d="third": self.close_shade(d),"",2,"Times",20,"darkblue","white",5,5),
        ]
        labels = []

        self.screen_wipe(buttons,labels)
    
    def cool(self, room):
        thermostat = self.mcp.thermostats[room]
        target_low = thermostat.settings.temperature_low_setting - 1
        self.mcp.thermostats[room].settings.temperature_low_setting = target_low
        target_high = thermostat.settings.temperature_high_setting - 1
        self.mcp.thermostats[room].settings.temperature_high_setting = target_high
        self.mcp.mqtt.publish("smarter_circuits/thermosettings/"+room,"temperature_low_setting:"+str(target_low))
        time.sleep(0.5)
        self.mcp.mqtt.publish("smarter_circuits/thermosettings/"+room,"temperature_high_setting:"+str(target_high))
        time.sleep(1)
        self.thermostat_screen()

    def warm(self, room):
        thermostat = self.mcp.thermostats[room]
        target_low = thermostat.settings.temperature_low_setting + 1
        self.mcp.thermostats[room].settings.temperature_low_setting = target_low
        target_high = thermostat.settings.temperature_high_setting + 1
        self.mcp.thermostats[room].settings.temperature_high_setting = target_high
        self.mcp.mqtt.publish("smarter_circuits/thermosettings/"+room,"temperature_low_setting:"+str(target_low))
        time.sleep(0.5)
        self.mcp.mqtt.publish("smarter_circuits/thermosettings/"+room,"temperature_high_setting:"+str(target_high))
        time.sleep(1)
        self.thermostat_screen()

    def toggle_system(self, room):
        thermostat = self.mcp.thermostats[room]
        target = thermostat.settings.system_disabled is False
        self.mcp.thermostats[room].settings.system_disabled = target
        self.mcp.mqtt.publish("smarter_circuits/thermosettings/"+room,"system_disabled:"+str(target))
        time.sleep(1)
        self.thermostat_screen()

    def thermostat_screen(self):
        self.title.text.set("Thermostats")
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5)
        ]
        labels = []
        r = 1
        c = len(self.mcp.thermostats)
        for room in self.mcp.thermostats.keys():
            thermostat = self.mcp.thermostats[room]
            setting = str(thermostat.settings.temperature_low_setting) + "/" + str(thermostat.settings.temperature_high_setting)
            state = ""
            if thermostat.state.heat_on is True:
                state = state + "H"
            if thermostat.state.ac_on is True:
                state = state + "A"
            if thermostat.state.fan_on is True:
                state = state + "F"
            if thermostat.state.whf_on is True:
                state = state + "W"
            labels.append(SmartLabel(r,0,room.upper()+ " " + setting,"Times",16,"black","white",5,5))
            labels.append(SmartLabel(r,1,str(round(thermostat.state.temperature,1))+"F","Times",24,"black","red",5,5))
            labels.append(SmartLabel(r,2,str(round(thermostat.state.humidity,1))+"% - "+state,"Times",24,"black","blue",5,5))
            r = r + 1

        for sensor_id in self.mcp.config.ht_sensors.keys():
            sensor = self.mcp.config.ht_sensors[sensor_id]
            labels.append(SmartLabel(r,0,sensor.name.upper(),"Times",16,"black","white",5,5))
            labels.append(SmartLabel(r,1,str(round(sensor.status.temperature,1))+"F","Times",24,"black","red",5,5))
            labels.append(SmartLabel(r,2,str(round(sensor.status.humidity,1))+"%","Times",24,"black","blue",5,5))
            
            r = r + 1

        for room in self.mcp.thermostats.keys():
            thermostat = self.mcp.thermostats[room]
            color = "darkgreen"
            if thermostat.settings.system_disabled is True:
                color = "darkred"
            buttons.append(SmartButton(r,0,"toggle "+room,lambda d=room: self.toggle_system(d),"",2,"Times",20,color,"white",5,5))
            buttons.append(SmartButton(r,1,"cool "+room,lambda d=room: self.cool(d),"",2,"Times",20,"darkblue","white",5,5))
            buttons.append(SmartButton(r,2,"warm "+room,lambda d=room: self.warm(d),"",2,"Times",20,"darkred","white",5,5))
            r = r + 1

        self.screen_wipe(buttons,labels)
    
    def mode_screen(self):
        self.title.text.set("Mode: "+self.mcp.mode)
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5)
        ]
        labels = []
        modes = []
        r = 1
        c = 0
        for circuit in self.mcp.config.circuits:
            for mode in circuit.on_modes:
                if mode not in modes:
                    modes.append(mode)
            for mode in circuit.off_modes:
                if mode not in modes:
                    modes.append(mode)
        for mode in modes:
            buttons.append(SmartButton(r,c,mode,lambda d=mode: self.set_mode(d),"",2,"Times",20,"darkblue","white",5,5))
            if c == 2:
                r = r + 1
                c = 0
            else:
                c = c + 1

        self.screen_wipe(buttons,labels)

    def zone_button_screen(self, zone):
        self.title.text.set(zone)
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5),
            SmartButton(0,2,"Zones",self.zone_screen,"",1,"Times",16,"darkblue","white",5,5)
        ]
        r = 1
        c = 0
        for circuit in self.mcp.config.circuits:
            if zone in circuit.zones:
                color = "darkred"
                if circuit.status.relay.on is True:
                    color = "darkgreen"
                buttons.append(SmartButton(r,c,circuit.name,lambda d=circuit: self.toggle_circuit(d),"",2,"Times",20,color,"white",5,5))
                if c == 2:
                    r = r + 1
                    c = 0
                else:
                    c = c + 1
        self.screen_wipe(buttons, [])
    
    def zone_screen(self):
        self.title.text.set("Zones")
        zones = []
        buttons = [
            SmartButton(0,0,"Main Menu",self.main_screen,"",1,"Times",16,"darkorange","black",5,5)
        ]
        for circuit in self.mcp.config.circuits:
            for zone in circuit.zones:
                if zone not in zones:
                    zones.append(zone)
        r = 1
        c = 0
        for zone in zones:
            buttons.append(SmartButton(r,c,zone,lambda d=zone: self.zone_button_screen(d),"",1,"Times",20,"darkblue","white",5,5))
            
            if c == 2:
                r = r + 1
                c = 0
            else:
                c = c + 1
        self.screen_wipe(buttons, [])

    def clear(self):
        for button in self.buttons:
            button.clear()
        
        for label in self.labels:
            label.clear()
        
        self.buttons = []
        self.labels = []

    def draw(self):
        for button in self.buttons:
            button.draw()
        
        for label in self.labels:
            label.draw()

    
class SmartButton:
    def __init__(self, row, col, text, func, target, height, fontname, fontsize, bg, fg, padx, pady):
        self.text = tk.StringVar()
        self.text.set(text)
        self.func = func
        self.target = target
        self.height = height
        self.fontname = fontname
        self.fontsize = fontsize
        self.bg = bg
        self.fg = fg
        self.row = row
        self.col = col
        self.sticky = "nesw"
        self.padx = padx
        self.pady = pady
        self.__make__()
    def __make__(self):
        #self.button = tk.Button(text=self.text,command=lambda d=self: self.screen.onclick(d), height=self.height, font = (self.fontname, self.fontsize), bg=self.bg, fg=self.fg)
        self.button = tk.Button(textvariable=self.text,command=self.func, height=self.height, font = (self.fontname, self.fontsize), bg=self.bg, fg=self.fg)
    def draw(self):
        self.button.grid(row=self.row, column=self.col, sticky=self.sticky, padx=self.padx, pady=self.pady)
    def clear(self):
        self.button.grid_forget()
    def redraw(self):
        self.clear()
        self.__make__()
        self.draw()
    def set_text(self, text):
        self.text.set(text)

class SmartLabel:
    def __init__(self, row, col, text, fontname, fontsize, bg, fg, padx, pady):
        self.text = tk.StringVar()
        self.text.set(text)
        self.fontname = fontname
        self.fontsize = fontsize
        self.bg = bg
        self.fg = fg
        self.row = row
        self.col = col
        self.sticky = "nesw"
        self.padx = padx
        self.pady = pady
        self.__make__()
    def __make__(self):
        self.label = tk.Label(textvariable=self.text, font = (self.fontname, self.fontsize), bg=self.bg, fg=self.fg)
    def draw(self):
        self.label.grid(row=self.row, column=self.col, sticky=self.sticky, padx=self.padx, pady=self.pady)
    def clear(self):
        self.label.grid_forget()
    def redraw(self):
        self.clear()
        self.__make__()
        self.draw()
    def set_text(self, text):
        self.text.set(text)
