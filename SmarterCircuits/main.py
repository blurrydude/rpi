import time
from os import name
import SmarterCircuitsMQTT
import SmarterConfiguration
from SmarterLogging import SmarterLog

def on_message(client, userdata, message):
    print(message) # placeholder

if __name__ == "__main__":
    SmarterLog.log("Main","starting...")
    config = SmarterConfiguration.SmarterConfig()
    while config.loaded is False:
        time.sleep(1)
    mqtt = SmarterCircuitsMQTT.SmarterMQTTClient(["192.168.1.200"],["shellies/#"],on_message)

    input("Press any key to stop...")

    SmarterLog.log("Main","stopping...")
    config.stop()
    mqtt.stop()
    time.sleep(5)
    SmarterLog.log("Main","stopped.")