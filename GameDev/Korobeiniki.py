import os
import time

# Define the frequencies and durations of the notes in the song
notes = [
    (784, 250), (784, 250), (988, 250), (784, 250), (659, 250), (523, 250),
    (587, 250), (494, 250), (784, 250), (784, 250), (988, 250), (784, 250),
    (659, 250), (523, 250), (587, 250), (494, 250), (523, 250), (880, 250),
    (880, 250), (698, 250), (659, 250), (523, 250), (587, 250), (494, 250)
]

# Play the song
for note in notes:
    os.system(f"play -n synth {note[1]/1000} sine {note[0]}")
    time.sleep(0.25)

print("Finished playing Korobeiniki!")
