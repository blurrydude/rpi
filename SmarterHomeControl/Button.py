#! /usr/bin/env python3
from tkinter import * 

class Button:
    def __init__(self,ui,x,y,text,color,on_click = None):
        self.ui = ui
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.on_click = on_click
        
    def draw(self):
        unit = self.ui.brain.config.circuit_button_height
        self.ui.canvas.create_rectangle(self.x,self.y,self.x+self.ui.brain.config.circuit_button_width,self.y+self.ui.brain.config.circuit_button_height,fill=self.color,outline=self.color)
        self.ui.canvas.create_text(self.x+(self.ui.brain.config.circuit_button_width/2),self.y+(unit/2),text=self.text,fill="white", font='times '+str(self.ui.brain.config.circuit_button_font_size))
    
    def click(self, x, y):
        if self.on_click is None:
            return
        if self.ui.point_in_rect((x,y),[(self.x,self.y),(self.x+self.ui.brain.config.circuit_button_width,self.y+self.ui.brain.config.circuit_button_height)]):
            self.on_click()