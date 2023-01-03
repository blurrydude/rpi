import math

# Define the basic parameters of the gear
num_teeth = 20
pitch_diameter = 50.0
pressure_angle = 20.0

# Calculate the points that define the involute curve
points = []
for i in range(num_teeth):
    angle = 2 * math.pi * i / num_teeth
    x = pitch_diameter * math.cos(angle)
    y = pitch_diameter * math.sin(angle)
    points.append((x, y))

# Generate G-Code commands to move the laser to each point
gcode = ""
for point in points:
    x, y = point
    gcode += "G1 X{:.3f} Y{:.3f} F100.0 S0.5\n".format(x, y)

# End the G-Code program
gcode += "M2"

# Save the G-Code to a file
with open("/home/ian/rpi/Laser/gear.gcode", "w") as f:
    f.write(gcode)