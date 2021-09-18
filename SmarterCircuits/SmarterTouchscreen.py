import tkinter as tk
import _thread

class Touchscreen:
    def __init__(self, mcp):
        self.mcp = mcp
        self.window = tk.Tk()
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()

        self.window.attributes("-fullscreen", 1)
        self.window.geometry(str(width)+"x"+str(height))
        self.window.configure(bg='black')
        self.window.columnconfigure(0, minsize=width/3)
        self.window.columnconfigure(1, minsize=width/3)
        self.window.columnconfigure(2, minsize=width/3)
        _thread.start_new_thread(self.start, ())

    
    def start(self):
        self.window.mainloop()
