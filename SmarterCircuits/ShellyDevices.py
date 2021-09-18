class RelayModule:
    def __init__(self, id, ip_address, name, relay_id, location, room, zones, on_modes, off_modes):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.relay_id = relay_id
        self.rollershutter = id.__contains__("switch25")
        self.location = location
        self.room = room
        self.zones = zones
        self.on_modes = on_modes
        self.off_modes = off_modes
        self.status = RelayModuleStatus()

class RelayModuleStatus:
    def __init__(self):
        self.relay = RelayStatus()
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

class DoorWindowSensor:
    def __init__(self, id, name, ip_address, open_command, close_command):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.open_command = open_command
        self.close_command = close_command
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
    def __init__(self, id, ip_address, room, auto_off, off_time_minutes):
        self.id = id
        self.ip_address = ip_address
        self.room = room
        self.commands = []
        self.auto_off = auto_off
        self.off_time_minutes = off_time_minutes
        self.status = MotionSensorStatus()

class MotionSensorStatus:
    def __init__(self):
        self.motion = False
        self.timestamp = 0
        self.active = False
        self.vibration = False
        self.lux = 0
        self.battery = 0

class MotionSensorCommand:
    def __init__(self, start, stop, conditions):
        self.start = start
        self.stop = stop
        self.conditions = conditions

class CommandCondition:
    def __init__(self, prop, comparitor, value):
        self.prop = prop
        self.comparitor = comparitor
        self.value = value
