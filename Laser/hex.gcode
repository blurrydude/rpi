(Hexagon)
G17 (set XY plane)
G20 (set units to inches)
G40 (cancel cutter radius compensation)
G49 (cancel tool length compensation)
G54 (use reference coordinate system 1)

(set hexagon size)
#1 = 10 (side length)

(calculate hexagon coordinates)
#2 = #1 * 0.866 (distance from center to corner)
#3 = #1 / 2 (distance from center to side)
#4 = #3 * 1.5 (distance between points on same side)
#5 = #1 (distance between points on opposite sides)

(set feed rate and spindle speed)
F100 (feed rate)
S1000 (spindle speed)

(move to starting point)
G0 Z0.1 (rapid move to starting point)
G0 X0 Y#2 (move to starting point)
G1 Z-0.1 (lower cutter)

(generate hexagon)
G1 X#3 Y#3 (move to first point)
G1 X#4 Y0 (move to second point)
G1 X#3 Y-#3 (move to third point)
G1 X0 Y-#2 (move to fourth point)
G1 X-#3 Y-#3 (move to fifth point)
G1 X-#4 Y0 (move to sixth point)
G1 X-#3 Y#3 (move to seventh point)
G1 X0 Y#2 (move back to starting point)

G0 Z0.1 (raise cutter)
G0 X0 Y0 (move to home position)
M2 (end program)
