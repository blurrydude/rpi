from machine import Pin, PWM, I2C

class Buttons:
    def __init__(self):
        self.button_g = Pin(16, Pin.IN, Pin.PULL_DOWN)
        self.button_y = Pin(17, Pin.IN, Pin.PULL_DOWN)
        self.button_b = Pin(18, Pin.IN, Pin.PULL_DOWN)
        self.button_r = Pin(19, Pin.IN, Pin.PULL_DOWN)
        self.button_r_pressed = False
        self.button_g_pressed = False
        self.button_b_pressed = False
        self.button_y_pressed = False
        self.since_last_press = 0
        self.button_down_r = None
        self.button_down_g = None
        self.button_down_b = None
        self.button_down_y = None
        self.button_up_r = None
        self.button_up_g = None
        self.button_up_b = None
        self.button_up_y = None

    def update(self):
        self.r_pressed = self.button_r.value() > 0
        self.g_pressed = self.button_g.value() > 0
        self.b_pressed = self.button_b.value() > 0
        self.y_pressed = self.button_y.value() > 0
        if self.r_pressed != self.button_r_pressed:
            self.button_r_pressed = self.r_pressed
            self.since_last_press = 0
            self.handle_r_button()
        if self.g_pressed != self.button_g_pressed:
            self.button_g_pressed = self.g_pressed
            self.since_last_press = 0
            self.handle_g_button()
        if self.b_pressed != self.button_b_pressed:
            self.button_b_pressed = self.b_pressed
            self.since_last_press = 0
            self.handle_b_button()
        if self.y_pressed != self.button_y_pressed:
            self.button_y_pressed = self.y_pressed
            self.since_last_press = 0
            self.handle_y_button()

    def handle_r_button(self):
        if self.button_r_pressed and self.button_down_r is not None:
            self.button_down_r()
        if self.button_r_pressed is False and self.button_up_r is not None:
            self.button_up_r()

    def handle_g_button(self):
        if self.button_g_pressed and self.button_down_g is not None:
            self.button_down_g()
        if self.button_g_pressed is False and self.button_up_g is not None:
            self.button_up_g()

    def handle_b_button(self):
        if self.button_b_pressed and self.button_down_b is not None:
            self.button_down_b()
        if self.button_b_pressed is False and self.button_up_b is not None:
            self.button_up_b()

    def handle_y_button(self):
        if self.button_y_pressed and self.button_down_y is not None:
            self.button_down_y()
        if self.button_y_pressed is False and self.button_up_y is not None:
            self.button_up_y()