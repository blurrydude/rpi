import datetime
import time
#from buzzer import Buzzer

class Reminder:
    def __init__(self, time_of_day, days_of_week, notes, text):
        self.time_of_day = time_of_day
        self.days_of_week = days_of_week
        self.notes = notes
        self.text = text

#buzzer = Buzzer()

def check_reminders():
    # Get the current time and day of the week
    now = datetime.datetime.now()
    day_of_week = now.strftime("%A")
    time_of_day = now.strftime("%H:%M")
    
    # Iterate through the collection of reminders
    for reminder in reminders:
        # Check if the current time and day of the week match the reminder
        if time_of_day == reminder.time_of_day and day_of_week in reminder.days_of_week:
            #buzzer.play_music(reminder.notes)
            print(reminder.text)

# Create a collection of reminder objects
reminders = [
    Reminder("09:30", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "c--e--g--_", "Nicotine"),
    Reminder("10:40", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "c--e--g--_", "Stand Up Soon"),
    Reminder("12:10", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "c--e--g--_", ""),
    Reminder("18:00", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "c--e--g--_", "")
]

# Check for reminders every minute
while True:
    check_reminders()
    time.sleep(60)
