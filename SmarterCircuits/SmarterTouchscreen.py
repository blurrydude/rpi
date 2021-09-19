from SmarterLogging import SmarterLog
from ShellyDevices import RelayModule
import tkinter as tk
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

        self.button_exit = SmartButton(0,0,"Close",self.stop,"",1,"Times",16,"darkred","white",5,5)
        self.button_exit.draw()

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
        self.mcp.execute_command(command)
        self.main_screen()
    
    def set_mode(self, mode):
        command = "set mode " + mode.lower()
        self.mcp.execute_command(command)
        self.main_screen()
    
    def screen_wipe(self, buttons, labels):
        self.clear()
        self.buttons = buttons
        self.labels = labels
        self.draw()
    
    def main_screen(self):
        self.title.text.set(self.mcp.name)
        buttons = [
            SmartButton(1,1,"Zones",self.zone_screen,"",1,"Times",20,"darkblue","white",5,5),
            SmartButton(2,1,"Modes",self.mode_screen,"",1,"Times",20,"darkgreen","white",5,5),
            SmartButton(3,1,"Thermostat",self.thermostat_screen,"",1,"Times",20,"darkorange","white",5,5),
        ]
        labels = []

        self.screen_wipe(buttons,labels)
    
    def thermostat_screen(self):
        self.title.text.set("Environment")
        buttons = [
            SmartButton(1,1,"Zones",self.zone_screen,"",1,"Times",20,"darkblue","white",5,5),
            SmartButton(2,1,"Modes",self.mode_screen,"",1,"Times",20,"darkgreen","white",5,5),
            SmartButton(3,1,"Thermostat",self.thermostat_screen,"",1,"Times",20,"darkorange","white",5,5),
        ]
        labels = []

        self.screen_wipe(buttons,labels)
    
    def mode_screen(self):
        self.title.text.set("Mode: "+self.mcp.mode)
        buttons = []
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
        buttons = []
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
        buttons = []
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
