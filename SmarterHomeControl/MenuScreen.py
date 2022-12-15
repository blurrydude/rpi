from Button import Button

class MenuScreen:
    def __init__(self, ui):
        self.ui = ui
        self.buttons = [
            Button(self.ui,self.ui.config.circuit_button_height,self.ui.config.circuit_button_height*2,"Climate Control","blue",self.climate_button_click),
            Button(self.ui,self.ui.config.circuit_button_height,self.ui.config.circuit_button_height*3+8,"Map Labels [off]","orange", self.labels_button_click),
            Button(self.ui,self.ui.config.circuit_button_height,self.ui.config.circuit_button_height*4+16,"Map Points [off]","green", self.points_button_click),
            Button(self.ui,self.ui.config.circuit_button_height,self.ui.config.circuit_button_height*5+24,"Fullscreen [on]","magenta", self.fullscreen_button_click),
            Button(self.ui,self.ui.config.circuit_button_height,self.ui.config.circuit_button_height*6+32,"Exit","red", self.exit_button_click)
        ]
    
    def draw(self):
        self.ui.draw_screen_title("MENU")
        self.ui.draw_home_button()
        self.ui.draw_mqtt_status()
        for button in self.buttons:
            button.draw()

    def click(self, x, y):
        if self.ui.detect_home_click(x,y):
            return
        for button in self.buttons:
            button.click(x,y)

    def climate_button_click(self):
        self.ui.switch_screen("climate")
    
    def labels_button_click(self):
        self.ui.show_room_names = self.ui.show_room_names == False
        show = "[on]"
        if self.ui.show_room_names is False:
            show = "[off]"
        self.buttons[1].text = 'Map Labels '+show
        self.ui.draw_all()
    
    def points_button_click(self):
        self.ui.show_points = self.ui.show_points == False
        show = "[on]"
        if self.ui.show_points is False:
            show = "[off]"
        self.buttons[2].text = 'Map Points '+show
        self.ui.draw_all()
    
    def fullscreen_button_click(self):
        self.ui.toggle_fullscreen()
        show = "[on]"
        if self.ui.fullscreen is False:
            show = "[off]"
        self.buttons[3].text = 'Fullscreen '+show
        self.ui.draw_all()
    
    def exit_button_click(self):
        self.ui.brain.stop()