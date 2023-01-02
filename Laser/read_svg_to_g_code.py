import xml.etree.ElementTree as ET

# Parse the SVG file
tree = ET.parse('/home/ian/rpi/Laser/image.svg')
root = tree.getroot()

# Iterate over the paths in the SVG file
for path in root.findall('.//{http://www.w3.org/2000/svg}path'):
  # Get the "d" attribute of the path element, which contains the path data
  path_data = path.get('d')

  # Split the path data into individual commands
  commands = path_data.split()

  # Iterate over the commands
  for command in commands:
    # Extract the command type and arguments
    cmd_type = command[0]
    cmd_args = command[1:]

    # Process the command based on its type
    if cmd_type == 'M':
      # "Move to" command
      x, y = cmd_args.split(',')
      print(f"G1 X{x} Y{y}")
    elif cmd_type == 'L':
      # "Line to" command
      x, y = cmd_args.split(',')
      print(f"G1 X{x} Y{y}")
    elif cmd_type == 'C':
      # "Curve to" command
      x1, y1, x2, y2, x, y = cmd_args.split(',')
      print(f"G3 X{x} Y{y} I{x1} J{y1} K{x2} L{y2}")
    elif cmd_type == 'A':
      # "Arc" command
      rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y = cmd_args.split(',')
      print(f"G2/G3 X{x} Y{y} R{rx} I{ry} J{x_axis_rotation} K{large_arc_flag} L{sweep_flag}")
    elif cmd_type == 'Z':
      # "Close path" command
      print("G0 Z0")
    elif cmd_type == 'z':
      # "Close path" command (alternate form)
      print("G0 Z0")
    elif cmd_type == 'H':
      # "Horizontal line to" command
      x = cmd_args
      print(f"G1 X{x}")
    elif cmd_type == 'V':
      # "Vertical line to" command
      y = cmd_args
      print(f"G1 Y{y}")
    elif cmd_type == 'S':
      # "Smooth curve to" command
      x2, y2, x, y = cmd_args.split(',')
      print(f"G3 X{x} Y{y} K{x2} L{y2}")
    elif cmd_type == 'T':
      # "Smooth quadratic curve to" command
      x, y = cmd_args.split(',')
      print(f"G2 X{x} Y{y}")
    elif cmd_type == 'Q':
      # "Quadratic curve to" command
      x1, y1, x, y = cmd_args.split(',')
      print(f"G2 X{x} Y{y} I{x1} J{y1}")
    elif cmd_type == 'circle':
      # "Circle" command
      cx, cy, r = cmd_args.split(',')
      print(f"G3 X{cx} Y{cy} R{r}")
