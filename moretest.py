import json
from datetime import datetime
f = open("timeCommands.json")
timeCommands = json.load(f)

now = datetime.now().strftime("%H:%M")
day = datetime.now().strftime("%a").lower()

for tc in timeCommands:
    if now in tc["days_time"] and day in tc["days_time"]:
        print("match")