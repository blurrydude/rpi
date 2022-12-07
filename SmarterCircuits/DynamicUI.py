from tkinter import * 
 
master = Tk() 

class DynamicButton:
    def __init__(self, x, y, w, h, bgcolor, color, text):
        self.x = x
        self.y = y
        self.px = 10
        self.py = 10
        self.w = w
        self.h = h
        self.color = color
        self.bgcolor = bgcolor
        self.text = text
        
    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.w, self.h, fill=self.bgcolor, outline=self.color) 
        canvas.create_text(self.x + self.px, self.y + self.py,text=self.text,fill=self.color)
    
    def click(self):
        print(self.text)

class Screen:
    def __init__(self):
        self.buttons = []
        self.labels = []
    
    def draw(self, canvas):
        for button in self.buttons:
            button.draw(canvas)
        
        for label in self.labels:
            label.draw(canvas)
    
    def click(self, x, y):
        for button in self.buttons:
            if x >= button.x and x <= button.x + button.w and y >= button.y and y <= button.y + button.h:
                button.click()

def click(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))
 
w = Canvas(master, width=1024, height=768) 
w.place(x=0, y=0) 

main_screen = Screen()
main_screen.buttons = [
    DynamicButton(20,20,200,36,"orange","green","THIS IS A TEST")
]
main_screen.draw(w)

# w.create_rectangle(0, 0, 1024, 768, fill="black", outline="green") 
# w.create_text(10,10,text="TESTING",fill="green")
#master.bind('<Motion>', motion)
 
master.bind('<Button-1>', click)
master.mainloop() 