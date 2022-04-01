from time import sleep
import SmarterCircuitsMQTT
import os
import time
import pyautogui
import tkinter as tk

class SmarterCircuitsPassiveMonitor:
    def __init__(self):
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.2.200"],["notifications"],self.on_message)
        self.running = True
        self.window = tk.Tk()
        self.labels = []
        self.display_on = False
        self.start()

    def start(self):
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()

        self.window.attributes("-fullscreen", 1)
        self.window.geometry(str(width)+"x"+str(height))
        self.window.configure(bg='black')
        self.window.columnconfigure(0, minsize=width*0.1)
        self.window.columnconfigure(1, minsize=width*0.8)
        self.window.columnconfigure(2, minsize=width*0.1)
        self.window.mainloop()
    
    def stop(self):
        self.window.destroy()
        self.mqtt.stop()
        self.running = False
    
    def on_message(self, client, userdata, message):
        try:
            topic = message.topic
            text = str(message.payload.decode("utf-8"))
            if text == "closecloseclose":
                self.stop()
                return
            if self.display_on is False:
                os.system("echo 'on 0.0.0.0' | cec-client -s -d 1")
                self.display_on = True
            # print("alerting: "+text)
            # pyautogui.alert(text, "HOUSE ALERT")
            self.screen_wipe([
                SmartLabel(2,2,text,"Times",32,"black","white",5,5)
            ])
            time.sleep(30)
            if self.display_on is True:
                os.system("echo 'standby 0.0.0.0' | cec-client -s -d 1")
                self.display_on = False

        except Exception as e: 
            error = str(e)
            print(error)
    
    def screen_wipe(self, labels):
        self.clear()
        self.labels = labels
        self.draw()

    def draw(self):
        for label in self.labels:
            label.draw()

    def clear(self):
        for label in self.labels:
            label.clear()
        
        self.labels = []

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

if __name__ == "__main__":
    scpm = SmarterCircuitsPassiveMonitor()