import textwrap
from time import sleep
import SmarterCircuitsMQTT
import os
import time
import pyautogui
import tkinter as tk
import _thread
import beepy
 
class SmarterCircuitsPassiveMonitor:
    def __init__(self):
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.2.200"],["notifications"],self.on_message)
        self.running = True
        self.window = tk.Tk()
        self.labels = []
        self.display_on = False
        self.screen_timer = 0
        self.start()

    def start(self):
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()

        self.window.attributes("-fullscreen", 1)
        self.window.geometry(str(width)+"x"+str(height))
        self.window.configure(bg='black')
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
            # print("alerting: "+text)
            # pyautogui.alert(text, "HOUSE ALERT")
            labels = []
            wrapped = textwrap.wrap(text,24)#.split("\n")
            for i in range(len(wrapped)):
                labels.append(SmartLabel(i+1,1,wrapped[i],"Times",64,"black","white",5,5))
            self.screen_wipe(labels)
            if self.display_on == False:
                _thread.start_new_thread(self.screen_open, ())
                _thread.start_new_thread(self.screen_close_timer, ())
            else:
                self.screen_timer = 120

        except Exception as e: 
            error = str(e)
            print(error)
    
    def screen_open(self):
        if self.display_on is False:
            os.system("echo 'on 0.0.0.0' | cec-client -s -d 1")
            self.display_on = True
        # time.sleep(5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")
        # time.sleep(0.5)
        # beepy.beep(sound="ping")

    def screen_close_timer(self):
        if self.screen_timer >= 120:
            self.screen_timer = 0
            os.system("echo 'standby 0.0.0.0' | cec-client -s -d 1")
            self.display_on = False
        else:
            self.screen_timer = self.screen_timer + 1
            time.sleep(1)
            self.screen_close_timer()
    
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