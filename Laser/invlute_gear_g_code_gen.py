import math

# Number of teeth on the gear
n = int(input("Enter the number of teeth on the gear: "))

# Pitch diameter of the gear (distance between the pitch points of the gear)
p = float(input("Enter the pitch diameter of the gear (in mm): "))

# Pressure angle (angle between the line of action and the common normal)
alpha = float(input("Enter the pressure angle (in degrees): "))

# Module (ratio of the pitch diameter to the number of teeth)
m = p/n

# Base diameter (diameter of the pitch circle of the basic rack)
b = m*math.cos(alpha*math.pi/180)

# Distance from the center of the gear to the base diameter
r = p/2

# Angular resolution (angle between points in the involute curve)
angular_resolution = float(input("Enter the angular resolution (in degrees): "))

# Opening the G-Code file
f = open("/home/ian/rpi/Laser/gear.gcode", "w")

# Write the header information to the file
f.write("G21 (Use millimeters)\n")
f.write("G90 (Use absolute coordinates)\n")

# Starting point of the involute curve
x = r*math.cos(alpha*math.pi/180)
y = r*math.sin(alpha*math.pi/180)

# Move the tool to the starting point
f.write("G0 X{:.4f} Y{:.4f} (Move to the starting point)\n".format(x, y))

# Generate the G-Code for the involute curve
for i in range(1, int(360/angular_resolution)+1):
  angle = i*angular_resolution
  x = r*math.cos((alpha+angle)*math.pi/180) + r*math.tan(angle*math.pi/180)*math.sin((alpha+angle)*math.pi/180)
  y = r*math.sin((alpha+angle)*math.pi/180) - r*math.tan(angle*math.pi/180)*math.cos((alpha+angle)*math.pi/180)
  f.write("G1 X{:.4f} Y{:.4f}\n".format(x, y))

# End the G-Code file
f.write("G0 X0 Y0 (Move back to the origin)\n")
f.write("M30 (End program)")

# Close the file
f.close()
