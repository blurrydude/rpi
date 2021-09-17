class RelayModule:
    def __init__(self, id, ip_address, name, location, room, zones, on_modes, off_modes):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.rollershutter = name.__contains__("switch25")
        self.location = location
        self.room = room
        self.zones = zones
        self.on_modes = on_modes
        self.off_modes = off_modes
        self.status = RelayModuleStatus()

class RelayModuleStatus:
    def __init__(self):
        self.relay_0 = RelayStatus()
        self.relay_1 = RelayStatus()
        self.input = []
        self.temperature = 0.0
        self.temperature_f = 0.0
        self.overtemperature = 0
        self.temperature_status = "Normal"
        self.voltage = 0.0

class RelayStatus:
    def __init__(self):
        self.on = False
        self.power = 0.0
        self.energy = 0
        self.command = ""

class DoorWindowSensor:
    def __init__(self, name, ip_address):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.status = DoorWindowSensorStatus()

class DoorWindowSensorStatus:
    def __init__(self):
        self.tilt = 0
        self.vibration = 0
        self.temperature = 0.0
        self.lux = 0
        self.illumination = "dark"
        self.battery = 0
        self.error = 0
        self.act_reasons = []
        self.state = "close"

class HumidityTemperatureSensor:
    def __init__(self, id, ip_address, name):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.status = HumidityTemperatureSensorStatus()

class HumidityTemperatureSensorStatus:
    def __init__(self):
        self.temperature = 0.0
        self.humidity = 0.0
        self.battery = 0

class MotionSensor:
    def __init__(self, id, ip_address, name):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.status = MotionSensorStatus()

class MotionSensorStatus:
    def __init__(self):
        self.motion = False
        self.timestamp = 0
        self.active = False
        self.vibration = False
        self.lux = 0
        self.battery = 0
    