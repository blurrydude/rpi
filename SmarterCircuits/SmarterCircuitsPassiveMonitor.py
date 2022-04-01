import textwrap
from time import sleep
import SmarterCircuitsMQTT
import os
import time
import pyautogui
import tkinter as tk
import _thread
import numpy
import pyaudio
import math
 
 
class ToneGenerator(object):
 
    def __init__(self, samplerate=44100, frames_per_buffer=4410):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.streamOpen = False
 
    def sinewave(self):
        if self.buffer_offset + self.frames_per_buffer - 1 > self.x_max:
            # We don't need a full buffer or audio so pad the end with 0's
            xs = numpy.arange(self.buffer_offset,
                              self.x_max)
            tmp = self.amplitude * numpy.sin(xs * self.omega)
            out = numpy.append(tmp,
                               numpy.zeros(self.frames_per_buffer - len(tmp)))
        else:
            xs = numpy.arange(self.buffer_offset,
                              self.buffer_offset + self.frames_per_buffer)
            out = self.amplitude * numpy.sin(xs * self.omega)
        self.buffer_offset += self.frames_per_buffer
        return out
 
    def callback(self, in_data, frame_count, time_info, status):
        if self.buffer_offset < self.x_max:
            data = self.sinewave().astype(numpy.float32)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return (None, pyaudio.paComplete)
 
    def is_playing(self):
        if self.stream.is_active():
            return True
        else:
            if self.streamOpen:
                self.stream.stop_stream()
                self.stream.close()
                self.streamOpen = False
            return False
 
    def play(self, frequency, duration, amplitude):
        self.omega = float(frequency) * (math.pi * 2) / self.samplerate
        self.amplitude = amplitude
        self.buffer_offset = 0
        self.streamOpen = True
        self.x_max = math.ceil(self.samplerate * duration) - 1
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)

class SmarterCircuitsPassiveMonitor:
    def __init__(self):
        self.mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.2.200"],["notifications"],self.on_message)
        self.running = True
        self.window = tk.Tk()
        self.labels = []
        self.display_on = False
        self.tonegen = ToneGenerator()
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
            wrapped = textwrap.wrap(text,32)#.split("\n")
            for i in range(len(wrapped)):
                labels.append(SmartLabel(i+1,1,wrapped[i],"Times",38,"black","white",5,5))
            self.screen_wipe(labels)
            self.tonegen.play(440, 2, 1)
            _thread.start_new_thread(self.screen_open, ())
            _thread.start_new_thread(self.screen_close_timer, ())

        except Exception as e: 
            error = str(e)
            print(error)
    
    def screen_open(self):
        if self.display_on is False:
            os.system("echo 'on 0.0.0.0' | cec-client -s -d 1")
            self.display_on = True

    def screen_close_timer(self):
        time.sleep(90)
        if self.display_on is True:
            os.system("echo 'standby 0.0.0.0' | cec-client -s -d 1")
            self.display_on = False
    
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