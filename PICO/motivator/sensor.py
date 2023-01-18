from machine import ADC

#Celsius = (Fahrenheit – 32) * 5/9
#Fahrenheit = (Celsius * 9/5) + 32

class Sensor:
    def __init__(self):
        self.temperature = ADC(4)

    def get_temp(self):
        conversion_factor = 3.3 / (65535)
        reading = self.temperature.read_u16() * conversion_factor
        temperature_c = 27 - (reading - 0.706)/0.001721
        temperature_f = (temperature_c * 9/5) + 32
        return { "F": temperature_f, "C": temperature_c }