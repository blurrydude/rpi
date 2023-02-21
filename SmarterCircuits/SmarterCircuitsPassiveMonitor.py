import textwrap
from time import sleep
from datetime import datetime, timedelta
import SmarterCircuitsMQTT
import os
import time
import pyautogui
import tkinter as tk
import _thread
import beepy
# import cv2
 
class SmarterCircuitsPassiveMonitor:
    def __init__(self):
        self.discord_house_room = "976692334920077342"
        self.discord_debug_room = "922927575884505119"
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.2.200"],["notifications","remote_menu","camera_motion/#"],self.on_message)
        self.running = True
        # self.cameras = [
        #     cv2.VideoCapture("http://192.168.0.201/videostream.cgi?user=viewer&pwd=viewer"),
        #     cv2.VideoCapture("http://192.168.0.200/videostream.cgi?user=viewer&pwd=viewer")
        # ]
        self.window = tk.Tk()
        self.labels = []
        self.display_on = False
        self.screen_timer = 0
        self.font_size = 48
        self.line_char_width = 64
        self.lines = 12
        self.last_display = datetime.now()
        _thread.start_new_thread(self.sleep_timer, ())
        self.last_camera_motion = {}
        self.start()

    def send_discord_message(self, room, message):
        self.mqtt.publish("discord/out/"+room,message)

    def sleep_timer(self):
        while self.running is True:
            time.sleep(1)
            if datetime.now() > self.last_display + timedelta(seconds=60):
                self.last_display = datetime.now()
                self.do_display(["","",self.last_display.strftime("%A"),self.last_display.strftime("%-I:%M %p"),self.last_display.strftime("%B %-d")])
            # if datetime.now() > self.last_display + timedelta(seconds=40):
            #     self.screen_wipe([])
            #     self.last_display = datetime.now()


    def start(self):
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()

        self.window.attributes("-fullscreen", 1)
        self.window.geometry(str(width)+"x"+str(height))
        self.window.columnconfigure(0, minsize=width)
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
            # if "cap" in text:
            #     d = text.split(':')
            #     cam = int(d[1])
            #     sec = int(d[2])
            #     self.do_video_display(cam, sec)
            if text == "closecloseclose":
                self.stop()
                return
            if "camera_motion" in topic:
                camera = topic.split('/')[1]
                now = datetime.now()
                if camera not in self.last_camera_motion.keys():
                    self.last_camera_motion[camera] = now
                if now > self.last_camera_motion[camera] + timedelta(seconds=30):
                    self.send_discord_message(self.discord_house_room,f"motion on {camera}")
                    self.last_camera_motion[camera] = now
                return
            if "set font size" in text:
                self.font_size = int(text.split(' ')[3])
                return
            if "set line size" in text:
                self.line_char_width = int(text.split(' ')[3])
                return
            if "set line limit" in text:
                self.lines = int(text.split(' ')[3])
                return
            # print("alerting: "+text)
            # pyautogui.alert(text, "HOUSE ALERT")
            if "~~~" in text:
                wrapped = text.split('~~~')
            elif "\\n" in text:
                wrapped = text.split('\\n')
            elif "\n" in text:
                wrapped = text.split('\n')
            else:
                wrapped = textwrap.wrap(text,self.line_char_width)
            
            self.last_display = datetime.now()
            self.screen_open()
            self.do_display(wrapped)
            # if self.display_on == False:
            #     _thread.start_new_thread(self.screen_open, ())
            #     _thread.start_new_thread(self.screen_close_timer, ())
            # else:
            #     self.screen_timer = 120

        except Exception as e: 
            error = str(e)
            print(error)
    
    # def do_video_display(self, camera, seconds):
    #     cap = self.cameras[camera]
    #     now = datetime.now()
    #     fps = [ 20.0, 20.0 ]
    #     res = [(640, 480), (640, 480)]
    #     while(now > datetime.now() - timedelta(seconds=seconds)):
    #         ref, frame = cap.read()
    #     cv2.destroyAllWindows()
    
    def do_display(self, wrapped):
        labels = []
        lim = self.lines
        if wrapped[-1] == "":
            wrapped.pop(-1)
        if len(wrapped) > lim:
            newwrap = wrapped[:lim]
            for i in range(lim):
                wrapped.pop(0)
            for i in range(len(newwrap)):
                labels.append(SmartLabel(i+1,0,newwrap[i],"Times",self.font_size,"black","white",5,5))
            self.screen_wipe(labels)
            time.sleep(5)
            self.do_display(wrapped)
        else:
            wrapcount = len(wrapped)
            need = lim - wrapcount
            for i in range(wrapcount):
                labels.append(SmartLabel(i+1,0,wrapped[i],"Times",self.font_size,"black","white",5,5))
            for i in range(need):
                labels.append(SmartLabel(i+wrapcount+1,0,"","Times",self.font_size,"black","white",5,5))
            self.screen_wipe(labels)
    
    def screen_open(self):
        # if self.display_on is False:
            # self.mqtt.publish("smarter_circuits/command","turn on cabinet projector")
            # time.sleep(3)
            # os.system("echo 'on 0.0.0.0' | cec-client -s -d 1")
            # os.system("DISPLAY=:0 xset dpms force on")
            # self.display_on = True
        os.system("DISPLAY=:0 xset dpms force on")
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
            time.sleep(5)
            self.mqtt.publish("smarter_circuits/command","turn off cabinet projector")
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