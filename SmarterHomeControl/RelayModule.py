class RelayModule:
    def __init__(self, id, ip_address, name, relay_id, location, zones, on_modes, off_modes):
        self.id = id
        self.ip_address = ip_address
        self.name = name
        self.relay_id = relay_id
        self.rollershutter = id.__contains__("switch25")
        self.location = location
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